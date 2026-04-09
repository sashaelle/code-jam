using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CodeJam2026.Pages
{
    public class SubmissionModel : PageModel
    {
        [BindProperty(SupportsGet = true)]
        public string TeamName { get; set; } = "";

        public void OnGet()
        {
        }
    }
}