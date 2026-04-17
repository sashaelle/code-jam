# Team-Facing Compiler IDE

## Dependencies

### Python
Install the required Python packages:
```bash
pip install flask
pip install flask-socketio
pip install localStoragePy
```

### Node.js
Download and install Node.js from https://nodejs.org/

### MinGW (C++ Support)
Download and install MinGW from https://sourceforge.net/projects/mingw/

In the MinGW Installation Manager, mark the following packages for installation:
- `mingw32-gcc-g++` — the actual g++ compiler
- `mingw32-base-bin`
- `msys-base-bin`

Then click **Installation → Apply Changes**.

After installation, add MinGW to your system PATH:
```bash
C:\MinGW\bin
```

Go to **System Environment Variables → Path → Edit → New** and add the path above. Restart your terminal after.

Verify the installation:
```bash
g++ --version
```

## Running the App
```bash
cd team-facing
python app.py
```
The command might also be:
```bash
py app.py
```


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