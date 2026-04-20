document.addEventListener("DOMContentLoaded", () => {
    loadQueue();
    setInterval(loadQueue, 3000); // refresh queue every 3 seconds
});

let activeSubmissionId = null;
window.currentJudgeSubmission = null;

async function loadQueue() {
    const res = await fetch(`${window.judgeApiUrl}/pending?_=${Date.now()}`, {
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

        // If this judge already has one active, lock everything else
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
        }
        // No active submission for this judge yet
        else {
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