"""Build the list of Babylonia Judaica entries with BJ's own status, from its General Index.

BJ (Oppenheimer 1983) is an archive.org lending scan; its "search inside" returns snippets
with page numbers without a loan. Snippets from the General Index (pp. 530-546) were saved in
data/fts_bj_index*.json (local only: in-copyright text). BJ's index prints every entry in bold
with its page range and the names of its sub-sections, e.g.
  "Be Katil, 80-81 (Location, 80; Attempts at Identification, 80; Sages, 81)"
  "Almin (A), 423, 433, 465"
The sub-section names give BJ's status:
  attempts   "Attempts at Identification": unidentified or disputed (what this project targets)
  proposed   "Proposed Location": BJ proposes a location itself
  earlier    "Already Proposed Location": BJ discusses earlier proposals and decides
  located    "Location" only: BJ treats the place as located
  appendix   "(A)": appendix entry (minor place, usually no location)
Output: data/bj_entries.csv (bj_entry, bj_pages, bj_sections, bj_status, bj_index_page)
    py -3.13 -I scripts/build_bj_index.py
"""
import csv, glob, json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
snips = {}
for f in glob.glob(str(ROOT / "data" / "fts_bj_index*.json")):
    d = json.load(open(f, encoding="utf-8"))
    for k, v in d.items():
        items = v["idx"] if isinstance(v, dict) else v
        if isinstance(items, str):
            continue
        for p, t in items:
            if p and 530 <= p <= 547:
                snips[t] = p
text = " ".join(f" {t} " for t in snips)
text = re.sub(r"-\s+(?=[a-z])", "", text)          # Identifica- tion -> Identification
text = re.sub(r"Loca\s*-?\s*tion|Loca\.\s*tion", "Location", text)
ENTRY = re.compile(r"([A-Z‘'][\w‘'’&\-\.]*(?:[ \-](?:do|de|of|and|the|al|[A-Z‘'][\w‘'’&\-\.]*)){0,4})"
                   r"(?:\s*\(\s*(A)\s*\))?,\s*((?:[\d—\-–]+,\s*)*)"
                   r"([\d]+[—\-–][\d]+|\d+)\s*\(([^)]{5,300})\)")
APPX = re.compile(r"([A-Z‘'][\w‘'’&\-\.]*(?:[ \-](?:do|de|[A-Z‘'][\w‘'’&\-\.]*)){0,3})\s*\(\s*A\s*\)\s*,\s*([\d ,—\-–]+)")
rows = {}
for m in ENTRY.finditer(text):
    name, appx, rng, sec = m.group(1).strip(), m.group(2), m.group(4), m.group(5)
    if not re.search(r"Location|Identification|Sages|History", sec):
        continue
    s = sec
    status = ("attempts" if "Attempts" in s else "proposed" if re.search(r"(?<!Already )Propo\w*ed Loc", s) else
              "earlier" if "Already" in s else "located" if "Location" in s else "other")
    rows[name] = {"bj_entry": name, "bj_pages": rng.replace("—", "-").replace("–", "-"), "bj_sections": s.strip(),
                  "bj_status": status, "bj_index_page": snips.get(next((t for t in snips if name in t), ""), "")}
# second pass: every "Attempts at Identification" belongs to the nearest entry name before it
NAMEPOS = re.compile(r"([A-Z‘'][\w‘'’&\-\.]*(?:[ \-](?:do|de|of|and|[A-Z‘'][\w‘'’&\-\.]*)){0,4}),\s*(?:[\d—\-–]+,\s*)*[\d]+[—\-–]?[\d]*\s*\(")
for m in re.finditer(r"Attempts\s+at\s+Identi", text):
    before = text[max(0, m.start() - 400):m.start()]
    names = list(NAMEPOS.finditer(before))
    if not names:
        continue
    nm = names[-1]
    name = nm.group(1).strip()
    if name in rows:
        rows[name]["bj_status"] = "attempts"
        continue
    rng = re.search(r",\s*((?:[\d—\-–]+,\s*)*[\d]+[—\-–]?[\d]*)\s*\($", before[nm.start():nm.end()])
    rows[name] = {"bj_entry": name, "bj_pages": (rng.group(1) if rng else "").replace("—", "-"),
                  "bj_sections": text[m.start() - (len(before) - nm.end()):m.start() + 60].strip(),
                  "bj_status": "attempts", "bj_index_page": snips.get(next((t for t in snips if name in t), ""), "")}
for m in APPX.finditer(text):
    name = m.group(1).strip()
    if name not in rows:
        rows[name] = {"bj_entry": name, "bj_pages": m.group(2).strip(" ,"), "bj_sections": "(A)", "bj_status": "appendix",
                      "bj_index_page": snips.get(next((t for t in snips if name in t), ""), "")}
out = sorted(rows.values(), key=lambda r: r["bj_entry"])
with open(ROOT / "data" / "bj_entries.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
from collections import Counter
print(f"{len(snips)} index snippets -> {len(out)} BJ entries:", dict(Counter(r["bj_status"] for r in out)))
