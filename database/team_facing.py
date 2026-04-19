"""
Team-Facing API
===============
POST /team-facing/submit  – Submit a solution attempt for a problem.
GET  /team-facing/submit  – Retrieve a team's own submissions.



import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from datetime import datetime, timezone

from flask import Flask, Blueprint, request, jsonify


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE  (shared connection helper)
# ─────────────────────────────────────────────────────────────────────────────

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/codejam_dev"
)

def _get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

@contextmanager
def _db_cursor():
    conn = _get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                yield cur
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# BLUEPRINT
# ─────────────────────────────────────────────────────────────────────────────

team_bp = Blueprint("team", __name__)


# ─────────────────────────────────────────────────────────────────────────────
# POST /team-facing/submit
# ─────────────────────────────────────────────────────────────────────────────

@team_bp.route("/submit", methods=["POST"])
def create_submission():
    """
    Submit a team's solution attempt for a problem.

    Request body (JSON):
        code        : str  – submitted solution code           (required)
        team        : str  – team name or team_number          (required)
        id          : str  – problem number (problem_num)      (required unless problem_id given)
        problem_id  : str  – numeric problem_id in DB          (required unless id given)
        status      : str  – ignored on intake; always stored as "pending"
        feedback    : str  – ignored on intake; set by judges later
        timestamp   : str  – ISO 8601 client timestamp         (optional; server time used if absent)

    Response 201:
        {
            "submission_id" : "<uuid>",
            "team"          : "<team_number>",
            "team_name"     : "<team_name>",
            "problem_num"   : <int>,
            "status"        : "pending",
            "timestamp"     : "<iso>"
        }

    Error responses:
        400  missing / invalid fields
        404  team or problem not found
    """
    body = request.get_json(silent=True) or {}

    # ── Required fields ──────────────────────────────────────────────────────
    code     = body.get("code", "").strip()
    team_ref = body.get("team", "").strip()          # team_number or team_name

    if not code:
        return jsonify({"error": "'code' is required"}), 400
    if not team_ref:
        return jsonify({"error": "'team' is required"}), 400

    # ── Problem lookup: accept either `id` (problem_num) or `problem_id` ─────
    problem_num_raw = body.get("id")
    problem_id_raw  = body.get("problem_id")

    if problem_num_raw is None and problem_id_raw is None:
        return jsonify({"error": "Either 'id' (problem number) or 'problem_id' is required"}), 400

    # ── Optional fields ───────────────────────────────────────────────────────
    # `status` and `feedback` from the client are intentionally ignored:
    # status is always set to 'pending' on submission; feedback is judge-only.
    language  = body.get("language", "unknown")
    client_ts = body.get("timestamp")

    # Parse or discard the client timestamp – we store server time in the DB
    # but return whichever the client sent (or server time if absent).
    server_ts = datetime.now(timezone.utc).replace(tzinfo=None)
    display_ts = server_ts

    if client_ts:
        try:
            # Accept ISO 8601 with or without trailing Z
            display_ts = datetime.fromisoformat(client_ts.replace("Z", "+00:00"))
        except ValueError:
            return jsonify({"error": "Invalid 'timestamp' format; expected ISO 8601"}), 400

    # ── Resolve team ──────────────────────────────────────────────────────────
    with _db_cursor() as cur:
        cur.execute(
            """
            SELECT team_id, team_number, team_name
            FROM   public.teams
            WHERE  team_number = %s OR team_name = %s
            LIMIT  1
            """,
            (team_ref, team_ref),
        )
        team_row = cur.fetchone()

    if not team_row:
        return jsonify({"error": f"Team '{team_ref}' not found"}), 404

    # ── Resolve problem ───────────────────────────────────────────────────────
    with _db_cursor() as cur:
        if problem_id_raw is not None:
            try:
                pid = int(problem_id_raw)
            except (TypeError, ValueError):
                return jsonify({"error": "'problem_id' must be an integer"}), 400

            cur.execute(
                "SELECT problem_id, problem_num FROM public.problems WHERE problem_id = %s",
                (pid,),
            )
        else:
            try:
                pnum = int(problem_num_raw)
            except (TypeError, ValueError):
                return jsonify({"error": "'id' (problem number) must be an integer"}), 400

            cur.execute(
                "SELECT problem_id, problem_num FROM public.problems WHERE problem_num = %s",
                (pnum,),
            )
        problem_row = cur.fetchone()

    if not problem_row:
        identifier = problem_id_raw if problem_id_raw is not None else problem_num_raw
        return jsonify({"error": f"Problem '{identifier}' not found"}), 404

    # ── Insert submission ─────────────────────────────────────────────────────
    with _db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.submissions
                (team_id, problem_id, submission_code, language, status, timestamp)
            VALUES
                (%s, %s, %s, %s, 'pending', %s)
            RETURNING submission_id, status, timestamp
            """,
            (
                team_row["team_id"],
                problem_row["problem_id"],
                code,
                language,
                server_ts,
            ),
        )
        row = cur.fetchone()

    return jsonify({
        "submission_id": str(row["submission_id"]),
        "team":          team_row["team_number"],
        "team_name":     team_row["team_name"],
        "problem_num":   problem_row["problem_num"],
        "status":        row["status"],
        "timestamp":     row["timestamp"].isoformat(),
    }), 201


# ─────────────────────────────────────────────────────────────────────────────
# GET /team-facing/submit
# ─────────────────────────────────────────────────────────────────────────────

@team_bp.route("/submit", methods=["GET"])
def list_team_submissions():
    """
    Retrieve submissions for a given team.

    Query params:
        team        : str  – team_number or team_name          (required)
        problem_id  : int  – filter by problem_id              (optional)
        status      : str  – filter by status                  (optional)

    Response 200:
        {
            "team":        "<team_number>",
            "team_name":   "<team_name>",
            "submissions": [
                {
                    "submission_id" : "<uuid>",
                    "problem_num"   : <int>,
                    "status"        : "pending" | "correct" | "incorrect" | "partial",
                    "points"        : <float|null>,
                    "feedback"      : "<str|null>",
                    "timestamp"     : "<iso>"
                },
                …
            ]
        }

    Error responses:
        400  missing 'team' param
        404  team not found
    """
    team_ref   = request.args.get("team", "").strip()
    problem_id = request.args.get("problem_id", type=int)
    status     = request.args.get("status", "").strip() or None

    if not team_ref:
        return jsonify({"error": "'team' query parameter is required"}), 400

    # ── Resolve team ──────────────────────────────────────────────────────────
    with _db_cursor() as cur:
        cur.execute(
            """
            SELECT team_id, team_number, team_name
            FROM   public.teams
            WHERE  team_number = %s OR team_name = %s
            LIMIT  1
            """,
            (team_ref, team_ref),
        )
        team_row = cur.fetchone()

    if not team_row:
        return jsonify({"error": f"Team '{team_ref}' not found"}), 404

    # ── Build query ───────────────────────────────────────────────────────────
    filters = ["s.team_id = %s"]
    params  = [team_row["team_id"]]

    if problem_id:
        filters.append("s.problem_id = %s")
        params.append(problem_id)
    if status:
        filters.append("s.status = %s")
        params.append(status)

    where_clause = "WHERE " + " AND ".join(filters)

    query = f"""
        SELECT
            s.submission_id,
            p.problem_num,
            s.status,
            s.points,
            s.judge_feedback,
            s.timestamp
        FROM   public.submissions s
        JOIN   public.problems p ON p.problem_id = s.problem_id
        {where_clause}
        ORDER BY s.timestamp DESC
    """

    with _db_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    submissions = [
        {
            "submission_id": str(r["submission_id"]),
            "problem_num":   r["problem_num"],
            "status":        r["status"],
            "points":        float(r["points"]) if r["points"] is not None else None,
            "feedback":      r["judge_feedback"],
            "timestamp":     r["timestamp"].isoformat(),
        }
        for r in rows
    ]

    return jsonify({
        "team":        team_row["team_number"],
        "team_name":   team_row["team_name"],
        "submissions": submissions,
    }), 200


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE ENTRY POINT
# Run directly:  python team_facing.py
# Or register in combined app.py:
#   from team_facing import team_bp
#   app.register_blueprint(team_bp, url_prefix="/team-facing")
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(team_bp, url_prefix="/team-facing")
    app.run(debug=True, port=5001)
