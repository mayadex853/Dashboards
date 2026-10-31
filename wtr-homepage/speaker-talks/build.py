"""Rebuild the /speaker2 keynote carousel cards (Kajabi theme 2162751237, block 1778109604561_0).

live-block.html is the block as it was live on 2026-10-31. This swaps in the five talks and filters below,
writes new-block.html, and writes talks.js, a loader the Code block includes with one <script src>.
"""
import html
import json
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).parent
ARROW_DOWN = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6l5 5 5-5"/></svg>'
ARROW_RIGHT = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 8h12M9 3l5 5-5 5"/></svg>'

FILTERS = [("all", "All Talks"), ("signature", "Signature"), ("ai", "AI &amp; Future"),
           ("founders", "Founders"), ("story", "Storytelling"), ("corporate", "Corporate")]

TALKS = [
    dict(f="signature", tag="Signature Keynote", title="Wreck The Room&trade;", sub="Built to Survive, Not to Lead",
         ideal="Founders, leadership teams, entrepreneur conferences, mixed corporate audiences",
         talk=["Every high performer eventually hits a wall they can't explain. The strategy is right, the team is in place, and the work ethic was never the problem.",
               "This talk is about the identity running things underneath all of it: the one built to survive something, which was never designed to lead at this level. Jody shows how that identity gets built early and why hitting the number doesn't fix it. Then he shows what changes when people stop optimizing the work and start rebuilding the person doing it."],
         take=["Name the &ldquo;room&rdquo; they've been operating from, and see what it's been costing them",
               "Understand why most change efforts wear off, and what makes change hold",
               "Use the three Wreck The Room&trade; steps (Wreck-ognize It, Wreck It, Wrock It) on one real pattern before they leave",
               "Walk out knowing exactly what to wreck first"],
         mail="Wreck The Room (Signature)"),
    dict(f="ai", tag="AI &amp; Future of Work", title="Night of the Living Expert", sub="AI Isn't Killing Jobs. It's Killing Excuses.",
         ideal="Innovation conferences, HR and people teams, organizations rolling out AI",
         talk=["Most resistance to AI isn't technical or generational. It's identity protection. People built their authority on being the one with the answers, and learning AI means becoming a beginner again, in public, at the exact career stage where they're supposed to have arrived.",
               "So they defend the room where they're still the expert and call it skepticism. Jody shows why the smartest people in a room are often the slowest to adopt the next tool, and what that habit costs while the ground keeps moving."],
         take=["Recognize the difference between healthy skepticism and identity protection",
               "Understand why expertise can slow adoption, and how to stop it from happening",
               "Leave ready to learn in public again, without feeling smaller for it",
               "See adaptability as the asset worth protecting"],
         mail="Night of the Living Expert"),
    dict(f="founders", tag="Founders &amp; Entrepreneurs", title="Nobody's Coming", sub="The Room Called &ldquo;I Don't Need Anyone&rdquo;",
         ideal="Founder and entrepreneur events, women's leadership conferences, small business audiences",
         talk=["At nineteen, Jody sat across from a hospital board member with an $80,000 bill and no one else in the room to speak for him. That was the day he learned nobody was coming, so he built a life around never needing anyone. It looked like strength for years, right up until it kept people out who genuinely wanted to help.",
               "This talk is about the identity built in rooms where nobody comes. It looks at what that room costs in every relationship and business decision, and at what it takes to let people in without feeling you've failed."],
         take=["Tell the difference between self-reliance and isolation in their own life and business",
               "Spot where &ldquo;I'll just do it myself&rdquo; is capping their growth",
               "Learn a practical way to ask for and accept support without losing what makes them strong"],
         mail="Nobody's Coming"),
    dict(f="story", tag="Storytelling Keynote", title="When the Red Light Turns Off",
         sub="What 20 Years Inside Hollywood Taught Me About Reinvention, Performance and Identity",
         ideal="Opening and closing keynotes, creative industries, any audience that needs a story first",
         talk=["Jody's first job at CNN was feeding scripts to anchors, and he watched them flip the switch the second the red light came on. He spent two decades learning that switch himself, working with Netflix, HBO, Disney and Marvel and hearing his own songs fill theaters.",
               "Then his father died suddenly, and grief turned the performance off. This keynote follows what twenty years of performing and winning really taught him: identity is what remains when the red light turns off."],
         take=["See where they've been performing instead of being present",
               "Understand why each milestone stops satisfying soon after it arrives",
               "Leave with a clearer picture of who they are when nobody's watching"],
         mail="When the Red Light Turns Off"),
    dict(f="corporate", tag="Corporate Track", title="Break the Hidden Ceiling", sub="The Identity Framework Holding Your Organization Back",
         ideal="Leadership development programs, C-suite offsites, organizations going through change",
         talk=["Organizations invest heavily in leadership training and culture initiatives, and most fall short of the change they promise. The missing piece is almost always identity.",
               "Most leaders are operating from rooms built long before they stepped into their current role, rooms shaped by survival and approval. Those rooms once worked, and now they're the ceiling. Jody shows how real organizational change starts with the identity leaders operate from every day, and gives teams a pathway they can act on the next morning."],
         take=["Understand why most development initiatives don't stick, and what does",
               "Identify the unspoken patterns quietly limiting performance across the team",
               "Apply the Wreck The Room&trade; framework to create next-day behavior change",
               "Build a culture of ownership without losing structure or execution"],
         mail="Break the Hidden Ceiling"),
]


def card(t, first):
    lis = "\n".join(f"<li>{x}</li>" for x in t["take"])
    subj = quote("Speaking Inquiry: " + html.unescape(t["mail"]).replace("™", ""))
    return f"""<div class="wtr-c{' on' if first else ''}" data-t="{t['f']} all">
<div class="wtr-ca"></div>
<div class="wtr-ci">
<div class="wtr-ct">{t['tag']}</div>
<div class="wtr-cn">{t['title']}</div>
<div class="wtr-cs">{t['sub']}</div>
<div class="wtr-readmore">Read more {ARROW_DOWN}</div>
<div class="wtr-expanded">
<div class="wtr-div"></div>
<div class="wtr-sl">Ideal For</div>
<div class="wtr-au">{t['ideal']}</div>
<div class="wtr-sl">The Talk</div>
<div class="wtr-de">{'<br><br>'.join(t['talk'])}</div>
<div class="wtr-sl">Audience Takeaways</div>
<ul class="wtr-ul">
{lis}
</ul>
<div class="wtr-note">The title, examples and audience framing of this keynote are tailored for each engagement.</div>
<a class="wtr-lnk" href="mailto:jody@jodyfriedman.com?subject={subj}">Inquire About This Talk {ARROW_RIGHT}</a>
</div>
</div>
</div>"""


def main():
    s = (HERE / "live-block.html").read_text(encoding="utf-8")
    a = s.index('<div class="wtr-filters" id="wtrF">'); b = s.index("</div>", a) + len("</div>")
    filters = '<div class="wtr-filters" id="wtrF">\n' + "\n".join(
        f'<button class="wtr-fb{" on" if k == "all" else ""}" data-f="{k}">{v}</button>' for k, v in FILTERS) + "\n</div>"
    s = s[:a] + filters + s[b:]
    start = s.index('<div class="wtr-t" id="wtrT">') + len('<div class="wtr-t" id="wtrT">')
    end = s.index('<div class="wtr-c', start)
    last = s.rindex('<div class="wtr-c', start)
    # the cards end where the track closes: three closing divs after the last card's link
    import re
    m = re.compile(r'</a>\s*</div>\s*</div>\s*</div>').search(s, last)
    tail = m.end()
    s = s[:end] + "\n".join(card(t, i == 0) for i, t in enumerate(TALKS)) + s[tail:]
    s = s.replace("Swipe to explore, then let's find your fit.", "Swipe to explore, then let's find your fit.")
    (HERE / "new-block.html").write_text(s, encoding="utf-8")
    js = ("(function(){var h=" + json.dumps(s) + ";var s=document.currentScript;"
          "if(document.readyState==='loading'){document.write(h);}"
          "else if(s){var r=document.createRange();r.selectNode(s);s.parentNode.insertBefore(r.createContextualFragment(h),s.nextSibling);}})();\n")
    (HERE / "talks.js").write_text(js, encoding="utf-8")
    print(len(s), len(js))


if __name__ == "__main__":
    main()
