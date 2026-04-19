# Judge Backend – Judge-Facing API

A Flask + PostgreSQL backend for the CodeJam judge-facing endpoints.

## Setup

```bash
pip install -r requirements.txt

# Point at your Postgres instance (defaults to localhost/codejam_dev)
export DATABASE_URL="postgresql://postgres:<password>@localhost:5432/codejam_dev"

python app.py
```

`init_db()` runs on startup and creates any missing tables (`submissions`,
`problems`, `test_cases`, `contest_timer`) without touching the existing schema.

---

## Endpoints

### Authentication

| Method | Path | Auth | Owner |
|--------|------|------|-------|
| POST | `/api/judge/login` | none | Security / Judge-Facing |

**POST /api/judge/login**
```json
// Request
{ "username": "judge", "password": "codejamjudge" }

// Response 200
{ "token": "<bearer>", "judge_id": 1, "display_name": "Judge 1" }
```
Include the token in all protected requests:
`Authorization: Bearer <token>`

---

### Submissions

| Method | Path | Auth | Owner |
|--------|------|------|-------|
| POST | `/api/submissions` | none | Team-Facing (stub here for testing) |
| GET  | `/api/submissions` | judge | Judge-Facing |

**POST /api/submissions** *(dummy for testing scoring logic)*
```json
// Request
{ "team_id": 1, "problem_id": 1, "submission_code": "print('hello')", "language": "python" }

// Response 201
{ "submission_id": "<uuid>", "status": "pending", "timestamp": "2026-04-17T..." }
```

**GET /api/submissions**
Optional query params: `?status=pending`, `?team_id=1`, `?problem_id=2`
```json
// Response 200
{ "submissions": [ { "submission_id": "...", "team_name": "...", ... } ] }
```

---

### Scoring

| Method | Path | Auth | Owner |
|--------|------|------|-------|
| POST | `/api/judge/score/<submission_id>` | judge | Judge-Facing |

**POST /api/judge/score/\<submission_id\>**
```json
// Request
{ "status": "correct", "points": 100, "judge_feedback": "Great solution!" }
// status options: "correct" | "incorrect" | "partial"
// points required for "correct" and "partial"; auto-set to 0 for "incorrect"

// Response 200
{ "submission_id": "...", "status": "correct", "points": 100.0, ... }
```

---

### Scoreboard

| Method | Path | Auth | Owner |
|--------|------|------|-------|
| GET | `/api/scoreboard` | none | Judge-Facing / Design |

**GET /api/scoreboard**
```json
// Response 200
{
  "rankings": [
    {
      "rank": 1,
      "team_number": "team_1",
      "team_name": "Team 1",
      "total_points": 150.0,
      "problems": [
        { "problem_num": 1, "status": "correct", "points": 100.0 }
      ]
    }
  ],
  "submissions": [ { "team_name": "...", "problem_num": 1, "status": "correct", ... } ]
}
```

---

### Timer

| Method | Path | Auth | Owner |
|--------|------|------|-------|
| GET  | `/api/time`       | none  | Judge-Facing |
| POST | `/api/time/start` | judge | Judge-Facing |

**GET /api/time**
```json
// Response 200
{
  "status": "running",
  "duration_seconds": 10800,
  "elapsed_seconds": 120,
  "remaining_seconds": 10680,
  "started_at": "2026-04-17T10:00:00"
}
// status: "not_started" | "running" | "finished"
```

**POST /api/time/start**
```json
// Request (duration_seconds optional, defaults to 10800 / 3 hrs)
{ "duration_seconds": 7200 }

// Response 200
{ "started_at": "2026-04-17T10:00:00", "duration_seconds": 7200 }
// Response 409 if already running
```

---

## File structure

```
judge_backend/
├── app.py              # Flask app + blueprint registration
├── db.py               # DB connection, context manager, DDL init
├── auth.py             # Session store + @judge_required decorator
├── requirements.txt
└── routes/
    ├── auth.py         # POST /api/judge/login
    ├── submissions.py  # POST & GET /api/submissions
    ├── scoring.py      # POST /api/judge/score/<id>
    ├── scoreboard.py   # GET /api/scoreboard
    └── time.py         # GET /api/time, POST /api/time/start
```
