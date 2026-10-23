"""Build the Wreck the Room checkout styling (Kajabi offer checkout pages).

Kajabi gives every offer's checkout page its own theme. This writes the two theme settings we change on each:
  css  src/checkout.css (dark page, light card, gold pay button, short terms box)
  js   src/checkout.js  (brand bar, headline and three steps above the checkout)

Two variants: "course" offers grant access right away; "session" offers (1:1 coaching) send the buyer
to book a time. Outputs checkout-settings.json: {"course": {"css", "js"}, "session": {"css", "js"}}.

Offer checkout themes (all use section 1744906803654):
  course   Blueprint 2164998185, Inner Circle 2164028110, Council 2166311814,
           Drifting 2166312486, Stalling 2166312488, Renovating 2166312492, Rebuilding 2166750082
  session  Clarity Session 2163971752, Blueprint Add-On 2167881080
Before this, every one of these themes had Kajabi's default empty CSS and JS.

Usage: python3 build_checkout.py
"""
import json
from pathlib import Path

from build import LOGO

HERE = Path(__file__).parent
SRC = HERE / "src"


VARIANTS = {
    "course": {"STEP3": "Get instant access by email", "TRUST": "Instant access by email"},
    "session": {"STEP3": "Pick your session time", "TRUST": "Schedule right after payment"},
}


def main():
    out = {}
    for name, words in VARIANTS.items():
        css = (SRC / "checkout.css").read_text().replace("{{TRUST}}", words["TRUST"])
        js = (SRC / "checkout.js").read_text().replace("{{LOGO}}", LOGO).replace("{{STEP3}}", words["STEP3"])
        out[name] = {"css": css, "js": js}
    (HERE / "checkout-settings.json").write_text(json.dumps(out, indent=1))
    print("checkout-settings.json:", ", ".join(f"{k} css {len(v['css']):,} / js {len(v['js']):,}" for k, v in out.items()))


if __name__ == "__main__":
    main()
