
window.onSubmission = function ()
{
    const code = window.editor.getValue();
    let status = false;
    const submitBtn = document.getElementById("submit");
    const submitTime = document.getElementById("submitTime");

    submitBtn.disabled = true;
    submitBtn.textContent = "Waiting for Feedback...";

    const now = new Date();

    const formattedTime = now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });

    submitTime.textContent = `Last submitted at: ${formattedTime}`;

    fetch("/team-facing/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            code: code,
            feedback: null,
            id: "1",
            problem_id: "1",
            status: pending,
            team: "Team A",
            timestamp: formattedTime})
    })

    setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit";
    }, 4000);
}
