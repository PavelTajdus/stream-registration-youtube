-- Stream soutěž 2025
CREATE TABLE IF NOT EXISTS registrations (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(8) NOT NULL,
    newsletter BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pro rychlé vyhledávání podle kódu
CREATE INDEX IF NOT EXISTS idx_registrations_code ON registrations(code);
