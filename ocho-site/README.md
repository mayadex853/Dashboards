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

**Loader used on the live pages** (Kajabi Code block; set `data-page`/`data-lang` per page). It loads the current
build from our own Cloudflare domain (`python3 publish.py` replaces it; 5-minute cache) and falls back to a pinned
commit on jsDelivr if that fails:

```html
<div id="ocho-mount" data-page="albums" data-lang="en" style="min-height:100vh;background:#07050a"></div>
<script>(function(){var pin='<last known good commit>';function load(u,next){var s=document.createElement('script');s.src=u;s.onerror=function(){s.remove();if(next)next();};document.body.appendChild(s);}load('https://ochoaudio.com/site/ocho.js',function(){load('https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@'+pin+'/ocho-site/ocho.js');});})();</script>
```

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

## Live (since 2026-10-15)
The new site is live on ochomusicgroup.com. Kajabi landing pages (Encore theme, Code block + native contact form):
`/` (homepage = landing page "new-home", set as the site homepage in Kajabi), `/es`, `/about`, `/about_es`,
`/albums`, `/albums_es`, `/placements`, `/placements_es`, `/production-music`, `/production-music_es`.
Form thank-you pages (no form section, `data-page="thanks"`): `/thankyou` (EN) and `/gracias` (ES). Every EN form
section's thank-you URL is `/resource_redirect/landing_pages/2150704344`, every ES one `.../2150704348`.
Live pages omit `data-test` (links use PATHS); a test copy can add `data-test="1"` to link to TEST_PATHS instead.
The pre-redesign pages are kept as unpublished drafts: `es-legacy`, `about-legacy`, `about_es-legacy`
(to roll back: rename and republish them, and point the homepage setting back to the Kajabi site home page).
After a page edit in Kajabi, republish it (publish_at = now); the bare homepage URL can stay cached for a few minutes.
