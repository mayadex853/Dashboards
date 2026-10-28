"""Build the Wreck The Room™ thank-you pages (where each offer sends buyers after checkout).

One script serves every page; the Kajabi Code block picks the version with data-v:
  <div id="wtr-ty-mount" data-v="blueprint"></div>
  <script src="https://mayadex853.github.io/Dashboards/wtr-homepage/thankyou.js"></script>

Versions and the offers that redirect to them:
  blueprint   Blueprint (also offers the Blueprint Add-On, so only Blueprint buyers see it)
  inner       Inner Circle
  council     Council
  guided      Drifting, Stalling, Renovating, Rebuilding
  session     Clarity Session, Blueprint Add-On

Every link here comes from the offer's own welcome email or checkout.
Outputs thankyou-preview.html (all versions, ?v=<name> to switch) and thankyou.js.

Usage: python3 build_thankyou.py
"""
import json
import re
from pathlib import Path

from build import LOGO, minify_css

HERE = Path(__file__).parent
SRC = HERE / "src"

LIBRARY = "https://www.wrecktheroom.com/library"
WORKBOOK = "https://workbook.wrecktheroom.com/"
TEAM = "team@jodyfriedman.com"
ADDON = "https://www.wrecktheroom.com/offers/x9YkpqPT/checkout"

EMAIL_STEP = ("Check your email",
              "Your receipt and login details are on their way. If you don't see them in a few minutes, "
              "check your spam or promotions folder.", None)


def btn(label, href, kind="p"):
    return f'<a class="w-btn {kind}" href="{href}">{label} <span class="ar">→</span></a>'


def link(label, href):
    return f'<a class="w-link" href="{href}" target="_blank" rel="noopener">{label} →</a>'


VERSIONS = {
    "blueprint": {
        "lead": "Welcome to <b>Wreck The Room™: Blueprint</b>. Here's exactly what to do next.",
        "steps": [
            EMAIL_STEP,
            ("Open your workbook",
             "This is your companion for the whole program. Keep it open <b>alongside every lesson</b>. "
             "Your answers save in your browser, so export a backup as you go.",
             link("Open workbook.wrecktheroom.com", WORKBOOK)),
            ("Start Lesson 1: Welcome & Orientation",
             "Watch the lesson, then do the workbook exercise, in that order. "
             "The work happens in the exercise, not the video.",
             btn("Go to my library", LIBRARY)),
            ("Introduce yourself in Architects",
             "Your private community is inside your account. Say hello in <b>Discussion</b>; "
             "you're not the only one doing this work right now.", None),
        ],
        "upsell": True,
    },
    "inner": {
        "lead": "Welcome to <b>Wreck The Room™: Inner Circle</b>. Here's exactly what to do next.",
        "steps": [
            EMAIL_STEP,
            ("Start Lesson 1: Welcome & Orientation",
             "Open your workbook, log in, and start with the orientation. "
             "Most people finish it within 24 to 48 hours. Awareness is the goal.",
             btn("Go to my library", LIBRARY) + " " + link("Open the workbook", WORKBOOK)),
            ("Book your first private session",
             "Once you've done the orientation, book your first session with Jody. "
             "<b>Save this link</b>: it's your booking link for every session in your container.",
             btn("Book my first session", "https://calendly.com/jody_friedman/wreck-the-room-private-client", "o")),
            ("Connect on Voxer",
             "Download <b>Voxer</b> and connect with Jody at <b>@jodyfriedman</b> for support between sessions.", None),
        ],
    },
    "council": {
        "lead": "Welcome to <b>Wreck The Room™: Council</b>. Here's exactly what to do next.",
        "steps": [
            EMAIL_STEP,
            ("Start Lesson 1: Welcome & Orientation",
             "Open your workbook, log in, and complete the orientation <b>before your first group call</b>.",
             btn("Go to my library", LIBRARY) + " " + link("Open the workbook", WORKBOOK)),
            ("Join Architects & find your call schedule",
             "Introduce yourself in <b>Discussion</b>, then check <b>Meetups</b> inside the community "
             "for your cohort's start date and group call schedule.", None),
            ("Book your orientation call with Jody",
             "Right after Lesson 1, book your first of three private milestone calls (45 minutes).",
             btn("Book my orientation call", "https://calendly.com/jody_friedman/45-min-orientation", "o")),
        ],
    },
    "guided": {
        "lead": "Welcome to your <b>Wreck The Room™ Guided Transformation</b>. Here's exactly what to do next.",
        "steps": [
            EMAIL_STEP,
            ("Open your program",
             "Your program is waiting in your library. Start with the first lesson.",
             btn("Go to my library", LIBRARY)),
            ("Do the exercise after every lesson",
             "Watch the lesson, then do the exercise, in that order. "
             "The work happens in the exercise, not the video. Give it five weeks.", None),
        ],
    },
    "session": {
        "lead": "Your session with Jody is confirmed. Here's exactly what to do next.",
        "steps": [
            EMAIL_STEP,
            ("Pick your session time",
             "Open your account and choose a time that works for you. "
             "Book it now while it's top of mind.",
             btn("Go to my library", LIBRARY)),
            ("Come with one honest question",
             "Before the session, write down the one thing you most want clarity on. "
             "That's where we'll start.", None),
        ],
    },
}

UPSELL = f"""<aside class="ty-up w-rv">
  <div class="ty-up-l">
    <span class="ty-up-k">Optional · Blueprint add-on</span>
    <h2>Want Jody in your <em>corner?</em></h2>
    <p>Add three 1:1 alignment coaching sessions with Jody, timed to your Blueprint work.</p>
    <ul><li>One at the beginning</li><li>One in the middle</li><li>One at the end</li></ul>
  </div>
  <div class="ty-up-r">
    <small>Add-on</small>
    <span class="ty-price">$2,000</span>
    {btn("Add the 3 sessions", ADDON)}
    <span class="w-micro">Non-refundable. All sales are final.</span>
  </div>
</aside>"""


def render(name):
    v = VERSIONS[name]
    steps = "".join(
        f'<li class="ty-step w-rv"><span class="ty-n">{i}</span><div><h3>{t}</h3><p>{body}</p>{cta or ""}</div></li>'
        for i, (t, body, cta) in enumerate(v["steps"], 1))
    return f"""<div class="wtr ty" id="wtr-ty" data-dir="brick">
<div class="w-wrap">
  <div class="ty-bar"><a href="https://www.wrecktheroom.com/"><img src="{LOGO}" alt="Jody Friedman"></a><span>Payment confirmed</span></div>
  <header class="ty-hero">
    <div class="ty-check"><svg viewBox="0 0 24 24"><path pathLength="1" d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>
    <h1>You're <em>in.</em></h1>
    <p>{v["lead"]}</p>
  </header>
  <ol class="ty-steps">{steps}</ol>
  {UPSELL if v.get("upsell") else ""}
  <div class="ty-help"><p>Questions? Email <a href="mailto:{TEAM}">{TEAM}</a> and we'll take care of you.</p></div>
</div>
</div>"""


def main():
    css = minify_css((SRC / "wtr.css").read_text() + (SRC / "thankyou.css").read_text())
    js = (SRC / "wtr.js").read_text()
    pages = {k: render(k) for k in VERSIONS}
    loader = ("(function(){var m=document.getElementById('wtr-ty-mount');if(!m)return;"
              f"var P={json.dumps(pages)};var v=m.getAttribute('data-v');m.innerHTML=P[v]||P.guided;"
              f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);\n{js}\n"
              "var r=document.getElementById('wtr-ty');"
              "if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){wtrInit(r);});else wtrInit(r);"
              "})();\n")
    (HERE / "thankyou.js").write_text(loader)
    preview = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Thank-you pages (preview)</title><style>{css}</style><style>html,body{{margin:0;background:#0a0908;}}</style></head><body>
<div id="wtr-ty-mount"></div>
<script>var v=new URLSearchParams(location.search).get('v')||'blueprint';document.getElementById('wtr-ty-mount').setAttribute('data-v',v);</script>
<script>{loader.replace(f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);", "")}</script>
</body></html>"""
    (HERE / "thankyou-preview.html").write_text(preview)
    for f in ("thankyou-preview.html", "thankyou.js"):
        print(f"{f}: {(HERE / f).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
