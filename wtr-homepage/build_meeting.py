"""Build the Wreck The Room™ "meeting confirmed" page (wrecktheroom.com/meeting-confirmed), shown after a strategy call is booked.

Outputs:
  meeting-preview.html  standalone review page with a stand-in header
  meeting.js            the page as a script; the Kajabi Code block loads it with:
                           <div id="wtr-mc-mount"></div>
                           <script src="https://mayadex853.github.io/Dashboards/wtr-homepage/meeting.js"></script>

The four-area self-rating is interactive: tapping Red / Yellow / Green fills a snapshot to bring to the call,
remembered in the visitor's browser if storage is available.

Usage: python3 build_meeting.py
"""
import json
import re
from pathlib import Path

from build import KAJABI, LOGO, minify_css

HERE = Path(__file__).parent
SRC = HERE / "src"

RATE_JS = """
/* keep visitors at the top on arrival: the autoplaying video frame can grab focus and pull the page down */
(function(){if(location.hash)return;var t0=Date.now(),user=false;
['wheel','touchstart','keydown','mousedown'].forEach(function(e){window.addEventListener(e,function(){user=true;},{passive:true,once:true});});
function back(){if(!user&&Date.now()-t0<6000&&window.pageYOffset>0)window.scrollTo(0,0);}
window.addEventListener('scroll',back,{passive:true});window.addEventListener('load',function(){setTimeout(back,50);});})();
(function(){var K='wtr-mc-rate',S={};try{S=JSON.parse(localStorage.getItem(K)||'{}')||{};}catch(e){}
function paint(){[].forEach.call(document.querySelectorAll('.mc-area'),function(a){var n=a.getAttribute('data-area'),v=S[n]||'';
  if(v)a.setAttribute('data-v',v);else a.removeAttribute('data-v');
  [].forEach.call(a.querySelectorAll('.mc-pick button'),function(b){var on=b.getAttribute('data-v')===v;b.classList.toggle('on',on);b.setAttribute('aria-pressed',on);});
  var d=document.querySelector('.mc-dots li[data-s="'+n+'"]');if(d)d.className=v;});}
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.mc-pick button');if(!b)return;
  var n=b.closest('.mc-area').getAttribute('data-area'),v=b.getAttribute('data-v');S[n]=S[n]===v?'':v;
  try{localStorage.setItem(K,JSON.stringify(S));}catch(e){}paint();});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',paint);else paint();})();
"""


def parts():
    css = minify_css((SRC / "wtr.css").read_text() + (SRC / "meeting.css").read_text())
    body = re.sub(r"<!--.*?-->", "", (SRC / "meeting.html").read_text(), flags=re.S).replace("{{K}}", KAJABI).strip()
    js = (SRC / "wtr.js").read_text() + RATE_JS
    return css, body, js


def loader(css, body, js):
    return ("(function(){var m=document.getElementById('wtr-mc-mount');"
            "if(!m){m=document.createElement('div');m.id='wtr-mc-mount';var s=document.currentScript;s.parentNode.insertBefore(m,s);}"
            f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);"
            f"m.innerHTML={json.dumps(body)};\n{js}\n"
            "var r=document.getElementById('wtr-mc');"
            "if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){wtrInit(r);});else wtrInit(r);"
            "})();\n")


def preview(css, body, js):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Call Confirmed · Jody Friedman (preview)</title>
<style>{css}</style>
<style>html,body{{margin:0;background:#0a0908;}}
.pv-head{{position:absolute;top:0;left:0;right:0;z-index:60;display:flex;align-items:center;justify-content:space-between;padding:22px 32px;font:600 12px/1 Manrope,system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;}}
.pv-head img{{width:150px;display:block;}}.pv-head a{{color:#d9d2c4;text-decoration:none;}}.pv-head .bk{{border:1px solid #c9a84c;color:#ecd69b;padding:14px 20px;}}
@media(max-width:760px){{.pv-head{{padding:16px 20px;}}.pv-head img{{width:120px;}}.pv-head .bk{{padding:11px 12px;font-size:10px;}}}}</style></head><body>
{body}
<script>{js}
wtrInit(document.getElementById('wtr-mc'));</script></body></html>
"""


def main():
    css, body, js = parts()
    (HERE / "meeting-preview.html").write_text(preview(css, body, js))
    (HERE / "meeting.js").write_text(loader(css, body, js))
    for f in ("meeting-preview.html", "meeting.js"):
        print(f"{f}: {(HERE / f).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
