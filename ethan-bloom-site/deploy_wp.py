#!/usr/bin/env python3
"""Publish the Ethan Bloom page to the WordPress site at ethanbloomthefilm.com (hosted on 10Web).

Credentials come from the environment, never from this file:
  WP_USER          WordPress username
  WP_APP_PASSWORD  Application Password (Users > Profile > Application Passwords)

  python3 deploy_wp.py stage     upload images + trailer, publish the page at /new-home (blank Elementor Canvas template)
  python3 deploy_wp.py live      make /new-home the homepage (the previous homepage id is saved to .wp_previous_home)
  python3 deploy_wp.py revert    restore the previous homepage (the original is page 162)
"""
import base64, json, mimetypes, os, re, sys, urllib.error, urllib.request
from pathlib import Path

SITE = "https://ethanbloomthefilm.com"
API = SITE + "/wp-json/wp/v2"
SLUG = "new-home"
HERE = Path(__file__).resolve().parent
OLD_TRAILER = SITE + "/wp-content/uploads/2025/10/Ethan-Bloom-Trailer-720-Menemsha.mov"


def auth_header():
    user, pw = os.environ.get("WP_USER"), os.environ.get("WP_APP_PASSWORD")
    if not user or not pw:
        sys.exit("Set WP_USER and WP_APP_PASSWORD in the environment first.")
    return "Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode()


def call(method, path, data=None, raw=None, headers=None):
    h = {"Authorization": auth_header(), "Accept": "application/json"}
    body = None
    if raw is not None:
        body = raw
    elif data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    req = urllib.request.Request(path if path.startswith("http") else API + path, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} failed: {e.code} {e.read()[:400].decode(errors='replace')}")


def upload(path: Path):
    """Upload one file to the Media Library, reusing an earlier upload with the same name."""
    name = "eb-" + path.name
    slug = re.sub(r"[^a-z0-9-]", "-", Path(name).stem.lower())
    found = call("GET", f"/media?slug={slug}&per_page=1")
    if found:
        return found[0]["source_url"]
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    item = call("POST", "/media", raw=path.read_bytes(),
                headers={"Content-Type": mime, "Content-Disposition": f'attachment; filename="{name}"'})
    print("  uploaded", path.name, "->", item["source_url"])
    return item["source_url"]


def build_content():
    html = (HERE / "page.html").read_text()
    # WordPress supplies <head>, so drop the artifact-only tags at the top.
    html = re.sub(r"<title>.*?</title>\n|<meta name=\"claude:[^>]*>\n", "", html)
    for img in sorted((HERE / "img").glob("*.jpg")):
        html = html.replace(f'"img/{img.name}"', f'"{upload(img)}"')
    try:
        trailer = upload(HERE / "trailer.mp4")
    except SystemExit as e:
        print("  trailer upload refused, using the trailer already on the site:", e)
        trailer = OLD_TRAILER
    html = html.replace('src="trailer.mp4" type="video/mp4"', f'src="{trailer}"' + (' type="video/mp4"' if trailer.endswith(".mp4") else ""))
    # Same-site links: the page now lives on ethanbloomthefilm.com itself.
    html = html.replace(f'href="{SITE}/becomeafan/"', 'href="/becomeafan/"')
    # The 10Web/Elementor site kit styles h1/button/a through `.elementor-kit-183 …` on <body>, which outranks
    # the page's own classes, and body.custom-background tiles a dark texture behind every band that has no colour
    # of its own, so drop both classes before anything renders. The theme also centres <main>, boxes every <article>
    # in #222 with a black border (dark text on dark cards) and colours headings silver; these resets sit after the
    # theme but before the page's own CSS, so they win over the theme and lose to any rule the design sets.
    fix = ("<script>[...document.body.classList].filter(c => /^(elementor-kit-|custom-background$)/.test(c))"
           ".forEach(c => document.body.classList.remove(c));</script>\n"
           "<style>main{text-align:start;margin:0}"
           " main :where(article){display:block;width:auto;padding:0;border:0;background:none;text-align:inherit}"
           " main :where(h1,h2,h3,h4,h5,h6){color:inherit}</style>\n")
    return "<!-- wp:html -->\n" + fix + html + "\n<!-- /wp:html -->"


def stage():
    content = build_content()
    page = {"title": "Ethan Bloom", "slug": SLUG, "status": "publish", "content": content, "template": "elementor_canvas"}
    existing = call("GET", f"/pages?slug={SLUG}&status=publish,draft,private&context=edit")
    res = call("POST", f"/pages/{existing[0]['id']}" if existing else "/pages", data=page)
    print("Staged:", res["link"], f"(page id {res['id']})")


def purge_cache(page_id):
    """10Web's server cache keeps serving the old homepage after a switch; re-saving the page clears it."""
    status = call("GET", f"/pages/{page_id}?context=edit")["status"]
    call("POST", f"/pages/{page_id}", data={"status": status})


def live():
    page = call("GET", f"/pages?slug={SLUG}")
    if not page:
        sys.exit("Run `stage` first.")
    settings = call("GET", "/settings")
    (HERE / ".wp_previous_home").write_text(json.dumps({"show_on_front": settings["show_on_front"], "page_on_front": settings["page_on_front"]}))
    call("POST", "/settings", data={"show_on_front": "page", "page_on_front": page[0]["id"]})
    purge_cache(page[0]["id"])
    print("Live: homepage is now page", page[0]["id"], "- previous setting saved to .wp_previous_home")


def revert():
    # The container is temporary, so fall back to the original homepage (page 162) if the saved file is gone.
    f = HERE / ".wp_previous_home"
    prev = json.loads(f.read_text()) if f.exists() else {"show_on_front": "page", "page_on_front": 162}
    call("POST", "/settings", data=prev)
    if prev.get("page_on_front"):
        purge_cache(prev["page_on_front"])
    print("Reverted homepage to", prev)


if __name__ == "__main__":
    {"stage": stage, "live": live, "revert": revert}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
