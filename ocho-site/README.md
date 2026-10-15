# Ocho Music Group website

Custom site for ochomusicgroup.com (English + Spanish): Home, About, Albums and Placements.
Same setup as `hdmn-homepage`: everything lives in one script, `ocho.js`, loaded by a single Kajabi Code block per page.

```html
<div id="ocho-mount" data-page="home" data-lang="en"></div>
<script src="https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@<commit>/ocho-site/ocho.js"></script>
```

| Kajabi page   | data-page    | data-lang |
|---------------|--------------|-----------|
| `/`           | `home`       | `en`      |
| `/es`         | `home`       | `es`      |
| `/about`      | `about`      | `en`      |
| `/about_es`   | `about`      | `es`      |
| `/albums`     | `albums`     | `en`      |
| `/albums_es`  | `albums`     | `es`      |
| `/placements` | `placements` | `en`      |
| `/placements_es` | `placements` | `es`   |

Keep the native Kajabi contact form section directly under the Code block on every page: every
"Contact / License Worldwide / Submit" button scrolls to it. The site draws its own navigation and footer,
so hide the Kajabi header/footer on these pages.

## Updating albums and placements (no code)

Albums and placements are read live from the Google Sheet **"Ocho Music Group – Website Albums & Placements"**
(`SHEET_ID`). The sheet must be shared as *Anyone with the link: Viewer*. If it can't be reached, the site
shows the built-in lists from `data.py`.

| Column           | Meaning |
|------------------|---------|
| Section          | `Album` or `Placement` |
| ID               | Albums only: catalog number (e.g. `OCHO-0023`). Connects the album to its streaming tracks |
| Title            | Album or show title |
| Artist / Network | Artist (albums) or network/platform (placements) |
| Category         | Albums: `Tropical & Salsa`, `Urbano`, `Regional Mexican & Tejano`, `Cinematic Underscore`, `TV Packages`, `Holiday`. Placements: `TV & Streaming`, `News & Talk`, `Sports`, `Ads`, `Video Games`. A new name creates a new filter. |
| Image            | A file already on the site (e.g. `telecumbias.jpg`), any image URL, or a Google Drive share link (file shared "anyone with the link") |
| Link             | Not used |
| Order            | Position (1 = first) |

## Streaming player

Album panels list every track with a waveform, plus alternate versions (instrumental, TV mix, stings...).
Audio is MP3 (320 kbps) on Cloudflare R2; its public URL goes in `AUDIO_BASE` (the player stays hidden while
that file is missing). Track lists live in `tracks/<ALBUM-ID>.json`.

To add or refresh audio: put the release masters through the Mega download step (320k MP3 + WAV discarded), then

```bash
python3 tracks.py <work dir>   # writes tracks/*.json and <work dir>/dist/<ALBUM-ID>/*.mp3
```

and upload `dist/` to the R2 bucket as-is.

## Rebuilding (code or copy changes)

```bash
python3 build.py <commit>   # writes ocho.js and preview.html
```

Copy (both languages) lives in `data.py`. Images are in `img/` and are served from raw.githubusercontent.com at the
given ref, with jsDelivr as an automatic fallback. Open `preview.html` locally to review every page:
`#/en/home`, `#/es/about`, `#/en/albums`, `#/es/placements`, and so on.
