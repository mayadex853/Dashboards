"""Print the Kajabi Code-block HTML for each custom page, pinned to one commit.

Every page carries the same site nav (header_html) and loads its script from jsDelivr at a fixed commit,
so a page only changes when its block is updated. Kajabi's own header is hidden on these pages.

Usage: python3 kajabi_blocks.py <commit>          # prints JSON {page: html}
"""
import json
import sys

from build import header_html

CDN = "https://cdn.jsdelivr.net/gh/mayadex853/Dashboards@{sha}/wtr-homepage/{file}"
RESET = ("#section-{s} .container,#section-{s} .row,#section-{s} [class*=col-],#section-{s} .block"
         "{{padding:0 !important;margin:0 !important;max-width:none !important;width:100% !important;flex:0 0 100% !important}}")
# lets the pinned framework section and other sticky elements work inside Kajabi's wrappers
UNCLIP = "body:not(.stop-scroll--body){{overflow-x:clip !important;overflow-y:visible !important}}#section-{s} .block{{overflow:clip !important}}"
BOOK_POPUP = ("#two-step", " data-k-book")
CREDITS_SHA = "8c8d8159c426b92b283f40ddef947018af99f041"


def style(*sections, unclip=True, extra=""):
    css = "body{background:#0a0908 !important}" + "".join(RESET.format(s=s) for s in sections)
    if unclip:
        css += UNCLIP.format(s=sections[0])
    return f"<style>{css}{extra}</style>"


def blocks(sha):
    src = lambda f: f'<script src="{CDN.format(sha=sha, file=f)}"></script>'
    return {
        "home": style("wtr_home") + '<div style="position:relative">' + header_html("#wtr-book")
                + '<div id="wtr-mount" data-dir="brick"></div></div>' + src("wtr.js"),
        "speaker_top": style("wtr_sp_top", "wtr_sp_bottom", unclip=False) + '<div style="position:relative">'
                + header_html("#wtr-book") + '<div id="wtr-sp-top-mount"></div></div>',
        "speaker_bottom": '<div id="wtr-sp-bottom-mount"></div>' + src("speaker.js"),
        "coaching": style("wtr_coach", unclip=False) + '<div style="position:relative">' + header_html(*BOOK_POPUP)
                + '<div id="wtr-coach-mount"></div></div>' + src("coaching.js"),
        # the About page is a website page, so the site header (used by the blog) is hidden here
        "about": style("wtr_about", extra="#section-header{display:none !important}") + '<div style="position:relative">'
                + header_html(*BOOK_POPUP) + '<div id="wtr-about-mount"></div></div>' + src("about.js"),
        # credits.js is pinned separately: it reads the live credits sheet, so it is only rebuilt on purpose
        "credits": "<style>body{background:#0a0908 !important;margin:0}" + RESET.format(s="wtr_credits") + "</style>"
                + '<div style="position:relative">' + header_html() + '<div id="wtr-credits-mount"></div></div>'
                + f'<script src="{CDN.format(sha=CREDITS_SHA, file="credits.js")}"></script>',
    }


if __name__ == "__main__":
    print(json.dumps(blocks(sys.argv[1]), indent=1))
