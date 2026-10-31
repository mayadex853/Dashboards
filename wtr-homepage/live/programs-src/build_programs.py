"""Build the Wreck The Room™ Guided Transformation offer pages (one per program: $27 / $47 / $67 / $97, shown against the regular $997).

One script serves all four; the Kajabi Code block picks the version with data-v:
  <div id="wtr-prog-mount" data-v="drifting"></div>
  <script src="https://mayadex853.github.io/Dashboards/wtr-homepage/programs.js"></script>

Versions: drifting, stalling, renovating, rebuilding (the four quiz results).

Copy comes from each offer's Kajabi description and the existing WTR pages; the client stories are the
same videos as the homepage and Work With Me page.
Outputs programs-preview.html (?v=<name>) and programs.js.

Usage: python3 build_programs.py
"""
import json
from pathlib import Path

from build import KAJABI, minify_css

HERE = Path(__file__).parent
SRC = HERE / "src"

CHECKOUT = "https://www.wrecktheroom.com/offers/{}/checkout"
QUIZ = "https://quiz.wrecktheroom.com"
WORK = "https://www.wrecktheroom.com/rebuild"
TEAM = "team@jodyfriedman.com"
HERO_IMG = KAJABI + "themes/2164062548/settings_images/5c2ccb4-53e8-036b-1e5-e5337614e3_Jody_Horizontal_Sunset.jpg"
WAS = 997  # regular price, shown struck through

PROGRAMS = {
    "drifting": {
        "name": "Drifting",
        "cta": "Break Out of Drifting",
        "offer": "CfbMiu8q",
        "price": 27,
        "headline": ["Life is happening", "<em>to</em> you.", "When did you stop steering?"],
        "sub": "Five lessons to wake up from autopilot and take back control, at your own pace.",
        "pain": ["Your days run on autopilot: same routine, same pressures, same results.",
                 "It feels like the rat race. You keep running, but you never chose the track.",
                 "Decisions get made <em>for</em> you by your calendar, your obligations, other people’s expectations.",
                 "You’re not unhappy enough to change anything, and not fulfilled enough to feel good about it.",
                 "Years go by, and you can’t point to when you last chose your direction on purpose."],
        "after": "You’re awake. You can see the room you’ve been living in and who built it, so it stops running you. "
                 "You’re back in the driver’s seat, making choices on purpose instead of letting life happen to you.",
        "weeks": [("Identify the room", "Identify the room you’ve been operating from."),
                  ("Trace who built it", "Trace that room back to who built it."),
                  ("See the cost", "See clearly what the drift has actually cost you.")],
        "who": "High achievers who are running on autopilot: not yet aware of the room they’re in, and not taking "
               "action to change it. Life is happening to them instead of being chosen by them.",
    },
    "stalling": {
        "name": "Stalling",
        "cta": "Break Out of Stalling",
        "offer": "UFGxioGz",
        "price": 47,
        "headline": ["You know what", "needs to change.", "<em>So why do you keep finding reasons not to?</em>"],
        "sub": "Five lessons to stop thinking about it and start doing the work, at your own pace.",
        "pain": ["You’ve analyzed it from every angle, and you’re still in the same place.",
                 "There’s always a reason it isn’t the right time: too busy, need more info, after this next thing.",
                 "You stay busy with everything <em>except</em> the one thing that actually needs your attention.",
                 "Analysis paralysis feels productive. It isn’t.",
                 "No one is harder on you about it than you are."],
        "after": "You’re someone who moves. You’ve seen what the excuses were protecting, so they lose their grip. "
                 "You’ve done the real work instead of the busy work, and you’ve made the first real move. Not a plan. A move.",
        "weeks": [("Name the stalls", "Name the stalls you’ve been living with."),
                  ("Spot the Almost", "Identify the Almost behaviors keeping you comfortable."),
                  ("Find what it protects", "Find what the stall is actually protecting."),
                  ("Make the move", "Make the first real move.")],
        "who": "High achievers who are fully aware of what needs to change but aren’t taking action on it. "
               "They find excuses, distractions and analysis instead of doing the real work.",
    },
    "renovating": {
        "name": "Renovating",
        "cta": "Break Out of Renovating",
        "offer": "RujeXGKk",
        "price": 67,
        "headline": ["New strategy. New hire.", "New city. Same results.", "<em>What if the problem isn’t out there?</em>"],
        "sub": "Five lessons to stop rearranging the furniture and work on the one thing that moves everything: who you are.",
        "pain": ["When something isn’t working, you change something: the plan, the team, the business model, the location.",
                 "Each fix feels like <em>the</em> answer, for a while.",
                 "Then the same problems show up again in the new setup.",
                 "You’re working hard, but the results don’t match the effort.",
                 "Nobody has told you the truth: the strategy isn’t the problem. The identity running the strategy is."],
        "after": "You stop renovating the house and start working on the person living in it. You can see the identity "
                 "that’s been driving your decisions, so your effort finally goes to the thing that changes everything else.",
        "weeks": [("Trace the patterns", "Trace the patterns that keep repeating back to their origin."),
                  ("Audit the cost", "Audit what all the fixing has actually cost you."),
                  ("Find the foundation", "Find the identity underneath that none of the changes have touched.")],
        "who": "High achievers who are taking plenty of action, but on the wrong things: a new strategy, a new hire, "
               "a new location. They haven’t yet seen that what really needs work is who they are.",
    },
    "rebuilding": {
        "name": "Rebuilding",
        "cta": "Take Your Rebuild Further",
        "offer": "CGtLAnun",
        "price": 97,
        "headline": ["You’re doing the work.", "<em>So why do you keep hitting the same ceiling?</em>"],
        "sub": "Five lessons and a real framework to take your rebuild further, at your own pace.",
        "pain": ["You’re self-aware, and you act on it.",
                 "You’ve grown a lot, and lately the growth has flattened out.",
                 "You can feel there’s another level, but you don’t have a clear way to dig into what’s holding you there.",
                 "Insight on its own isn’t getting you through anymore.",
                 "The higher you go, the more those last blind spots cost."],
        "after": "You have a framework for going deeper into your identity, not just more insight. You know where you’re fully "
                 "activated and where you’re still running on old wiring, and you have a clear path through the plateau to your next level.",
        "weeks": [("Audit your activation", "Audit where you’re genuinely activated and where you’re still on autopilot."),
                  ("Map the blind spots", "Map the blind spots your conscious work hasn’t reached."),
                  ("Picture full activation", "Build a clear picture of what full activation actually looks like for you.")],
        "who": "High achievers who are aware and taking action, and still hitting plateaus, because they don’t yet have "
               "a framework to dig into their identity at the next level.",
    },
}

# Same client-story videos as the homepage and Work With Me page.
STORIES = """<div class="w-vids">
      <button class="w-vid w-rv" data-vimeo="1212945373" aria-label="Play Amara P.'s story"><img src="https://i.vimeocdn.com/video/2183502542-6dbdb5864e6b6d6e359c5610e8183b21375b41e76a0f4a63e0ed0be5c774e93d-d_640" alt="" loading="lazy"><span class="pl"></span><span class="nm"><b>Amara P.</b><span>Client story</span></span></button>
      <button class="w-vid w-rv d1" data-vimeo="1183442453" aria-label="Play Christy B.'s story"><img src="https://i.vimeocdn.com/video/2146308089-b43c720e144a206be4a8cafcec94672b0e0c9628a5dd43cce7b0c2b373d60259-d_640" alt="" loading="lazy"><span class="pl"></span><span class="nm"><b>Christy B.</b><span>Wreck The Room™ story</span></span></button>
      <button class="w-vid w-rv d2" data-vimeo="1183442331" aria-label="Play Jeremy D.'s story"><img src="https://i.vimeocdn.com/video/2146307512-9e5b02f9328fd95dc5d80a9dc62f277ee32edd65b3f8e85d807281ddafd24df0-d_640" alt="" loading="lazy"><span class="pl"></span><span class="nm"><b>Jeremy D.</b><span>Wreck The Room™ story</span></span></button>
    </div>"""


def btn(label, href, kind="p"):
    return f'<a class="w-btn {kind}" href="{href}">{label} <span class="ar">→</span></a>'


def render(key):
    p = PROGRAMS[key]
    name, buy = p["name"], CHECKOUT.format(p["offer"])
    price = f'${p["price"]}'
    pain = "".join(f'<li class="w-rv d{min(i, 3)}">{t}</li>' for i, t in enumerate(p["pain"]))
    h1 = "".join(f'<span class="ln"><span>{t}</span></span>' for t in p["headline"])
    weeks = "".join(f'<div class="w-rv d{min(i, 3)}"><span class="w-num">0{i + 1}</span><h3>{t}</h3><p>{d}</p></div>'
                    for i, (t, d) in enumerate(p["weeks"]))
    faq = [
        ("Who is this for?", p["who"]),
        ("How much time does it take?",
         "As much as you want it to. It’s five lessons, each with an exercise. Some people finish in one focused "
         "sitting, some take five days, some spread it over five weeks. The choice is yours. Just don’t skip the "
         "exercises: that’s where the work happens."),
        ("Why is it priced so low?",
         f"The program is normally ${WAS}. Right now it’s {{PRICE}} because the fastest way to see what this work "
         "can do is to start it. Same lessons, same exercises."),
        ("What if this isn’t my room?",
         f'Take the free assessment at <a href="{QUIZ}">quiz.wrecktheroom.com</a>. It shows whether you’re drifting, '
         "stalling, renovating, or rebuilding, and what’s actually creating the friction."),
        ("What if I want more support?",
         "Blueprint is the full Wreck The Room™ curriculum, self-guided. Council adds bi-weekly group coaching and "
         f'three private milestone calls with Jody. <a href="{WORK}">Compare Blueprint, Council and Inner Circle</a>.'),
    ]
    qs = "".join(f"<details><summary>{q}</summary><p>{a.replace('{PRICE}', price)}</p></details>" for q, a in faq)
    return f"""<div class="wtr pg" id="wtr-prog" data-dir="brick">

<header class="w-hero">
  <div class="w-hero-img"><img src="{HERO_IMG}" alt="Jody looking out at the ocean at sunset" fetchpriority="high"></div>
  <div class="w-wrap">
    <div class="w-hero-copy">
      <span class="w-eb">Wreck The Room™: {name} · A guided transformation in five lessons</span>
      <h1 class="p-h1">{h1}</h1>
      <p class="w-hero-sub">{p["sub"]}</p>
      <div class="w-cta-row">
        {btn(p["cta"] + " · " + price, buy)}
        <a class="w-link" href="#p-weeks" data-w-scroll>How you’ll get there ↓</a>
      </div>
      <ul class="p-facts">
        <li><b>5 lessons</b><span>Guided</span></li>
        <li><b>Your pace</b><span>1 sitting to 5 weeks</span></li>
        <li class="p-fact-price"><b><s>${WAS}</s>{price}</b><span>One-time</span></li>
      </ul>
    </div>
  </div>
</header>

<div class="w-sec w-diag p-fit">
  <div class="w-wrap p-fit-grid">
    <div><span class="w-eb w-rv">If you’re {name.lower()}</span><h2 class="w-rv d1">Sound <em>familiar?</em></h2></div>
    <div><ul class="p-list">{pain}</ul></div>
  </div>
</div>

<div class="w-sec p-after">
  <div class="w-wrap">
    <span class="w-eb c w-rv">Who you’ll be</span>
    <h2 class="w-rv d1">Five lessons <em>from now.</em></h2>
    <p class="p-after-t w-rv d2">{p["after"]}</p>
    <div class="w-cta-row w-rv d3">{btn(p["cta"] + " · " + price, buy)}</div>
  </div>
</div>

<div class="w-sec p-weeks" id="p-weeks">
  <div class="w-wrap">
    <div class="p-weeks-head"><span class="w-eb c w-rv">The path</span><h2 class="w-rv d1">How you’ll <em>get there.</em></h2></div>
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
      <li class="w-rv d2"><span class="p-n">3</span><div><h3>Go at your pace</h3><p>One sitting, five days or five weeks. The choice is yours. Just finish what you start.</p></div></li>
    </ol>
  </div>
</div>

<div class="w-sec p-offer" id="p-join">
  <div class="w-wrap">
    <div class="p-offer-card w-rv">
      <div class="p-offer-l">
        <span class="p-offer-k">What’s included</span>
        <h2>Wreck The Room™: <em>{name}</em></h2>
        <ul>
          <li><b>The full {name} program</b>: five guided lessons, all open the moment you join</li>
          <li><b>An exercise with every lesson</b>, so you do the work, not just watch it</li>
          <li><b>Instant access</b> in your library: one sitting, five days or five weeks</li>
          <li><b>Support from the team</b> at {TEAM}</li>
        </ul>
      </div>
      <div class="p-offer-r">
        <small>One-time</small>
        <span class="p-price"><s class="p-strike">${WAS}</s><span class="p-full">{price}</span><span class="p-save">You save ${WAS - p["price"]}</span></span>
        {btn(p["cta"], buy)}
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
    <div class="w-cta-row">{btn(p["cta"] + " · " + price, buy)}</div>
  </div>
</div>
<div class="p-help"><p>Questions? Email <a href="mailto:{TEAM}">{TEAM}</a> and we’ll take care of you.</p></div>
</div>"""


def main():
    css = minify_css((SRC / "wtr.css").read_text() + (SRC / "programs.css").read_text())
    js = (SRC / "wtr.js").read_text()
    pages = {k: render(k) for k in PROGRAMS}
    loader = ("(function(){var m=document.getElementById('wtr-prog-mount');if(!m)return;"
              f"var P={json.dumps(pages)};var v=m.getAttribute('data-v');m.innerHTML=P[v]||P.drifting;"
              f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);\n{js}\n"
              "var r=document.getElementById('wtr-prog');"
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
