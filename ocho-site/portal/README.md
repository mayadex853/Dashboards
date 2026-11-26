# Ocho client portal — https://portal.ochoaudio.com

Private catalog for Ocho admins and invited clients: browse/search the catalog, stream, build playlists,
download MP3/WAV (single files or ZIPs), share playlists/albums by link, and see who listened and downloaded.

## How it runs (all Cloudflare, free tiers)
| Piece | Where |
|---|---|
| App (server + page) | Worker `ocho-portal`, custom domain `portal.ochoaudio.com` (zone ochoaudio.com) |
| Database | D1 `ocho-portal` (users, invites, sessions, playlists, shares, files, events) — `schema.sql` |
| Streaming MP3s | public R2 bucket `ocho-audio` via https://ochoaudio.com/ (same files as the website) |
| WAV masters | **private** R2 bucket `ocho-masters` (`OCHO-00NN/<name>.wav`, same names as the MP3s) — only the Worker can read it |
| Images | the website's assets on ochoaudio.com/site/<ref>/img/ |

Costs: Worker/D1 free tier; WAV storage ~22 GB ≈ $0.33/mo; R2 has no download (egress) fees.

## Accounts and access
- Invite-only. Admins create users on **Users** and send the private set-password link themselves (no email service).
  Lost password: **Reset link** on the same page.
- `admin`: everything, including Shared Links, Users, Analytics; downloads MP3 + WAV.
- `client`: browse/search, own playlists, stream; downloads per user: none / MP3 / MP3 + WAV.
- Share links (`/s/<token>`) open without a login. Each link has its own download level (stream / MP3 / MP3 + WAV),
  optional expiry, and can be turned off at any time. Shared playlists stay live: edits to the playlist show up in the link.
- Passwords: the browser derives a PBKDF2-SHA256 key (200k rounds, salted with the email); the server stores a salted SHA-256
  of that key. Logins are rate-limited (6 failures / 15 min). Sessions are HttpOnly cookies, 30 days.

## Analytics
Every login, link open, play, file download and ZIP download is an `events` row (with country). The **Analytics** page shows
totals, a daily chart, activity per shared link and per client, top played / downloaded tracks and a live activity feed.

## Deploy / update
Needs `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` (same as the website's publish step).
```
python3 deploy.py schema                      # once, or after editing schema.sql (idempotent)
python3 deploy.py worker                      # after any change to worker.js / app.html / the catalog (data.py, tracks/*.json)
python3 deploy.py domain                      # once
python3 deploy.py invite EMAIL "NAME" admin wav   # bootstrap an admin; prints a set-password link
python3 deploy.py files MANIFEST.jsonl        # register files for ZIP downloads (lines of {"key","size","crc"})
```
`build.py` bundles `app.html` + the catalog into `dist/worker.js` (not committed).

## Adding an album
1. Run the audio pipeline for it (see `../pipeline/README.md`) and rebuild the website as usual.
2. Upload its WAV masters to `ocho-masters/<ALBUM-ID>/<same name as the MP3>.wav` and its MP3s as usual.
3. Register CRC32 + size of the new MP3s and WAVs with `deploy.py files` (ZIP downloads need them; single-file downloads work without).
4. `python3 deploy.py worker` so the portal catalog includes the album.
The one-off copy of the catalog's WAVs from Mega (2026-11) used `pipeline/wav/` (list.mjs → map.py → dl.mjs, then `deploy.py files manifest.jsonl`).
