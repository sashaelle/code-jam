window.updateProblem = function (inc) {
    const maxProblems = window.MAX_PROBLEMS;

    const problemText = document.querySelector(".problem-text").textContent;
    const problem = document.querySelector(".problem-text");

    const problemStr = problemText.substring(problemText.indexOf(" ") + 1);
    let problemNumber = Number(problemStr) + inc;

    if (problemNumber < 1) {
        problemNumber = 1;
    }

    if (problemNumber > maxProblems) {
        problemNumber = 1;
    }

    problem.textContent = "Problem " + problemNumber;
    window.problemNumber = problemNumber;
    localStorage.setItem("selectedProblemId", problemNumber);

    if (window.checkLatestSubmissionStatus) {
        window.checkLatestSubmissionStatus();
    }

    let codeToAdd = localStorage.getItem("code" + problemNumber);
    if (!codeToAdd) {
        console.log("No code to add. Setting default code.");
        codeToAdd = window.DEFAULT_CODE;
    }

    window.setEditorValue(codeToAdd);

    const submitBtn = document.getElementById("submit");
    const submitTime = document.getElementById("submitTime");

    submitBtn.disabled = false;
    submitBtn.textContent = "✓ Submit";
    submitTime.textContent = "";

    if (window.checkLatestSubmissionStatus) {
        window.checkLatestSubmissionStatus();
    }
};