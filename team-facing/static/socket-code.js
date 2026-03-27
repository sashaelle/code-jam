// Socket
const socket = io("http://localhost:5000");

// Terminal
const term = new Terminal({
    theme: {
        background: '#1e1e1e',
        scrollbar: '#4e4e4e'
    },
    cursorBlink: true,
 });
window.term = term;

let hasCompiled = false;

const terminalBox = document.getElementById("terminal");

term.open(terminalBox);

socket.on("connect", function () {
    console.log("Connected");
});

socket.on("output", function (line) {
    term.write(line);
})

socket.on("error-output", function (line) {
    console.log("ERROR LINE: ", line);
    term.write("\x1b[31m" + line + "\x1b[0m");
})

socket.on("compile_process", function () {
    hasCompiled = true;
})

socket.on("process_done", function () {
    // Change button to run
    const compileButton = document.querySelector(".stop-button");
    compileButton.textContent = "▶ Run";
    compileButton.classList.add("compile");
    compileButton.classList.remove("stop-button");
})


let inputStr = "";
handleTerminalInput();

function handleTerminalInput()
{
    term.onData((data) => {
        if(hasCompiled)
        {
            // Check for enter press
            // If not enter --> write to terminal
                // If backspace --> remove
                // If not enter and not backspace --> append to array/string
            // If enter
                // Stuff at bottom (input_added)
                // Send string
                // Clear string
            if (data != "\r") // Enter
            {
                if (data == "\x7f") // Backspace
                {
                    if (inputStr.length > 0)
                    {
                        term.write("\b \b"); // Backspace escape sequence
                        inputStr = inputStr.substring(0, inputStr.length-1) // Remove last char
                    }
                }
                else {
                    term.write(data);
                    inputStr += data;
                }
            }
            else // Pressed enter
            {
                socket.emit("input_added", inputStr);
                inputStr = "";
                term.write("\r\n"); // Newline
            }
        }
    });
}

window.clearTerminal = function()
{
    inputStr = "";
    term.reset();
}

function editorSetup()
{
    console.log("REFRESH!");
    const storedCode = localStorage.getItem("code" + window.problemNumber)
    if(storedCode != null && storedCode != "")
    {
        const codeBox = document.getElementById("editor");
        const code = storedCode;
        console.log("Code: ", code);
        setEditorValue(code);
    }
}

window.setEditorValue = function(code) {
    if (window.monacoEditor) {
        console.log("Found editor");
        window.monacoEditor.getModel().setValue(code);
    } else {
        console.log("Did not find editor. Waiting...");
        // editor not ready yet, retry after a short delay
        setTimeout(() => setEditorValue(code), 100);
    }
}

editorSetup();

socket.on("process_done", function() {
    console.log("Code compiled");
});

socket.on("disconnect", function () {
    console.log("Disconnected");
})