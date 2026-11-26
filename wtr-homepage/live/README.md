# Live hotfix builds

`speaker.js`: the speaker page as built from commit 993104c (branch `claude/fervent-hawking-3cd5em`, which carries the
pinned site nav), with one change: the hero line reads "Keynote speaker for founders, leaders & teams".
It is served from here so the live page keeps that branch's nav work. Once both branches merge, rebuild from
`build_speaker.py` and point the Kajabi Code block back at `wtr-homepage/speaker.js`.

`wtr.js`: the homepage as built from commit 993104c (same branch, for its nav), with the hero headline scaled to fit
(`clamp(46px,4.6vw,84px)`, so "old identity." no longer clips into the photo) and the micro line reading
"See which room is running your life." The same two edits are in `src/` on this branch.
Reds now match /rebuild: `--em:#d72626; --accent:#c21f1f`, brick wall tint `rgba(215,38,38,…)`, form errors `#ef5b5b` / `#d72626`.

Voice pass (brand board: no em dashes, no formulaic triads): `wtr.js`, `speaker.js` and `coaching.js` here are rebuilt
from 993104c with the copy edits in `src/` plus the hero fix and the /rebuild reds. Live pins point at these files.

`getstarted.js`: the new /getstarted page (src/getstarted.html + getstarted.css, build_getstarted.py), built on the
993104c base with the patches above. It reuses the homepage's wall + framework section. Old layout: data/old-getstarted-theme.json.

`programs.js`: the four Guided Transformation sales pages (/drifting-program etc.), built from 3b52cb1
(branch claude/email-fixes-welcome-drafts-v0xm2g) with the own-pace copy and new prices
($27 / $47 / $67 / $97 against a struck-through $997). Edited sources are in `programs-src/`.

`vip.js`, `meeting.js` (here, in live/): the /vip-retreat and /meeting-confirmed pages as pinned at 104658b, with
Christy B.'s graduation video in place of her original Vimeo video (kept as an HTML comment) and mp4 playback added.
The copies in `wtr-homepage/` carry later, unpublished edits.

Christy B. cleanup (Nov 15): one Christy testimonial per page, the graduation video. Her original Vimeo video and the
"Re-examining" quote are hidden, not deleted: HTML comments marked `hidden (Christy B. original)` in the built files,
and `"hidden": true` in data/testimonials.json (build_testimonials.py skips hidden entries). Note: coaching.js, wtr.js,
selfguided.js, testimonials.js and the /rebuild loaders include the copy rewrite from f5dc9ed, which was made in the
built files only; rebuilding them from src/ or the build scripts would drop that copy.
