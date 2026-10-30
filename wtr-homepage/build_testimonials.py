"""Build the Wreck The Room™ testimonials page (wrecktheroom.com/testimonials).

Every testimonial lives in data/testimonials.json. To add a new one, append an entry and rebuild:
  {"name": "...", "role": "...", "group": "client" | "speaker",
   "quote": "...",                                  (optional when there is a video)
   "video": {"host": "vimeo" | "wistia", "id": "...", "shape": "tall" | "wide"},   (optional)
   "image": "https://..."}                          (video poster, optional for Vimeo)

Outputs:
  testimonials-preview.html  standalone page for review
  testimonials.js            the page as a script; the Kajabi Code block loads it with:
                               <div id="wtr-tm-mount"></div>
                               <script src="https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@<sha>/wtr-homepage/testimonials.js"></script>
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "testimonials.json"
QUIZ = "https://quiz.wrecktheroom.com"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Manrope:wght@400;500;600;700&display=swap');
.wtt{--bg:#0a0908;--bg3:#17140f;--ink:#f3ede2;--mute:#d2cbbe;--dim:#aaa395;--gold:#c9a84c;--gold2:#ecd69b;--em:#d72626;--accent:#c21f1f;
 --line:rgba(201,168,76,.22);--line2:rgba(243,237,226,.08);background:var(--bg);color:var(--mute);font:400 17px/1.7 Manrope,system-ui,sans-serif;
 -webkit-font-smoothing:antialiased;text-align:left;overflow:hidden}
.wtt *,.wtt *::before,.wtt *::after{box-sizing:border-box}
.wtt h1,.wtt h2{font-family:Anton,Impact,'Arial Narrow',sans-serif !important;font-weight:400 !important;text-transform:uppercase;letter-spacing:.01em;
 line-height:.94 !important;color:var(--ink) !important;margin:0}
.wtt h1 em,.wtt h2 em{font-style:normal;color:var(--em) !important}
.wtt p{margin:0 0 1.1em;color:var(--mute)}
.wtt .in{max-width:1240px;margin:0 auto;padding:0 32px}
.wtt .eb{display:inline-block;font-size:11px;font-weight:600;letter-spacing:.32em;text-transform:uppercase;color:var(--gold);margin-bottom:22px}
.wtt .hero{padding:190px 0 70px;border-bottom:1px solid var(--line2)}
.wtt .hero h1{font-size:clamp(54px,8vw,128px)}
.wtt .hero p{max-width:640px;font-size:19px;margin-top:28px}
.wtt .tabs{display:flex;gap:10px;flex-wrap:wrap;margin:48px 0 0}
.wtt .tabs button{font:600 11px/1 Manrope,sans-serif;letter-spacing:.24em;text-transform:uppercase;color:var(--mute);background:none;
 border:1px solid var(--line);padding:14px 18px;cursor:pointer}
.wtt .tabs button[aria-pressed=true]{background:var(--em);border-color:var(--em);color:#fff}
.wtt .sec{padding:80px 0}
.wtt .sec h2{font-size:clamp(34px,4vw,58px);margin-bottom:40px}
.wtt .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px;align-items:start}
.wtt .card{border:1px solid var(--line2);background:var(--bg3);display:flex;flex-direction:column}
.wtt .card[hidden]{display:none}
.wtt .vid{position:relative;display:block;width:100%;padding:0;border:0;border-bottom:1px solid var(--line2);background:#000;cursor:pointer;
 overflow:hidden;aspect-ratio:9/16;font:inherit;color:inherit}
.wtt .vid.wide{aspect-ratio:16/9}
.wtt .vid img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.85;transition:transform 1.2s cubic-bezier(.2,.7,.2,1),opacity .5s}
.wtt .vid:hover img{transform:scale(1.04);opacity:1}
.wtt .vid .pl{position:absolute;z-index:2;left:50%;top:50%;width:76px;height:76px;margin:-38px 0 0 -38px;border-radius:50%;
 border:1px solid rgba(236,214,155,.85);display:grid;place-items:center;background:rgba(10,9,8,.35);transition:transform .3s,background .3s}
.wtt .vid .pl::before{content:"";border-left:15px solid var(--gold2);border-top:9px solid transparent;border-bottom:9px solid transparent;margin-left:4px}
.wtt .vid:hover .pl{transform:scale(1.08);background:rgba(215,38,38,.35)}
.wtt .vid iframe{position:absolute;inset:0;width:100%;height:100%;border:0;z-index:3}
.wtt blockquote{margin:0;padding:30px 30px 20px;font-family:'Cormorant Garamond',Georgia,serif;font-size:23px;line-height:1.4;color:var(--ink);flex:1}
.wtt blockquote::before{content:"\\201C";display:block;font-family:Anton,Impact,sans-serif;font-size:54px;line-height:.8;color:var(--em);margin-bottom:6px}
.wtt cite{display:block;font-style:normal;padding:0 30px 28px;font-weight:600;color:var(--ink);font-size:15px}
.wtt .card .vid + cite{padding-top:22px}
.wtt cite span{display:block;font-size:11px;letter-spacing:.24em;text-transform:uppercase;color:var(--gold);font-weight:600;margin-top:4px}
.wtt .cta{padding:110px 0 130px;border-top:1px solid var(--line2);text-align:center}
.wtt .cta h2{font-size:clamp(40px,5vw,76px)}
.wtt .cta p{max-width:560px;margin:24px auto 36px}
.wtt .btn{display:inline-block;background:var(--em);color:#fff !important;text-decoration:none !important;font:600 12px/1 Manrope,sans-serif;
 letter-spacing:.24em;text-transform:uppercase;padding:20px 30px;transition:background .3s}
.wtt .btn:hover{background:var(--accent)}
.wtt .ft{border-top:1px solid var(--line2);padding:34px 0;font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--dim)}
.wtt .ft .in{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
.wtt .ft a{color:var(--dim) !important;text-decoration:none !important;margin-left:24px}
.wtt .ft a:first-child{margin-left:0}
@media(max-width:760px){.wtt .in{padding:0 20px}.wtt .hero{padding:140px 0 50px}.wtt .sec{padding:56px 0}
 .wtt .grid{grid-template-columns:1fr}.wtt blockquote{font-size:21px;padding:26px 24px 16px}.wtt cite{padding:0 24px 24px}
 .wtt .ft .in{flex-direction:column}.wtt .ft a{margin:0 18px 0 0}}
"""

JS = r"""
function wtrTestimonials(root){
  var tabs=root.querySelectorAll('.tabs button');
  tabs.forEach(function(b){b.addEventListener('click',function(){
    tabs.forEach(function(x){x.setAttribute('aria-pressed',x===b);});
    var g=b.dataset.g;
    root.querySelectorAll('.card').forEach(function(c){c.hidden=!(g==='all'||c.dataset.g===g);});
  });});
  root.querySelectorAll('.vid').forEach(function(v){v.addEventListener('click',function(){
    if(v.querySelector('iframe'))return;
    var f=document.createElement('iframe');
    f.allow='autoplay; fullscreen; picture-in-picture';f.allowFullscreen=true;f.title=v.getAttribute('aria-label');
    f.src=v.dataset.host==='wistia'?'https://fast.wistia.net/embed/iframe/'+v.dataset.id+'?autoPlay=true&playerColor=d72626'
      :'https://player.vimeo.com/video/'+v.dataset.id+'?autoplay=1&badge=0&autopause=0&app_id=58479';
    v.appendChild(f);
  });});
}
"""


def esc(s):
    return html.escape(s or "", quote=True)


def card(t):
    vid = ""
    v = t.get("video")
    if v:
        img = t.get("image") or ""
        shape = " wide" if v.get("shape") == "wide" else ""
        vid = (f'<button class="vid{shape}" data-host="{v["host"]}" data-id="{esc(v["id"])}" '
               f'aria-label="Play {esc(t["name"])}\'s testimonial">'
               + (f'<img src="{esc(img)}" alt="" loading="lazy">' if img else "")
               + '<span class="pl"></span></button>')
    quote = f'<blockquote>{esc(t["quote"])}</blockquote>' if t.get("quote") else ""
    role = f'<span>{esc(t["role"])}</span>' if t.get("role") else ""
    return f'<figure class="card" data-g="{t["group"]}" style="margin:0">{vid}{quote}<cite>{esc(t["name"])}{role}</cite></figure>'


def body(items):
    # Video stories first, then written quotes, so the strongest proof leads.
    items = sorted(items, key=lambda t: (0 if t.get("video") else 1))
    cards = "".join(card(t) for t in items)
    return f"""<div class="wtt" id="wtr-tm">
<section class="hero"><div class="in">
 <span class="eb">Testimonials</span>
 <h1>In their <em>words.</em></h1>
 <p>Founders, leaders and speakers on what changed once they saw the room they were living in, and rebuilt it.</p>
 <div class="tabs" role="group" aria-label="Filter testimonials">
  <button type="button" data-g="all" aria-pressed="true">All</button>
  <button type="button" data-g="client" aria-pressed="false">Coaching clients</button>
  <button type="button" data-g="speaker" aria-pressed="false">Speaking</button>
 </div>
</div></section>
<section class="sec"><div class="in"><div class="grid">{cards}</div></div></section>
<section class="cta"><div class="in">
 <span class="eb">Your turn</span>
 <h2>Which room is running <em>your life?</em></h2>
 <p>Take the free 3-minute quiz. You'll get your room and your exact next step right away.</p>
 <a class="btn" href="{QUIZ}">Take the quiz</a>
</div></section>
<footer class="ft"><div class="in"><span>© Wreck The Room™ · Jody Friedman</span>
 <span><a href="https://www.wrecktheroom.com/about">About</a><a href="https://www.wrecktheroom.com/speaker">Speaking</a><a href="https://www.wrecktheroom.com/coaching">Work With Me</a><a href="https://www.wrecktheroom.com/privacy-policy">Privacy</a></span>
</div></footer>
</div>"""


def minify(css):
    return " ".join(line.strip() for line in css.strip().splitlines())


def main():
    items = json.loads(DATA.read_text())
    css, page = minify(CSS), body(items)
    loader = ("(function(){var m=document.getElementById('wtr-tm-mount');"
              "if(!m){m=document.createElement('div');m.id='wtr-tm-mount';var s=document.currentScript;s.parentNode.insertBefore(m,s);}"
              f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);"
              f"m.innerHTML={json.dumps(page)};\n{JS}\nwtrTestimonials(document.getElementById('wtr-tm'));\n}})();\n")
    (HERE / "testimonials.js").write_text(loader)
    (HERE / "testimonials-preview.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Testimonials | Wreck The Room™</title><style>body{margin:0;background:#0a0908}</style></head><body>'
        '<div id="wtr-tm-mount"></div><script src="testimonials.js"></script></body></html>')
    print(f"{len(items)} testimonials -> testimonials.js ({len(loader)} bytes)")


if __name__ == "__main__":
    main()
