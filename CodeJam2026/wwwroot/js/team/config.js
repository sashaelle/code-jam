const MAX_PROBLEMS = 10;
window.MAX_PROBLEMS = MAX_PROBLEMS;

const HOST_ADDRESS = "http://localhost:5001";
window.HOST_ADDRESS = HOST_ADDRESS;

window.problemNumber = 1;

if (!localStorage.getItem("selectedProblemId")) {
    localStorage.setItem("selectedProblemId", 1);
}

window.DEFAULT_CODE = `print("Hello Game Jam!")`;

window.EXTENSION_PYTHON = ".py";
window.EXTENSION_JAVA = ".java";
window.EXTENSION_JS = ".js";
window.EXTENSION_CPP = ".cpp";

window.CURRENT_LANGUAGE = ".py";