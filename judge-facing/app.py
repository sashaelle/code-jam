from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

START_SCORE = 20

# Track submissions and scoring
# Structure: scores[team][problem_id] = {score, wrong_submissions, teams_before, solved}
scores = {}

# Track correct solve order per problem
# solved_order[problem_id] = [team1, team2, ...]
solved_order = {}

@app.route("/api/time", methods=["GET"])
def get_time():
    return jsonify({
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Judge backend is running"
    })

@app.route("/api/submissions", methods=["POST"])
def submit_code():
    data = request.get_json()

    team = data.get("team")
    problem_id = str(data.get("problem_id"))
    code = data.get("code")

    if not team or not problem_id or not code:
        return jsonify({"error": "Missing team, problem_id, or code"}), 400

    timestamp = datetime.utcnow().isoformat()

    # Initialize structures if needed
    scores.setdefault(team, {})
    solved_order.setdefault(problem_id, [])

    if problem_id not in scores[team]:
        scores[team][problem_id] = {
            "score": START_SCORE,
            "wrong_submissions": 0,
            "teams_before": 0,
            "solved": False
        }

    team_problem = scores[team][problem_id]

    # If already solved, ignore further submissions
    if team_problem["solved"]:
        return jsonify({
            "message": "Problem already solved",
            "score": team_problem["score"]
        })

    # Placeholder judge logic
    is_correct = "correct" in code.lower()

    if is_correct:
        team_problem["solved"] = True
        team_problem["teams_before"] = len(solved_order[problem_id])
        penalty = team_problem["teams_before"]
        team_problem["score"] = max(
            0, team_problem["score"] - penalty
        )
        solved_order[problem_id].append(team)

        return jsonify({
            "team": team,
            "problem_id": problem_id,
            "result": "correct",
            "teams_solved_before": team_problem["teams_before"],
            "final_score": team_problem["score"],
            "timestamp": timestamp
        })

    else:
        team_problem["wrong_submissions"] += 1
        team_problem["score"] = max(0, team_problem["score"] - 1)

        return jsonify({
            "team": team,
            "problem_id": problem_id,
            "result": "incorrect",
            "current_score": team_problem["score"],
            "feedback": "Output did not match expected result.",
            "timestamp": timestamp
        })

@app.route("/api/scoreboard", methods=["GET"])
def scoreboard():
    return jsonify(scores)

if __name__ == "__main__":
    app.run(debug=True)
