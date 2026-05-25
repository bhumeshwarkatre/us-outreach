CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    creator_name TEXT,
    email TEXT UNIQUE,
    platform TEXT,
    niche TEXT,
    followers INTEGER,
    country TEXT,
    profile_url TEXT UNIQUE,

    status TEXT DEFAULT 'new',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);