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
- Money Spent (per week)
- Money Earned (per week)

History Engine also shows a **Spend vs. Earned** panel below the cards: both
money lines on one chart with total earned, total spent, net profit, and ROI,
plus a **Weekly / Monthly** toggle (monthly sums each calendar month).

## Export & backup

Three tools live under **Export & backup** at the bottom of the panel:

- **Export this project (CSV)** — downloads the current project's weeks as a CSV
  (Week + one column per metric), ready for Excel / Google Sheets.
- **Download full backup (JSON)** — a single snapshot of *both* projects.
- **Restore from backup…** — imports a JSON backup. Weeks are merged into whatever
  is already there; matching weeks are overwritten. Accepts both the wrapped backup
  file and a raw data export.

## Cloud Sync (share live between devices & people)

By default the dashboard is local to one browser. Turn on **Cloud Sync** (in the
panel, under Export & backup) and it becomes a shared, live dashboard: you and
anyone with the same login see and edit the same numbers from any device —
desktop, laptop, or phone. Changes save to the cloud and appear everywhere.

It runs on a **free Firebase project** (Google). The dashboard talks to Firebase
directly over HTTPS, so **use it from the GitHub Pages URL**
(`https://mayadex853.github.io/Dashboards/`), not the Claude artifact link (Claude
artifacts block outside network calls).

### One-time setup (~10 minutes)

1. Go to <https://console.firebase.google.com> → **Add project** (name it anything;
   you can skip Google Analytics). No credit card required.
2. **Create the database:** left menu → **Build → Realtime Database → Create
   Database**. Pick a location, start in **locked mode**. Copy the database URL
   shown at the top (looks like `https://your-app-default-rtdb.firebaseio.com`).
3. **Set the rules** so only logged-in people can read/write: open the **Rules**
   tab and paste, then **Publish**:
   ```json
   { "rules": { "store": { ".read": "auth != null", ".write": "auth != null" } } }
   ```
4. **Turn on login:** **Build → Authentication → Get started → Email/Password →
   Enable → Save**. Then **Users → Add user** and create one shared login (an
   email + password you and your son will both use). *(Prefer separate logins?
   Add one user each — any of them works.)*
5. **Get the Web API key:** gear icon → **Project settings → General**. Under
   *Your apps*, click the **web** icon (`</>`) to register a web app (any
   nickname). In the config shown, copy the **`apiKey`** value (starts with
   `AIza…`).
6. In the dashboard, open **Cloud Sync**, paste the **API key**, the **Database
   URL**, and the **shared email + password**, then **Connect & sync**.

Do step 6 once on each device (yours and your son's) using the same login. After
that, every change syncs automatically. The header shows a live status dot
(grey = local only, green = synced, blue = syncing, red = error). Sync is
best-effort and offline-safe: edits always save locally first and push to the
cloud when the connection is back.

**Security note:** the API key and database URL are not secrets — they only
identify your project. Access is controlled by the login and the rule above, so
keep the email/password private and don't loosen the rules to `true`.

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
