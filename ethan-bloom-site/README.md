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

The "Upcoming Screenings" list reads the same Google Sheet tab ("Screenings") as hdmusicnow.com,
so one edit updates both sites. If the sheet can't be reached, the built-in list in the page script is shown.
