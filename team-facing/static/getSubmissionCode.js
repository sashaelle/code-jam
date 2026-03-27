
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
    let compileButton = document.querySelector(".compile");

    if(!compileButton)
    {
        compileButton = document.querySelector(".stop-button");
    }

    if(compileButton.textContent.includes("Run"))
    {
        const code = window.monacoEditor.getValue();
        console.log(code);
        localStorage.setItem("code" + window.problemNumber, code);

        console.log("Before code: ", localStorage.getItem("code" + window.problemNumber));

        // Clear terminal
        window.clearTerminal();

        // Change button to stop
        compileButton.textContent = "⏹ Stop";
        compileButton.classList.add("stop-button");
        compileButton.classList.remove("compile");

        const problemStr = document.querySelector(".problem-text").textContent;
        const num = Number(problemStr.substring(problemStr.indexOf(" ")+1, problemStr.length));
        // Emit the compile event with the code
        socket.emit("compile", {code: code, problem_number: num });
    }
    else
    {
        window.term.write("\n\x1b[1;31mProcess Stopped.\x1b[0m")
        socket.emit("stop_process");
    }
}