#!/bin/bash
# Recreate the live build base: 993104c + every patch that is live, plus this branch's getstarted sources.
set -e
cd /home/user/Dashboards && rm -rf /tmp/claude-0/wt && git worktree prune && git worktree add -q /tmp/claude-0/wt 993104c
cd /tmp/claude-0/wt/wtr-homepage
sed -i 's#^\.w-hero h1{white-space:nowrap;font-size:clamp(46px,6vw,100px);#.w-hero h1{white-space:nowrap;font-size:clamp(46px,4.6vw,84px);#; s#^\.wtr\[data-dir="brick"\] \.w-hero h1{font-size:clamp(50px,6vw,100px);}#.wtr[data-dir="brick"] .w-hero h1{font-size:clamp(46px,4.6vw,84px);}#; s#--em:\#d8483b; --accent:\#b8322a;#--em:\#d72626; --accent:\#c21f1f;#; s#rgba(184,50,42,#rgba(215,38,38,#g; s#color:\#e08b7e;#color:\#ef5b5b;#; s#border-color:\#c4675a#border-color:\#d72626#' src/wtr.css
sed -i 's#See which of 4 operating modes is running your life.#See which room is running your life.#' src/wtr.html
sed -i 's#Keynote speaker for high-performance teams &amp; leaders#Keynote speaker for founders, leaders \&amp; teams#' src/speaker.html
python3 /tmp/claude-0/scratch/voice.py . >/dev/null
cp /home/user/Dashboards/wtr-homepage/src/getstarted.html /home/user/Dashboards/wtr-homepage/src/getstarted.css src/
cp /home/user/Dashboards/wtr-homepage/build_getstarted.py .
python3 /tmp/claude-0/scratch/hero.py .
python3 /tmp/claude-0/scratch/brand.py . >/dev/null
bash /tmp/claude-0/scratch/herocss.sh
python3 /tmp/claude-0/scratch/copy.py .
bash /tmp/claude-0/scratch/quizmodal.sh
python3 /tmp/claude-0/scratch/simplify.py .
