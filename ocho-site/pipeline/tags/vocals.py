"""Add a per-version vocals flag ("voc": 1 = has vocals, 0 = instrumental) to ../../tracks/*.json from APM Facet Names sheets.

  python3 vocals.py PLAN.json APM_DIR     (APM_DIR holds OCHO_OCHO_00NN_Facet_Names.csv)

APM facets decide (HasVocals / ACappella -> 1, InstrumentalOnly -> 0). Versions APM doesn't flag: instrumental-type mix
names (instrumental, underscore, inst, beat, no vocals) -> 0, a cappella -> 1, otherwise the track's main version, otherwise 0.
"""
import csv
import glob
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.argv, _argv = sys.argv[:1] + ["/nonexistent"], sys.argv
import tag  # noqa: E402  (also imports tracks.py)
sys.argv = _argv


def flag(facets):
    s = {x.strip().lower() for x in (facets or "").split(";")}
    if "hasvocals" in s or "acappella" in s:
        return 1
    if "instrumentalonly" in s:
        return 0
    return None


def main():
    plan, apm = json.load(open(sys.argv[1])), sys.argv[2]
    rows_by_alb = {}
    for f in glob.glob(os.path.join(apm, "*Facet_Names*.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            if (r.get("Stem Name") or "").strip() or not (r.get("CD ID") or "").strip():
                continue
            rows_by_alb.setdefault(r["CD ID"].strip(), []).append((r["Track Title"], flag(r.get("Facet Names"))))
    apm_flag = tag.match_titles(plan, rows_by_alb, unique=False)
    stats = {"apm": 0, "name": 0, "main": 0, "default": 0}
    for f in sorted((HERE.parent.parent / "tracks").glob("OCHO-*.json")):
        d = json.loads(f.read_text())
        for t in d["tracks"]:
            for i, v in enumerate(t["v"]):
                k, lab = v["f"][:-4], (v["l"] or "").lower()
                val = apm_flag.get(k)
                if val is not None:
                    stats["apm"] += 1
                elif re.search(r"instr|underscore|\binst\b|beat|no vo[cx]|karaoke", lab):
                    val = 0; stats["name"] += 1
                elif re.search(r"a ?cap+el+a", lab):
                    val = 1; stats["name"] += 1
                elif i and t["v"][0].get("voc") is not None:
                    val = t["v"][0]["voc"]; stats["main"] += 1
                else:
                    val = 0; stats["default"] += 1
                v["voc"] = val
        f.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    print(stats)


if __name__ == "__main__":
    main()
