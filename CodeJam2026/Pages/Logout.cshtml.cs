using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using System.Security.Claims;

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
        var teamName = User.FindFirst("TeamName")?.Value;

        if (role == "Team" && !string.IsNullOrWhiteSpace(teamName))
        {
            _teamSessionStore.ClearActiveSession(teamName);
        }

        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        return RedirectToPage("/Index");
    }
}
