using System.Security.Claims;
using CodeJam2026.Services;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CodeJam2026.Pages;

public class LogoutModel : PageModel
{
    private readonly ITeamSessionStore _teamSessionStore;

    public LogoutModel(ITeamSessionStore teamSessionStore)
    {
        _teamSessionStore = teamSessionStore;
    }

    public async Task<IActionResult> OnGet()
    {
        var role = User.FindFirst(ClaimTypes.Role)?.Value;
        var name = User.FindFirst(ClaimTypes.Name)?.Value;

        if (string.Equals(role, "Team", StringComparison.OrdinalIgnoreCase) &&
            !string.IsNullOrWhiteSpace(name))
        {
            _teamSessionStore.ClearActiveSession(name);
        }

        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        return RedirectToPage("/Login");
    }
}