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
