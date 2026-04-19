window.onSubmission = async function () {
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

        const now = new Date();
        const formattedTime = now.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });

        submitTime.textContent = `Submitted at ${formattedTime}`;
    }
    catch (error) {
        console.error("Submission error:", error);
        submitTime.textContent = "Submission failed. Check console/server.";
    }
    finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "✓ Submit";

        setTimeout(() => {
            submitTime.textContent = "";
        }, 4000);
    }
};