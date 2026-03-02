
/*window.getSubmissionCode = function ()
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

    const socket = io("http://localhost:5000");
    socket.emit("compile", data);
});
}*/
window.getSubmissionCode = function() {
    const code = window.editor.getValue();

    // Clear previous output
    document.querySelector(".output").textContent = "";
    document.querySelector(".error-output").textContent = "";

    // Emit the compile event with the code
    socket.emit("compile", {code: code});
}