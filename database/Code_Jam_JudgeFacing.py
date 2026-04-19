"""
Includes: auth, db, submissions, scoring, scoreboard, and timer routes.
"""

import os
import secrets
import functools
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from datetime import datetime, timezone

from flask import Flask, Blueprint, request, jsonify, g


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────────────────────

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/codejam_dev"
)

def get_conn():
    """Return a new psycopg2 connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

@contextmanager
def db_cursor():
    """Context manager that yields a cursor and auto-commits / rolls back."""
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                yield cur
    finally:
        conn.close()

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS public.problems (
    problem_id  SERIAL PRIMARY KEY,
    problem_num INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS public.test_cases (
    test_case_id   SERIAL PRIMARY KEY,
    problem_id     INTEGER NOT NULL REFERENCES public.problems(problem_id) ON DELETE CASCADE,
    test_case_num  INTEGER NOT NULL,
    input_text     TEXT,
    expected_output TEXT,
    UNIQUE (problem_id, test_case_num)
);

CREATE TABLE IF NOT EXISTS public.submissions (
    submission_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id         INTEGER NOT NULL REFERENCES public.teams(team_id) ON DELETE CASCADE,
    problem_id      INTEGER NOT NULL REFERENCES public.problems(problem_id) ON DELETE CASCADE,
    submission_code TEXT NOT NULL,
    judge_feedback  TEXT,
    points          NUMERIC(6,2),
    language        VARCHAR(50),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'correct', 'incorrect', 'partial')),
    timestamp       TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS public.contest_timer (
    id              SERIAL PRIMARY KEY,
    duration_seconds INTEGER NOT NULL,
    started_at      TIMESTAMP WITHOUT TIME ZONE
);

-- Seed one timer row if empty
INSERT INTO public.contest_timer (duration_seconds)
SELECT 10800          -- 3 hours default
WHERE NOT EXISTS (SELECT 1 FROM public.contest_timer);
"""

def init_db():
    """Create missing tables on startup."""
    with db_cursor() as cur:
        cur.execute(_SCHEMA_SQL)
    print("[db] Schema initialised.")


# ─────────────────────────────────────────────────────────────────────────────
# AUTH / SESSION
# ─────────────────────────────────────────────────────────────────────────────

# In-memory session store (swap for Redis/DB in production)
_active_sessions: dict[str, dict] = {}  # token -> {"account_id": ..., "judge_id": ...}

def create_session(token: str, account_id: str, judge_id: int):
    _active_sessions[token] = {"account_id": account_id, "judge_id": judge_id}

def revoke_session(token: str):
    _active_sessions.pop(token, None)

def lookup_session(token: str):
    return _active_sessions.get(token)

def judge_required(f):
    """Reject requests that do not carry a valid judge session token."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.removeprefix("Bearer ").strip()
        session = lookup_session(token)
        if not session:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.session = session  # available to the route as flask.g.session
        return f(*args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# BLUEPRINTS
# ─────────────────────────────────────────────────────────────────────────────

auth_bp        = Blueprint("auth",        __name__)
submissions_bp = Blueprint("submissions", __name__)
scoring_bp     = Blueprint("scoring",     __name__)
scoreboard_bp  = Blueprint("scoreboard",  __name__)
time_bp        = Blueprint("time",        __name__)


# ─────────────────────────────────────────────────────────────────────────────
# AUTH ROUTES  –  /api/judge
# ─────────────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def judge_login():
    """
    POST /api/judge/login
    Authenticate a judge account.

    Request body (JSON):
        username  : str  – judge's username
        password  : str  – plaintext password (compared to stored hash via pgcrypto)

    Response 200:
        { "token": "<bearer token>", "judge_id": <int>, "display_name": "<str>" }

    Response 401:
        { "error": "Invalid credentials" }
    """
    body = request.get_json(silent=True) or {}
    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    with db_cursor() as cur:
        # Verify credentials – accounts table stores password_hash.
        # In production this should use pgcrypto crypt(); for the dev dump
        # passwords are stored in plain text, so we compare directly.
        cur.execute(
            """
            SELECT a.account_id, a.password_hash, a.role, a.is_active,
                   j.judge_id, j.display_name
            FROM   public.accounts a
            JOIN   public.judges   j ON j.account_id = a.account_id
            WHERE  a.username = %s
            """,
            (username,),
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "Invalid credentials"}), 401

    if not row["is_active"]:
        return jsonify({"error": "Account is disabled"}), 403

    if row["role"] != "judge":
        return jsonify({"error": "Account does not have judge privileges"}), 403

    # Password check – plain-text comparison for dev seed data.
    # TODO: replace with `crypt(password, password_hash)` once hashing is set up.
    if password != row["password_hash"]:
        return jsonify({"error": "Invalid credentials"}), 401

    token = secrets.token_hex(32)
    create_session(token, str(row["account_id"]), row["judge_id"])

    return jsonify({
        "token":        token,
        "judge_id":     row["judge_id"],
        "display_name": row["display_name"],
    }), 200


# ─────────────────────────────────────────────────────────────────────────────
# SUBMISSIONS ROUTES  –  /api
# ─────────────────────────────────────────────────────────────────────────────

@submissions_bp.route("/submissions", methods=["POST"])
def create_submission():
    """
    POST /api/submissions
    Accept a problem-solution submission from a team.

    Request body (JSON):
        team_id         : int
        problem_id      : int
        submission_code : str
        language        : str  (optional)

    Response 201:
        { "submission_id": "<uuid>", "status": "pending", "timestamp": "<iso>" }
    """
    body = request.get_json(silent=True) or {}

    team_id         = body.get("team_id")
    problem_id      = body.get("problem_id")
    submission_code = body.get("submission_code", "").strip()
    language        = body.get("language", "unknown")

    if not all([team_id, problem_id, submission_code]):
        return jsonify({"error": "team_id, problem_id, and submission_code are required"}), 400

    with db_cursor() as cur:
        cur.execute("SELECT team_id FROM public.teams WHERE team_id = %s", (team_id,))
        if not cur.fetchone():
            return jsonify({"error": f"team_id {team_id} not found"}), 404

        cur.execute("SELECT problem_id FROM public.problems WHERE problem_id = %s", (problem_id,))
        if not cur.fetchone():
            return jsonify({"error": f"problem_id {problem_id} not found"}), 404

        cur.execute(
            """
            INSERT INTO public.submissions (team_id, problem_id, submission_code, language)
            VALUES (%s, %s, %s, %s)
            RETURNING submission_id, status, timestamp
            """,
            (team_id, problem_id, submission_code, language),
        )
        row = cur.fetchone()

    return jsonify({
        "submission_id": str(row["submission_id"]),
        "status":        row["status"],
        "timestamp":     row["timestamp"].isoformat(),
    }), 201


@submissions_bp.route("/submissions", methods=["GET"])
@judge_required
def list_submissions():
    """
    GET /api/submissions
    Retrieve submissions for judges to review and score.

    Query params (all optional):
        status      : filter by status  (pending | correct | incorrect | partial)
        team_id     : filter by team
        problem_id  : filter by problem

    Response 200:
        { "submissions": [ { submission fields … }, … ] }
    """
    status     = request.args.get("status")
    team_id    = request.args.get("team_id",    type=int)
    problem_id = request.args.get("problem_id", type=int)

    filters = []
    params  = []

    if status:
        filters.append("s.status = %s")
        params.append(status)
    if team_id:
        filters.append("s.team_id = %s")
        params.append(team_id)
    if problem_id:
        filters.append("s.problem_id = %s")
        params.append(problem_id)

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    query = f"""
        SELECT
            s.submission_id,
            s.team_id,
            t.team_name,
            t.team_number,
            s.problem_id,
            p.problem_num,
            s.language,
            s.status,
            s.points,
            s.judge_feedback,
            s.timestamp
        FROM   public.submissions s
        JOIN   public.teams    t ON t.team_id    = s.team_id
        JOIN   public.problems p ON p.problem_id = s.problem_id
        {where_clause}
        ORDER BY s.timestamp DESC
    """

    with db_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    submissions = [
        {
            "submission_id":  str(r["submission_id"]),
            "team_id":        r["team_id"],
            "team_name":      r["team_name"],
            "team_number":    r["team_number"],
            "problem_id":     r["problem_id"],
            "problem_num":    r["problem_num"],
            "language":       r["language"],
            "status":         r["status"],
            "points":         float(r["points"]) if r["points"] is not None else None,
            "judge_feedback": r["judge_feedback"],
            "timestamp":      r["timestamp"].isoformat(),
        }
        for r in rows
    ]

    return jsonify({"submissions": submissions}), 200


# ─────────────────────────────────────────────────────────────────────────────
# SCORING ROUTES  –  /api/judge
# ─────────────────────────────────────────────────────────────────────────────

VALID_STATUSES = {"correct", "incorrect", "partial"}

@scoring_bp.route("/score/<submission_id>", methods=["POST"])
@judge_required
def score_submission(submission_id: str):
    """
    POST /api/judge/score/<submission_id>
    Mark a submission as correct/incorrect/partial, assign points, and add feedback.

    Path param:
        submission_id : UUID

    Request body (JSON):
        status         : str   – "correct" | "incorrect" | "partial"
        points         : float – score awarded (required when status is "correct" or "partial")
        judge_feedback : str   – optional written feedback for the team

    Response 200:
        { "submission_id": "...", "status": "...", "points": ..., "judge_feedback": "..." }

    Response 404:
        { "error": "Submission not found" }
    """
    body           = request.get_json(silent=True) or {}
    status         = body.get("status", "").strip().lower()
    points         = body.get("points")
    judge_feedback = body.get("judge_feedback", "").strip() or None

    if status not in VALID_STATUSES:
        return jsonify({
            "error": f"status must be one of: {', '.join(sorted(VALID_STATUSES))}"
        }), 400

    if status in ("correct", "partial"):
        if points is None:
            return jsonify({"error": "points is required when status is 'correct' or 'partial'"}), 400
        try:
            points = float(points)
            if points < 0:
                raise ValueError
        except (TypeError, ValueError):
            return jsonify({"error": "points must be a non-negative number"}), 400
    else:
        points = 0.0

    with db_cursor() as cur:
        cur.execute(
            """
            UPDATE public.submissions
            SET    status         = %s,
                   points         = %s,
                   judge_feedback = %s
            WHERE  submission_id  = %s
            RETURNING submission_id, status, points, judge_feedback, team_id, problem_id
            """,
            (status, points, judge_feedback, submission_id),
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "Submission not found"}), 404

    return jsonify({
        "submission_id":  str(row["submission_id"]),
        "team_id":        row["team_id"],
        "problem_id":     row["problem_id"],
        "status":         row["status"],
        "points":         float(row["points"]) if row["points"] is not None else None,
        "judge_feedback": row["judge_feedback"],
        "scored_by":      g.session["judge_id"],
    }), 200


# ─────────────────────────────────────────────────────────────────────────────
# SCOREBOARD ROUTES  –  /api
# ─────────────────────────────────────────────────────────────────────────────

@scoreboard_bp.route("/scoreboard", methods=["GET"])
def get_scoreboard():
    """
    GET /api/scoreboard
    Return current team rankings and scores (leaderboard + submission summary).

    Response 200:
        {
            "rankings": [
                {
                    "rank":         1,
                    "team_number":  "team_1",
                    "team_name":    "Team 1",
                    "total_points": 150.0,
                    "problems": [
                        { "problem_num": 1, "status": "correct",   "points": 100.0 },
                        { "problem_num": 2, "status": "incorrect",  "points": 0.0 },
                        …
                    ]
                },
                …
            ],
            "submissions": [ … ]
        }
    """
    with db_cursor() as cur:
        # Per-team totals
        cur.execute(
            """
            SELECT
                t.team_number,
                t.team_name,
                COALESCE(SUM(s.points), 0)  AS total_points
            FROM   public.teams t
            LEFT JOIN public.submissions s
                   ON s.team_id = t.team_id
                  AND s.status  IN ('correct', 'partial')
            GROUP BY t.team_id, t.team_number, t.team_name
            ORDER BY total_points DESC, t.team_number
            """
        )
        team_rows = cur.fetchall()

        # Best submission per team/problem (latest scored)
        cur.execute(
            """
            WITH ranked AS (
                SELECT
                    s.team_id,
                    t.team_number,
                    p.problem_num,
                    s.status,
                    s.points,
                    ROW_NUMBER() OVER (
                        PARTITION BY s.team_id, s.problem_id
                        ORDER BY
                            CASE s.status
                                WHEN 'correct'   THEN 1
                                WHEN 'partial'   THEN 2
                                WHEN 'incorrect' THEN 3
                                ELSE 4
                            END,
                            s.timestamp DESC
                    ) AS rn
                FROM  public.submissions s
                JOIN  public.teams    t ON t.team_id    = s.team_id
                JOIN  public.problems p ON p.problem_id = s.problem_id
                WHERE s.status != 'pending'
            )
            SELECT team_number, problem_num, status, points
            FROM   ranked
            WHERE  rn = 1
            ORDER  BY team_number, problem_num
            """
        )
        problem_rows = cur.fetchall()

        # All scored submissions (for the submissions feed)
        cur.execute(
            """
            SELECT
                s.submission_id,
                t.team_name,
                p.problem_num,
                s.status,
                s.points,
                s.timestamp
            FROM  public.submissions s
            JOIN  public.teams    t ON t.team_id    = s.team_id
            JOIN  public.problems p ON p.problem_id = s.problem_id
            WHERE s.status != 'pending'
            ORDER BY s.timestamp DESC
            LIMIT 100
            """
        )
        sub_rows = cur.fetchall()

    problems_by_team: dict[str, list] = {}
    for r in problem_rows:
        problems_by_team.setdefault(r["team_number"], []).append({
            "problem_num": r["problem_num"],
            "status":      r["status"],
            "points":      float(r["points"]) if r["points"] is not None else 0.0,
        })

    rankings = []
    for rank, r in enumerate(team_rows, start=1):
        rankings.append({
            "rank":         rank,
            "team_number":  r["team_number"],
            "team_name":    r["team_name"],
            "total_points": float(r["total_points"]),
            "problems":     problems_by_team.get(r["team_number"], []),
        })

    submissions = [
        {
            "submission_id": str(r["submission_id"]),
            "team_name":     r["team_name"],
            "problem_num":   r["problem_num"],
            "status":        r["status"],
            "points":        float(r["points"]) if r["points"] is not None else None,
            "timestamp":     r["timestamp"].isoformat(),
        }
        for r in sub_rows
    ]

    return jsonify({"rankings": rankings, "submissions": submissions}), 200


# ─────────────────────────────────────────────────────────────────────────────
# TIMER ROUTES  –  /api
# ─────────────────────────────────────────────────────────────────────────────

def _get_timer_row(cur):
    cur.execute(
        "SELECT id, duration_seconds, started_at FROM public.contest_timer LIMIT 1"
    )
    return cur.fetchone()


@time_bp.route("/time", methods=["GET"])
def get_time():
    """
    GET /api/time
    Return time information for the contest.

    Response 200:
        {
            "status":             "not_started" | "running" | "finished",
            "duration_seconds":   10800,
            "elapsed_seconds":    450,
            "remaining_seconds":  10350,
            "started_at":         "2026-04-17T10:00:00"   (null if not started)
        }
    """
    with db_cursor() as cur:
        row = _get_timer_row(cur)

    if not row:
        return jsonify({"error": "Timer not configured"}), 500

    now        = datetime.now(timezone.utc).replace(tzinfo=None)
    duration   = row["duration_seconds"]
    started_at = row["started_at"]

    if started_at is None:
        return jsonify({
            "status":            "not_started",
            "duration_seconds":  duration,
            "elapsed_seconds":   0,
            "remaining_seconds": duration,
            "started_at":        None,
        }), 200

    elapsed   = max(0, int((now - started_at).total_seconds()))
    remaining = max(0, duration - elapsed)
    status    = "finished" if remaining == 0 else "running"

    return jsonify({
        "status":            status,
        "duration_seconds":  duration,
        "elapsed_seconds":   elapsed,
        "remaining_seconds": remaining,
        "started_at":        started_at.isoformat(),
    }), 200


@time_bp.route("/time/start", methods=["POST"])
@judge_required
def start_timer():
    """
    POST /api/time/start
    Start (or restart) the contest timer. Judge authentication required.

    Optional request body (JSON):
        duration_seconds : int  – override the default contest duration

    Response 200:
        { "started_at": "<iso>", "duration_seconds": 10800 }

    Response 409:
        { "error": "Contest is already running" }
    """
    body     = request.get_json(silent=True) or {}
    override = body.get("duration_seconds")

    with db_cursor() as cur:
        row = _get_timer_row(cur)
        if not row:
            return jsonify({"error": "Timer not configured"}), 500

        started_at = row["started_at"]
        duration   = row["duration_seconds"]
        now        = datetime.now(timezone.utc).replace(tzinfo=None)

        if started_at is not None:
            elapsed   = (now - started_at).total_seconds()
            remaining = duration - elapsed
            if remaining > 0:
                return jsonify({"error": "Contest is already running"}), 409

        if override is not None:
            try:
                duration = int(override)
                if duration <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                return jsonify({"error": "duration_seconds must be a positive integer"}), 400

        cur.execute(
            """
            UPDATE public.contest_timer
            SET    started_at       = %s,
                   duration_seconds = %s
            WHERE  id               = %s
            """,
            (now, duration, row["id"]),
        )

    return jsonify({
        "started_at":       now.isoformat(),
        "duration_seconds": duration,
    }), 200


# ─────────────────────────────────────────────────────────────────────────────
# APP FACTORY
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)

app.register_blueprint(auth_bp,        url_prefix="/api/judge")
app.register_blueprint(submissions_bp, url_prefix="/api")
app.register_blueprint(scoring_bp,     url_prefix="/api/judge")
app.register_blueprint(scoreboard_bp,  url_prefix="/api")
app.register_blueprint(time_bp,        url_prefix="/api")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
