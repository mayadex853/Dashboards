"""Build the Wreck The Room™ self-guided programs page (wrecktheroom.com/self-guided-programs).

Outputs:
  selfguided-preview.html  standalone page for review
  selfguided.js            the page as a script; the Kajabi Code block loads it after the shared header:
                             <div id="wtr-sg-mount"></div>
                             <script src="https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@<sha>/wtr-homepage/selfguided.js"></script>
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
W = "https://www.wrecktheroom.com"
QUIZ = "https://quiz.wrecktheroom.com"
MEDIA = "https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@29498cc27c2ee8d517e81e35e46071434b208343/wtr-homepage/media/"
WAS = 997

PROGRAMS = [
    ("Drifting", 27, "drifting-program",
     "Life is happening to you, and you can't remember the last time you chose the direction on purpose.",
     "Wake up from autopilot and get back in the driver's seat."),
    ("Stalling", 47, "stalling-program",
     "You know exactly what needs to change, and you keep finding good reasons not to do it yet.",
     "See what the stall is protecting, and make the first real move."),
    ("Renovating", 67, "renovating-program",
     "New strategy, new hire, new city, and somehow the same problems keep showing up.",
     "Stop rearranging the furniture and work on the person living in the house."),
    ("Rebuilding", 97, "rebuilding-program",
     "You've done real work on yourself, and your growth has still flattened out.",
     "Go deeper into the identity layer and find a clear path through the plateau."),
]

VIDEOS = [
    ("mp4", MEDIA + "sharn-clark-testimonial.mp4", MEDIA + "sharn-clark-poster.jpg", "Shar'n Clark"),
    ("vimeo", "1212945373", "https://i.vimeocdn.com/video/2183502542-6dbdb5864e6b6d6e359c5610e8183b21375b41e76a0f4a63e0ed0be5c774e93d-d_640", "Amara P."),
    ("vimeo", "1183442453", "https://i.vimeocdn.com/video/2146308089-b43c720e144a206be4a8cafcec94672b0e0c9628a5dd43cce7b0c2b373d60259-d_640", "Christy B."),
    ("vimeo", "1183442331", "https://i.vimeocdn.com/video/2146307512-9e5b02f9328fd95dc5d80a9dc62f277ee32edd65b3f8e85d807281ddafd24df0-d_640", "Jeremy D."),
]

QUOTES = [
    ("I've done programs with Mel Robbins&hellip; and I feel that Wreck the Room is more beneficial. I got more out of it.", "Shar'n Clark", "Small business owner"),
    ("Re-examining my personal values has been a game changer. It's helped me say no more easily, say yes when it's right for me, and my life has really blossomed.", "Christy B.", "Realtor and business owner"),
    ("This helped me wreck beliefs that were in the way. It made so much sense and I could feel the shift.", "Ran S.", "Client"),
]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Manrope:wght@400;500;600;700&display=swap');
.wsg{--bg:#0a0908;--bg2:#110f0c;--bg3:#17140f;--ink:#f3ede2;--mute:#ddd6c9;--dim:#aaa395;--gold:#c9a84c;--gold2:#ecd69b;--em:#d72626;--accent:#c21f1f;
 --line:rgba(201,168,76,.24);--line2:rgba(243,237,226,.09);background:var(--bg);color:var(--mute);font:400 17px/1.7 Manrope,system-ui,sans-serif;-webkit-font-smoothing:antialiased;text-align:left;overflow:hidden}
.wsg *,.wsg *::before,.wsg *::after{box-sizing:border-box}
.wsg h1,.wsg h2,.wsg h3{font-family:Anton,Impact,'Arial Narrow',sans-serif !important;font-weight:400 !important;text-transform:uppercase;letter-spacing:.01em;line-height:.95 !important;color:var(--ink) !important;margin:0}
.wsg h1 em,.wsg h2 em{font-style:normal;color:var(--em) !important}
.wsg p{margin:0 0 1.1em;color:var(--mute)}
.wsg .in{max-width:1240px;margin:0 auto;padding:0 32px}
.wsg .eb{display:inline-block;font-size:11px;font-weight:600;letter-spacing:.32em;text-transform:uppercase;color:var(--gold);margin-bottom:22px}
.wsg .btn{display:inline-block;background:var(--em);color:#fff !important;text-decoration:none !important;font:600 12px/1 Manrope,sans-serif;letter-spacing:.22em;text-transform:uppercase;padding:20px 28px;transition:background .3s}
.wsg .btn:hover{background:var(--accent)}
.wsg .btn.ghost{background:none;border:1px solid var(--gold);color:var(--gold2) !important}
.wsg .btn.ghost:hover{background:rgba(201,168,76,.12)}
.wsg .hero{padding:190px 0 90px;border-bottom:1px solid var(--line2);background:radial-gradient(ellipse at 80% 0%,rgba(215,38,38,.14),transparent 55%)}
.wsg .hero h1{font-size:clamp(50px,7.4vw,118px)}
.wsg .hero .sub{max-width:660px;font-size:20px;margin:30px 0 36px;color:var(--ink)}
.wsg .hero .row{display:flex;gap:16px;flex-wrap:wrap;align-items:center}
.wsg .hero .note{font-size:14px;color:var(--dim)}
.wsg .sec{padding:96px 0}
.wsg .sec h2{font-size:clamp(36px,4.4vw,64px);margin-bottom:18px}
.wsg .lead{max-width:640px;font-size:18px;margin-bottom:48px}
.wsg .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.wsg .pc{position:relative;display:flex;flex-direction:column;border:1px solid var(--line2);background:var(--bg3);padding:34px 28px 30px;transition:border-color .3s,transform .3s}
.wsg .pc:hover{border-color:var(--gold);transform:translateY(-4px)}
.wsg .pc .n{font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--gold);font-weight:600;margin-bottom:12px}
.wsg .pc h3{font-size:44px;margin-bottom:16px}
.wsg .pc .pain{font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;line-height:1.35;color:var(--ink);margin-bottom:14px}
.wsg .pc .gain{font-size:15px;color:var(--mute);flex:1}
.wsg .pc .meta{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--dim);margin:20px 0 14px;font-weight:600}
.wsg .pc .was{display:block;font-family:Anton,Impact,sans-serif;font-size:50px;line-height:1;color:#8a8478;text-decoration:line-through;text-decoration-color:var(--em);text-decoration-thickness:4px}
.wsg .pc .now{display:block;font-family:Anton,Impact,sans-serif;font-size:56px;line-height:1;color:var(--ink);margin:6px 0 22px}
.wsg .pc .now small{font-size:.5em;vertical-align:top;margin-right:2px}
.wsg .pc .btn{text-align:center;padding:18px 16px}
.wsg .quizbar{margin-top:30px;border:1px dashed var(--line);padding:24px 28px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}
.wsg .quizbar p{margin:0;color:var(--ink);font-size:18px}
.wsg .how{background:var(--bg2);border-top:1px solid var(--line2);border-bottom:1px solid var(--line2)}
.wsg .steps{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:10px}
.wsg .step b{display:block;font-family:Anton,Impact,sans-serif;font-weight:400;font-size:58px;line-height:1;color:var(--em);margin-bottom:14px}
.wsg .step h3{font-size:26px;margin-bottom:12px}
.wsg .step p{font-size:16px}
.wsg .vids{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-bottom:26px}
.wsg .vid{position:relative;display:block;width:100%;aspect-ratio:9/16;padding:0;border:1px solid var(--line2);background:#000;cursor:pointer;overflow:hidden;font:inherit}
.wsg .vid img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.88;transition:transform 1s,opacity .4s}
.wsg .vid:hover img{transform:scale(1.04);opacity:1}
.wsg .vid .pl{position:absolute;z-index:2;left:50%;top:50%;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;background:var(--em);display:grid;place-items:center;box-shadow:0 6px 20px rgba(0,0,0,.45)}
.wsg .vid .pl::before{content:"";border-left:14px solid #fff;border-top:9px solid transparent;border-bottom:9px solid transparent;margin-left:4px}
.wsg .vid .nm{position:absolute;z-index:2;left:0;right:0;top:0;padding:16px 16px 34px;background:linear-gradient(180deg,rgba(0,0,0,.78),transparent);font:600 13px/1 Manrope,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#fff;text-align:left}
.wsg .vid iframe,.wsg .vid video{position:absolute;inset:0;width:100%;height:100%;border:0;z-index:3;background:#000}
.wsg .quotes{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.wsg .q{margin:0;border:1px solid var(--line2);background:var(--bg3);padding:28px 28px 24px;display:flex;flex-direction:column}
.wsg .q blockquote{margin:0 0 18px;font-family:'Cormorant Garamond',Georgia,serif;font-size:21px;line-height:1.4;color:var(--ink);flex:1}
.wsg .q blockquote::before{content:"\\201C";display:block;font-family:Anton,Impact,sans-serif;font-size:48px;line-height:.8;color:var(--em);margin-bottom:6px}
.wsg .q cite{font-style:normal;font-weight:600;color:var(--ink);font-size:15px}
.wsg .q cite span{display:block;font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);margin-top:4px}
.wsg .more{margin-top:26px;font-size:15px}.wsg .more a{color:var(--gold2) !important}
.wsg .deeper{display:grid;grid-template-columns:1.2fr 1fr;gap:48px;align-items:center;border:1px solid var(--line);padding:56px;background:linear-gradient(135deg,rgba(201,168,76,.08),transparent 60%)}
.wsg .deeper h2{font-size:clamp(32px,3.6vw,52px)}
.wsg .deeper p{font-size:17px}
.wsg .cta{padding:110px 0 130px;text-align:center;border-top:1px solid var(--line2)}
.wsg .cta h2{font-size:clamp(40px,5vw,76px)}
.wsg .cta p{max-width:560px;margin:24px auto 34px}
.wsg .ft{border-top:1px solid var(--line2);padding:32px 0;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--dim)}
.wsg .ft .in{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
.wsg .ft a{color:var(--dim) !important;text-decoration:none !important;margin-left:24px}.wsg .ft a:first-child{margin-left:0}
@media(max-width:1100px){.wsg .grid{grid-template-columns:repeat(2,1fr)}.wsg .deeper{grid-template-columns:1fr;padding:40px}}
@media(max-width:760px){.wsg .in{padding:0 20px}.wsg .hero{padding:130px 0 60px}.wsg .sec{padding:64px 0}
 .wsg .grid,.wsg .steps,.wsg .quotes{grid-template-columns:1fr}
 .wsg .vids{grid-template-columns:repeat(4,64%);overflow-x:auto;scroll-snap-type:x mandatory;margin-right:-20px;padding-right:20px}.wsg .vid{scroll-snap-align:start}
 .wsg .deeper{padding:30px 24px}.wsg .ft .in{flex-direction:column}.wsg .ft a{margin:0 18px 0 0}}
"""

JS = r"""
function wtrSG(root){
  root.addEventListener('click',function(e){
    var v=e.target.closest('.vid');if(!v||v.querySelector('iframe,video'))return;var m;
    if(v.dataset.mp4){m=document.createElement('video');m.src=v.dataset.mp4;m.controls=true;m.autoplay=true;m.playsInline=true;v.appendChild(m);m.play();return;}
    m=document.createElement('iframe');m.src='https://player.vimeo.com/video/'+v.dataset.vimeo+'?autoplay=1&badge=0&autopause=0&title=0&byline=0&portrait=0&color=d72626';
    m.allow='autoplay; fullscreen; picture-in-picture';m.setAttribute('allowfullscreen','');m.title=v.getAttribute('aria-label');v.appendChild(m);
  });
}
"""


def body():
    cards = "".join(
        f'<article class="pc"><div class="n">Room {i + 1}</div><h3>{name}</h3>'
        f'<p class="pain">{pain}</p><p class="gain">{gain}</p>'
        f'<div class="meta">5 lessons &middot; your pace</div>'
        f'<span class="was">${WAS}</span><span class="now"><small>$</small>{price}</span>'
        f'<a class="btn" href="{W}/{slug}">Start {name}</a></article>'
        for i, (name, price, slug, pain, gain) in enumerate(PROGRAMS))
    vids = "".join(
        f'<button type="button" class="vid" data-{h}="{i}" aria-label="Play {n}&#39;s story">'
        f'<img src="{p}" alt="" loading="lazy"><span class="pl"></span><span class="nm">{n}</span></button>'
        for h, i, p, n in VIDEOS)
    quotes = "".join(f'<figure class="q"><blockquote>{q}</blockquote><cite>{n}<span>{r}</span></cite></figure>' for q, n, r in QUOTES)
    return f"""<div class="wsg" id="wtr-sg">
<section class="hero"><div class="in">
 <span class="eb">Self-guided programs</span>
 <h1>Start in the room<br><em>you're in.</em></h1>
 <p class="sub">Four short programs, one for each room. Five lessons each, at your own pace: finish in one sitting, over five days or over five weeks.</p>
 <div class="row"><a class="btn" href="#rooms">See the programs</a><a class="btn ghost" href="{QUIZ}">Not sure? Take the free quiz</a></div>
</div></section>
<section class="sec" id="rooms" style="scroll-margin-top:90px"><div class="in">
 <span class="eb">Launch pricing</span>
 <h2>Pick your <em>room.</em></h2>
 <p class="lead">Each program is regularly ${WAS}. Right now each one is a fraction of that, so you can start the work today.</p>
 <div class="grid">{cards}</div>
 <div class="quizbar"><p>Not sure which room you're in? The 3-minute quiz tells you, and gives you your next step right away.</p><a class="btn ghost" href="{QUIZ}">Take the quiz</a></div>
</div></section>
<section class="sec how"><div class="in">
 <span class="eb">How it works</span>
 <h2>Small lessons. <em>Real work.</em></h2>
 <div class="steps">
  <div class="step"><b>01</b><h3>Watch the lesson</h3><p>Each lesson is short and focused on one idea about the room you're in.</p></div>
  <div class="step"><b>02</b><h3>Do the exercise</h3><p>The exercise is where the change happens. Finish it before you move on to the next lesson.</p></div>
  <div class="step"><b>03</b><h3>Go at your pace</h3><p>One afternoon, one lesson a day or one a week. Every pace works, as long as you do the exercises.</p></div>
 </div>
</div></section>
<section class="sec"><div class="in">
 <span class="eb">In their words</span>
 <h2>People who <em>did the work.</em></h2>
 <p class="lead">Founders and business owners on what changed once they saw the room they were living in.</p>
 <div class="vids">{vids}</div>
 <div class="quotes">{quotes}</div>
 <p class="more"><a href="{W}/testimonials">Read every testimonial &rarr;</a></p>
</div></section>
<section class="sec" style="padding-top:0"><div class="in"><div class="deeper">
 <div><span class="eb">Ready to go further?</span><h2>The full <em>Wreck The Room&trade;</em> program</h2></div>
 <div><p>The self-guided programs work on one room. The full program takes you through all three phases with the Architects community, and you can add group or 1:1 coaching with Jody.</p>
 <a class="btn ghost" href="{W}/rebuild">See Blueprint, Council and Inner Circle</a></div>
</div></div></section>
<section class="cta"><div class="in">
 <span class="eb">Start today</span>
 <h2>Which room is running <em>your life?</em></h2>
 <p>Take the free 3-minute quiz. You'll get your room and your exact next step right away.</p>
 <a class="btn" href="{QUIZ}">Take the quiz</a>
</div></section>
<footer class="ft"><div class="in"><span>&copy; Wreck The Room&trade; &middot; Jody Friedman</span>
 <span><a href="{W}/about">About</a><a href="{W}/testimonials">Testimonials</a><a href="{W}/coaching">Work With Me</a><a href="{W}/privacy-policy">Privacy</a></span>
</div></footer>
</div>"""


def main():
    css = " ".join(l.strip() for l in CSS.strip().splitlines())
    page = body()
    js = ("(function(){var m=document.getElementById('wtr-sg-mount');"
          "if(!m){m=document.createElement('div');m.id='wtr-sg-mount';var s=document.currentScript;s.parentNode.insertBefore(m,s);}"
          f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);"
          f"m.innerHTML={json.dumps(page)};\n{JS}\nwtrSG(document.getElementById('wtr-sg'));\n}})();\n")
    (HERE / "selfguided.js").write_text(js)
    (HERE / "selfguided-preview.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Self-Guided Programs | Wreck The Room™</title><style>body{margin:0;background:#0a0908}</style></head><body>'
        '<div style="position:relative"><script src="live/header.js" data-btn="Take the quiz" data-href="https://quiz.wrecktheroom.com"></script>'
        '<div id="wtr-sg-mount"></div></div><script src="selfguided.js"></script></body></html>')
    print(len(js))


if __name__ == "__main__":
    main()
