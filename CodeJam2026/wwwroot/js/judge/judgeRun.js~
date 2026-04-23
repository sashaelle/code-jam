const judgeSocket = io(window.HOST_ADDRESS);

const judgeRunBtn = document.getElementById("judge-run-btn");
const judgeTerminalBox = document.getElementById("judge-terminal");

const judgeTerm = new Terminal({
    theme: {
        background: "#1e1e1e",
        scrollbar: "#4e4e4e"
    },
    cursorBlink: true
});

judgeTerm.open(judgeTerminalBox);

let judgeProcessRunning = false;
let judgeInputStr = "";

window.clearJudgeTerminal = function () {
    judgeInputStr = "";
    judgeTerm.reset();
};

judgeSocket.on("connect", function () {
    console.log("Judge connected to runner");
});

judgeSocket.on("output", function (line) {
    judgeTerm.write(line);
});

judgeSocket.on("error-output", function (line) {
    judgeTerm.write("\x1b[31m" + line + "\x1b[0m");
});

judgeSocket.on("compile_process", function () {
    judgeProcessRunning = true;

    if (judgeRunBtn) {
        judgeRunBtn.textContent = "⏹ Stop";
        judgeRunBtn.disabled = false;
    }
});

judgeSocket.on("process_done", function () {
    judgeProcessRunning = false;
    judgeInputStr = "";

    if (judgeRunBtn) {
        judgeRunBtn.textContent = "Run";
        judgeRunBtn.disabled = false;
    }
});

judgeTerm.onData((data) => {
    if (!judgeProcessRunning) {
        return;
    }

    if (data !== "\r") {
        if (data === "\x7f") {
            if (judgeInputStr.length > 0) {
                judgeTerm.write("\b \b");
                judgeInputStr = judgeInputStr.substring(0, judgeInputStr.length - 1);
            }
        } else {
            judgeTerm.write(data);
            judgeInputStr += data;
        }
    } else {
        judgeSocket.emit("input_added", judgeInputStr);
        judgeInputStr = "";
        judgeTerm.write("\r\n");
    }
});

if (judgeRunBtn) {
    judgeRunBtn.addEventListener("click", function () {
        if (judgeProcessRunning) {
            judgeTerm.write("\n\r\x1b[1;31mProcess Stopped.\x1b[0m");
            judgeSocket.emit("stop_process");
            return;
        }

        const selected = window.currentJudgeSubmission;

        if (!selected) {
            alert("Select a submission first.");
            return;
        }

        window.clearJudgeTerminal();

        judgeRunBtn.textContent = "⏹ Stop";

        judgeSocket.emit("compile", {
            code: selected.code,
            problem_number: selected.problemId,
            language: normalizeJudgeLanguage(selected.language)
        });
    });
}

function normalizeJudgeLanguage(language) {
    if (!language) return ".py";

    switch (language.toLowerCase()) {
        case "python":
        case ".py":
            return ".py";
        case "java":
        case ".java":
            return ".java";
        case "cpp":
        case "c++":
        case ".cpp":
            return ".cpp";
        case "javascript":
        case "js":
        case ".js":
            return ".js";
        default:
            return ".py";
    }
}