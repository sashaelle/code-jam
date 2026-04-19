window.updateProblem = function(inc)
{
    const maxProblems = window.MAX_PROBLEMS;  // Get max problems from DB

    const problemText = document.querySelector(".problem-text").textContent;
    const problem = document.querySelector(".problem-text");

    const problemStr = problemText.substring(problemText.indexOf(" ")+1, problemText.length);

    let problemNumber = Number(problemStr) + inc;

    if(problemNumber < 1)
    {
        problemNumber = 1;
    }

    if(problemNumber > maxProblems)
    {
        problemNumber = 1;
    }

    problem.textContent = "Problem " + problemNumber;

    // Store problemNumber in memory;
    window.problemNumber = problemNumber;
    
    let codeToAdd = localStorage.getItem("code" + problemNumber);
    if(!codeToAdd)
    {
        console.log("No code to add. Setting default code.");
        codeToAdd = window.DEFAULT_CODE;
    }

    window.setEditorValue(codeToAdd);
}