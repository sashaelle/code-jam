using Microsoft.AspNetCore.Mvc;
using Npgsql;

namespace CodeJam2026.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ProblemsController : ControllerBase
    {
        private readonly string _connectionString;

        public ProblemsController(IConfiguration config)
        {
            _connectionString = config.GetConnectionString("DefaultConnection");
        }

        [HttpGet]
        public async Task<IActionResult> GetProblems()
        {
            var problems = new List<object>();

            using var conn = new NpgsqlConnection(_connectionString);
            await conn.OpenAsync();

            using var cmd = new NpgsqlCommand(
                "SELECT problem_id, problem_num FROM problems ORDER BY problem_num",
                conn);

            using var reader = await cmd.ExecuteReaderAsync();

            while (await reader.ReadAsync())
            {
                problems.Add(new {
                    problemId = reader.GetInt32(0),
                    problemNum = reader.GetInt32(1)
                });
            }

            return Ok(problems);
        }
    }
}