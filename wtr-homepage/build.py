"""Build the Wreck the Room homepage embed.

Sources live in src/ (wtr.css, wtr.html, wtr.js). Outputs:
  preview.html       standalone page for review, including a stand-in Kajabi header and booking pop-up
                     (bottom-left switch flips between design directions; opens on B, add #a for A)
  kajabi-embed.html  the whole embed, can be pasted into a single Kajabi Code block
  wtr.js             the same embed as a script; the Kajabi Code block loads it with:
                       <div id="wtr-mount" data-dir="brick"></div>
                       <script src="https://mayadex853.github.io/Dashboards/wtr-homepage/wtr.js"></script>
                     data-dir="brick" is direction B (Demolition, the chosen default); data-dir="noir" is direction A (Gold Noir).

Usage: python3 build.py
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "src"
KAJABI = "https://kajabi-storefronts-production.kajabi-cdn.com/kajabi-storefronts-production/file-uploads/"
LOGO = KAJABI + "themes/2162751237/settings_images/47ed02-ebc5-250f-cdd2-17c278b4e31_JODY_LOGO_smaller.png"

# Copy of the live Kajabi booking form (same action and field names). Preview only: the live page uses
# Kajabi's own form, which carries the security token this copy can't have.
PREVIEW_FORM = """<form action="https://www.wrecktheroom.com/forms/2149142005/form_submissions" method="post" data-preview>
<div>
<div class="text-field form-group"><input type="text" name="form_submission[custom_4]" id="form_submission_custom_4" required class="form-control" placeholder="First Name"></div>
<div class="text-field form-group"><input type="text" name="form_submission[custom_5]" id="form_submission_custom_5" required class="form-control" placeholder="Last Name"></div>
<div class="email-field form-group"><input required class="form-control" placeholder="Email" type="email" name="form_submission[email]" id="form_submission_email"></div>
<div class="phone-field form-group"><input class="form-control" placeholder="Phone Number" type="tel" name="form_submission[phone_number]" id="form_submission_phone_number"></div>
<div class="text-field form-group"><input type="text" name="form_submission[custom_3]" id="form_submission_custom_3" required class="form-control" placeholder="Company Name"></div>
<div class="select-box-field form-group"><select name="form_submission[custom_2]" id="form_submission_custom_2" required class="form-control"><option value="">I'm Interested In</option><option>Speaking</option><option>Consulting</option><option>Virtual Event</option></select></div>
<div class="text-field form-group"><input type="text" name="form_submission[custom_6]" id="form_submission_custom_6" required class="form-control" placeholder="Event Date (or &quot;Approximate&quot;)"></div>
<div class="text-field form-group"><input type="text" name="form_submission[custom_7]" id="form_submission_custom_7" class="form-control" placeholder="Event Location (or &quot;Virtual&quot;)"></div>
<div class="select-box-field form-group"><select name="form_submission[custom_8]" id="form_submission_custom_8" class="form-control"><option value="">Audience Size</option><option>Under 100</option><option>100-500</option><option>500-5,000</option><option>5,000+</option></select></div>
<div class="select-box-field form-group"><select name="form_submission[custom_9]" id="form_submission_custom_9" required class="form-control"><option value="">Budget Range</option><option>$5,000-$10,000</option><option>$10,000-$15,000</option><option>$15,000-$25,000</option><option>$25,000+</option><option>Not sure yet</option></select></div>
<div class="text-field form-group"><input type="text" name="form_submission[custom_10]" id="form_submission_custom_10" class="form-control" placeholder="What outcome do you want Jody to create at your event?"></div>
<div class="text-area-field form-group"><textarea name="form_submission[custom_1]" id="form_submission_custom_1" class="form-control" placeholder="Anything else you wish to share?"></textarea></div>
<div><button id="form-button" class="form-btn" type="submit">SUBMIT</button></div>
</div></form>"""


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    return re.sub(r"\s*([{};,>])\s*", r"\1", css).replace(";}", "}").strip()


def parts():
    css = minify_css((SRC / "wtr.css").read_text())
    body = (SRC / "wtr.html").read_text().replace("{{K}}", KAJABI)
    body = re.sub(r"<!--(?!FORM).*?-->", "", body, flags=re.S)
    js = (SRC / "wtr.js").read_text()
    return css, body, js


def embed(css, body, js):
    return (f"<style>{css}</style>\n{body}\n<script>{js}\n"
            "(function(){var r=document.getElementById('wtr');"
            "var m=document.getElementById('wtr-mount');if(m&&m.dataset.dir)r.setAttribute('data-dir',m.dataset.dir);"
            "wtrInit(r);})();</script>\n")


def loader(css, body, js):
    return ("(function(){var m=document.getElementById('wtr-mount');"
            "if(!m){m=document.createElement('div');m.id='wtr-mount';"
            "var s=document.currentScript;s.parentNode.insertBefore(m,s);}"
            f"var st=document.createElement('style');st.textContent={json.dumps(css)};document.head.appendChild(st);"
            f"m.innerHTML={json.dumps(body)};var r=document.getElementById('wtr');"
            "if(m.dataset.dir)r.setAttribute('data-dir',m.dataset.dir);"
            f"{js}\n"
            "if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){wtrInit(r);});else wtrInit(r);"
            "})();\n")


def preview(css, body, js):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wreck the Room · Home (preview)</title>
<style>
html,body{{margin:0;background:#0a0908;}}
.pv-head{{position:absolute;top:0;left:0;right:0;z-index:60;display:flex;align-items:center;justify-content:space-between;padding:22px 32px;font:600 12px/1 Manrope,system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;}}
.pv-head img{{height:40px;mix-blend-mode:screen;}}
.pv-head nav{{display:flex;gap:30px;align-items:center;}}
.pv-head a{{color:#d9d2c4;text-decoration:none;}}
.pv-head .bk{{border:1px solid #c9a84c;color:#ecd69b;padding:14px 20px;}}
@media(max-width:760px){{.pv-head nav a:not(.bk){{display:none;}}.pv-head{{padding:16px 20px;}}.pv-head .bk{{padding:11px 12px;font-size:10px;}}}}
.modal{{display:none;}}
.pv-dir{{position:fixed;left:16px;bottom:16px;z-index:999;display:flex;gap:0;font:700 11px/1 Manrope,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;border:1px solid #c9a84c;background:rgba(10,9,8,.92);backdrop-filter:blur(6px);}}
.pv-dir button{{all:unset;cursor:pointer;padding:12px 14px;color:#d2cbbe;}}
.pv-dir button[aria-pressed=true]{{background:#c9a84c;color:#0a0908;}}
.pv-dir span{{padding:12px 12px;color:#aaa395;}}
</style></head><body>
<div class="pv-head"><img src="{LOGO}" alt="Jody Friedman">
<nav><a href="https://www.wrecktheroom.com/about">About</a><a href="https://www.wrecktheroom.com/speaker2">Speaking</a><a href="https://www.wrecktheroom.com/coaching">Work With Me</a><a href="https://www.wrecktheroom.com/blog">Blog</a>
<a class="bk" href="#two-step" data-target="#two-step" data-toggle="modal">Book Jody to speak</a></nav></div>
<style>{css}</style>
{body}
<div class="modal two-step" id="two-step"><div class="modal__content">{PREVIEW_FORM}</div></div>
<div class="pv-dir" role="group" aria-label="Design direction"><span>Direction</span>
<button data-d="noir" aria-pressed="false">A · Gold Noir</button><button data-d="brick" aria-pressed="true">B · Demolition</button></div>
<script>{js}
wtrInit(document.getElementById('wtr'));
document.querySelector('.pv-dir').addEventListener('click',function(e){{var b=e.target.closest('button');if(!b)return;
document.getElementById('wtr').setAttribute('data-dir',b.dataset.d);
[].forEach.call(this.querySelectorAll('button'),function(x){{x.setAttribute('aria-pressed',x===b);}});}});
if(location.hash==='#a')document.querySelector('[data-d=noir]').click();
document.addEventListener('submit',function(e){{if(e.target.matches('[data-preview]')){{e.preventDefault();alert('Preview only: on the live page this submits to Kajabi exactly as today.');}}}});
</script></body></html>
"""


def main():
    css, body, js = parts()
    (HERE / "preview.html").write_text(preview(css, body, js))
    (HERE / "kajabi-embed.html").write_text(embed(css, body, js))
    (HERE / "wtr.js").write_text(loader(css, body, js))
    for f in ("preview.html", "kajabi-embed.html", "wtr.js"):
        print(f"{f}: {(HERE / f).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
