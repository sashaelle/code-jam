
window.onSubmission = function ()
{
    const code = window.editor.getValue();
    let is_feedback = false;
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
            is_feedback: is_feedback,
            submitted_at: formattedTime})
    })

    setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit";
    }, 5000);
}
