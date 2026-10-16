"""Merge APM metadata exports ("OCHO_OCHO_00NN_Facet_Names.csv") into tracks/<ALBUM-ID>.json.

Fills in track descriptions, BPM, key, composers, publishers and album descriptions that are
missing, and replaces each track's mood/use tags with the cleaned APM facets. Audio and
waveforms are untouched, so this runs without the master audio (tracks.py needs that).

Usage: python3 apm_meta.py DIR_WITH_APM_CSVS
Then: python3 build.py && python3 publish.py
"""
import csv
import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent

# Facets that describe the delivery rather than the music: useless to a supervisor searching by mood.
SKIP = {
    "main", "alt", "alternate", "hasvocals", "hasaistems", "artist-driven", "instrumentgroupings", "stemsavailable",
    "instrumentalonly", "english", "haslyrics", "performerseries", "tvmix", "acappella", "male", "female",
    "vocalbackground", "vocalduet", "busy", "building", "person/name",
}
SKIP_RE = re.compile(r"^(\d.*|[A-G][#b]?(Maj|Min))$")  # tempo ranges, decades, musical keys


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def tags(facets):
    """'Main;RealityTV,Unscripted;FilmScore/Orchestral;Tense' -> ['Reality TV, Unscripted', 'Film Score / Orchestral', 'Tense']"""
    out = {}
    for raw in (facets or "").split(";"):
        raw = raw.strip()
        if not raw or raw.lower() in SKIP or SKIP_RE.match(raw):
            continue
        f = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", raw).replace(",", ", ").replace("/", " / ")
        out.setdefault(f.lower(), f)
    return list(out.values())


def key_from_facets(facets):
    m = re.search(r"(?:^|;)([A-G][#b]?)(Maj|Min)(?:;|$)", facets or "")
    return f"{m.group(1)} {'major' if m.group(2) == 'Maj' else 'minor'}" if m else ""


def people(r, kind, n):
    if kind == "Composer":
        names = (" ".join(p for p in ((r.get(f"Composer{i} {x}") or "").strip() for x in ("First Name", "Middle Name", "Last Name")) if p)
                 for i in range(1, n + 1))
    else:
        names = ((r.get(f"Publisher{i}") or "").strip() for i in range(1, n + 1))
    return ", ".join(dict.fromkeys(x for x in names if x))


def read(path):
    try:
        return list(csv.DictReader(open(path, encoding="utf-8-sig")))
    except UnicodeDecodeError:
        return list(csv.DictReader(open(path, encoding="latin-1")))


def main(src):
    rows = {}
    for path in sorted(glob.glob(str(Path(src) / "*.csv"))):
        for r in read(path):
            if (r.get("CD ID") or "").strip() and not (r.get("Stem Name") or "").strip():
                rows.setdefault(r["CD ID"].strip(), []).append(r)
    for alb, rs in sorted(rows.items()):
        f = HERE / "tracks" / f"{alb}.json"
        if not f.exists():
            print(f"{alb}: no tracks/{alb}.json, skipped")
            continue
        d = json.loads(f.read_text())
        by_isrc = {re.sub(r"[^A-Z0-9]", "", (r.get("ISRC") or "").upper()): r for r in rs}
        # the main mix of each song: Track Title equals Song Title (else the song's first row)
        by_song = {}
        for r in rs:
            k = norm(r.get("Song Title"))
            if k not in by_song or norm(r.get("Track Title")) == k:
                by_song[k] = r
        if not d.get("desc") and rs[0].get("CD Description"):
            d["desc"] = rs[0]["CD Description"].strip()
        hit = 0
        for t in d["tracks"]:
            r = by_isrc.get(re.sub(r"[^A-Z0-9]", "", (t.get("isrc") or "").upper()))
            if r is not None and norm(r.get("Song Title")) in by_song:
                r = by_song[norm(r["Song Title"])]
            r = r or by_song.get(norm(t["t"])) or next((v for k, v in by_song.items() if k and (k.startswith(norm(t["t"])) or norm(t["t"]).startswith(k))), None)
            if r is None:
                print(f"  {alb}: no APM row for '{t['t']}'")
                continue
            hit += 1
            fill = {"desc": (r.get("Track Description") or "").strip(), "bpm": (r.get("BPM") or "").strip(),
                    "key": key_from_facets(r.get("Facet Names")), "comp": people(r, "Composer", 3), "pub": people(r, "Publisher", 3)}
            for k, v in fill.items():
                if v and not t.get(k):
                    t[k] = v
            tg = tags(r.get("Facet Names"))
            if tg:
                t["tags"] = tg
        f.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
        print(f"{alb}: {hit}/{len(d['tracks'])} tracks matched")


if __name__ == "__main__":
    main(sys.argv[1])
