# HD Music Now homepage

Custom homepage for hdmusicnow.com, embedded in Kajabi as a single Code block:

```html
<div id="hdmn-mount"></div>
<script src="https://mayadex853.github.io/Dashboards/hdmn-homepage/hdmn.js"></script>
```

## Updating credits (no code needed)

Credits, carousels, stats and the speaking/press lists are read live from the Google Sheet
**"HD Music Now – Website Credits"** (`SHEET_ID` in `build.py`). The sheet must be shared as
*Anyone with the link: Viewer*. If it can't be reached, the page shows the built-in data from `credits.py`.

| Column   | Meaning |
|----------|---------|
| Section  | `Placement`, `Project`, `Award/Panel`, `Podcast/Radio`, `Press` or `Stat` |
| Title    | Show/film/event name (for `Stat`: the number, e.g. `10,000+`) |
| Detail   | Network/studio (Placement), exact credited role (Project), role/note (others), label (Stat) |
| Year     | Year (Project only) |
| Type     | Placement: `TV`, `Film`, `Trailers`, `Ads & Campaigns`, `Video Games`. Project: `TV Series`, `Film`, ... |
| Poster   | A poster file already on the site (e.g. `breaking-bad.jpg`) or a full image URL |
| Carousel | `Yes` to show the poster in the carousel |
| Order    | Carousel position (1 = first) |

Rows appear on the site in sheet order; Google may take a few minutes to refresh after an edit.

## Rebuilding (code changes only)

```bash
python3 build.py   # writes preview.html, kajabi-embed.html, hdmn.js
```

Everything is served from GitHub Pages (the `main` branch), with raw.githubusercontent.com as an automatic
poster fallback. Merge to `main` and the live page updates within ~10 minutes; the Kajabi Code block never changes.
