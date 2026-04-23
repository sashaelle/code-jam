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

        [HttpGet("{problemId:int}/testcases")]
        public async Task<IActionResult> GetTestCases(int problemId)
        {
            var testCases = new List<object>();

            await using var conn = new NpgsqlConnection(_connectionString);
            await conn.OpenAsync();

            const string sql = @"
                SELECT test_case_id, test_case_num, input_text, expected_output
                FROM test_cases
                WHERE problem_id = @problemId
                ORDER BY test_case_num ASC;";

            await using var cmd = new NpgsqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@problemId", problemId);

            await using var reader = await cmd.ExecuteReaderAsync();

            while (await reader.ReadAsync())
            {
                testCases.Add(new
                {
                    testCaseId = reader.GetInt32(0),
                    testCaseNum = reader.GetInt32(1),
                    inputText = reader.IsDBNull(2) ? "" : reader.GetString(2),
                    expectedOutput = reader.IsDBNull(3) ? "" : reader.GetString(3)
                });
            }

            return Ok(testCases);
        }
    }
}