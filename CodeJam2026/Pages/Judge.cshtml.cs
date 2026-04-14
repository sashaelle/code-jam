using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CodeJam2026.Pages;

[Authorize(Roles = "Judge")]
public class JudgeModel : PageModel
{
    public void OnGet()
    {
    }
}