using System.Security.Claims;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Npgsql; 

namespace CodeJam2026.Pages.api.judge;

public class JudgeScoreModel : PageModel
{
    public async Task OnGetAsync()
    {
       
    }

    public async Task<IActionResult> OnPostAsync(int submission_id)
    {
        // This runs for:
        // POST /api/judge/score/123
    }
    
}