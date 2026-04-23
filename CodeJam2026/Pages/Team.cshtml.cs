using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CodeJam2026.Pages;

[Authorize(Roles = "Team")]
public class TeamModel : PageModel
{
    private readonly ITeamSessionStore _teamSessionStore;

    public TeamModel(ITeamSessionStore teamSessionStore)
    {
        _teamSessionStore = teamSessionStore;
    }

    [BindProperty(SupportsGet = true)]
    public string teamName { get; set; } = "";

    public async Task<IActionResult> OnGetAsync()
    {
        var loggedInTeam = User.FindFirst("TeamName")?.Value;
        var cookieSessionId = User.FindFirst("TeamSessionId")?.Value;

        if (string.IsNullOrWhiteSpace(loggedInTeam) || string.IsNullOrWhiteSpace(cookieSessionId))
        {
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            return RedirectToPage("/Index");
        }

        if (!string.Equals(loggedInTeam, teamName, StringComparison.OrdinalIgnoreCase))
            return Forbid();

        var activeSessionId = _teamSessionStore.GetActiveSession(loggedInTeam);

        if (activeSessionId != cookieSessionId)
        {
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            return RedirectToPage("/Index");
        }

        return Page();
    }
}
