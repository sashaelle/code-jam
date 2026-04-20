const judgeScoreBtn = document.getElementById("judge-score-btn");
const judgeFeedbackBox = document.getElementById("judge-feedback");
const judgeVerdictSelect = document.getElementById("judge-verdict");

function getJudgeVerdict() {
    return judgeVerdictSelect ? judgeVerdictSelect.value : null;
}

function clearJudgeSelection() {
    activeSubmissionId = null;
    window.currentJudgeSubmission = null;

    const codeBox = document.getElementById("judge-code-box");
    if (codeBox) {
        codeBox.value = "";
    }

    const testcases = document.getElementById("judge-testcases");
    if (testcases) {
        testcases.innerHTML = `<div class="judge-testcases-empty mono-pre">Select a submission to load test cases.</div>`;
    }

    if (judgeFeedbackBox) {
        judgeFeedbackBox.value = "";
    }

    if (judgeVerdictSelect) {
        judgeVerdictSelect.value = "incorrect";
    }

    if (window.clearJudgeTerminal) {
        window.clearJudgeTerminal();
    }
}

if (judgeScoreBtn) {
    judgeScoreBtn.addEventListener("click", async function () {
        const selectedSubmission = window.currentJudgeSubmission;

        if (!selectedSubmission) {
            alert("Select a submission first.");
            return;
        }

        const verdict = getJudgeVerdict();
        if (!verdict) {
            alert("Select a verdict first.");
            return;
        }

        const correct = verdict === "correct";
        const feedback = judgeFeedbackBox ? judgeFeedbackBox.value : "";

        const res = await fetch(`${window.judgeApiUrl}/score`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                submissionId: selectedSubmission.submissionId,
                correct: correct,
                feedback: feedback
            })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.message || "Failed to score submission.");
            return;
        }

        alert(`${data.result.toUpperCase()} | Points: ${data.points}`);

        clearJudgeSelection();
        await loadQueue();
    });
}