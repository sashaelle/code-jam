from flask import Flask, render_template, request
from markupsafe import escape
import subprocess

app = Flask(__name__)


@app.route("/team-facing")
def index():
    return render_template('render.html')


@app.route("/team-facing/compile_button", methods=["POST"])
def compile_button():
    fp = "submissions/submission.py"
    data = request.get_json()
    code = data["code"]
    print("Code: ", code)
    with open(fp, "w") as f:
        f.write(code)
    output = subprocess.run(["python", fp], capture_output=True, text=True, timeout=2)

    # Store somewhere

    """process = subprocess.Popen(["python", fp],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               text=True,
                               bufsize=1)
    output_lines = []
    for line in process.stdout:
        output_lines.append(line.rstrip())

    error_lines = []
    for line in process.stdout:
        error_lines.append(line.rstrip())

    process.wait()"""

    return {
        "stdout": output.stdout,
        "stderr": output.stderr,
    }


@app.route("/team-facing/close")
def close():
    print("Closed file")

@app.route("/team-facing/submit", methods=["POST"])
def submit():
    print("Submit")