"""Build the streaming catalog: tracks/<ALBUM-ID>.json plus web-ready MP3s named for upload.

Input (WORK dir, made by the Mega download step):
  out/<ALBUM-ID>/<source name>.mp3 + .json   320k MP3 and waveform peaks for every master WAV
  meta/OCHO_ISRC_MASTER_*.csv                 track IDs, ISRCs and proper titles for the whole catalog
  meta/apm/<ALBUM-ID>__OCHO_00NN*.csv         APM delivery sheets (BPM, timing, track and album descriptions)

Output:
  tracks/<ALBUM-ID>.json   one file per album, loaded by the site when the album is opened
  WORK/dist/<ALBUM-ID>/*.mp3   the audio, renamed to the paths the JSON points at (upload this folder as-is)

Usage: python3 tracks.py WORK
"""
import array
import csv
import difflib
import math
import subprocess
import glob
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

from apm_meta import tags  # cleaned APM facets, shared with apm_meta.py

HERE = Path(__file__).parent
WORK = Path(sys.argv[1])
OUT = HERE / "tracks"
DIST = WORK / "dist"
POINTS = 240  # waveform resolution shipped to the browser

# Suffixes that mark an alternate version of a main track, in display order.
VERSION_RE = re.compile(r"\s*(?:\((?P<p>[^)]*(?:mix|instrumental|no brass)[^)]*)\)|_(?P<u>.+))\s*$", re.I)


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def slug(s):
    return re.sub(r"\s+", "-", norm(s))


def split_version(name):
    """'3 Mucho money (TV Mix)' -> ('Mucho money', 'TV Mix');  'A ganar_30sec' -> ('A ganar', '30 Sec')."""
    name = re.sub(r"^\d+\s+", "", name)
    label = ""
    while True:
        m = VERSION_RE.search(name)
        if not m:
            break
        part = (m.group("p") or m.group("u")).replace("_", " ").strip()
        part = re.sub(r"(\d+)\s*sec\b", r"\1 Sec", part, flags=re.I)
        label = (part + (" / " + label if label else "")).strip()
        name = name[:m.start()].strip()
    return name, label


def rms_wave(mp3, n=POINTS):
    """Loudness envelope (RMS per slice) from the MP3, scaled 0-100; cached next to the file."""
    cache = mp3.with_suffix(".rms.json")
    if cache.exists() and cache.stat().st_mtime >= mp3.stat().st_mtime:
        return json.loads(cache.read_text())
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "1", "-ar", "4000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    s = array.array("h", pcm)
    step = max(1, len(s) // n)
    out = []
    for i in range(n):
        seg = s[i * step:(i + 1) * step] or array.array("h", [0])
        out.append(math.sqrt(sum(x * x for x in seg) / len(seg)))
    mx = max(out) or 1
    wave = [round(100 * (v / mx) ** 1.4) for v in out]
    cache.write_text(json.dumps(wave))
    return wave


def key_name(k):
    return re.sub(r"\s+min(or)?$", " minor", re.sub(r"\s+maj(or)?$", " major", k.strip(), flags=re.I), flags=re.I)


def downsample(peaks, n=POINTS):
    if len(peaks) <= n:
        return peaks
    step = len(peaks) / n
    return [max(peaks[int(i * step):max(int(i * step) + 1, int((i + 1) * step))]) for i in range(n)]


def load_isrc():
    path = sorted(glob.glob(str(WORK / "meta" / "OCHO_ISRC_MASTER_*.csv")))[-1]
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    by_album = {}
    for r in rows:
        alb = r["OCHO ALBUM ID#"].replace("_", "-").strip()
        if alb:
            by_album.setdefault(alb, []).append(r)
    return by_album


def load_apm():
    """Merge every APM sheet per album; later exports fill in fields earlier ones left blank."""
    tracks, albums = {}, {}
    for path in sorted(glob.glob(str(WORK / "meta" / "apm" / "*.csv"))):
        alb = os.path.basename(path).split("__")[0]
        try:
            rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
        except UnicodeDecodeError:
            rows = list(csv.DictReader(open(path, encoding="latin-1")))
        for r in rows:
            if r.get("CD Description"):
                albums[alb] = r["CD Description"].strip()
            fn = (r.get("Audio Filename") or "").strip()
            if not fn or (r.get("Stem Name") or "").strip():
                continue
            k = (alb, norm(os.path.splitext(fn)[0]))
            cur = tracks.setdefault(k, {})
            for field in ("Track Title", "BPM", "Track Description", "ISRC", "Track Number", "Key", "Facet Names"):
                if r.get(field) and not cur.get(field):
                    cur[field] = r[field].strip()
            comp = ", ".join(dict.fromkeys(n for n in (" ".join(
                (r.get(f"Composer{i} {part}") or "").strip() for part in ("First Name", "Middle Name", "Last Name")
                if (r.get(f"Composer{i} {part}") or "").strip()) for i in (1, 2, 3)) if n))
            pub = ", ".join(dict.fromkeys(v for v in ((r.get(f"Publisher{i}") or "").strip() for i in (1, 2, 3)) if v))
            cur["comp"] = cur.get("comp") or comp
            cur["pub"] = cur.get("pub") or pub
    return tracks, albums


def main():
    isrc = load_isrc()
    apm, album_desc = load_apm()
    OUT.mkdir(exist_ok=True)
    total = 0
    for adir in sorted(p for p in (WORK / "out").iterdir() if p.is_dir()):
        alb = adir.name
        titles = {norm(r["TRACK TITLE"]): r for r in isrc.get(alb, [])}
        groups = {}
        for js in sorted(adir.glob("*.json")):
            mp3 = js.with_suffix(".mp3")
            if not mp3.exists():
                continue
            meta = json.loads(js.read_text())
            src = os.path.splitext(meta["src"].split("/")[-1])[0]
            base, label = split_version(src)
            g = groups.setdefault(norm(base), {"base": base, "versions": [], "order": 999})
            num = re.match(r"^(\d+)\s", src)
            info = apm.get((alb, norm(src)), {})
            if not label and (num or info.get("Track Number", "").isdigit()):
                g["order"] = int(num.group(1)) if num else int(info["Track Number"])
            rec = titles.get(norm(src)) or titles.get(norm(base + (f" ({label})" if label else "")))
            fname = f"{slug(base)}{'--' + slug(label) if label else ''}.mp3"
            (DIST / alb).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(mp3, DIST / alb / fname)
            g["versions"].append({
                "l": label, "f": f"{alb}/{fname}", "d": meta["dur"], "p": rms_wave(mp3),
                "bpm": info.get("BPM", ""), "desc": info.get("Track Description", ""),
                "isrc": (rec or {}).get("ISRC CODE", "") or info.get("ISRC", ""),
                "title": (rec or {}).get("TRACK TITLE", "") or info.get("Track Title", ""),
                "key": key_name(info.get("Key", "")), "tags": tags(info.get("Facet Names", "")),
                "comp": info.get("comp", ""), "pub": info.get("pub", ""),
            })
        # Alternate mixes whose file name drifts from the master's ("Tu me enseñaste" vs "...enseñastes",
        # "Yerba buena" vs "Yerba buena (yo te dejo 3)") would form a row led by an alt: fold them into the master.
        mains = {k: g for k, g in groups.items() if any(not v["l"] for v in g["versions"])}
        for k, g in list(groups.items()):
            if k in mains:
                continue
            best = max(mains, default=None, key=lambda m: (m.startswith(k) or k.startswith(m),
                                                          difflib.SequenceMatcher(None, k, m).ratio()))
            if best and (best.startswith(k) or k.startswith(best)
                         or difflib.SequenceMatcher(None, k, best).ratio() >= 0.85):
                mains[best]["versions"] += g["versions"]
                del groups[k]
        tracks = []
        for g in groups.values():
            vs = sorted(g["versions"], key=lambda v: (v["l"] != "", v["l"]))
            main = vs[0]
            title = re.sub(r"\s*\((?:[^)]*mix[^)]*)\)\s*$", "", main["title"] or g["base"], flags=re.I) or g["base"]
            first = lambda f: next((v[f] for v in vs if v[f]), "")  # main mix first, else any version that has it
            tracks.append({
                "t": title, "isrc": main["isrc"], "bpm": first("bpm"), "desc": first("desc"), "order": g["order"],
                "key": first("key"), "tags": first("tags"), "comp": first("comp"), "pub": first("pub"),
                "v": [{"l": v["l"], "f": v["f"], "d": v["d"], "p": v["p"]} for v in vs],
            })
        tracks.sort(key=lambda x: (x["order"], norm(x["t"])))
        for x in tracks:
            del x["order"]
        (OUT / f"{alb}.json").write_text(json.dumps(
            {"id": alb, "desc": album_desc.get(alb, ""), "tracks": tracks}, ensure_ascii=False, separators=(",", ":")))
        n = sum(len(x["v"]) for x in tracks)
        total += n
        print(f"{alb}: {len(tracks)} tracks, {n} versions")
    print(f"total versions: {total}")


if __name__ == "__main__":
    main()
