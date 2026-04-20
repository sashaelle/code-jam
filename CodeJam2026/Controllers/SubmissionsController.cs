using CodeJam2026.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Npgsql;
using System.Security.Claims;

namespace CodeJam2026.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize(Roles = "Team")]
    public class SubmissionsController : ControllerBase
    {
        private readonly IConfiguration _configuration;

        public SubmissionsController(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        [HttpPost]
        public async Task<IActionResult> Submit([FromBody] SubmissionRequest request)
        {
            if (request.ProblemId <= 0 || string.IsNullOrWhiteSpace(request.Code) || string.IsNullOrWhiteSpace(request.Language))
            {
                return BadRequest("Missing required submission data.");
            }

            var username = User.Identity?.Name;
            if (string.IsNullOrWhiteSpace(username))
            {
                return Unauthorized();
            }

            var connString = _configuration.GetConnectionString("DefaultConnection");
            await using var connection = new NpgsqlConnection(connString);
            await connection.OpenAsync();

            const string getTeamSql = @"
                SELECT t.team_id
                FROM teams t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE a.username = @username
                  AND a.is_active = true;";

            int teamId;
            await using (var teamCmd = new NpgsqlCommand(getTeamSql, connection))
            {
                teamCmd.Parameters.AddWithValue("@username", username);
                var result = await teamCmd.ExecuteScalarAsync();

                if (result is not int foundTeamId)
                {
                    return NotFound("No team found for logged-in account.");
                }

                teamId = foundTeamId;
            }

            const string insertSql = @"
                INSERT INTO submissions
                (team_id, problem_id, submission_code, judge_feedback, points, language, status, ""timestamp"")
                VALUES
                (@teamId, @problemId, @code, NULL, NULL, @language, NULL, NOW())
                RETURNING ""timestamp"";";


            DateTime submittedAt;

            await using (var insertCmd = new NpgsqlCommand(insertSql, connection))
            {
                insertCmd.Parameters.AddWithValue("@teamId", teamId);
                insertCmd.Parameters.AddWithValue("@problemId", request.ProblemId);
                insertCmd.Parameters.AddWithValue("@code", request.Code);
                insertCmd.Parameters.AddWithValue("@language", request.Language);

                submittedAt = (DateTime)(await insertCmd.ExecuteScalarAsync())!;
            }

            return Ok(new
            {
                message = "Submission received.",
                timestamp = submittedAt
            });
        }

        [HttpGet("latest/{problemId}")]
        public async Task<IActionResult> GetLatestSubmissionForProblem(int problemId)
        {
            if (problemId <= 0)
            {
                return BadRequest("Invalid problem ID.");
            }

            var username = User.Identity?.Name;
            if (string.IsNullOrWhiteSpace(username))
            {
                return Unauthorized();
            }

            var connString = _configuration.GetConnectionString("DefaultConnection");
            await using var connection = new NpgsqlConnection(connString);
            await connection.OpenAsync();

            const string getTeamSql = @"
                SELECT t.team_id
                FROM teams t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE a.username = @username
                  AND a.is_active = true;";

            int teamId;
            await using (var teamCmd = new NpgsqlCommand(getTeamSql, connection))
            {
                teamCmd.Parameters.AddWithValue("@username", username);
                var result = await teamCmd.ExecuteScalarAsync();

                if (result is not int foundTeamId)
                {
                    return NotFound("No team found for logged-in account.");
                }

                teamId = foundTeamId;
            }

            const string latestSql = @"
                SELECT submission_id, problem_id, status, judge_feedback, points, ""timestamp""
                FROM submissions
                WHERE team_id = @teamId
                  AND problem_id = @problemId
                ORDER BY ""timestamp"" DESC
                LIMIT 1;";

            await using var cmd = new NpgsqlCommand(latestSql, connection);
            cmd.Parameters.AddWithValue("@teamId", teamId);
            cmd.Parameters.AddWithValue("@problemId", problemId);

            await using var reader = await cmd.ExecuteReaderAsync();

            if (!await reader.ReadAsync())
            {
                return Ok(new
                {
                    hasSubmission = false
                });
            }

            return Ok(new
            {
                hasSubmission = true,
                submissionId = reader.GetInt32(0),
                problemId = reader.GetInt32(1),
                status = reader.IsDBNull(2) ? null : reader.GetString(2),
                judgeFeedback = reader.IsDBNull(3) ? null : reader.GetString(3),
                points = reader.IsDBNull(4) ? (int?)null : reader.GetInt32(4),
                timestamp = reader.GetDateTime(5)
            });
        }
    }
}