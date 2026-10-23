"""Build the Wreck the Room VIP Retreat page (wrecktheroom.com/vip-retreat).

Outputs:
  vip-preview.html  standalone review page with a stand-in header
  vip.js            the page as a script; the Kajabi Code block loads it with:
                           <div id="wtr-vip-mount"></div>
                           <script src="https://mayadex853.github.io/Dashboards/wtr-homepage/vip.js"></script>

Kajabi's header button still links to #section-1759512379056; the apply block carries that id so it keeps working.

Usage: python3 build_vip.py
"""
import json
import re
from pathlib import Path

from build import KAJABI, LOGO, minify_css

HERE = Path(__file__).parent
SRC = HERE / "src"

def parts():
    css = minify_css((SRC / "wtr.css").read_text() + (SRC / "vip.css").read_text())
    body = re.sub(r"<!--.*?-->", "", (SRC / "vip.html").read_text(), flags=re.S).replace("{{K}}", KAJABI).strip()
    js = (SRC / "wtr.js").read_text()
    return css, body, js


def loader(css, body, js):
    return ("(function(){var m=document.getElementById('wtr-vip-mount');"
            "if(!m){m=document.createElement('div');m.id='wtr-vip-mount';var s=document.currentScript;s.parentNode.insertBefore(m,s);}"
            f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);"
            f"m.innerHTML={json.dumps(body)};\n{js}\n"
            "var r=document.getElementById('wtr-vip');"
            "if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){wtrInit(r);});else wtrInit(r);"
            "})();\n")


def preview(css, body, js):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VIP Retreat · Jody Friedman (preview)</title>
<style>{css}</style>
<style>html,body{{margin:0;background:#0a0908;}}
.pv-head{{position:absolute;top:0;left:0;right:0;z-index:60;display:flex;align-items:center;justify-content:space-between;padding:22px 32px;font:600 12px/1 Manrope,system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;}}
.pv-head img{{width:150px;display:block;}}.pv-head a{{color:#d9d2c4;text-decoration:none;}}.pv-head .bk{{border:1px solid #c9a84c;color:#ecd69b;padding:14px 20px;}}
@media(max-width:760px){{.pv-head{{padding:16px 20px;}}.pv-head img{{width:120px;}}.pv-head .bk{{padding:11px 12px;font-size:10px;}}}}</style></head><body>
<div class="pv-head"><img src="{LOGO}" alt="Jody Friedman"><a class="bk" href="#section-1759512379056">Apply for the Private Retreat</a></div>
{body}
<script>{js}
wtrInit(document.getElementById('wtr-vip'));</script></body></html>
"""


def main():
    css, body, js = parts()
    (HERE / "vip-preview.html").write_text(preview(css, body, js))
    (HERE / "vip.js").write_text(loader(css, body, js))
    for f in ("vip-preview.html", "vip.js"):
        print(f"{f}: {(HERE / f).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
