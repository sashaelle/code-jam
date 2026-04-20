function getCurrentProblemId() {
    if (typeof currentProblemId !== "undefined" && currentProblemId) {
        return currentProblemId;
    }

    const saved = localStorage.getItem("selectedProblemId");
    return saved ? parseInt(saved, 10) : null;
}

function getFeedbackElements() {
    return {
        feedbackName: document.getElementById("feedback-problem-name"),
        feedbackMessage: document.getElementById("feedback-message"),
        submitBtn: document.getElementById("submit")
    };
}

function setSubmitButtonState(state) {
    const { submitBtn } = getFeedbackElements();
    if (!submitBtn) return;

    if (state === "pending") {
        submitBtn.disabled = true;
        submitBtn.textContent = "Waiting for Feedback...";
    } else if (state === "in_progress") {
        submitBtn.disabled = true;
        submitBtn.textContent = "Being Judged...";
    } else if (state === "correct") {
        submitBtn.disabled = true;
        submitBtn.textContent = "Correct ✓";
    } else {
        submitBtn.disabled = false;
        submitBtn.textContent = "✓ Submit";
    }
}

function setFeedbackMessage(problemId, statusText, feedbackText, pointsText) {
    const { feedbackName, feedbackMessage } = getFeedbackElements();

    if (feedbackName && problemId) {
        feedbackName.textContent = `Problem ${problemId}`;
    }

    if (feedbackMessage) {
        feedbackMessage.textContent =
`Status
${statusText}

Feedback
${feedbackText}

Points Awarded
${pointsText}`;
    }
}

async function checkLatestSubmissionStatus() {
    const problemId = getCurrentProblemId();
    if (!problemId) return;

    try {
        const response = await fetch(`${window.submissionApiUrl}/latest/${problemId}`, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        if (!data.hasSubmission) {
            setFeedbackMessage(
                problemId,
                "Not Submitted",
                "No feedback yet for this problem.",
                "--"
            );
            setSubmitButtonState("none");
            return;
        }

        const status = data.status;

        if (status === null || status === "pending") {
            setFeedbackMessage(
                problemId,
                "Pending",
                "Submission pending review.",
                "--"
            );
            setSubmitButtonState("pending");
            return;
        }

        if (status === "in_progress") {
            setFeedbackMessage(
                problemId,
                "In Progress",
                "Submission is currently being judged.",
                "--"
            );
            setSubmitButtonState("in_progress");
            return;
        }

        if (status === "incorrect") {
            setFeedbackMessage(
                problemId,
                "Incorrect",
                data.judgeFeedback && data.judgeFeedback.trim() !== ""
                    ? data.judgeFeedback
                    : "Your submission was marked incorrect.",
                `${data.points ?? 0} points`
            );
            setSubmitButtonState("incorrect");
            return;
        }

        if (status === "correct") {
            setFeedbackMessage(
                problemId,
                "Correct",
                data.judgeFeedback && data.judgeFeedback.trim() !== ""
                    ? data.judgeFeedback
                    : "This code works!",
                `${data.points ?? 0} points`
            );
            setSubmitButtonState("correct");
            return;
        }

        setFeedbackMessage(
            problemId,
            "Not Submitted",
            "No feedback yet for this problem.",
            "--"
        );
        setSubmitButtonState("none");
    } catch (error) {
        console.error("Failed to check submission status:", error);
    }
}

window.checkLatestSubmissionStatus = checkLatestSubmissionStatus;

document.addEventListener("DOMContentLoaded", function () {
    checkLatestSubmissionStatus();
    setInterval(checkLatestSubmissionStatus, 3000);
});