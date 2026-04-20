using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Npgsql;

namespace CodeJam2026.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize(Roles = "Judge,Admin")]
    public class JudgeController : ControllerBase
    {
        private readonly string _connectionString;

        public JudgeController(IConfiguration config)
        {
            _connectionString = config.GetConnectionString("DefaultConnection");
        }

        [HttpGet("pending")]
        public async Task<IActionResult> GetPendingSubmissions([FromQuery] int? problemId)
        {
            var submissions = new List<object>();

            await using var conn = new NpgsqlConnection(_connectionString);
            await conn.OpenAsync();

            const string sql = @"
                SELECT submission_id, team_id, problem_id, submission_code, language, status, ""timestamp""
                FROM submissions
                WHERE (status IS NULL OR status = 'pending' OR status = 'in_progress')
                  AND (@problemId IS NULL OR problem_id = @problemId)
                ORDER BY ""timestamp"" ASC;";

            await using var cmd = new NpgsqlCommand(sql, conn);
            var problemParam = cmd.Parameters.Add("@problemId", NpgsqlTypes.NpgsqlDbType.Integer);

            if (problemId.HasValue)
            {
                problemParam.Value = problemId.Value;
            }
            else
            {
                problemParam.Value = DBNull.Value;
            }
            await using var reader = await cmd.ExecuteReaderAsync();

            while (await reader.ReadAsync())
            {
                submissions.Add(new
                {
                    submissionId = reader.GetInt32(0),
                    teamId = reader.GetInt32(1),
                    problemId = reader.GetInt32(2),
                    code = reader.GetString(3),
                    language = reader.GetString(4),
                    status = reader.IsDBNull(5) ? null : reader.GetString(5),
                    timestamp = reader.GetDateTime(6)
                });
            }

            return Ok(submissions);
        }

        [HttpPost("claim")]
        public async Task<IActionResult> ClaimSubmission([FromBody] ClaimSubmissionRequest request)
        {
            await using var conn = new NpgsqlConnection(_connectionString);
            await conn.OpenAsync();

            const string sql = @"
                UPDATE submissions
                SET status = 'in_progress'
                WHERE submission_id = @submissionId
                  AND (status IS NULL OR status = 'pending');";

            await using var cmd = new NpgsqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@submissionId", request.SubmissionId);

            int rowsAffected = await cmd.ExecuteNonQueryAsync();

            if (rowsAffected == 0)
            {
                return Conflict(new { message = "Submission already claimed or already graded." });
            }

            return Ok(new { message = "Submission claimed." });
        }

        [HttpPost("release")]
        public async Task<IActionResult> ReleaseSubmission([FromBody] ReleaseSubmissionRequest request)
        {
            await using var conn = new NpgsqlConnection(_connectionString);
            await conn.OpenAsync();

            const string sql = @"
                UPDATE submissions
                SET status = 'pending'
                WHERE submission_id = @submissionId
                AND status = 'in_progress';";

            await using var cmd = new NpgsqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@submissionId", request.SubmissionId);

            await cmd.ExecuteNonQueryAsync();

            return Ok(new { message = "Submission released." });
        }

        [HttpPost("score")]
        public async Task<IActionResult> ScoreSubmission([FromBody] ScoreSubmissionRequest request)
        {
            await using var conn = new NpgsqlConnection(_connectionString);
            await conn.OpenAsync();

            int teamId;
            int problemId;
            string? currentStatus;

            const string getSubmissionSql = @"
                SELECT team_id, problem_id, status
                FROM submissions
                WHERE submission_id = @submissionId;";

            await using (var getCmd = new NpgsqlCommand(getSubmissionSql, conn))
            {
                getCmd.Parameters.AddWithValue("@submissionId", request.SubmissionId);

                await using var reader = await getCmd.ExecuteReaderAsync();

                if (!await reader.ReadAsync())
                {
                    return NotFound(new { message = "Submission not found." });
                }

                teamId = reader.GetInt32(0);
                problemId = reader.GetInt32(1);
                currentStatus = reader.IsDBNull(2) ? null : reader.GetString(2);
            }

            if (currentStatus != null && currentStatus != "pending" && currentStatus != "in_progress")
            {
                return Conflict(new { message = "Submission has already been graded." });
            }

            if (!request.Correct)
            {
                const string incorrectSql = @"
                    UPDATE submissions
                    SET status = 'incorrect',
                        judge_feedback = @feedback,
                        points = 0
                    WHERE submission_id = @submissionId;";

                await using var incorrectCmd = new NpgsqlCommand(incorrectSql, conn);
                incorrectCmd.Parameters.AddWithValue("@submissionId", request.SubmissionId);
                incorrectCmd.Parameters.AddWithValue("@feedback", (object?)request.Feedback ?? DBNull.Value);

                await incorrectCmd.ExecuteNonQueryAsync();

                return Ok(new
                {
                    message = "Submission scored as incorrect.",
                    result = "incorrect",
                    points = 0
                });
            }

            const string alreadySolvedSql = @"
                SELECT COUNT(*)
                FROM submissions
                WHERE team_id = @teamId
                  AND problem_id = @problemId
                  AND status = 'correct';";

            await using (var alreadySolvedCmd = new NpgsqlCommand(alreadySolvedSql, conn))
            {
                alreadySolvedCmd.Parameters.AddWithValue("@teamId", teamId);
                alreadySolvedCmd.Parameters.AddWithValue("@problemId", problemId);

                var alreadySolvedCount = Convert.ToInt32(await alreadySolvedCmd.ExecuteScalarAsync());

                if (alreadySolvedCount > 0)
                {
                    return Conflict(new { message = "This team has already solved this problem." });
                }
            }

            int wrongAttempts;
            const string wrongAttemptsSql = @"
                SELECT COUNT(*)
                FROM submissions
                WHERE team_id = @teamId
                  AND problem_id = @problemId
                  AND status = 'incorrect';";

            await using (var wrongCmd = new NpgsqlCommand(wrongAttemptsSql, conn))
            {
                wrongCmd.Parameters.AddWithValue("@teamId", teamId);
                wrongCmd.Parameters.AddWithValue("@problemId", problemId);

                wrongAttempts = Convert.ToInt32(await wrongCmd.ExecuteScalarAsync());
            }

            int teamsSolvedBefore;
            const string solvedBeforeSql = @"
                SELECT COUNT(DISTINCT team_id)
                FROM submissions
                WHERE problem_id = @problemId
                  AND team_id <> @teamId
                  AND status = 'correct';";

            await using (var solvedBeforeCmd = new NpgsqlCommand(solvedBeforeSql, conn))
            {
                solvedBeforeCmd.Parameters.AddWithValue("@problemId", problemId);
                solvedBeforeCmd.Parameters.AddWithValue("@teamId", teamId);

                teamsSolvedBefore = Convert.ToInt32(await solvedBeforeCmd.ExecuteScalarAsync());
            }

            int awardedPoints = Math.Max(0, 20 - wrongAttempts - teamsSolvedBefore);

            const string correctSql = @"
                UPDATE submissions
                SET status = 'correct',
                    judge_feedback = @feedback,
                    points = @points
                WHERE submission_id = @submissionId;";

            await using (var correctCmd = new NpgsqlCommand(correctSql, conn))
            {
                correctCmd.Parameters.AddWithValue("@submissionId", request.SubmissionId);
                correctCmd.Parameters.AddWithValue("@feedback", (object?)request.Feedback ?? DBNull.Value);
                correctCmd.Parameters.AddWithValue("@points", awardedPoints);

                await correctCmd.ExecuteNonQueryAsync();
            }

            return Ok(new
            {
                message = "Submission scored as correct.",
                result = "correct",
                points = awardedPoints
            });
        }

        public class ClaimSubmissionRequest
        {
            public int SubmissionId { get; set; }
        }

        public class ScoreSubmissionRequest
        {
            public int SubmissionId { get; set; }
            public bool Correct { get; set; }
            public string? Feedback { get; set; }
        }

        public class ReleaseSubmissionRequest
        {
            public int SubmissionId { get; set; }
        }
    }
}