document.addEventListener("DOMContentLoaded", async () => {
    await loadProblemFilterOptions();
    await loadQueue();
    setInterval(loadQueue, 3000);
});

let activeSubmissionId = null;
window.currentJudgeSubmission = null;

function getSelectedProblemFilter() {
    const filter = document.getElementById("judge-problem-filter");
    return filter ? filter.value : "";
}

async function loadProblemFilterOptions() {
    const filter = document.getElementById("judge-problem-filter");
    if (!filter) return;

    try {
        const res = await fetch(`${window.problemsApiUrl}`, {
            cache: "no-store"
        });

        if (!res.ok) {
            console.error("Failed to load problem filter options.");
            return;
        }

        const problems = await res.json();

        filter.innerHTML = `<option value="">All</option>`;

        problems.forEach(problem => {
            const option = document.createElement("option");
            option.value = problem.problemId;
            option.textContent = `Problem ${problem.problemNum}`;
            filter.appendChild(option);
        });

        filter.addEventListener("change", async () => {
            await loadQueue();
        });
    } catch (err) {
        console.error("Failed to initialize problem filter:", err);
    }
}

async function loadQueue() {
    const selectedProblemId = getSelectedProblemFilter();
    const query = new URLSearchParams({
        _: Date.now().toString()
    });

    if (selectedProblemId) {
        query.append("problemId", selectedProblemId);
    }

    const res = await fetch(`${window.judgeApiUrl}/pending?${query.toString()}`, {
        cache: "no-store"
    });

    if (!res.ok) {
        console.error("Failed to load submission queue.");
        return;
    }

    const submissions = await res.json();
    const queue = document.getElementById("submissionQueue");

    queue.innerHTML = "";

    submissions.forEach(sub => {
        const item = document.createElement("button");
        item.type = "button";
        item.className = "queue-item mono-pre";
        item.dataset.submissionId = sub.submissionId;

        const ts = new Date(sub.timestamp).toLocaleString();
        item.textContent = `Team ${sub.teamId} | Problem ${sub.problemId} | ${ts}`;

        if (activeSubmissionId !== null) {
            if (sub.submissionId === activeSubmissionId) {
                item.textContent += " | IN PROGRESS";
                item.disabled = true;
                item.classList.add("queue-item-in-progress");
            } else {
                item.disabled = true;
                item.classList.add("queue-item-locked");

                if (sub.status === "in_progress") {
                    item.textContent += " | IN PROGRESS";
                    item.classList.add("queue-item-in-progress");
                }
            }
        } else {
            if (sub.status === "in_progress") {
                item.textContent += " | IN PROGRESS";
                item.disabled = true;
                item.classList.add("queue-item-in-progress");
            } else {
                item.addEventListener("click", () => selectSubmission(sub));
            }
        }

        queue.appendChild(item);
    });
}

async function selectSubmission(sub) {
    if (activeSubmissionId !== null) {
        return;
    }

    const res = await fetch(`${window.judgeApiUrl}/claim`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            submissionId: sub.submissionId
        })
    });

    if (!res.ok) {
        alert("That submission was already taken by another judge.");
        await loadQueue();
        return;
    }

    activeSubmissionId = sub.submissionId;
    window.currentJudgeSubmission = sub;

    const codeBox = document.getElementById("judge-code-box");
    codeBox.value = sub.code;

    if (window.loadJudgeTestCases) {
        await window.loadJudgeTestCases(sub.problemId);
    }

    await loadQueue();
}