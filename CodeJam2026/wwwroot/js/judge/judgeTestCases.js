window.loadJudgeTestCases = async function (problemId) {
    const container = document.getElementById("judge-testcases");
    if (!container) return;

    container.innerHTML = `<div class="judge-testcases-empty mono-pre">Loading test cases...</div>`;

    try {
        const res = await fetch(`${window.problemsApiUrl}/${problemId}/testcases?_=${Date.now()}`, {
            cache: "no-store"
        });

        if (!res.ok) {
            container.innerHTML = `<div class="judge-testcases-empty mono-pre">Failed to load test cases.</div>`;
            return;
        }

        const testCases = await res.json();

        if (!testCases.length) {
            container.innerHTML = `<div class="judge-testcases-empty mono-pre">No test cases found for this problem.</div>`;
            return;
        }

        container.innerHTML = "";

        testCases.forEach(tc => {
            const card = document.createElement("div");
            card.className = "judge-testcase-card";

            card.innerHTML = `
                <div class="judge-testcase-title mono-pre">Test Case ${tc.testCaseNum}</div>

                <div class="judge-testcase-label mono-pre">Input</div>
                <pre class="judge-testcase-block mono-pre">${escapeHtml(tc.inputText || "")}</pre>

                <div class="judge-testcase-label mono-pre">Expected Output</div>
                <pre class="judge-testcase-block mono-pre">${escapeHtml(tc.expectedOutput || "")}</pre>
            `;

            container.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load judge test cases:", err);
        container.innerHTML = `<div class="judge-testcases-empty mono-pre">Failed to load test cases.</div>`;
    }
};

function escapeHtml(value) {
    return value
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}