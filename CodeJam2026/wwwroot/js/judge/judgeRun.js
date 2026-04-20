const judgeSocket = io(window.HOST_ADDRESS);

const judgeRunBtn = document.getElementById("judge-run-btn");
const judgeOutputBox = document.getElementById("judge-output-box");

let judgeProcessRunning = false;

function clearJudgeOutput() {
    if (judgeOutputBox) {
        judgeOutputBox.textContent = "";
    }
}

function appendJudgeOutput(text) {
    if (!judgeOutputBox) return;

    judgeOutputBox.textContent += text;
    judgeOutputBox.scrollTop = judgeOutputBox.scrollHeight;
}

judgeSocket.on("connect", function () {
    console.log("Judge connected to runner");
});

judgeSocket.on("output", function (line) {
    appendJudgeOutput(line.replace(/\r/g, ""));
});

judgeSocket.on("error-output", function (line) {
    appendJudgeOutput(line.replace(/\r/g, ""));
});

judgeSocket.on("compile_process", function () {
    judgeProcessRunning = true;
    if (judgeRunBtn) {
        judgeRunBtn.textContent = "Running...";
        judgeRunBtn.disabled = true;
    }
});

judgeSocket.on("process_done", function () {
    judgeProcessRunning = false;
    if (judgeRunBtn) {
        judgeRunBtn.textContent = "Run";
        judgeRunBtn.disabled = false;
    }
});

if (judgeRunBtn) {
    judgeRunBtn.addEventListener("click", function () {
        const selected = window.currentJudgeSubmission;

        if (!selected) {
            alert("Select a submission first.");
            return;
        }

        clearJudgeOutput();

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