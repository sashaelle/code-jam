using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Npgsql;

namespace CodeJam2026.Pages;

[Authorize(Roles = "Judge,Admin")]
public class ScoreboardModel : PageModel
{
    private readonly IConfiguration _configuration;

    public ScoreboardModel(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public List<ScoreboardEntry> Entries { get; private set; } = [];
    public List<SubmissionFeedItem> RecentSubmissions { get; private set; } = [];
    public string CurrentTimeDisplay { get; private set; } = "";

    public async Task OnGetAsync()
    {
        await LoadAllDataAsync();
    }

    public async Task<JsonResult> OnGetDataAsync()
    {
        await LoadAllDataAsync();

        return new JsonResult(new
        {
            currentTimeDisplay = CurrentTimeDisplay,
            entries = Entries,
            recentSubmissions = RecentSubmissions.Select(item => new
            {
                teamName = item.TeamName,
                problemNumber = item.ProblemNumber,
                timestamp = item.Timestamp,
                isCorrect = item.IsCorrect
            })
        });
    }

    private async Task LoadAllDataAsync()
    {
        CurrentTimeDisplay = DateTime.Now.ToString("HH:mm:ss");
        await LoadScoreboardAsync();
        await LoadRecentSubmissionsAsync();
    }

    private async Task LoadScoreboardAsync()
    {
        Entries = [];

        var connString = _configuration.GetConnectionString("DefaultConnection");
        await using var connection = new NpgsqlConnection(connString);
        await connection.OpenAsync();

        const string sql = """
            SELECT
                t.team_name,
                COALESCE(SUM(s.points), 0) AS total_points
            FROM teams t
            LEFT JOIN submissions s ON s.team_id = t.team_id
            GROUP BY t.team_id, t.team_name
            ORDER BY total_points DESC, t.team_name ASC;
            """;

        await using var cmd = new NpgsqlCommand(sql, connection);
        await using var reader = await cmd.ExecuteReaderAsync();

        while (await reader.ReadAsync())
        {
            Entries.Add(new ScoreboardEntry
            {
                TeamName = reader.GetString(0),
                TotalPoints = reader.GetInt32(1)
            });
        }
    }

    private async Task LoadRecentSubmissionsAsync()
    {
        RecentSubmissions = [];

        var connString = _configuration.GetConnectionString("DefaultConnection");
        await using var connection = new NpgsqlConnection(connString);
        await connection.OpenAsync();

        const string sql = """
            SELECT
                t.team_name,
                p.problem_num,
                s.timestamp,
                s.status = 'correct' AS is_correct
            FROM submissions s
            INNER JOIN teams t ON s.team_id = t.team_id
            INNER JOIN problems p ON s.problem_id = p.problem_id
            ORDER BY s.timestamp DESC
            LIMIT 10;
            """;

        await using var cmd = new NpgsqlCommand(sql, connection);
        await using var reader = await cmd.ExecuteReaderAsync();

        while (await reader.ReadAsync())
        {
            RecentSubmissions.Add(new SubmissionFeedItem
            {
                TeamName = reader.GetString(0),
                ProblemNumber = reader.GetInt32(1),
                Timestamp = reader.GetDateTime(2),
                IsCorrect = reader.GetBoolean(3)
            });
        }
    }

    public class ScoreboardEntry
    {
        public string TeamName { get; set; } = "";
        public int TotalPoints { get; set; }
    }

    public class SubmissionFeedItem
    {
        public string TeamName { get; set; } = "";
        public int ProblemNumber { get; set; }
        public DateTime Timestamp { get; set; }
        public bool IsCorrect { get; set; }
    }
}