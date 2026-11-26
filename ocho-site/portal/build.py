"""Bundle the client portal into dist/worker.js: the app page and the catalog (from ../data.py + ../tracks/*.json)."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import build as site  # noqa: E402  (site build: CDN paths)
import data  # noqa: E402


def catalog():
    albums = []
    for aid, title, artist, cat, img in data.ALBUMS:
        f = HERE.parent / "tracks" / f"{aid}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        tracks = [{"t": t["t"], "bpm": t.get("bpm") or "", "key": t.get("key") or "", "desc": t.get("desc") or "",
                   "tags": t.get("tags") or [], "comp": t.get("comp") or "", "pub": t.get("pub") or "",
                   "v": [{"l": v["l"], "f": v["f"], "d": v["d"], "voc": v.get("voc", 0)} for v in t["v"]]} for t in d["tracks"]]
        albums.append({"id": aid, "t": title, "a": artist, "c": cat, "img": img, "desc": d.get("desc") or "", "tracks": tracks})
    return {"base": site.CDN_BASE, "audio": site.AUDIO_BASE, "albums": albums, "cats": data.ALBUM_CATS,
            "moods": data.MOODS, "syn": data.SYNONYMS, "stop": data.FIND_STOP,
            "trackCount": sum(len(t["v"]) for a in albums for t in a["tracks"])}


def main():
    cat = catalog()
    cj = json.dumps(cat, ensure_ascii=False, separators=(",", ":"))
    html = (HERE / "app.html").read_text().replace("__LOGO__", site.CDN_BASE + "logo.png").replace("__VER__", hashlib.sha1(cj.encode()).hexdigest()[:10])
    js = (HERE / "worker.js").read_text()
    js = js.replace("const HTML = __HTML__;", "const HTML = " + json.dumps(html) + ";", 1)
    js = js.replace("const CATALOG = __CATALOG__;", "const CATALOG = " + cj + ";", 1)
    out = HERE / "dist" / "worker.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text(js)
    print(f"dist/worker.js: {out.stat().st_size:,} bytes, {len(cat['albums'])} albums, {cat['trackCount']} tracks")


if __name__ == "__main__":
    main()
