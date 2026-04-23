from importlib.resources import path
import os
import shutil
import re
from flask import Flask, render_template, request, redirect, jsonify
from flask_socketio import SocketIO, emit
from localStoragePy import localStoragePy
import subprocess
import threading

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
localStorage = localStoragePy('team-facing-namespace', 'text')

processes = {}
stop_flags = {}

@app.route("/team-facing")
def index():
    return render_template('render.html')

@app.route("/")
def root():
    return redirect("/team-facing")

@socketio.on("connect")
def handle_connect():
    #Remove after database is connected
    emit("clear_local_storage")

# On refresh --> disconnect
@socketio.on("disconnect")
def handle_disconnect():
    socket_id = request.sid
    process = processes.pop(socket_id, None)
    stop_flags.pop(socket_id, None)

    if process:
        process.terminate()

    safe_sid = socket_id.replace("-", "_")
    workdir = os.path.join("submissions", safe_sid)
    try:
        if os.path.exists(workdir):
            shutil.rmtree(workdir)
    except:
        pass

@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', json)

current_language = None
@socketio.on('compile')
def compile_button(data):
    socketio.emit("compile_process", to=request.sid)

    problem_number = data["problem_number"]
    current_language = data["language"]

    # File path for the submission code
    os.makedirs("submissions", exist_ok=True)
    code = data["code"]
    java_class_name = None

    submission_id = request.sid
    sid = request.sid

    stop_flags[sid] = False

    safe_sid = sid.replace("-", "_")
    workdir = os.path.join("submissions", safe_sid)
    os.makedirs(workdir, exist_ok=True)

    if current_language == ".py":
        fp = os.path.join(workdir, "submission.py")

    elif current_language == ".js":
        fp = os.path.join(workdir, "submission.js")

    elif current_language == ".cpp":
        fp = os.path.join(workdir, "submission.cpp")

    elif current_language == ".java":
        class_match = re.search(r"\b(?:public\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)", code)
        if class_match:
            java_class_name = class_match.group(1)
            fp = os.path.join(workdir, f"{java_class_name}.java")
        else:
            fp = os.path.join(workdir, "Main.java")
            java_class_name = "Main"

    with open(fp, "w", newline="\n") as f:
        f.write(code)

    # if java, run a subprocess for javac
    # run popen for java
    if current_language == ".java":
        compile_result = subprocess.run(["javac", fp], capture_output=True, text=True)
        if compile_result.returncode != 0:
            socketio.emit("error-output", compile_result.stderr.replace("\n", "\n\r"), to=sid)
            socketio.emit("process_done", to=sid)
            return

        class_name = java_class_name or os.path.splitext(os.path.basename(fp))[0]
        process = subprocess.Popen(["java", "-cp", workdir, class_name],
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
                                   text=True,
                                   bufsize=1)
    elif current_language == ".js":
        process = subprocess.Popen(["node", fp],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   bufsize=0)
    elif current_language == ".cpp":
        exe_path = os.path.join(workdir, "submission")

        result = subprocess.run(
            ["g++", fp, "-o", exe_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            socketio.emit("error-output", result.stderr.replace("\n", "\n\r"), to=sid)
            socketio.emit("process_done", to=sid)
            return

        process = subprocess.Popen(
            [exe_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    processes[submission_id] = process

    thread = threading.Thread(target=stream_output, args=(current_language, process, sid), daemon=True)
    thread.start()

    watcher = threading.Thread(target=watch_process, args=(process, sid), daemon=True)
    watcher.start()


    '''error_lines = []
    for line in process.stderr:
        error_lines.append(line.rstrip())'''

    # if line contains input --> make stop_printing = True

@socketio.on('input_added')
def input_added(data):
    sid = request.sid
    process_input = processes.get(sid)

    if process_input is None or process_input.poll() is not None:
        return

    output_data = data + "\n"
    process_input.stdin.write(output_data)
    process_input.stdin.flush()

def watch_process(p, sid):
    p.wait()
    processes.pop(sid, None)
    stop_flags.pop(sid, None)

    safe_sid = sid.replace("-", "_")
    workdir = os.path.join("submissions", safe_sid)
    try:
        if os.path.exists(workdir):
            shutil.rmtree(workdir)
    except:
        pass

    socketio.emit("process_done", to=sid)

def stream_output(current_language, p, sid = None):
    while True:
        if stop_flags.get(sid):
            break
        char = ""
        if current_language == ".java":
            char = p.stdout.read(1)
            if char == "\n":
                char = "\n\r"
            socketio.emit("output", char, to=sid)
        elif current_language == ".py":
            char = p.stdout.read(1)
            if char == "\n":
                char = "\n\r"
            socketio.emit("output", char, to=sid)
        elif current_language == ".js":
            char = p.stdout.read(1)
            if char == "\n":
                char = "\n\r"
            socketio.emit("output", char, to=sid)
        elif current_language == ".cpp":
            char = p.stdout.read(1)
            if stop_flags.get(sid):
                break
            socketio.emit("output", char, to=sid)
        if not char or char == "":
            stream_error_output(current_language, p, sid)
            break
        if p.poll() is not None:
            break

def stream_error_output(current_language, p, sid = None):
    char = ""
    if current_language == ".java":
        p.wait()
        char = p.stderr.read()
        char = char.replace("\n", "\n\r")
        if char and not stop_flags.get(sid):
            socketio.emit("error-output", char, to=sid)
    elif current_language == ".js":
        p.wait()
        char = p.stderr.read()
        char = char.replace("\n", "\n\r")
        if char and not stop_flags.get(sid):
            socketio.emit("error-output", char, to=sid)
    while True:
        if current_language == ".cpp":
            if not stop_flags.get(sid):
                char = p.stderr.read()
                socketio.emit("error-output", char, to=sid)
        elif current_language == ".py":
            if not stop_flags.get(sid):
                char = p.stderr.read()
                socketio.emit("error-output", char, to=sid)
        if p.poll() is not None:
            break

@socketio.on('stop_process')
def stop_process():
    sid = request.sid
    stop_flags[sid] = True

    process_to_stop = processes.pop(sid, None)
    if process_to_stop is None:
        safe_sid = sid.replace("-", "_")
        workdir = os.path.join("submissions", safe_sid)
        try:
            if os.path.exists(workdir):
                shutil.rmtree(workdir)
        except:
            pass
        socketio.emit("process_done", to=sid)
        return

    try:
        if process_to_stop.stdin:
            process_to_stop.stdin.close()
    except:
        pass

    try:
        if process_to_stop.stdout:
            process_to_stop.stdout.close()
    except:
        pass

    try:
        process_to_stop.kill()
    except:
        pass

    try:
        process_to_stop.wait(timeout=1)
    except:
        pass

    stop_flags.pop(sid, None)
    safe_sid = sid.replace("-", "_")
    workdir = os.path.join("submissions", safe_sid)
    try:
        if os.path.exists(workdir):
            shutil.rmtree(workdir)
    except:
        pass
    socketio.emit("process_done", to=sid)

@app.route("/team-facing/close")
def close():
    return jsonify({"ok": True})

@app.route("/team-facing/submit", methods=["POST"])
def submit():
    return jsonify({"ok": True})

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5001,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True
    )