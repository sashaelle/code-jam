document.addEventListener("DOMContentLoaded", () => {
    refreshScoreboard();
    setInterval(refreshScoreboard, 1000);
});

async function refreshScoreboard() {
    try {
        const response = await fetch("/Scoreboard?handler=Data", {
            cache: "no-store"
        });

        if (!response.ok) {
            console.error("Failed to refresh scoreboard.");
            return;
        }

        const data = await response.json();

        renderVisibility(data.isScoreboardVisible);
        renderClock(data.currentTimeDisplay);
        renderScoreboardRows(data.entries);
        renderRecentSubmissions(data.recentSubmissions);
    } catch (err) {
        console.error("Scoreboard refresh failed:", err);
    }
}

function renderVisibility(isVisible) {
    const visibleContent = document.getElementById("scoreboardVisibleContent");
    const hiddenMessage = document.getElementById("scoreboardHiddenMessage");

    if (visibleContent) {
        visibleContent.style.display = isVisible ? "block" : "none";
    }

    if (hiddenMessage) {
        hiddenMessage.style.display = isVisible ? "none" : "flex";
    }
}

function renderClock(timeText) {
    const clock = document.getElementById("scoreboardTimeValue");
    if (clock) {
        clock.textContent = timeText;
    }
}

function renderScoreboardRows(entries) {
    const container = document.getElementById("scoreboardRows");
    if (!container) return;

    let html = `
        <div class="scoreboard-row highlight-yellow">
            TEAM NAME | POINTS
        </div>
    `;

    if (entries && entries.length > 0) {
        entries.forEach(entry => {
            html += `
                <div class="scoreboard-row">
                    ${escapeHtml(entry.teamName)} | ${entry.totalPoints}
                </div>
            `;
        });
    } else {
        html += `
            <div class="scoreboard-row">
                NO TEAMS OR SUBMISSIONS FOUND
            </div>
        `;
    }

    container.innerHTML = html;
}

function renderRecentSubmissions(items) {
    const container = document.getElementById("recentSubmissionsFeed");
    if (!container) return;

    let html = "";

    if (items && items.length > 0) {
        items.forEach(item => {
            const ts = new Date(item.timestamp);
            const formatted = formatTimestamp(ts);

            html += `
                <div class="sb-feed-row">
                    <div class="sb-team">${escapeHtml(item.teamName)}&gt;&gt;</div>
                    <div class="sb-meta">
                        QUESTION ${item.problemNumber}, ${formatted}
                    </div>
                </div>
            `;
        });
    } else {
        html = `
            <div class="sb-feed-row">
                <div class="sb-team">NO SUBMISSIONS YET</div>
                <div class="sb-divider"></div>
            </div>
        `;
    }

    container.innerHTML = html;
}

function formatTimestamp(date) {
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");

    return `${month}/${day} ${hours}:${minutes}:${seconds}`;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}