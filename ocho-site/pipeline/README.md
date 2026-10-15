# Audio pipeline (Mega → MP3 → Cloudflare R2)

Only the final mixes are streamed (release masters + alternate mixes: instrumental, TV, acapella, cantina,
stings…). Stems, "export all" dry/wet bounces, backups and archive folders are skipped.

Sources (read-only Mega share links):
- Full catalog: https://mega.nz/folder/0bt1wJaL#8dYr_WZLa_bTmCp2PwHjYA (OCHO-0001…0023 except 0008/0014)
- OCHO-0008 Pistolero Guitars: https://mega.nz/folder/cfVUDJBK#8tUY_0BjEDZbPUKMtC2hEA
- OCHO-0014 Latin Holiday: https://mega.nz/folder/QaNwhK7K#syGHwI_BboIaU14-a6uvgg

## Steps (work dir W, e.g. a scratch folder)
1. `cd W && npm i megajs@latest` (1.3.7 cannot open the two single-album links).
2. Catalog: list the share into `selected.json` (WAVs not matching
   `stem|export all|backup|archive|/z_|/mp3/|dry|wet`), download
   `APM Releases/z_ISRC_Backup/OCHO_ISRC_MASTER_*.csv` to `meta/` and every `OCHO_00NN*.csv` APM sheet to
   `meta/apm/<ALBUM-ID>__<file>`, then `node mega-catalog.mjs <catalog link> 4`.
3. Single albums: `node mega-album.mjs <link> OCHO-0008` and `node mega-album.mjs <link> OCHO-0014`
   (run from a sibling folder; they write into `../mega/out`).
   Each WAV becomes a 320 kbps MP3 and is deleted. Mega is ~1–2 MB/s and has a transfer quota; the
   scripts retry with back-off. ~20 GB of WAVs → 1–3 hours.
4. `python3 ../tracks.py W` → writes `ocho-site/tracks/*.json` and `W/dist/<ALBUM-ID>/*.mp3`.
5. Upload `W/dist` to the R2 bucket (`CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`), enable public
   access and allow GET CORS from ochomusicgroup.com. Put the public base URL (ending in `/`) in
   `ocho-site/AUDIO_BASE` and rebuild.

## Live setup
- Bucket `ocho-audio` (Cloudflare R2), served at **https://ochoaudio.com/** (custom domain, CDN-cached;
  `ochoaudio.com` is registered with Cloudflare in the same account). The r2.dev test URL is disabled.
- CORS: GET/HEAD from https://www.ochomusicgroup.com and https://ochomusicgroup.com (Range allowed for seeking).
- To add an album: run steps 2–4 for it and upload only its new `dist/<ALBUM-ID>/` folder.

## Publishing the site (code, images, track lists)
The Kajabi pages load `https://ochoaudio.com/site/ocho.js` (cached 5 minutes). Images and track lists live under
`site/<asset-commit>/` on the same domain, with jsDelivr as an automatic fallback. After any change:
1. Commit image/track changes first (the asset folder is named after the last commit that touched `img/` or `tracks/`).
2. `python3 build.py`, commit `ocho.js` and `preview.html`, push.
3. `python3 publish.py` (uploads new assets once, then replaces `site/ocho.js`). Without this step the live
   pages keep showing the previous build.
