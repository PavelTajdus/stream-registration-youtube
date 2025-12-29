-- Stream soutěž 2025
CREATE TABLE IF NOT EXISTS registrations (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(8) NOT NULL,
    newsletter BOOLEAN DEFAULT FALSE,
    is_winner BOOLEAN DEFAULT FALSE,
    no_show BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pro rychlé vyhledávání podle kódu
CREATE INDEX IF NOT EXISTS idx_registrations_code ON registrations(code);

-- Migrace: přidání sloupců (pokud tabulka již existuje)
-- ALTER TABLE registrations ADD COLUMN IF NOT EXISTS is_winner BOOLEAN DEFAULT FALSE;
-- ALTER TABLE registrations ADD COLUMN IF NOT EXISTS no_show BOOLEAN DEFAULT FALSE;
