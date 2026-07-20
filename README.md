# Visual Analytics Dashboard

A single-file, local visual analytics dashboard for two projects — **Wreck the Room**
and **History Engine**. Dark, minimal, no build step, no server, no dependencies.

## How to use

Open `index.html` in any modern browser (double-click it, or drag it into a browser tab).
That's it — everything runs client-side.

- **Toggle** between the two projects using the pill switch at the top right.
- Each project shows its metrics as **cards** with the latest weekly value, a
  week-over-week delta, and a **trend line** (sparkline) underneath. Hover a
  sparkline to read individual weeks.
- **Add weekly data** with the form at the bottom: pick the week, type the totals,
  and hit **Save week**. Re-saving the same week updates it. Blank fields are skipped.
- **View / manage saved weeks** expands a table where you can review or delete weeks.
- **Load sample data** fills 8 weeks of placeholder numbers so you can preview the
  layout. Delete them individually from the table when you're done.

### Metrics

**Wreck the Room**
- VSL Views (Vimeo)
- Quiz Completions (ScoreApp)
- Call Bookings (Calendly)
- Calls Held
- Conversions to Paid

**History Engine**
- Video Output (per week)
- Total Views (all platforms)
- Follower Growth (all platforms)
- PDF Page Visits (Kajabi)
- PDF Sales

## Export & backup

Three tools live under **Export & backup** at the bottom of the panel:

- **Export this project (CSV)** — downloads the current project's weeks as a CSV
  (Week + one column per metric), ready for Excel / Google Sheets.
- **Download full backup (JSON)** — a single snapshot of *both* projects.
- **Restore from backup…** — imports a JSON backup. Weeks are merged into whatever
  is already there; matching weeks are overwritten. Accepts both the wrapped backup
  file and a raw data export.

## Data storage & moving to a new computer

Data is saved in your browser's **localStorage** under the key
`analytics-dashboard-v1`. Nothing is uploaded anywhere.

Because localStorage is tied to a specific browser on a specific machine, **your
history does not follow you to a new Mac/PC automatically** (Migration Assistant and
iCloud don't reliably carry it either). To move it:

1. On the old machine: **Download full backup (JSON)**.
2. Copy the `.json` file to the new machine (AirDrop, cloud drive, email…).
3. On the new machine: open `index.html` and **Restore from backup…**, pick the file.

Clearing browser site data also erases it — keep a periodic JSON backup.

## Connecting APIs later

The app is structured so metrics come from a single per-project data model
(`PROJECTS` config + a storage layer in `index.html`). When you're ready to wire up
Vimeo, ScoreApp, Calendly, Kajabi, etc., you can replace the manual `upsertWeek`
calls with fetched values while keeping the same card/sparkline rendering.
