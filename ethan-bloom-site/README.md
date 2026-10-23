# Ethan Bloom — site redesign

Static, single-page redesign of ethanbloomthefilm.com.

- `index.html` — deployable page (open in a browser or upload to any static host)
- `page.html` — same page as an artifact fragment (no doctype wrapper)
- `img/` — poster, stills and headshots (web-sized); `trailer.mp4` — trailer re-encoded to H.264 MP4

"Become a Fan" links to the existing WordPress page and form at /becomeafan/.

## Publishing to ethanbloomthefilm.com (WordPress on 10Web)

Needs `WP_USER` and `WP_APP_PASSWORD` (a WordPress Application Password) in the environment.

```bash
python3 deploy_wp.py stage    # uploads media, publishes the page at /new-home for review
python3 deploy_wp.py live     # makes it the homepage
python3 deploy_wp.py revert   # puts the original homepage (page 162) back
```

## Screenings

The "Upcoming Screenings" list reads the "Screenings" tab of its own Google Sheet, "Ethan Bloom Screenings"
(https://docs.google.com/spreadsheets/d/17LFDMVQwn0nRBs7uM53KXpaaNsJfCcPwk5UVypogzmc/edit), separate from the
HD Music Now sheet. The sheet must be viewable by anyone with the link; a "How to update" tab explains the columns. If the sheet can't be reached, the built-in list in the page script is shown.
Columns: City, Venue, Date (YYYY-MM-DD or blank), Label, Note, Tickets. A Tickets link adds a "Tickets" button to
that screening; upcoming rows without one get a "Showtimes" button to Menemsha Films, and past dates get no button.
