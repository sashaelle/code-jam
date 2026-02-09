
window.getSubmissionCode = function ()
{
    const code = window.editor.getValue();

    fetch("/team-facing/compile_button", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({code})
    })
    .then(res => res.json())
    .then(data => {
    document.querySelector(".output").textContent = data.stdout;
    document.querySelector(".error-output").textContent = data.stderr;
});
}

