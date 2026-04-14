using System.Security.Claims;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Npgsql; 

namespace CodeJam2026.Pages;

public class LoginModel : PageModel
{
    private static readonly Regex TrailingNumberRegex = new(@"(\d+)$", RegexOptions.Compiled);
    private readonly IConfiguration _configuration;

    public LoginModel(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    [BindProperty]
    public string SelectedUser { get; set; } = "";

    [BindProperty]
    public string Password { get; set; } = "";

    public List<string> LoginUsers { get; private set; } = [];

    public async Task OnGetAsync()
    {
        await LoadLoginUsersAsync();
    }

    public async Task<IActionResult> OnPostAsync()
    {
        if (string.IsNullOrWhiteSpace(SelectedUser))
        {
            ModelState.AddModelError("", "Please select a team.");
            await LoadLoginUsersAsync();
            return Page();
        }

        var connString = _configuration.GetConnectionString("DefaultConnection");

        await using var connection = new NpgsqlConnection(connString);
        await connection.OpenAsync();

        const string sql = @"
            SELECT username, password_hash, role
            FROM accounts
            WHERE username = @username AND is_active = true;";

        await using var cmd = new NpgsqlCommand(sql, connection);
        cmd.Parameters.AddWithValue("@username", SelectedUser);
        
        await using var reader = await cmd.ExecuteReaderAsync();
        if (!await reader.ReadAsync())
        {
            ModelState.AddModelError("", "User not found.");
            await LoadLoginUsersAsync();
            return Page();
        }

        var username = reader.GetString(reader.GetOrdinal("username"));
        var expectedPassword = reader.GetString(reader.GetOrdinal("password_hash"));
        var role = reader.GetString(reader.GetOrdinal("role"));

        if (string.IsNullOrWhiteSpace(expectedPassword) || Password != expectedPassword)
        {
            ModelState.AddModelError("", "Incorrect password.");
            await LoadLoginUsersAsync();
            return Page();
        }

        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.Name, username)
        };

        if (role.Equals("admin", StringComparison.OrdinalIgnoreCase))
        {
            claims.Add(new Claim(ClaimTypes.Role, "Admin"));
        }
        else if (role.Equals("team", StringComparison.OrdinalIgnoreCase))
        {
            claims.Add(new Claim(ClaimTypes.Role, "Team"));
            claims.Add(new Claim("TeamName", username));
        }
        else if (role.Equals("judge", StringComparison.OrdinalIgnoreCase))
        {
            claims.Add(new Claim(ClaimTypes.Role, "Judge"));
        }   

        var identity = new ClaimsIdentity(
            claims,
            CookieAuthenticationDefaults.AuthenticationScheme);

        var principal = new ClaimsPrincipal(identity);

        await HttpContext.SignInAsync(
            CookieAuthenticationDefaults.AuthenticationScheme,
            principal);

        if (role.Equals("admin", StringComparison.OrdinalIgnoreCase) || role.Equals("judge", StringComparison.OrdinalIgnoreCase)) 
        {
            return RedirectToPage("/Judge");
        }

        return RedirectToPage("/Team", new { teamName = username });
    }

    private async Task LoadLoginUsersAsync()
    {
        LoginUsers = [];

        var connString = _configuration.GetConnectionString("DefaultConnection");
        await using var connection = new NpgsqlConnection(connString);
        await connection.OpenAsync();

        const string sql = @"
            SELECT username
            FROM accounts
            WHERE is_active = true
              AND role IN ('team', 'admin')
            ORDER BY
              CASE WHEN role = 'admin' THEN 0 ELSE 1 END,
              regexp_replace(username, '\d+$', ''),
              COALESCE(NULLIF(substring(username from '\d+$'), '')::int, 2147483647),
              username;";

        await using var cmd = new NpgsqlCommand(sql, connection);
        await using var reader = await cmd.ExecuteReaderAsync();

        while (await reader.ReadAsync())
        {
            LoginUsers.Add(reader.GetString(0));
        }

        LoginUsers = LoginUsers
            .OrderBy(static username => IsAdminUser(username) ? 0 : 1)
            .ThenBy(static username => GetSortPrefix(username))
            .ThenBy(static username => GetSortNumber(username))
            .ThenBy(static username => username, StringComparer.OrdinalIgnoreCase)
            .ToList();
    }

    private static bool IsAdminUser(string username) =>
        string.Equals(username, "admin", StringComparison.OrdinalIgnoreCase);

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