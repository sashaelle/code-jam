namespace CodeJam2026.Models
{
    public class SubmissionRequest
    {
        public int ProblemId { get; set; }
        public string Code { get; set; } = "";
        public string Language { get; set; } = "";
    }
}