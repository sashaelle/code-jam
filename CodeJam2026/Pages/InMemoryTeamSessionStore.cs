using System.Collections.Concurrent;
public class InMemoryTeamSessionStore : ITeamSessionStore
{
    private readonly ConcurrentDictionary<string, string> _activeSessions = new();

    public string? GetActiveSession(string teamName)
    {
        _activeSessions.TryGetValue(teamName, out var sessionId);
        return sessionId;
    }

    public void SetActiveSession(string teamName, string sessionId)
    {
        _activeSessions[teamName] = sessionId;
    }

    public void ClearActiveSession(string teamName)
    {
        _activeSessions.TryRemove(teamName, out _);
    }
}