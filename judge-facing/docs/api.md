# Judge Backend API

This document defines the initial API endpoints for the judge backend.

## Judge Authentication
**POST /api/judge/login**
- This API call will authenticate a judge so they can access judge-only features.
- This API call will be created by the Security team, but the Judge-Facing team will need to access it.

## Submissions
**POST /api/submissions**
- This API call will accept a problem solution submission from a team.
- This API call will be created by the Team-Facing team, but the Judge-Facing team will need to retrieve it.
- *This is our dummy API call to test the scoring logic*

**GET /api/submissions**
- This API call will retrieve submissions for judges to review and score.
- This API call will be created by the Judge-Facing team to know which teams submitted, which problems were submitted, and which submissions need to be scored.

## Scoring
**POST /api/judge/score/{submission_id}**
- This API call will allow a judge to score a specific submission.
- This API call will be created by the Judge-Facing team to mark submissions as correct/incorrect, score the submissions, and add feedback.

## Scoreboard
**GET /api/scoreboard**
- This API call will returns current team rankings and scores (leaderboard & current submissions).
- This API call will be created by the Judge-Facing team, but designed by the Design team.
- *This will depend on how the design team organizes the pages for how we will put in team scores*

## Utilities
**GET /api/time**
- This API call will return the time remaining for the contest.
- This API call will be created by the Judge-Facing team to show the time remaining.

This list will be shared across teams to keep backend logic consistent.
