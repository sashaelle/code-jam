# Team-Facing API

## `POST /team-facing/submit`

Submit a team's solution attempt for a problem.

### Request

**Headers**

| Key            | Value              |
|----------------|--------------------|
| `Content-Type` | `application/json` |

**Body**

| Field        | Type     | Description                        |
|--------------|----------|------------------------------------|
| `code`       | `string` | The submitted solution code        |
| `feedback`   | `string` | Feedback on the submission         |
| `id`         | `string` | Problem number                     |
| `problem_id` | `string` | Unique ID for problem              |
| `status`     | `string` | Submission status                  |
| `team`       | `string` | Team name or identifier            |
| `timestamp`  | `string` | ISO 8601 timestamp of submission   |

**Example**
```json
{
  "code": "print('Hello, World!')",
  "feedback": "Runs successfully",
  "id": "1",
  "problem_id": "2",
  "status": "pending",
  "team": "team_a",
  "timestamp": "2026-04-01T12:00:00Z"
}
```

### Response

In Python, executing a valid submission runs a `print` statement.
```python
print("Submission received")
```

---
