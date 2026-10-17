"""Build the Wreck the Room About page (wrecktheroom.com/about).

The copy and photos are the ones the About page already had; this only rebrands them.

Outputs:
  about-preview.html  standalone review page with a stand-in header
  about.js            the page as a script; the Kajabi Code block loads it with:
                        <div id="wtr-about-mount"></div>
                        <script src="https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@<commit>/wtr-homepage/about.js"></script>

"Invite me to speak" / "Book Jody to speak" open Kajabi's booking pop-up on this page, as before.

Usage: python3 build_about.py
"""
import json
import re
from pathlib import Path

from build import KAJABI, LOGO, minify_css
from build_coaching import BOOK_JS

HERE = Path(__file__).parent
SRC = HERE / "src"

# Fade each paragraph of a chapter in as it reaches the viewport, and the chapter photo with it.
ABOUT_JS = """
(function(){var r=document.getElementById('wtr-about');if(!r)return;
  var els=r.querySelectorAll('.a-ch-body>*,.a-ch-img');
  if(!('IntersectionObserver' in window)||(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)){[].forEach.call(els,function(e){e.classList.add('in');});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{rootMargin:'0px 0px -10% 0px',threshold:.1});
  [].forEach.call(els,function(e){io.observe(e);});
})();
"""


def parts():
    css = minify_css((SRC / "wtr.css").read_text() + (SRC / "about.css").read_text())
    body = re.sub(r"<!--.*?-->", "", (SRC / "about.html").read_text(), flags=re.S).replace("{{K}}", KAJABI).strip()
    js = (SRC / "wtr.js").read_text() + BOOK_JS + ABOUT_JS
    return css, body, js


def loader(css, body, js):
    return ("(function(){var m=document.getElementById('wtr-about-mount');"
            "if(!m){m=document.createElement('div');m.id='wtr-about-mount';var s=document.currentScript;s.parentNode.insertBefore(m,s);}"
            f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);"
            f"m.innerHTML={json.dumps(body)};\n"
            "var r=document.getElementById('wtr-about');"
            f"function go(){{\n{js}\nwtrInit(r);}}"
            "if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',go);else go();"
            "})();\n")


def preview(css, body, js):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>About · Jody Friedman (preview)</title>
<style>{css}</style>
<style>html,body{{margin:0;background:#0a0908;}}
.pv-head{{position:absolute;top:0;left:0;right:0;z-index:60;display:flex;align-items:center;justify-content:space-between;padding:22px 32px;font:600 12px/1 Manrope,system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;}}
.pv-head img{{width:150px;display:block;}}.pv-head a{{color:#d9d2c4;text-decoration:none;}}.pv-head .bk{{border:1px solid #c9a84c;color:#ecd69b;padding:14px 20px;}}
@media(max-width:760px){{.pv-head{{padding:16px 20px;}}.pv-head img{{width:120px;}}.pv-head .bk{{padding:11px 12px;font-size:10px;}}}}</style></head><body>
<div class="pv-head"><img src="{LOGO}" alt="Jody Friedman"><a class="bk" href="#two-step">Book Jody to speak</a></div>
{body}
<script>{js}
wtrInit(document.getElementById('wtr-about'));</script></body></html>
"""


def main():
    css, body, js = parts()
    (HERE / "about-preview.html").write_text(preview(css, body, js))
    (HERE / "about.js").write_text(loader(css, body, js))
    for f in ("about-preview.html", "about.js"):
        print(f"{f}: {(HERE / f).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
