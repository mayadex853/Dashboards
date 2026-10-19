"""Build the Wreck the Room Guided Transformation offer pages (one per $997 program).

One script serves all four; the Kajabi Code block picks the version with data-v:
  <div id="wtr-prog-mount" data-v="drifting"></div>
  <script src="https://mayadex853.github.io/Dashboards/wtr-homepage/programs.js"></script>

Versions: drifting, stalling, renovating, rebuilding (the four quiz results).
Adding ?bonus=1 to the page URL shows the quiz-bonus banner; the quiz follow-up emails link with it.

Copy comes from each offer's Kajabi description and the existing WTR pages; the client stories are the
same videos as the homepage and Work With Me page.
Outputs programs-preview.html (?v=<name>, add &bonus=1 for the banner) and programs.js.

Usage: python3 build_programs.py
"""
import json
from pathlib import Path

from build import KAJABI, minify_css

HERE = Path(__file__).parent
SRC = HERE / "src"

CHECKOUT = "https://www.wrecktheroom.com/offers/{}/checkout"
QUIZ = "https://quiz.wrecktheroom.com"
WORK = "https://www.wrecktheroom.com/coaching"
TEAM = "team@jodyfriedman.com"
HERO_IMG = KAJABI + "themes/2164062548/settings_images/5c2ccb4-53e8-036b-1e5-e5337614e3_Jody_Horizontal_Sunset.jpg"
BONUS = "Join in the next 5 days and get a private 30&#8209;minute call with Jody at week 3."

PROGRAMS = {
    "drifting": {
        "name": "Drifting",
        "cta": "Break Out of Drifting",
        "offer": "CfbMiu8q",
        "promise": "You’ve built a successful life that doesn’t quite feel like your own. "
                   "In five weeks, you’ll see the room you’ve been living in for what it is.",
        "fit": ["You’re a high achiever who has built a successful life.",
                "That life doesn’t quite feel like your own.",
                "You want to see clearly what the drift has cost you before you try to rebuild anything."],
        "note": "This isn’t the rebuild. It’s the work that has to happen before any rebuild is real.",
        "weeks": [("Identify the room", "Identify the room you’ve been operating from."),
                  ("Trace who built it", "Trace that room back to who built it."),
                  ("See the cost", "See clearly what the drift has actually cost you.")],
        "who": "High achievers who’ve built a successful life that doesn’t quite feel like their own.",
    },
    "stalling": {
        "name": "Stalling",
        "cta": "Break Out of Stalling",
        "offer": "UFGxioGz",
        "promise": "You can see exactly what needs to change, and you haven’t moved on it. "
                   "In five weeks, you’ll make the first real move.",
        "fit": ["You’re a high achiever who can see exactly what needs to change.",
                "You haven’t moved on it.",
                "You’re done with “almost” and ready to actually move."],
        "note": "Not a plan. A move.",
        "weeks": [("Name the stalls", "Name the stalls you’ve been living with."),
                  ("Spot the Almost", "Identify the Almost behaviors keeping you comfortable."),
                  ("Find what it protects", "Find what the stall is actually protecting."),
                  ("Make the move", "Make the first real move.")],
        "who": "High achievers who can see exactly what needs to change and haven’t moved on it.",
    },
    "renovating": {
        "name": "Renovating",
        "cta": "Break Out of Renovating",
        "offer": "RujeXGKk",
        "promise": "You’ve done serious work on yourself and keep running into the same patterns. "
                   "This is what comes after it.",
        "fit": ["You’re a high achiever who has done serious work on yourself: therapy, coaching, breakthroughs.",
                "You keep running into the same patterns anyway.",
                "You’re ready for something other than more of the same."],
        "note": "This isn’t more of the same. This is what comes after it.",
        "weeks": [("Trace the patterns", "Trace your patterns back to their origin."),
                  ("Audit the cost", "Audit what the work has actually cost you."),
                  ("Find the foundation", "Find the foundation none of it has touched.")],
        "who": "High achievers who’ve done serious work on themselves and keep running into the same patterns.",
    },
    "rebuilding": {
        "name": "Rebuilding",
        "cta": "Take Your Rebuild Further",
        "offer": "CGtLAnun",
        "promise": "You’re operating at a high level, and something below the surface is still running the show. "
                   "Not from zero. From exactly where you are.",
        "fit": ["You’re a high achiever operating at a high level.",
                "You sense something below the surface is still running the show.",
                "You want a clear picture of what full activation looks like for you."],
        "note": "Not from zero. From exactly where you are.",
        "weeks": [("Audit your activation", "Audit where you’re genuinely activated and where you’re still on autopilot."),
                  ("Map the blind spots", "Map the blind spots your conscious work hasn’t reached."),
                  ("Picture full activation", "Build a clear picture of what full activation actually looks like for you.")],
        "who": "High achievers operating at a high level who sense something below the surface is still running the show.",
    },
}

# Same client-story videos as the homepage and Work With Me page.
STORIES = """<div class="w-vids">
      <button class="w-vid w-rv" data-vimeo="1212945373" aria-label="Play Amara P.'s story"><img src="https://i.vimeocdn.com/video/2183502542-6dbdb5864e6b6d6e359c5610e8183b21375b41e76a0f4a63e0ed0be5c774e93d-d_640" alt="" loading="lazy"><span class="pl"></span><span class="nm"><b>Amara P.</b><span>Client story</span></span></button>
      <button class="w-vid w-rv d1" data-vimeo="1183442453" aria-label="Play Christy B.'s story"><img src="https://i.vimeocdn.com/video/2146308089-b43c720e144a206be4a8cafcec94672b0e0c9628a5dd43cce7b0c2b373d60259-d_640" alt="" loading="lazy"><span class="pl"></span><span class="nm"><b>Christy B.</b><span>Wreck the Room story</span></span></button>
      <button class="w-vid w-rv d2" data-vimeo="1183442331" aria-label="Play Jeremy D.'s story"><img src="https://i.vimeocdn.com/video/2146307512-9e5b02f9328fd95dc5d80a9dc62f277ee32edd65b3f8e85d807281ddafd24df0-d_640" alt="" loading="lazy"><span class="pl"></span><span class="nm"><b>Jeremy D.</b><span>Wreck the Room story</span></span></button>
    </div>"""


def btn(label, href, kind="p"):
    return f'<a class="w-btn {kind}" href="{href}">{label} <span class="ar">→</span></a>'


def render(key):
    p = PROGRAMS[key]
    name, buy = p["name"], CHECKOUT.format(p["offer"])
    fit = "".join(f'<li class="w-rv d{min(i, 3)}">{t}</li>' for i, t in enumerate(p["fit"]))
    weeks = "".join(f'<div class="w-rv d{min(i, 3)}"><span class="w-num">0{i + 1}</span><h3>{t}</h3><p>{d}</p></div>'
                    for i, (t, d) in enumerate(p["weeks"]))
    faq = [
        ("Who is this for?", p["who"]),
        ("How much time does it take?",
         "It runs over five weeks, at your own pace. Each lesson comes with an exercise. Plan time every week "
         "for the exercises, not just the videos: that’s where the work happens."),
        ("What if this isn’t my room?",
         f'Take the free assessment at <a href="{QUIZ}">quiz.wrecktheroom.com</a>. It shows whether you’re drifting, '
         "stalling, renovating, or rebuilding, and what’s actually creating the friction."),
        ("What if I want more support?",
         "Blueprint is the full Wreck the Room curriculum, self-guided. Council adds bi-weekly group coaching and "
         f'three private milestone calls with Jody. <a href="{WORK}">See all the ways to work with Jody</a>.'),
    ]
    qs = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faq)
    return f"""<div class="wtr pg" id="wtr-prog" data-dir="brick">
<div class="p-bonus" hidden><div class="w-wrap"><b>Quiz bonus</b><span>{BONUS}</span></div></div>

<header class="w-hero">
  <div class="w-hero-img"><img src="{HERO_IMG}" alt="Jody looking out at the ocean at sunset" fetchpriority="high"></div>
  <div class="w-wrap">
    <div class="w-hero-copy">
      <span class="w-eb">A Guided Transformation · 5 weeks</span>
      <h1><span class="ln"><span>Wreck the Room:</span></span><span class="ln"><span><em>{name}.</em></span></span></h1>
      <p class="w-hero-sub">{p["promise"]}</p>
      <div class="w-cta-row">
        {btn(p["cta"] + " · $997", buy)}
        <a class="w-link" href="#p-weeks" data-w-scroll>What you’ll do ↓</a>
      </div>
      <ul class="p-facts">
        <li><b>5 weeks</b><span>Guided</span></li>
        <li><b>Your pace</b><span>In your library</span></li>
        <li><b>$997</b><span>One-time</span></li>
      </ul>
    </div>
  </div>
</header>

<div class="w-sec w-diag p-fit">
  <div class="w-wrap p-fit-grid">
    <div><span class="w-eb w-rv">Is this your room?</span><h2 class="w-rv d1">This is for you <em>if…</em></h2></div>
    <div>
      <ul class="p-list">{fit}</ul>
      <p class="p-note w-rv">{p["note"]}</p>
    </div>
  </div>
</div>

<div class="w-sec p-weeks" id="p-weeks">
  <div class="w-wrap">
    <div class="p-weeks-head"><span class="w-eb c w-rv">Over five weeks</span><h2 class="w-rv d1">What you’ll <em>do.</em></h2></div>
    <div class="p-wk">{weeks}</div>
  </div>
</div>

<div class="w-sec p-how">
  <div class="w-wrap p-how-grid">
    <div>
      <span class="w-eb w-rv">How it works</span>
      <h2 class="w-rv d1">Watch. Do the work. <em>In that order.</em></h2>
      <p class="w-rv d2">The work happens in the exercise, not the video. Watching without doing the exercise is how people end up back in the same room a year from now with a lot of notes and nothing rebuilt.</p>
    </div>
    <ol class="p-steps">
      <li class="w-rv"><span class="p-n">1</span><div><h3>Open your program</h3><p>Everything is waiting in your library the moment you join. Start with the first lesson.</p></div></li>
      <li class="w-rv d1"><span class="p-n">2</span><div><h3>Watch, then do the exercise</h3><p>Don’t move on to the next lesson until you’ve done the exercise for the one you’re on.</p></div></li>
      <li class="w-rv d2"><span class="p-n">3</span><div><h3>Give it five weeks</h3><p>Block a little time each week and protect it. Consistency matters more than intensity.</p></div></li>
    </ol>
  </div>
</div>

<div class="w-sec p-offer" id="p-join">
  <div class="w-wrap">
    <div class="p-offer-card w-rv">
      <div class="p-offer-l">
        <span class="p-offer-k">What’s included</span>
        <h2>Wreck the Room: <em>{name}</em></h2>
        <ul>
          <li><b>The full {name} program</b>: five weeks of guided lessons</li>
          <li><b>An exercise with every lesson</b>, so you do the work, not just watch it</li>
          <li><b>Instant access</b> in your library, at your own pace</li>
          <li><b>Support from the team</b> at {TEAM}</li>
        </ul>
      </div>
      <div class="p-offer-r">
        <small>One-time</small>
        <span class="p-price">$997</span>
        {btn(p["cta"], buy)}
        <span class="p-bonus-note">Quiz bonus: {BONUS}</span>
        <span class="w-micro">Secure checkout. Instant access after payment.</span>
      </div>
    </div>
  </div>
</div>

<div class="w-sec p-stories">
  <div class="w-wrap">
    <div class="w-vids-head"><div><span class="w-eb w-rv">Client stories</span><h3 class="w-rv">Their rooms, in their words.</h3></div></div>
    {STORIES}
  </div>
</div>

<div class="w-sec p-faq">
  <div class="w-wrap">
    <div class="p-faq-head"><span class="w-eb c w-rv">Questions</span><h2 class="w-rv d1">Before you <em>start.</em></h2></div>
    <div class="p-qs w-rv">{qs}</div>
  </div>
</div>

<div class="w-shift">
  <div class="w-wrap">
    <p class="w-rv">You already know which room you’re in.</p>
    <h2 class="w-rv d1">Now <em>do something about it.</em></h2>
    <div class="w-cta-row">{btn(p["cta"] + " · $997", buy)}</div>
  </div>
</div>
<div class="p-help"><p>Questions? Email <a href="mailto:{TEAM}">{TEAM}</a> and we’ll take care of you.</p></div>
</div>"""


BONUS_JS = ("if(/[?&]bonus=1(&|$)/.test(location.search)){r.classList.add('has-bonus');"
            "var b=r.querySelector('.p-bonus');if(b)b.hidden=false;}")


def main():
    css = minify_css((SRC / "wtr.css").read_text() + (SRC / "programs.css").read_text())
    js = (SRC / "wtr.js").read_text()
    pages = {k: render(k) for k in PROGRAMS}
    loader = ("(function(){var m=document.getElementById('wtr-prog-mount');if(!m)return;"
              f"var P={json.dumps(pages)};var v=m.getAttribute('data-v');m.innerHTML=P[v]||P.drifting;"
              f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);\n{js}\n"
              f"var r=document.getElementById('wtr-prog');{BONUS_JS}"
              "if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){wtrInit(r);});else wtrInit(r);"
              "})();\n")
    (HERE / "programs.js").write_text(loader)
    preview = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Guided Transformation pages (preview)</title><style>{css}</style><style>html,body{{margin:0;background:#0a0908;}}</style></head><body>
<div id="wtr-prog-mount"></div>
<script>var v=new URLSearchParams(location.search).get('v')||'drifting';document.getElementById('wtr-prog-mount').setAttribute('data-v',v);</script>
<script>{loader.replace(f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);", "")}</script>
</body></html>"""
    (HERE / "programs-preview.html").write_text(preview)
    for f in ("programs-preview.html", "programs.js"):
        print(f"{f}: {(HERE / f).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
