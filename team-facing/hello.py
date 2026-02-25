from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import threading

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

processes = {}

@app.route("/team-facing")
def index():
    return render_template('render.html')

@socketio.on("connect")
def handle_connect():
    print("Client has been connected")

# On refresh --> disconnect
@socketio.on("disconnect")
def handle_disconnect():
    socket_id = request.sid
    process = processes.pop(socket_id, None)

    if process:
        process.terminate()
    print("Client disconnected")

@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', json)


#@app.route("/team-facing/compile_button", methods=["POST"])
process = None
@socketio.on('compile')
def compile_button(data):
    global process
    fp = "submissions/submission.py"
    #data = request.get_json()
    code = data["code"]
    submission_id = request.sid
    sid = request.sid
    print("Code: ", code)
    with open(fp, "w") as f:
        f.write(code)
    #output = subprocess.run(["python", fp], capture_output=True, text=True, timeout=2)

    # Store somewhere

    process = subprocess.Popen(["python", "-u", fp],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=False,
                               bufsize=1)

    processes[submission_id] = process

    stream_output(process, sid)

    thread = threading.Thread(target=stream_output, daemon=True)
    thread.start()
    process.wait()
    socketio.emit("process_done")

    '''error_lines = []
    for line in process.stderr:
        error_lines.append(line.rstrip())'''

    # if line contains input --> make stop_printing = True

@socketio.on('input_added')
def input_added(data):
    sid = request.sid
    process_input = processes.get(sid)
    print("Output Process: ", process_input.stdout)
    print("Input Process: ", process_input.stdin)
    output_data = (data + "\n").encode("utf-8")
    process_input.stdin.write(output_data)
    process_input.stdin.flush()
    stream_output(process_input, sid)

def stream_output(p, sid = None):
    while True:
        char = p.stdout.read1(1024)
        if not char:
            break
        socketio.emit("output", char.decode("utf-8"), to=sid)
        if p.poll() is not None:
            break

@socketio.on('process_done')
def process_done():
    print("PROCESS DONE")
    #process.stdin.flush()

@app.route("/team-facing/close")
def close():
    print("Closed file")

@app.route("/team-facing/submit", methods=["POST"])
def submit():
    print("Submit")

if __name__ == "__main__":
    socketio.run(app, debug=True)