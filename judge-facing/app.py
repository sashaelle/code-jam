from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

#Store and track submissions and scoring
START_SCORE = 20 #starting score is 20
scores = {} #scores[team][problem_id] = {score, wrong_submissions, teams_before, solved}
submissions = [] #store submissions
submission_counter = 1 #counts the number of submissions

#Store recent submissions for live feed
recent_submissions = [] #stores recent submissions
MAX_RECENT = 10 #defining recent submissions as the last 10

#Track correct solve order per problem
solved_order = {} #solved_order[problem_id] = [team1, team2, ...]

#Keeps track of if the contest has started
contest = {
    "start_time": None, #no set starting time
    "duration_minutes": 60  #how long contest is
}

#API to start the timer for the contestents
#No input necessary
@app.route("/api/time/start", methods=["POST"])
def start_contest():
    #Returns error message if contest has already started
    if contest["start_time"] is not None:
        return jsonify({"error": "Contest already started"}), 400

    #Sets the current time as the start time
    contest["start_time"] = datetime.utcnow()

    #Returns the message that the contest has started
    return jsonify({
        "message": "Contest started",
        "start_time": contest["start_time"].isoformat()
    })

#Turns those remaining seconds into an understanding format
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}:{minutes:02}:{secs:02}"

#API call to get the start time, end time, and time remaining
@app.route("/api/time", methods=["GET"])
def get_time():
    #Returns error is contest hasn't started yet
    if contest["start_time"] is None:
        return jsonify({
            "started": False,
            "message": "Contest has not started"
        })

    #Gets the time now for start time and finds when the contest ends
    now = datetime.utcnow()
    end_time = contest["start_time"] + timedelta(minutes=contest["duration_minutes"])
    remaining = end_time - now

    #Finds how many seconds are remaining
    seconds_remaining = int(remaining.total_seconds())

    #If the time remaining is 0, end the contest
    if seconds_remaining <= 0:
        return jsonify({
            "started": True,
            "ended": True,
            "time_remaining": "0:00:00"
        })

    #Return the time information after contest is started
    return jsonify({
        "started": True,
        "ended": False,
        "current_time": now.isoformat(),
        "start_time": contest["start_time"].isoformat(),
        "end_time": end_time.isoformat(),
        "time_remaining_seconds": format_time(seconds_remaining)
    })

#Temporary API call where students post a submission
#Required {team, problem_id, code}
#Every submission is stored in submission list and updates submission_counter by 1
@app.route("/api/submissions", methods=["POST"])
def submit_code():
    global submission_counter

    #Requests the data from the json
    data = request.get_json()

    #Receives the team name, problem_id, and code
    team = data.get("team")
    problem_id = str(data.get("problem_id"))
    code = data.get("code")

    #Returns error message if missing necessary information
    if not team or not problem_id or not code:
        return jsonify({"error": "Missing team, problem_id, or code"}), 400

    timestamp = datetime.utcnow().isoformat()

    #Initialize team/problem score state
    scores.setdefault(team, {})
    solved_order.setdefault(problem_id, [])

    #Initialize team/problem score for a new problem 
    if problem_id not in scores[team]:
        scores[team][problem_id] = {
            "score": START_SCORE,
            "wrong_submissions": 0,
            "teams_before": 0,
            "solved": False
        }

    #Create the submission record
    submission = {
        "id": submission_counter,
        "team": team,
        "problem_id": problem_id,
        "code": code,
        "timestamp": timestamp,
        "status": "pending",
        "feedback": None
    }

    #Add the submission to the submission list and update the submission_counter
    submissions.append(submission)
    submission_counter += 1

    # Add to recent submissions
    recent_submissions.insert(0, submission)

    # Keep only most recent submissions 
    if len(recent_submissions) > MAX_RECENT: 
        recent_submissions.pop()

    #Return the message that the submission is received, the submission_id, and timestamp
    return jsonify({
        "message": "Submission received",
        "submission_id": submission["id"],
        "timestamp": timestamp
    }), 201

#API call that returns submissions that are waiting to be scored
@app.route("/api/submissions", methods=["GET"])
def get_submissions():
    result = []

    for s in submissions:
        team = s["team"]
        problem_id = s["problem_id"]

        entry = s.copy()

        # Attach score only if judged
        if s["status"] in ["correct", "incorrect"]:
            team_problem = scores[team][problem_id]
            entry["score"] = team_problem["score"]

        result.append(entry)

    #Return a list of submissions
    return jsonify(result), 200

#API call where judges post the result of a submission 
#Required {submission_id, correct/incorrect, feedback} 
@app.route("/api/judge/score/<int:submission_id>", methods=["POST"])  
def judge_score(submission_id):  
    #Requests the data from the json 
    data = request.get_json()  

    #Receives if submission is correct (true/false) and custom feedback 
    correct = data.get("correct")  
    feedback = data.get("feedback", "")  

    #Returns error message if missing necessary information 
    if correct is None:  
        return jsonify({"error": "Missing 'correct' field"}), 400  

    #Find the requested submission  
    submission = next((s for s in submissions if s["id"] == submission_id), None)  

    #Returns error message if the submission doesn't exist 
    if not submission:  
        return jsonify({"error": "Submission not found"}), 404  

    #Returns error message if the submission has been reviewed 
    if submission["status"] != "pending":  
        return jsonify({"error": "Submission already scored"}), 400  

    #Create necessary variables 
    team = submission["team"]  
    problem_id = submission["problem_id"]  
    team_problem = scores[team][problem_id]  

    #If the submission is correct 
    if correct:  
        submission["status"] = "correct"  
        submission["feedback"] = feedback  

        #If the team hasn't solved this problem, mark problem as solved and add 1 to the teams_before 
        if not team_problem["solved"]:  
            team_problem["solved"] = True  
            team_problem["teams_before"] = len(solved_order[problem_id])  

            #Create variable of how many teams answered before & remove a point from the final score 
            penalty = team_problem["teams_before"]  
            team_problem["score"] = max(0, team_problem["score"] - penalty)  

            #Add the solved submission to the solved_order list 
            solved_order[problem_id].append(team)  

        #Return the submission_id, that the submission is correct, their final score, and how many teams answered that problem correctly before 
        return jsonify({  
            "submission_id": submission_id,  
            "result": "correct",  
            "final_score": team_problem["score"],  
            "teams_solved_before": team_problem["teams_before"] 
        }), 200  

    #If the submission is incorrect 
    else:  
        submission["status"] = "incorrect"  
        submission["feedback"] = feedback  

        #Add to wrong submission counter & remove a point from the final score 
        team_problem["wrong_submissions"] += 1  
        team_problem["score"] = max(0, team_problem["score"] - 1)  

        #Return the submission_id, that the submission is incorrect, their current score, and how many wrong submission that team submitted 
        return jsonify({  
            "submission_id": submission_id,  
            "result": "incorrect",  
            "current_score": team_problem["score"],  
            "wrong_submissions": team_problem["wrong_submissions"]
        }), 200 

#API call where judges see the submission and its information
@app.route("/api/judge/submission/<int:submission_id>", methods=["GET"])
def get_submission(submission_id):
    #Search for the submission based on its submission_id
    submission = next((s for s in submissions if s["id"] == submission_id), None)

    #Error message if the submission isn't found
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    return jsonify(submission), 200

#API call where judges get the recommended score of a submission 
@app.route("/api/judge/recommend_score/<int:submission_id>")
def recommend_score(submission_id):
    #Search for the submission based on its submission_id
    submission = next((s for s in submissions if s["id"] == submission_id), None)

    #Error message if the submission isn't found
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    team = submission["team"]
    problem_id = submission["problem_id"]
    team_problem = scores[team][problem_id]

    #Return the recommended score for the submission and the reasoning why
    return jsonify({
        "score": team_problem["score"],
        "wrong_submissions": team_problem["wrong_submissions"],
        "teams_before": team_problem["teams_before"]
    })

#API call where judges post the final score of a submission 
#Required {final_score} 
@app.route("/api/judge/final_score/<int:submission_id>", methods=["POST"])
def overwrite_final_score(submission_id):
    data = request.get_json()
    final_score = data.get("final_score")

    #Error message if the the final score is invalid
    if final_score is None or final_score < 0:
        return jsonify({"error": "Invalid final_score"}), 400

    #Find the submission
    submission = next((s for s in submissions if s["id"] == submission_id), None)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    team = submission["team"]
    problem_id = submission["problem_id"]
    team_problem = scores[team][problem_id]

    #Update the final score
    team_problem["score"] = final_score

    #Mark the submission as reviewed if not already
    submission["status"] = "correct"
    submission["final_score_overwritten"] = True

    return jsonify({"submission_id": submission_id, "final_score": final_score}), 200  
    
#API call that returns the recent submissions (last 10)
@app.route("/api/submissions/recent", methods=["GET"])
def recent_feed():
    recent = []

    #Only returns the 10 most recent submissions that aren't 'pending'
    for s in recent_submissions:
        if s["status"] in ["correct", "incorrect"]:
            team = s["team"]
            problem_id = s["problem_id"]
            team_problem = scores[team][problem_id]

            recent.append({
                "team": team,
                "problem_id": problem_id,
                "status": s["status"],
                "score": team_problem["score"] if s["status"] == "correct" else 0,
                "timestamp": s["timestamp"]
            })
    return jsonify(recent)

#API call that returns the scoreboard (all scores)
@app.route("/api/scoreboard", methods=["GET"])
def scoreboard():
    return jsonify(scores)

#API call that renders the HTML page for the leaderboard & recent submissions
@app.route("/scoreboard")
def scoreboard_page():
    return render_template("scoreboard.html")

#API call that renders the HTML page for the submissions
@app.route("/submissions")
def submissions_page():
    return render_template("submissions.html")

#API call that renders the HTML page for the judges scoring the submissions
@app.route("/scoring")
def scoring_page():
    return render_template("scoring.html")

if __name__ == "__main__":
    app.run(debug=True)
