# Team-Facing API



---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the database

Set the `DATABASE_URL` environment variable to point to your PostgreSQL instance:

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/codejam_dev
```

If the variable is not set, the app defaults to:
```
postgresql://postgres:postgres@localhost:5432/codejam_dev
```

### 3. Run standalone

```bash
python team_facing.py
```

The API will start on `http://localhost:5001` by default.

### 4. Or mount inside the combined app

Add the following two lines to `app.py`:

```python
from team_facing import team_bp
app.register_blueprint(team_bp, url_prefix="/team-facing")
```

---

## Endpoints

### `POST /team-facing/submit`

Submit a solution attempt for a problem.

**Headers**

| Key            | Value              |
|----------------|--------------------|
| `Content-Type` | `application/json` |

**Request Body**

| Field        | Type     | Required | Description                                                                 |
|--------------|----------|----------|-----------------------------------------------------------------------------|
| `code`       | `string` | ✅ Yes   | The submitted solution code                                                 |
| `team`       | `string` | ✅ Yes   | Team number or team name (e.g. `"team_1"` or `"The Coders"`)               |
| `id`         | `string` | ✅ Yes*  | Problem number (`problem_num`). Required if `problem_id` is not provided   |
| `problem_id` | `string` | ✅ Yes*  | Unique problem ID in the database. Required if `id` is not provided        |
| `language`   | `string` | ❌ No    | Programming language of the submission (defaults to `"unknown"`)           |
| `timestamp`  | `string` | ❌ No    | ISO 8601 client timestamp. Server time is stored; this is returned as-is   |
| `status`     | `string` | —        | Ignored. Submissions are always stored as `pending`                        |
| `feedback`   | `string` | —        | Ignored. Feedback is set by judges only                                    |

*Either `id` or `problem_id` must be provided.

**Example Request**

```json
{
  "code": "print('Hello, World!')",
  "team": "team_a",
  "id": "1",
  "language": "python",
  "timestamp": "2026-04-01T12:00:00Z"
}
```

**Response `201 Created`**

```json
{
  "submission_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "team":          "team_a",
  "team_name":     "Team Alpha",
  "problem_num":   1,
  "status":        "pending",
  "timestamp":     "2026-04-01T12:00:00"
}
```

**Error Responses**

| Code | Reason                                      |
|------|---------------------------------------------|
| `400` | Missing required fields or invalid format  |
| `404` | Team or problem not found in the database  |

---

### `GET /team-facing/submit`

Retrieve all submissions for a given team, including judge feedback and points once scored.

**Query Parameters**

| Parameter    | Type     | Required | Description                                                  |
|--------------|----------|----------|--------------------------------------------------------------|
| `team`       | `string` | ✅ Yes   | Team number or team name                                     |
| `problem_id` | `int`    | ❌ No    | Filter results by problem ID                                 |
| `status`     | `string` | ❌ No    | Filter by status: `pending`, `correct`, `incorrect`, `partial` |

**Example Request**

```
GET /team-facing/submit?team=team_a&status=pending
```

**Response `200 OK`**

```json
{
  "team":      "team_a",
  "team_name": "Team Alpha",
  "submissions": [
    {
      "submission_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "problem_num":   1,
      "status":        "pending",
      "points":        null,
      "feedback":      null,
      "timestamp":     "2026-04-01T12:00:00"
    }
  ]
}
```

**Error Responses**

| Code  | Reason                              |
|-------|-------------------------------------|
| `400` | `team` query parameter is missing   |
| `404` | Team not found in the database      |

---

## Database Schema

The API reads from and writes to the following tables:

```
submissions       — stores all submission records
teams             — used to resolve team name/number to team_id
problems          — used to resolve problem number to problem_id
```

The following fields are **never set by teams** and are managed exclusively by judges:

- `judge_feedback`
- `points`
- `status` (beyond the initial `pending`)

---

## Notes

- **Authentication** — the current implementation does not require teams to authenticate. If team-level auth is needed, the `account_id` FK on the `teams` table supports adding it.
- **Timestamps** — the server timestamp is always what gets stored in the database. The client-provided `timestamp` field is validated and echoed back in the response but does not affect the stored record.
- **Status on submission** — status is always set to `pending` regardless of what the client sends. Only judges can update it via the Judge-Facing API.
