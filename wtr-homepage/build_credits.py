"""Build the Wreck the Room credits page (wrecktheroom.com/credits).

Credits come from the same Google Sheet that feeds hdmusicnow.com. The page reads the sheet live; this build also
saves a snapshot (data/credits.json) that renders instantly and is used if the sheet can't be reached.

Outputs:
  credits-preview.html  standalone page for review (with a stand-in header)
  credits.js            the page as a script; the Kajabi Code block loads it with:
                          <div id="wtr-credits-mount"></div>
                          <script src="https://mayadex853.github.io/Dashboards/wtr-homepage/credits.js"></script>

Usage: python3 build_credits.py            (refreshes the snapshot from the sheet, then builds)
       python3 build_credits.py --offline  (builds from the saved snapshot)
"""
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

from build import minify_css
from hdmn_clone import ethan_bloom

HERE = Path(__file__).parent
SRC = HERE / "src"
SNAPSHOT = HERE / "data" / "credits.json"
SHEET_ID = "1CBPFj3m63C8k471r3ONv7FZtacY-HdBJon5hwO40bjQ"  # "HD Music Now – Website Credits"
POSTERS = "https://mayadex853.github.io/Dashboards/hdmn-homepage/posters/"
LOGO = ("https://kajabi-storefronts-production.kajabi-cdn.com/kajabi-storefronts-production/file-uploads/themes/"
        "2162751237/settings_images/47ed02-ebc5-250f-cdd2-17c278b4e31_JODY_LOGO_smaller.png")  # the site header logo


def fetch_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&headers=1"
    with urllib.request.urlopen(url, timeout=30) as r:
        rows = list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
    keep = ("Section", "Title", "Detail", "Year", "Type", "Poster", "Carousel", "Order")
    return [{k: (row.get(k) or "").strip() for k in keep} for row in rows if (row.get("Section") or "").strip()]


def header_html(logo=LOGO):
    """Header used on the custom pages (the Kajabi header is hidden on them)."""
    return (
        "<style>.wtr-hd{position:absolute;top:0;left:0;right:0;z-index:60;display:flex;align-items:center;justify-content:space-between;"
        "padding:20px 32px;font:600 12px/1 Manrope,system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase}"
        ".wtr-hd img{width:150px;height:auto;display:block}"
        ".wtr-hd nav{display:flex;gap:30px;align-items:center}.wtr-hd a{color:#d9d2c4 !important;text-decoration:none !important}"
        ".wtr-hd .bk{border:1px solid #c9a84c;color:#ecd69b !important;padding:14px 20px}"
        "@media(max-width:760px){.wtr-hd{padding:14px 20px}.wtr-hd img{width:120px}.wtr-hd nav a:not(.bk){display:none}"
        ".wtr-hd .bk{padding:11px 12px;font-size:10px}}</style>"
        f'<div class="wtr-hd"><a href="https://www.wrecktheroom.com/"><img src="{logo}" alt="Jody Friedman"></a>'
        '<nav><a href="https://www.wrecktheroom.com/about">About</a><a href="https://www.wrecktheroom.com/speaker2">Speaking</a>'
        '<a href="https://www.wrecktheroom.com/credits">Credits</a><a href="https://www.wrecktheroom.com/coaching">Work With Me</a>'
        '<a class="bk" href="https://www.wrecktheroom.com/speaker2">Book Jody to speak</a></nav></div>'
    )


def parts(data):
    eb_import, eb_css, eb_html, eb_js = ethan_bloom()  # the Ethan Bloom section, cloned from hdmusicnow.com
    css = eb_import + minify_css((SRC / "wtr.css").read_text() + (SRC / "credits.css").read_text() + eb_css)
    body = (SRC / "credits.html").read_text().replace("{{POSTERS}}", POSTERS).replace("{{ETHAN}}", eb_html)
    js = (SRC / "credits.js").read_text() + "\n" + eb_js
    init = (f"wtrCredits(document.getElementById('wtr-credits'),{json.dumps(data, separators=(',', ':'))},"
            f"{json.dumps(POSTERS)},{json.dumps(SHEET_ID)});")
    return css, body, js, init


def loader(css, body, js, init):
    return ("(function(){var m=document.getElementById('wtr-credits-mount');"
            "if(!m){m=document.createElement('div');m.id='wtr-credits-mount';var s=document.currentScript;s.parentNode.insertBefore(m,s);}"
            f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);"
            f"m.innerHTML={json.dumps(body)};\n{js}\n{init}\n}})();\n")


def preview(css, body, js, init):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Credits · Jody Friedman (preview)</title>
<style>{css}</style>
<style>html,body{{margin:0;background:#0a0908;}}</style></head><body>
<div style="position:relative">{header_html()}
{body}</div>
<script>{js}
{init}</script></body></html>
"""


def main():
    if "--offline" not in sys.argv:
        try:
            data = fetch_sheet()
            SNAPSHOT.parent.mkdir(exist_ok=True)
            SNAPSHOT.write_text(json.dumps(data, indent=1, ensure_ascii=False))
            print(f"snapshot: {len(data)} rows from the sheet")
        except Exception as err:  # noqa: BLE001 - fall back to the saved snapshot
            print(f"sheet unreachable ({err}); using saved snapshot")
    data = json.loads(SNAPSHOT.read_text())
    css, body, js, init = parts(data)
    (HERE / "credits-preview.html").write_text(preview(css, body, js, init))
    (HERE / "credits.js").write_text(loader(css, body, js, init))
    for f in ("credits-preview.html", "credits.js"):
        print(f"{f}: {(HERE / f).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
