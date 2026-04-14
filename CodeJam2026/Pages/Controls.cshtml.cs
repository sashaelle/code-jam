using System.Security.Cryptography;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Npgsql;

namespace CodeJam2026.Pages;

[Authorize(Roles = "Judge,Admin")]
public class ControlsModel : PageModel
{
    private static readonly Regex TrailingNumberRegex = new(@"(\d+)$", RegexOptions.Compiled);
    private readonly IConfiguration _configuration;

    public ControlsModel(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    [BindProperty]
    public int TeamCount { get; set; }

    public List<TeamCredential> TeamCredentials { get; private set; } = [];

    [TempData]
    public string StatusMessage { get; set; } = "";

    public async Task OnGetAsync()
    {
        await LoadTeamCredentialsAsync();
    }

    public async Task<IActionResult> OnPostGenerateTeamsAsync()
    {
        if (TeamCount < 1 || TeamCount > 20)
        {
            ModelState.AddModelError(string.Empty, "Please enter a team count between 1 and 20.");
            await LoadTeamCredentialsAsync();
            return Page();
        }

        var connString = _configuration.GetConnectionString("DefaultConnection");
        await using var connection = new NpgsqlConnection(connString);
        await connection.OpenAsync();

        const string ensureTableSql = @"
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role VARCHAR(20) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT true
            );";

        await using (var ensureCmd = new NpgsqlCommand(ensureTableSql, connection))
        {
            await ensureCmd.ExecuteNonQueryAsync();
        }

        await using var transaction = await connection.BeginTransactionAsync();

        const string deleteTeamsSql = "DELETE FROM accounts WHERE role = 'team';";
        await using (var deleteCmd = new NpgsqlCommand(deleteTeamsSql, connection, transaction))
        {
            await deleteCmd.ExecuteNonQueryAsync();
        }

        const string insertAccountSql = @"
            INSERT INTO accounts (username, password_hash, role, is_active)
            VALUES (@username, @password, 'team', true)
            RETURNING account_id;";

        const string insertTeamSql = @"
            INSERT INTO teams (account_id, team_number, team_name)
            VALUES (@accountId, @teamNumber, @teamName);";

        for (var i = 1; i <= TeamCount; i++)
        {
            var username = $"Team{i}";
            var password = GeneratePassword(12);

            await using var insertAccountCmd = new NpgsqlCommand(insertAccountSql, connection, transaction);
            insertAccountCmd.Parameters.AddWithValue("@username", username);
            insertAccountCmd.Parameters.AddWithValue("@password", password);

            var accountIdObj = await insertAccountCmd.ExecuteScalarAsync();
            if (accountIdObj is not Guid accountId)
            {
                throw new InvalidOperationException($"Failed to create account ID for {username}.");
            }

            await using var insertTeamCmd = new NpgsqlCommand(insertTeamSql, connection, transaction);
            insertTeamCmd.Parameters.AddWithValue("@accountId", accountId);
            insertTeamCmd.Parameters.AddWithValue("@teamNumber", $"team_{i}");
            insertTeamCmd.Parameters.AddWithValue("@teamName", $"Team {i}");
            await insertTeamCmd.ExecuteNonQueryAsync();
        }

        await transaction.CommitAsync();

        StatusMessage = $"Generated {TeamCount} team account(s).";
        return RedirectToPage();
    }

    private async Task LoadTeamCredentialsAsync()
    {
        TeamCredentials = [];

        var connString = _configuration.GetConnectionString("DefaultConnection");
        await using var connection = new NpgsqlConnection(connString);
        await connection.OpenAsync();

        const string sql = @"
            SELECT username, password_hash
            FROM accounts
            WHERE role = 'team' AND is_active = true
            ORDER BY
              regexp_replace(username, '\d+$', ''),
              COALESCE(NULLIF(substring(username from '\d+$'), '')::int, 2147483647),
              username;";

        await using var cmd = new NpgsqlCommand(sql, connection);
        await using var reader = await cmd.ExecuteReaderAsync();

        while (await reader.ReadAsync())
        {
            TeamCredentials.Add(new TeamCredential
            {
                Username = reader.GetString(0),
                Password = reader.GetString(1)
            });
        }

        TeamCredentials = TeamCredentials
            .OrderBy(static credential => GetSortPrefix(credential.Username))
            .ThenBy(static credential => GetSortNumber(credential.Username))
            .ThenBy(static credential => credential.Username, StringComparer.OrdinalIgnoreCase)
            .ToList();
    }

    private static string GeneratePassword(int length)
    {
        const string chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*";
        var buffer = new byte[length];
        RandomNumberGenerator.Fill(buffer);

        var output = new char[length];
        for (var i = 0; i < length; i++)
        {
            output[i] = chars[buffer[i] % chars.Length];
        }

        return new string(output);
    }

    public class TeamCredential
    {
        public string Username { get; set; } = "";
        public string Password { get; set; } = "";
    }

    private static string GetSortPrefix(string username)
    {
        var match = TrailingNumberRegex.Match(username);
        var prefixLength = match.Success ? username.Length - match.Value.Length : username.Length;
        return username[..prefixLength];
    }

    private static int GetSortNumber(string username)
    {
        var match = TrailingNumberRegex.Match(username);
        return match.Success && int.TryParse(match.Value, out var number)
            ? number
            : int.MaxValue;
    }
}
