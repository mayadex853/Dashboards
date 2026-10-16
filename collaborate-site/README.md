# Collaborate Music Productions website

Static redesign of collaboratemusic.com. It needs no build step: `index.html` plus `img/`.

- **Edit:** change the text in `index.html`. Posters are in `img/` at 500×750 px.
- **Preview locally:** `python3 -m http.server` inside this folder, then open http://localhost:8000.
- **Host free:** connect this repo to Cloudflare Pages (or Netlify), set the build output directory to `collaborate-site`, leave the build command blank, then add `collaboratemusic.com` as a custom domain.
- **Inquiries** go to music@collaboratemusic.com. **Playlists** live in DISCO and are linked, not embedded.

## Bottom player and trailer pop-ups
- The player at the bottom streams `audio/<slug>.mp3` (128 kbps copies of the DISCO masters). Artwork lives in `img/art/<slug>.jpg`.
- Track names, artists, "Heard in" credits and waveforms are in the `TRACKS` list in the script at the end of `index.html`. To add a track, drop the MP3 and artwork in, then add one entry there.
- Any element with `data-play="<slug>"` plays that track. Any element with `data-video="yt:<YouTube id>"` or `data-video="vm:<Vimeo id>"` opens that video in the pop-up.
- The gold emblem (`img/emblem.png`) is used in the opening section, the contact section and the favicon.
