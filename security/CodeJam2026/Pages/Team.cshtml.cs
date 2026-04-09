using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CodeJam2026.Pages;

[Authorize(Roles = "Team")]
public class TeamModel : PageModel
{
    [BindProperty(SupportsGet = true)]
    public string teamName { get; set; } = "";

    public IActionResult OnGet()
    {
        var loggedInTeam = User.FindFirst("TeamName")?.Value;

        if (string.IsNullOrWhiteSpace(loggedInTeam))
            return Forbid();

        if (!string.Equals(loggedInTeam, teamName, StringComparison.OrdinalIgnoreCase))
            return Forbid();

        return Page();
    }
}