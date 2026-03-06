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

let hasCompiled = false;

const terminalBox = document.getElementById("terminal");

term.open(terminalBox);

editorSetup();

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
    console.log("PROCESS DONE");
    hasCompiled = true;
})

socket.on("process_done", function () {
    console.log("FINAL PROCESS");

    // Change button to run
    const compileButton = document.getElementById("compile");
    //compileButton.textContent = "Run";
})


let inputStr = "";
handleTerminalInput();

function handleTerminalInput()
{
    term.onData((data) => {
        console.log("HAS COMPILED? ", hasCompiled);
        if(hasCompiled)
        {
            console.log("RUNNING");

            console.log(data);
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
                console.log(inputStr);
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
    if(localStorage.getItem("code") != null && localStorage.getItem("code") != "")
    {
        const codeBox = document.getElementById("editor");
        const code = localStorage.getItem("code");
        console.log("Code: ", code);
        setEditorValue(code);
    }
}

function setEditorValue(code) {
    if (window.monacoEditor) {
        console.log("Found editor");
        window.monacoEditor.getModel().setValue(code);
    } else {
        console.log("Did not find editor. Waiting...");
        // editor not ready yet, retry after a short delay
        setTimeout(() => setEditorValue(code), 100);
    }
}

socket.on("process_done", function() {
    console.log("Process finished");
});

socket.on("disconnect", function () {
    console.log("Disconnected");
})