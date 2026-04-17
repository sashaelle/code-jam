
window.onSubmission = function () {

    showConfirmPopup(() => {
        executeSubmission();
    });
};

window.executeSubmission = function ()
{
    const code = window.monacoEditor.getValue();
    const submitBtn = document.getElementById("submit");
    const submitTime = document.getElementById("submitTime");

    submitBtn.disabled = true;

    submitBtn.textContent = "Waiting for Feedback...";

    const now = new Date();
    const problemStr = document.querySelector(".problem-text").textContent;
    const num = Number(problemStr.substring(problemStr.indexOf(" ")+1, problemStr.length));
    const problemNum = String(num);

    const storageKey = `problem_${problemNum}_status`;

    if (localStorage.getItem(storageKey) === "pending") {
        submitTime.textContent = `This problem already has a pending submission.`;
        submitBtn.disabled = false;
        submitBtn.textContent = "✓ Submit";
        setTimeout(() => {
        submitTime.textContent = ``;
        }, 4000);
        //alert("This problem already has a pending submission.");
        return;
    }

    localStorage.setItem(storageKey, "pending");


    const formattedTime = now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });
    //Time
    //submitTime.textContent = `Last submitted at: ${formattedTime}`;

    fetch("/team-facing/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            submission_id: "1",
            team_id: null,
            problem_id: problemNum,
            submission_code: code,
            judge_feedback: null,
            points: null,
            language: window.CURRENT_LANGUAGE,
            status: "pending",
            timestamp: null})
    })
    //DEBUG - enables the button shortly after submission
    /*setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = "✓ Submit";
    }, 4000);*/
}

window.showConfirmPopup = function (onConfirm) {
    const popup = document.getElementById("confirmPopup");

    popup.style.display = "block";

    const yesBtn = document.getElementById("confirmYes");
    const noBtn = document.getElementById("confirmNo");

    yesBtn.onclick = null;
    noBtn.onclick = null;

    yesBtn.onclick = () => {
        popup.style.display = "none";
        if (onConfirm) onConfirm();
    };

    noBtn.onclick = () => {
        popup.style.display = "none";
    };
};