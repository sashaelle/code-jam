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
        public async Task<IActionResult> GetPendingSubmissions()
        {
            var submissions = new List<object>();

            await using var conn = new NpgsqlConnection(_connectionString);
            await conn.OpenAsync();

            const string sql = @"
                SELECT submission_id, team_id, problem_id, submission_code, language, status, ""timestamp""
                FROM submissions
                WHERE status IS NULL OR status = 'pending' OR status = 'in_progress'
                ORDER BY ""timestamp"" ASC;";

            await using var cmd = new NpgsqlCommand(sql, conn);
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

        public class ClaimSubmissionRequest
        {
            public int SubmissionId { get; set; }
        }
    }
}