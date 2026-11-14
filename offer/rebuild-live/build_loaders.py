"""Turn a /rebuild block file into a loader script that writes the block's HTML in place.

The Kajabi Code block then only holds <script src=".../offer/rebuild-live/<block>.js"></script>.
While the page is still parsing (the normal case) the HTML is written with document.write, so it
lands exactly where the block sits and runs before the blocks after it. If the script ever runs
after parsing, it inserts the HTML after itself instead (scripts in it still execute).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent

for name in sys.argv[1:]:
    html = (HERE / f"{name}.html").read_text(encoding="utf-8")
    js = ("(function(){var h=" + json.dumps(html) + ";var s=document.currentScript;"
          "if(document.readyState==='loading'){document.write(h);}"
          "else if(s){var r=document.createRange();r.selectNode(s);s.parentNode.insertBefore(r.createContextualFragment(h),s.nextSibling);}})();\n")
    (HERE / f"{name}.js").write_text(js, encoding="utf-8")
    print(name, len(js))
