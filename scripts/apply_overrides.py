"""Apply hand corrections to data/talmud_toponyms.csv (in place) and strip a leading ו.

    py -3.13 -I scripts/apply_overrides.py
Every corrected row gets talmud_form_source = "manual" (else "sefaria-alignment") and the
reason in talmud_note. Rows with no region in the overrides get talmud_region = "Babylonia".
"""
import csv, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "data" / "talmud_toponyms.csv"
rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
ov = {r["talmud_name_en"]: r for r in csv.DictReader(open(ROOT / "data" / "talmud_form_overrides.csv", encoding="utf-8-sig"))}
n = 0
for r in rows:
    r.setdefault("talmud_form_source", "sefaria-alignment")
    if r.get("talmud_form_source") in (None, ""):
        r["talmud_form_source"] = "sefaria-alignment"
    f = r["talmud_form_he"]
    if re.match(r"^ו[א-ת]{3,}", f):
        r["talmud_form_he"] = f[1:]
        r["talmud_note"] = (r["talmud_note"] + "; " if r["talmud_note"] else "") + "leading ו stripped"
    o = ov.get(r["talmud_name_en"])
    r["talmud_region"] = (o or {}).get("talmud_region") or "Babylonia"
    if o:
        if o["talmud_form_he"]:
            r["talmud_form_he"] = o["talmud_form_he"]
            r["talmud_form_source"] = "manual"
            n += 1
        if o["talmud_note"]:
            r["talmud_note"] = o["talmud_note"]
fields = list(rows[0])
with open(p, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(f"{n} forms corrected by hand; {len(rows)} rows")
