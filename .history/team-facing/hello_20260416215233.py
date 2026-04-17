from importlib.resources import path
import os
import shutil
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from localStoragePy import localStoragePy
import subprocess
import threading

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
localStorage = localStoragePy('team-facing-namespace', 'text')

processes = {}

@app.route("/team-facing")
def index():
    return render_template('render.html')

@socketio.on("connect")
def handle_connect():
    print("Client has been connected")
    #Remove after database is connected
    emit("clear_local_storage")

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


process = None
is_stopped = False
current_language = None
@socketio.on('compile')
def compile_button(data):
    socketio.emit("compile_process")

    global process, is_stopped
    global current_language
    problem_number = data["problem_number"]
    current_language = data["language"]
    is_stopped = False

    # File path for the submission code
    fp = f"submissions/submission{current_language}"
    print("File path: ", fp)
    print("Problem number: ",problem_number)
    code = data["code"]

    submission_id = request.sid
    sid = request.sid

    print(code)
    with open(fp, "w", newline="\n") as f:
        f.write(code)

    # if java, run a subprocess for javac
    # run popen for java
    if current_language == ".java":
        subprocess.run(["javac", fp])
        process = subprocess.Popen(["java", fp],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   bufsize=0)
    elif current_language == ".py":
        process = subprocess.Popen(["python", "-u", fp],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=False,
                                   bufsize=1)
    elif current_language == ".js":
        process = subprocess.Popen(["node", fp],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   bufsize=0)
    elif current_language == ".cpp":
        
        process = subprocess.Popen([".\\submissions\\submission.exe"],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   bufsize=0)

    processes[submission_id] = process

    thread = threading.Thread(target=stream_output, args=(current_language, process, sid), daemon=True)
    thread.start()
    
    process.wait()

    print("PROGRAM STOPPED") # Here is where the program stops
    socketio.emit("process_done")


    '''error_lines = []
    for line in process.stderr:
        error_lines.append(line.rstrip())'''

    # if line contains input --> make stop_printing = True

@socketio.on('input_added')
def input_added(data):
    global current_language
    sid = request.sid
    process_input = processes.get(sid)
    print("Output Process: ", process_input.stdout)
    print("Input Process: ", process_input.stdin)
    output_data = ""

    if current_language == ".java":
        output_data = (data + "\n")
    elif current_language == ".py":
        output_data = (data + "\n").encode("utf-8")
    elif current_language == ".js":
        output_data = (data + "\n")
    elif current_language == ".cpp":
        output_data = (data + "\n")

    process_input.stdin.write(output_data)
    process_input.stdin.flush()
    stream_output(current_language, process_input, sid)

def stream_output(current_language, p, sid = None):
    while True:
        if is_stopped:
            break
        char = ""
        if current_language == ".java":
            char = p.stdout.read(1)
            if char == "\n":
                char = "\n\r"
            socketio.emit("output", char, to=sid)
        elif current_language == ".py":
            char = p.stdout.read1(1024)
            socketio.emit("output", char.decode("utf-8"), to=sid)
        elif current_language == ".js":
            char = p.stdout.read(1)
            if char == "\n":
                char = "\n\r"
            socketio.emit("output", char, to=sid)
        elif current_language == ".cpp":
            char = p.stdout.read(1)
            if char == "\n":
                char = "\n\r"
            socketio.emit("output", char, to=sid)
        if not char or char == "":
            stream_error_output(current_language, p, sid)
            break
        if p.poll() is not None:
            break

def stream_error_output(current_language, p, sid = None):
    print("Current error language: ", current_language)
    char = ""
    if current_language == ".java":
        process.wait()
        char = p.stderr.read()
        char = char.replace("\n", "\n\r")
        if char and is_stopped == False:
            socketio.emit("error-output", char, to=sid)
    elif current_language == ".js":
        process.wait()
        char = p.stderr.read()
        char = char.replace("\n", "\n\r")
        if char and is_stopped == False:
            socketio.emit("error-output", char, to=sid)
    elif current_language == ".cpp":
        process.wait()
        char = p.stderr.read()
        char = char.replace("\n", "\n\r")
        if char and is_stopped == False:
            socketio.emit("error-output", char, to=sid)
    while True:
        if current_language == ".py":
            if is_stopped == False:
                char = p.stderr.read1(1024)
                socketio.emit("error-output", char.decode("utf-8"), to=sid)
        if p.poll() is not None:
            break

@socketio.on('process_done')
def process_done():
    process.stdin.flush()

@socketio.on('stop_process')
def stop_process():
    global process, is_stopped
    is_stopped = True

    process.stdin.close()
    process.stdout.close()
    process.kill()
    process.wait()

    print("Process killed.")
    # Clear the submission folder
    path = "submissions"
    shutil.rmtree(path)
    os.makedirs(path)
    print("Submission folder cleared")

@app.route("/team-facing/close")
def close():
    print("Closed file")

@app.route("/team-facing/submit", methods=["POST"])
def submit():
    print("Submit")

if __name__ == "__main__":
    socketio.run(app, debug=True)