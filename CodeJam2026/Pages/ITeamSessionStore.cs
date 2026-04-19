public interface ITeamSessionStore
{
    string? GetActiveSession(string teamName);
    void SetActiveSession(string teamName, string sessionId);
    void ClearActiveSession(string teamName);
}