from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

#Store and track submissions and scoring
START_SCORE = 20 #starting score is 20
scores = {} #scores[team][problem_id] = {score, wrong_submissions, teams_before, solved}
submissions = [] #store submissions
submission_counter = 1 #counts the number of submissions

#Track correct solve order per problem
solved_order = {} #solved_order[problem_id] = [team1, team2, ...]


#Currently, this API call returns if the judge backend is running
@app.route("/api/time", methods=["GET"])
def get_time():
    #Returns timestamp & message that backend is working
    return jsonify({
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Judge backend is running"
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

    #Return the message that the submission is received, the submission_id, and timestamp
    return jsonify({
        "message": "Submission received",
        "submission_id": submission["id"],
        "timestamp": timestamp
    }), 201


#API call that returns submissions that are waiting to be scored
@app.route("/api/submissions", methods=["GET"])
def get_submissions():
    #Extracts the status parameter
    status_filter = request.args.get("status")

    #Reassigns the submission list to a variable for easier use
    result = submissions

    #Only include submissions that match the extracted status
    if status_filter:
        result = [s for s in result if s["status"] == status_filter]

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


#API call that returns the scoreboard (all scores)
@app.route("/api/scoreboard", methods=["GET"])
def scoreboard():
    #Returns the team/problem/scoring information
    return jsonify(scores)


if __name__ == "__main__":
    app.run(debug=True)
