using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Npgsql; 

namespace InvestorPrototype.Pages;

public class IndexModel : PageModel
{
    private readonly IConfiguration _configuration;

    public IndexModel(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    [BindProperty]
    public string SelectedUser { get; set; } = "";

    [BindProperty]
    public string Password { get; set; } = "";

    public void OnGet()
    {
    }

    public async Task<IActionResult> OnPostAsync()
    {
        if (string.IsNullOrWhiteSpace(SelectedUser))
        {
            ModelState.AddModelError("", "Please select a team.");
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
            return Page();
        }

        var username = reader.GetString(reader.GetOrdinal("username"));
        var expectedPassword = reader.GetString(reader.GetOrdinal("password_hash"));
        var role = reader.GetString(reader.GetOrdinal("role"));

        if (string.IsNullOrWhiteSpace(expectedPassword) || Password != expectedPassword)
        {
            ModelState.AddModelError("", "Incorrect password.");
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
}