CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true
);

INSERT INTO accounts (username, password_hash, role, is_active)
VALUES
    ('Team1', 'team1pass', 'team', true),
    ('Team2', 'team2pass', 'team', true),
    ('Team3', 'team3pass', 'team', true),
    ('Team4', 'team4pass', 'team', true),
    ('Admin', 'adminpass', 'admin', true),
    ('judge', 'adminpass', 'judge', true)
ON CONFLICT (username) DO UPDATE
SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;
