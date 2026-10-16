"""Upload the site to Cloudflare R2 (served at AUDIO_BASE, e.g. https://ochoaudio.com/).

  site/<asset-ref>/img/**, site/<asset-ref>/tracks/*.json   immutable, uploaded once per asset commit
  site/ocho.js                                             the current build, cached for 5 minutes

Run `python3 build.py` first. Needs CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID.
Usage: python3 publish.py
"""
import mimetypes
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
BUCKET = "ocho-audio"
API = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/r2/buckets/{BUCKET}/objects/"
TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]
BASE = (HERE / "AUDIO_BASE").read_text().strip()


def put(key, path, cache):
    ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    req = urllib.request.Request(API + key, data=path.read_bytes(), method="PUT", headers={
        "Authorization": f"Bearer {TOKEN}", "Content-Type": ctype, "Cache-Control": cache})
    with urllib.request.urlopen(req, timeout=120) as r:
        if r.status != 200:
            raise SystemExit(f"upload failed: {key} ({r.status})")
    return key


def exists(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ocho-publish/1.0"}), timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    js = (HERE / "ocho.js").read_text()
    m = re.search(r'"base": "' + re.escape(BASE) + r'(site/[0-9a-f]{12}/)img/"', js)
    if not m:
        sys.exit("ocho.js does not point at AUDIO_BASE; run build.py first")
    prefix = m.group(1)
    if exists(BASE + prefix + ".done"):
        print(f"assets already uploaded: {prefix}")
    else:
        files = [p for d in ("img", "tracks") for p in (HERE / d).rglob("*") if p.is_file()]
        immutable = "public, max-age=31536000, immutable"
        with ThreadPoolExecutor(8) as ex:
            list(ex.map(lambda p: put(prefix + p.relative_to(HERE).as_posix(), p, immutable), files))
        marker = HERE / ".done"
        marker.write_text("ok")
        put(prefix + ".done", marker, immutable)
        marker.unlink()
        print(f"uploaded {len(files)} assets to {prefix}")
    put("site/ocho.js", HERE / "ocho.js", "public, max-age=300")
    print(f"published {BASE}site/ocho.js")


if __name__ == "__main__":
    main()
