"""Index the place names of Chabot's French translation (Synodicon Orientale, 1902).

The archive.org text layer (sources/chabot_synodicon_djvu.txt) has good OCR of the French and
useless OCR of the Syriac. Each scanned leaf ends with "Digitized by Google". The running heads
("SYNODES NESTORIENS. 287") give the printed page; pages between heads are interpolated.

Output: data/chabot_places.csv: one row per (form, printed page): chabot_form, chabot_page,
chabot_leaf, chabot_context ("X de <form>" signature or "<form>" after eveque/ville/pays).
    py -3.13 -I scripts/build_chabot_index.py
"""
import csv, re, sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
t = (ROOT / "sources" / "chabot_synodicon_djvu.txt").read_text(encoding="utf-8")
leaves = re.split(r"Digitized\s+by\s*\n*\s*Google", t)
pages = []
for i, lf in enumerate(leaves):
    m = re.search(r"^\s*S\w{5,6}\s+NEST\w{4,6}\.\s+(\d{1,3})\s*$", lf, re.M)
    pages.append(int(m.group(1)) if m else None)
# interpolate: page = leaf + offset, offset from the nearest known head
known = [(i, p) for i, p in enumerate(pages) if p]
def page_of(i):
    best = min(known, key=lambda k: abs(k[0] - i))
    return best[1] + (i - best[0])

PAT = re.compile(
    r"(?:\b(?:[eé6]v\.|[eé]v[eê^]*que|[eé]v[eê^]*ques|m[eé]tropolitain|ville|pays|r[eé]gion|village|si[eè]ge|province|diocese|dioc[eè]se)\s+(?:de\s+|d['’])|"
    r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,?\s+(?:[eé]v[eê^]*que\s+)?(?:de\s+|d['’]))"
    r"((?:Beit\s+|Beth\s+)?[A-Z][\w'’\-]+(?:\s+(?:de|d['’])\s+[A-Z][\w'’\-]+)?)")
rows = defaultdict(lambda: defaultdict(set))
STOP = {"Dieu", "Notre", "Christ", "Seigneur", "Jesus", "Mar", "Orient", "Rome", "Constantinople", "Pierre", "Paul"}
for i, lf in enumerate(leaves):
    flat = re.sub(r"\s+", " ", lf)
    for m in PAT.finditer(flat):
        form = m.group(1).strip(" ,.;:'’")
        if form.split()[0] in STOP or len(form) < 3:
            continue
        rows[form][page_of(i)].add(i + 1)
out = ROOT / "data" / "chabot_places.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["chabot_form", "chabot_pages", "chabot_leaves", "chabot_count"])
    for form, pg in sorted(rows.items()):
        w.writerow([form, "; ".join(str(p) for p in sorted(pg)), "; ".join(str(l) for s in pg.values() for l in sorted(s)),
                    sum(len(s) for s in pg.values())])
print(f"{len(leaves)} leaves, {len(known)} with a running head; {len(rows)} forms -> {out}")
