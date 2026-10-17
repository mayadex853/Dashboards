"""Build the Wreck the Room speaker page (wrecktheroom.com/speaker2).

The page keeps Kajabi's own Keynote Topics section untouched and wraps it with two Custom Code sections:
  top     hero, speaker reel, About Jody, the identity-problem statement
  bottom  what you get, speaking & consulting options, testimonials, booking form

Outputs:
  speaker-preview.html  standalone review page (stand-in header, a copy of the live Keynote Topics section,
                        and a copy of the booking form)
  speaker.js            one script for both Code sections; each section holds a mount:
                          <div id="wtr-sp-top-mount"></div>      (section before Keynote Topics)
                          <div id="wtr-sp-bottom-mount"></div>   (section after Keynote Topics, plus the <script>)

Usage: python3 build_speaker.py
"""
import json
import re
from pathlib import Path

from build import KAJABI, LOGO, PREVIEW_FORM, minify_css

HERE = Path(__file__).parent
SRC = HERE / "src"
KEYNOTE_SNAPSHOT = HERE / "data" / "speaker-keynote-topics.html"  # copy of the live section, for the preview only

REEL_JS = """
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-reel]');if(!b)return;
  var r=document.querySelector('.s-reel');if(!r)return;e.preventDefault();
  var hd=document.querySelector('#section-header header'),hh=hd?hd.getBoundingClientRect().height:0;
  window.scrollTo({top:r.getBoundingClientRect().top+window.pageYOffset-Math.max(40,hh+20),behavior:'smooth'});
  setTimeout(function(){if(!r.querySelector('iframe'))r.click();},700);});
"""


def parts():
    css = minify_css((SRC / "wtr.css").read_text() + (SRC / "speaker.css").read_text())
    html = re.sub(r"<!--(?!FORM|SPLIT).*?-->", "", (SRC / "speaker.html").read_text(), flags=re.S).replace("{{K}}", KAJABI)
    top, bottom = html.split("<!--SPLIT-->")
    js = (SRC / "wtr.js").read_text() + REEL_JS
    return css, top.strip(), bottom.strip(), js


def loader(css, top, bottom, js):
    return ("(function(){"
            f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);"
            f"var T={json.dumps(top)},B={json.dumps(bottom)};"
            "var mt=document.getElementById('wtr-sp-top-mount'),mb=document.getElementById('wtr-sp-bottom-mount');"
            "if(mt)mt.innerHTML=T;if(mb)mb.innerHTML=B;\n"
            f"{js}\n"
            "function go(){[].forEach.call(document.querySelectorAll('#wtr-sp-top,#wtr-sp-bottom'),function(r){wtrInit(r);});}"
            "if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',go);else go();"
            "})();\n")


def preview(css, top, bottom, js):
    keynote = KEYNOTE_SNAPSHOT.read_text() if KEYNOTE_SNAPSHOT.exists() else "<div style='padding:120px;text-align:center;color:#999'>[Keynote Topics section]</div>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Speaking · Jody Friedman (preview)</title>
<style>{css}</style>
<style>html,body{{margin:0;background:#0a0908;}}
.pv-head{{position:absolute;top:0;left:0;right:0;z-index:60;display:flex;align-items:center;justify-content:space-between;padding:22px 32px;font:600 12px/1 Manrope,system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;}}
.pv-head img{{width:150px;display:block;}}.pv-head nav{{display:flex;gap:30px;align-items:center;}}.pv-head a{{color:#d9d2c4;text-decoration:none;}}
.pv-head .bk{{border:1px solid #c9a84c;color:#ecd69b;padding:14px 20px;}}
@media(max-width:760px){{.pv-head nav a:not(.bk){{display:none;}}.pv-head{{padding:16px 20px;}}.pv-head img{{width:120px;}}.pv-head .bk{{padding:11px 12px;font-size:10px;}}}}
.modal{{display:none;}}</style></head><body>
<div class="pv-head"><img src="{LOGO}" alt="Jody Friedman"><nav><a href="#about">About Jody</a><a href="#section-1778109604561">Topics</a><a href="#testimonials">Testimonials</a>
<a class="bk" href="#two-step" data-target="#two-step" data-toggle="modal">Book Jody to speak</a></nav></div>
{top}
{keynote}
{bottom}
<div class="modal two-step" id="two-step"><div class="modal__content">{PREVIEW_FORM}</div></div>
<script>{js}
wtrInit(document.getElementById('wtr-sp-top'));wtrInit(document.getElementById('wtr-sp-bottom'));
document.addEventListener('submit',function(e){{if(e.target.matches('[data-preview]')){{e.preventDefault();alert('Preview only: on the live page this submits to Kajabi exactly as today.');}}}});
</script></body></html>
"""


def main():
    css, top, bottom, js = parts()
    (HERE / "speaker-preview.html").write_text(preview(css, top, bottom, js))
    (HERE / "speaker.js").write_text(loader(css, top, bottom, js))
    for f in ("speaker-preview.html", "speaker.js"):
        print(f"{f}: {(HERE / f).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
