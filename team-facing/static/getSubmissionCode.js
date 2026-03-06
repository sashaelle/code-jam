
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
    const code = window.monacoEditor.getValue();
    localStorage.setItem("code", code);
    console.log("Before code: ", localStorage.getItem("code"));

    // Clear previous output
    document.querySelector(".output").textContent = "";
    document.querySelector(".error-output").textContent = "";

    // Clear terminal
    window.clearTerminal();

    // Change button to stop
    const compileButton = document.getElementById("compile");
    //compileButton.textContent = "Stop";

    // Emit the compile event with the code
    socket.emit("compile", {code: code});
}