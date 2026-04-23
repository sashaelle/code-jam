namespace CodeJam2026.Services;

public interface ITeamSessionStore
{
    bool TryStartSession(string accountName, string sessionId, TimeSpan timeout);

    bool ValidateSession(string accountName, string sessionId, TimeSpan timeout);

    void RefreshSession(string accountName, string sessionId);

    void ClearActiveSession(string accountName);
}

public sealed class InMemoryTeamSessionStore : ITeamSessionStore
{
    private sealed class TeamSessionInfo
    {
        public string SessionId { get; set; } = "";
        public DateTime LastSeenUtc { get; set; }
    }

    private readonly Dictionary<string, TeamSessionInfo> _sessions = new(StringComparer.OrdinalIgnoreCase);
    private readonly object _sync = new();

    public bool TryStartSession(string accountName, string sessionId, TimeSpan timeout)
    {
        lock (_sync)
        {
            if (_sessions.TryGetValue(accountName, out var existing))
            {
                var age = DateTime.UtcNow - existing.LastSeenUtc;
                if (age <= timeout)
                {
                    return false;
                }
            }

            _sessions[accountName] = new TeamSessionInfo
            {
                SessionId = sessionId,
                LastSeenUtc = DateTime.UtcNow
            };

            return true;
        }
    }

    public bool ValidateSession(string accountName, string sessionId, TimeSpan timeout)
    {
        lock (_sync)
        {
            if (!_sessions.TryGetValue(accountName, out var existing))
            {
                return false;
            }

            if (!string.Equals(existing.SessionId, sessionId, StringComparison.Ordinal))
            {
                return false;
            }

            var age = DateTime.UtcNow - existing.LastSeenUtc;
            if (age > timeout)
            {
                _sessions.Remove(accountName);
                return false;
            }

            return true;
        }
    }

    public void RefreshSession(string accountName, string sessionId)
    {
        lock (_sync)
        {
            if (_sessions.TryGetValue(accountName, out var existing) &&
                string.Equals(existing.SessionId, sessionId, StringComparison.Ordinal))
            {
                existing.LastSeenUtc = DateTime.UtcNow;
            }
        }
    }

    public void ClearActiveSession(string accountName)
    {
        lock (_sync)
        {
            _sessions.Remove(accountName);
        }
    }
}