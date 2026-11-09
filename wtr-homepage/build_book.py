"""Build the book waitlist pieces. Both post to Kajabi's "[Waitlist] Book Release - 1st Book" form
(2149477099) in the background, so the visitor never leaves the page.

Outputs (each is the full contents of one Kajabi Code block, pasted inline):
  book-ps-code.html    the P.S. strip on wrecktheroom.com/training (theme 2165135178, section 1774589888033,
                       block wtr_book_ps, placed right under the "Your Results Are On Their Way" headline)
  book-page-code.html  the whole wrecktheroom.com/book page (landing page 2152353318, theme 2167998360)
  book-preview.html    both, for local review (?v=ps or ?v=page)

Usage: python3 build_book.py
"""
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "src"
BOOK_PAGE_ID = "2152353318"


def main():
    js = "<script>" + (SRC / "book.js").read_text() + "</script>"
    ps = (SRC / "book-ps.html").read_text().strip() + js
    page = (SRC / "book-page.html").read_text().replace("{{LP}}", BOOK_PAGE_ID).strip() + js
    (HERE / "book-ps-code.html").write_text(ps)
    (HERE / "book-page-code.html").write_text(page)
    preview = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="csrf-token" content="preview"><title>Book waitlist (preview)</title>
<style>body{{margin:0;font-family:Georgia,serif;background:#f6f6f6}}</style></head><body>
<div id="v-ps" style="padding:20px"><h2 style="text-align:center;color:#000fff">✉️ Your Results Are On Their Way To Your Inbox Right Now</h2>
<h2 style="text-align:center">While You Wait...Watch the Video Below 👇</h2>{ps}<div style="max-width:1100px;margin:0 auto;aspect-ratio:16/9;background:#222"></div></div>
<div id="v-page">{page}</div>
<script>var v=new URLSearchParams(location.search).get('v')||'ps';document.getElementById(v==='ps'?'v-page':'v-ps').remove();</script>
</body></html>"""
    (HERE / "book-preview.html").write_text(preview)
    for f in ("book-ps-code.html", "book-page-code.html", "book-preview.html"):
        print(f"{f}: {(HERE / f).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
