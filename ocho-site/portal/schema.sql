-- Ocho client portal (Cloudflare D1)
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL DEFAULT '',
  company TEXT NOT NULL DEFAULT '',
  role TEXT NOT NULL DEFAULT 'client',          -- admin | client
  download TEXT NOT NULL DEFAULT 'mp3',         -- none | mp3 | wav (what this user may download)
  pw_salt TEXT, pw_hash TEXT,
  disabled INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL, last_login INTEGER
);
CREATE TABLE IF NOT EXISTS invites (              -- account invites and password resets
  token_hash TEXT PRIMARY KEY,
  email TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'invite',   -- invite | reset
  created_by INTEGER, created_at INTEGER NOT NULL, expires_at INTEGER NOT NULL, used_at INTEGER
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created_at INTEGER NOT NULL, expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS login_fails (email TEXT NOT NULL, ts INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS playlists (
  id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER NOT NULL, name TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS playlist_items (
  playlist_id INTEGER NOT NULL, file TEXT NOT NULL,   -- version file key without extension, e.g. OCHO-0001/mucho-money--tv-mix
  position INTEGER NOT NULL, added_at INTEGER NOT NULL, PRIMARY KEY (playlist_id, file)
);
CREATE TABLE IF NOT EXISTS shares (
  token TEXT PRIMARY KEY, kind TEXT NOT NULL, ref TEXT NOT NULL,   -- kind: playlist (ref = id) | album (ref = OCHO-00NN)
  title TEXT NOT NULL, recipient TEXT NOT NULL DEFAULT '', download TEXT NOT NULL DEFAULT 'none',
  created_by INTEGER NOT NULL, created_at INTEGER NOT NULL, expires_at INTEGER, revoked INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS files (                -- sizes + CRC32 so ZIPs can stream without re-reading files
  key TEXT PRIMARY KEY, size INTEGER NOT NULL, crc INTEGER NOT NULL      -- key: OCHO-0001/name.mp3 | .wav
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER NOT NULL, kind TEXT NOT NULL,   -- login | view | play | download | zip
  user_id INTEGER, share TEXT, file TEXT, fmt TEXT, n INTEGER, country TEXT
);
CREATE INDEX IF NOT EXISTS ev_ts ON events(ts);
CREATE INDEX IF NOT EXISTS ev_share ON events(share);
CREATE INDEX IF NOT EXISTS pi_pl ON playlist_items(playlist_id, position);
