# Live hotfix builds

`speaker.js`: the speaker page as built from commit 993104c (branch `claude/fervent-hawking-3cd5em`, which carries the
pinned site nav), with one change: the hero line reads "Keynote speaker for founders, leaders & teams".
It is served from here so the live page keeps that branch's nav work. Once both branches merge, rebuild from
`build_speaker.py` and point the Kajabi Code block back at `wtr-homepage/speaker.js`.
