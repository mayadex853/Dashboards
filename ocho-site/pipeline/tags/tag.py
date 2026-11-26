"""Write ID3 tags into every MP3 (R2 ocho-audio) and WAV master (R2 ocho-masters), then refresh the portal's files table.

  python3 tag.py mp3|wav PLAN.json ISRC_MASTER.csv [--only KEY] [--dry OUT_DIR]

PLAN.json: [{key: "OCHO-00NN/<name>.wav", mp3: "...mp3", path: "<Mega path>"}] from pipeline/wav/map.py (source names give per-version ISRCs).
Tags: Title, Artist, Album Artist, Album, Track n/N, Genre (album category), Composer, Publisher, BPM, Key, ISRC,
Grouping + Comments (contact line + the site's search keywords), Copyright, label/contact TXXX frames, cover art.
Resumable: finished keys are appended to tagged_<fmt>.txt.
"""
import concurrent.futures as cf
import csv
import difflib
import re
import json
import os
import sys
import tempfile
import threading
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

from mutagen.id3 import APIC, COMM, ID3, TALB, TBPM, TCOM, TCON, TCOP, TIT1, TIT2, TKEY, TPE1, TPE2, TPUB, TRCK, TSRC, TXXX, WPUB
from mutagen.wave import WAVE

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent))
sys.path.append(str(HERE.parent.parent / "portal"))
sys.argv, _argv = sys.argv[:1] + ["/nonexistent"], sys.argv  # tracks.py reads argv[1] at import
import tracks  # noqa: E402
sys.argv = _argv
import deploy  # noqa: E402
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("portal_build", HERE.parent.parent / "portal" / "build.py")
_pb = importlib.util.module_from_spec(_spec)
_saved, sys.argv = sys.argv, sys.argv[:1]  # the site build reads argv at import
_spec.loader.exec_module(_pb)
sys.argv = _saved
catalog = _pb.catalog

ACC, TOK = os.environ["CLOUDFLARE_ACCOUNT_ID"], os.environ["CLOUDFLARE_API_TOKEN"]
CONTACT = "Contact music@ochomusicgroup.com"
LOCK = threading.Lock()


def r2_url(bucket, key):
    return f"https://api.cloudflare.com/client/v4/accounts/{ACC}/r2/buckets/{bucket}/objects/" + "/".join(urllib.parse.quote(p) for p in key.split("/"))


def http(url, data=None, method="GET", ctype=None):
    h = {"User-Agent": "ocho-tags"}
    if "api.cloudflare.com" in url:
        h["Authorization"] = "Bearer " + TOK
    if ctype:
        h["Content-Type"] = ctype
    for a in range(5):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers=h), timeout=300).read()
        except Exception as e:  # noqa: BLE001
            err = e
    raise err


def match_titles(plan, rows_by_alb, unique=True):
    """Map each planned file (mp3 key without extension) to a value from rows_by_alb {album: [(track title, value)]},
    matching the file's source name to the sheet's track title (exact, then same version label + near-identical title)."""
    exact = {alb: {tracks.norm(t): v for t, v in rows} for alb, rows in rows_by_alb.items()}
    lab = lambda x: tracks.norm(re.sub(r"(?i)mix|version", "", x)).replace(" ", "")
    out, fuzzy = {}, set()
    for p in plan:
        alb, src = p["key"].split("/")[0], os.path.splitext(p["path"].split("/")[-1])[0]
        base, label = tracks.split_version(src)
        t = exact.get(alb, {})
        hit = t.get(tracks.norm(src)) or t.get(tracks.norm(base + (f" ({label})" if label else "")))
        if hit is None:  # naming drift: "enseñaste"/"enseñastes", "(Acapella)"/"(Acapella Mix)"
            mb, ml = tracks.norm(base), lab(label)
            for title, val in rows_by_alb.get(alb, []):
                rb, rl = tracks.split_version(title)
                rl_, rb_ = lab(rl), tracks.norm(rb)
                same_label = rl_ == ml or (ml and rl_ and (rl_.startswith(ml) or ml.startswith(rl_)))
                same_base = rb_ == mb or rb_.startswith(mb) or mb.startswith(rb_) or difflib.SequenceMatcher(None, rb_, mb).ratio() >= 0.88
                if same_label and same_base:
                    hit = val
                    fuzzy.add(p["mp3"][:-4])
                    break
        out[p["mp3"][:-4]] = hit
    if unique:  # e.g. an ISRC belongs to one recording: drop fuzzy guesses that collide
        seen = {}
        for k, v in out.items():
            if v:
                seen.setdefault(v, []).append(k)
        for v, ks in seen.items():
            if len(ks) > 1:
                for k in ks:
                    if k in fuzzy:
                        out[k] = None
    return out


def isrc_map(plan, csv_path):
    rows_by_alb = {}
    for r in csv.DictReader(open(csv_path, encoding="utf-8-sig")):
        rows_by_alb.setdefault(r["OCHO ALBUM ID#"].replace("_", "-").strip(), []).append((r["TRACK TITLE"], r["ISRC CODE"].strip()))
    return {k: v or "" for k, v in match_titles(plan, rows_by_alb).items()}


def main():
    fmt, plan_path, csv_path = sys.argv[1], sys.argv[2], sys.argv[3]
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    dry = sys.argv[sys.argv.index("--dry") + 1] if "--dry" in sys.argv else None
    plan = json.load(open(plan_path))
    isrc = isrc_map(plan, csv_path)
    cat = catalog()
    files = {}
    for a in cat["albums"]:
        vs = [(t, v) for t in a["tracks"] for v in t["v"]]
        for n, (t, v) in enumerate(vs, 1):
            files[v["f"][:-4]] = (a, t, v, n, len(vs))
    covers = {}
    done_path = HERE / f"tagged_{fmt}.txt"
    done = set(done_path.read_text().split()) if done_path.exists() and not dry else set()
    todo = [k for k in files if k not in done and (not only or k == only)]
    print(f"{fmt}: {len(todo)} to tag, {sum(1 for k in files if isrc.get(k))}/{len(files)} with ISRC")

    def tag(key):
        a, t, v, n, total = files[key]
        if a["img"] not in covers:
            covers[a["img"]] = http(cat["base"] + "covers/" + a["img"] + ".jpg")
        bucket, ext = ("ocho-audio", "mp3") if fmt == "mp3" else ("ocho-masters", "wav")
        data = http(("https://ochoaudio.com/" + urllib.parse.quote(key + ".mp3") + "?t=1") if fmt == "mp3" else r2_url(bucket, key + ".wav"))
        kw = ", ".join(t["tags"])
        frames = [
            TIT2(encoding=3, text=t["t"] + (f" ({v['l']})" if v["l"] else "")),
            TPE1(encoding=3, text=a["a"]), TPE2(encoding=3, text=a["a"]), TALB(encoding=3, text=a["t"]),
            TRCK(encoding=3, text=f"{n}/{total}"), TCON(encoding=3, text=a["c"]),
            TIT1(encoding=3, text=f"{CONTACT} · Ocho Music Group" + (f" · {kw}" if kw else "")),
            COMM(encoding=3, lang="eng", desc="", text=f"{CONTACT} · " + " ".join(x for x in [t["desc"], f"Keywords: {kw}." if kw else ""] if x)),
            TCOP(encoding=3, text="Ocho Music Group LLC"), WPUB(url="https://www.ochomusicgroup.com"),
            TXXX(encoding=3, desc="LABEL", text="Ocho Music Group"), TXXX(encoding=3, desc="CONTACT", text="music@ochomusicgroup.com"),
            TXXX(encoding=3, desc="CATALOG", text=a["id"]),
            APIC(encoding=0, mime="image/jpeg", type=3, desc="Cover", data=covers[a["img"]]),
        ]
        if t["comp"]: frames.append(TCOM(encoding=3, text=t["comp"]))
        if t["pub"]: frames.append(TPUB(encoding=3, text=t["pub"]))
        if t["bpm"]: frames.append(TBPM(encoding=3, text=str(t["bpm"])))
        if t["key"]: frames.append(TKEY(encoding=3, text=t["key"]))
        if isrc.get(key): frames.append(TSRC(encoding=3, text=isrc[key].replace("-", "")))
        with tempfile.NamedTemporaryFile(suffix="." + ext, delete=False) as f:
            f.write(data)
            tmp = f.name
        try:
            if fmt == "mp3":
                tags = ID3()
                for fr in frames:
                    tags.add(fr)
                tags.save(tmp, v2_version=3)
            else:
                w = WAVE(tmp)
                if w.tags is None:
                    w.add_tags()
                w.tags.clear()
                for fr in frames:
                    w.tags.add(fr)
                w.save(v2_version=3)
            out = Path(tmp).read_bytes()
        finally:
            os.unlink(tmp)
        if dry:
            Path(dry, key.replace("/", "__") + "." + ext).write_bytes(out)
            return key
        http(r2_url(bucket, key + "." + ext), out, "PUT", "audio/mpeg" if fmt == "mp3" else "audio/wav")
        deploy.sql("INSERT OR REPLACE INTO files (key, size, crc) VALUES (?,?,?)", [key + "." + ext, len(out), zlib.crc32(out)])
        with LOCK, open(done_path, "a") as fh:
            fh.write(key + "\n")
        return key

    with cf.ThreadPoolExecutor(4 if fmt == "mp3" else 3) as ex:
        for i, k in enumerate(ex.map(tag, todo), 1):
            if i % 25 == 0 or i == len(todo):
                print(i, k, flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
