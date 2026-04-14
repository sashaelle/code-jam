CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true
);

INSERT INTO accounts (username, password_hash, role, is_active)
VALUES
    ('Admin', 'adminpass', 'admin', true)
ON CONFLICT (username) DO UPDATE
SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active;
