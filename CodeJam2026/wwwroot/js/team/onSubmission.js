async function submitConfirmedCode() {
    const code = window.monacoEditor.getValue();
    const submitBtn = document.getElementById("submit");
    const submitTime = document.getElementById("submitTime");
    const language = document.getElementById("languages").value;

    const problemStr = document.querySelector(".problem-text").textContent;
    const problemId = Number(problemStr.substring(problemStr.indexOf(" ") + 1));

    if (!code || !code.trim()) {
        submitTime.textContent = "Cannot submit empty code.";
        setTimeout(() => {
            submitTime.textContent = "";
        }, 4000);
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";

    try {
        const response = await fetch(window.submissionApiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                problemId: problemId,
                code: code,
                language: language
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            submitTime.textContent = `Submission failed: ${errorText}`;
            return;
        }

        const data = await response.json();

        const submittedAt = new Date(data.timestamp);
        const formattedTime = submittedAt.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });

        submitTime.textContent = `Submitted at ${formattedTime}`;

        localStorage.setItem(`problem_${problemId}_status`, "pending");
    }
    catch (error) {
        console.error("Submission error:", error);
        submitTime.textContent = "Submission failed. Check console/server.";
    }
    finally {
        // Get CURRENTLY DISPLAYED problem (NOT the one just submitted)
        const currentProblemStr = document.querySelector(".problem-text").textContent;
        const currentProblemId = Number(currentProblemStr.substring(currentProblemStr.indexOf(" ") + 1));

        const status = localStorage.getItem(`problem_${currentProblemId}_status`);

        if (status === "pending") {
            submitBtn.disabled = true;
            submitBtn.textContent = "Waiting for Feedback...";
        } else {
            submitBtn.disabled = false;
            submitBtn.textContent = "✓ Submit";
        }

        setTimeout(() => {
            submitTime.textContent = "";
        }, 4000);
    }
}

function closeSubmitPopup() {
    const popup = document.getElementById("confirmPopup");
    if (popup) {
        popup.style.display = "none";
    }
}

window.onSubmission = function () {
    const popup = document.getElementById("confirmPopup");
    if (popup) {
        popup.style.display = "block";
    }
};

document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("confirmPopup");
    const confirmYes = document.getElementById("confirmYes");
    const confirmNo = document.getElementById("confirmNo");

    if (!popup || !confirmYes || !confirmNo) {
        return;
    }

    confirmYes.addEventListener("click", async function () {
        closeSubmitPopup();
        await submitConfirmedCode();
    });

    confirmNo.addEventListener("click", closeSubmitPopup);

    popup.addEventListener("click", function (event) {
        if (event.target === popup) {
            closeSubmitPopup();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && popup.style.display === "block") {
            closeSubmitPopup();
        }
    });
});