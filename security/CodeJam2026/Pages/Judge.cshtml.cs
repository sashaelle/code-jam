using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace InvestorPrototype.Pages;

[Authorize(Roles = "Admin")]
public class JudgeModel : PageModel
{
    public void OnGet()
    {
    }
}