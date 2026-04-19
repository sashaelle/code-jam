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
                (@teamId, @problemId, @code, NULL, NULL, @language, NULL, NOW());";

            await using (var insertCmd = new NpgsqlCommand(insertSql, connection))
            {
                insertCmd.Parameters.AddWithValue("@teamId", teamId);
                insertCmd.Parameters.AddWithValue("@problemId", request.ProblemId);
                insertCmd.Parameters.AddWithValue("@code", request.Code);
                insertCmd.Parameters.AddWithValue("@language", request.Language);

                await insertCmd.ExecuteNonQueryAsync();
            }

            return Ok(new { message = "Submission received." });
        }
    }
}