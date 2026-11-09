"""Clone the Ethan Bloom section from the HD Music Now homepage build (../hdmn-homepage/build.py).

The markup, styles, trailer pop-up and live screenings list are taken straight from that build, so changes made
there carry over the next time the credits page is built. Only the colors change: HDMN's purple becomes the
Wreck the Room gold and red.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

HDMN = Path(__file__).parent.parent / "hdmn-homepage"
POSTERS = "https://mayadex853.github.io/Dashboards/hdmn-homepage/posters/"

# HDMN purple -> WTR gold / red
RECOLOR = [
    ("--vio:#b14bf4;--vio2:#c084fc;--blu:#38bdf8;--brand:#7b1fa2;", "--vio:#c9a84c;--vio2:#ecd69b;--blu:#c9a84c;--brand:#b8322a;"),
    ("rgba(177,75,244,", "rgba(201,168,76,"), ("rgba(192,132,252,", "rgba(236,214,155,"),
    ("rgba(123,31,162,", "rgba(184,50,42,"), ("rgba(99,19,133,", "rgba(140,114,49,"),
    ("#e9d5ff", "#ecd69b"), ("#f3e8ff", "#f6e7c1"), ("#9333ea", "#d8483b"),
]
# rules the Ethan Bloom section depends on (selector prefixes) besides its own block
DEPS_EXACT = {".hd", ".hd-eb", ".hd-btn"}
DEPS = (".hd *", ".hd h1", ".hd p", ".hd a", ".hd-wrap", ".hd-h2", ".hd-grad", ".hd-btn.", ".hd-reveal", ".hd-ctas",
        ".hd-ticker", ".hd-marquee", ".hd-track", ".hd-f-back", ".hd-f-x", "@keyframes hd-")


def _load():
    if str(HDMN) not in sys.path:
        sys.path.insert(0, str(HDMN))
    argv, sys.argv = sys.argv, sys.argv[:1]  # the HDMN build reads an optional CLI argument
    try:
        spec = importlib.util.spec_from_file_location("hdmn_build", HDMN / "build.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


def _rules(css):
    """Split top-level CSS into (selector, text) rules."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        depth, k = 1, j + 1
        while k < n and depth:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        sel = css[i:j].strip()
        sel = re.sub(r"/\*.*?\*/", "", sel, flags=re.S).strip()
        out.append((sel, css[i:k]))
        i = k
    return out


def ethan_bloom():
    m = _load()
    css = m.CSS
    imp = css[css.index("@import"):css.index("');", css.index("@import")) + 3]
    block = css[css.index("/* ETHAN BLOOM */"):]
    block = block[:block.index("\n/* ", 10)] if "\n/* " in block[10:] else block
    deps = "".join(r for sel, r in _rules(css.replace(imp, "")) if (sel in DEPS_EXACT or sel.startswith(DEPS)) and "ETHAN" not in sel)
    out_css = deps + block
    for a, b in RECOLOR:
        out_css = out_css.replace(a, b)

    tpl = m.TEMPLATE
    s = tpl.index('<section class="hd-ethan"')
    e = tpl.index("<section", s + 10)
    html = tpl[s:e].strip().format(
        base=POSTERS,
        eb_n=len(m.EB_FESTIVALS),
        eb_showtimes=m.EB_SHOWTIMES,
        eb_trailer=m.EB_TRAILER,
        eb_shows=m.e(json.dumps(m.EB_SCREENINGS)),
        eb_open=m.EB_DELRAY_OPEN,
        eb_quotes="".join(f'<figure class="hd-eb-q hd-reveal"><blockquote>&ldquo;{m.e(q)}&rdquo;</blockquote>'
                          f'<figcaption>{m.e(src)}</figcaption></figure>' for q, src in m.EB_QUOTES),
        eb_fest=m._marquee(m.EB_FESTIVALS),
    )
    html = f'<div class="hd hd-clone">{html}</div>'

    js = m.JS
    js = js[js.index("/* Ethan Bloom: trailer pop-up */"):js.index("/* music finder")]
    js = "(function(){\n" + js.replace("__SHEET__", m.SHEET_ID) + "\n})();"
    return imp, out_css, html, js


if __name__ == "__main__":
    imp, c, h, j = ethan_bloom()
    print(len(c), len(h), len(j))
