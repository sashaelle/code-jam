using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CodeJam2026.Pages;

public class LoginModel : PageModel
{
    private readonly IConfiguration _configuration;

    public LoginModel(IConfiguration configuration)
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

        var expectedPassword = _configuration[$"CodeJamAuth:Users:{SelectedUser}"];

        if (string.IsNullOrWhiteSpace(expectedPassword) || Password != expectedPassword)
        {
            ModelState.AddModelError("", "Incorrect password.");
            return Page();
        }

        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.Name, SelectedUser)
        };

        if (SelectedUser == "Admin")
        {
            claims.Add(new Claim(ClaimTypes.Role, "Admin"));
        }
        else
        {
            claims.Add(new Claim(ClaimTypes.Role, "Team"));
            claims.Add(new Claim("TeamName", SelectedUser));
        }

        var identity = new ClaimsIdentity(
            claims,
            CookieAuthenticationDefaults.AuthenticationScheme);

        var principal = new ClaimsPrincipal(identity);

        await HttpContext.SignInAsync(
            CookieAuthenticationDefaults.AuthenticationScheme,
            principal);

        if (SelectedUser == "Admin")
            return RedirectToPage("/Judge");

        return RedirectToPage("/Team", new { teamName = SelectedUser });
    }
}