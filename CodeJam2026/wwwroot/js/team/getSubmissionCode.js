const languageDropdown = document.getElementById("languages");
languageDropdown.addEventListener('change', (event) => {
    const language = event.target.value;

    // Switch monaco language
    console.log("Switched to: ", language);
    localStorage.setItem("language", language);
    monaco.editor.setModelLanguage(window.monacoEditor.getModel(), language);

    // Check for other language
    if (language == "python")
    {
        window.CURRENT_LANGUAGE = ".py";
    } 
    else if (language == "java")
    {
        window.CURRENT_LANGUAGE = ".java";
    } 
    else if (language == "cpp")
    {
        window.CURRENT_LANGUAGE = ".cpp";
    }
    else if (language == "javascript")
    {
        window.CURRENT_LANGUAGE = ".js";
    }

})

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
        socket.emit("compile", {code: code, problem_number: num, language: window.CURRENT_LANGUAGE });
    }
    else
    {
        window.term.write("\n\r\x1b[1;31mProcess Stopped.\x1b[0m")
        socket.emit("stop_process");
    }
}