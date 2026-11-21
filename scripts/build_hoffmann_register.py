"""Parse the name register of Hoffmann, Auszüge aus syrischen Akten persischer Märtyrer (1880).

Source: sources/hoffmann_auszuege_djvu.txt (archive.org auszgeaussyris00hoff, Toronto copy).
The register (printed pp. 298 ff.) mixes persons and places. Each entry is "Name  page page n note".
Numbers after "n" are note numbers, the others are pages.

Output: data/hoffmann_register.csv (hoffmann_form, hoffmann_pages, hoffmann_notes)
    py -3.13 -I scripts/build_hoffmann_register.py
"""
import csv, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
t = (ROOT / "sources" / "hoffmann_auszuege_djvu.txt").read_text(encoding="utf-8")
start = t.index("Die  mit  n   vers")
reg = t[start:]
rows = []
buf = ""
for line in reg.splitlines():
    line = line.strip()
    if not line or re.fullmatch(r"\d{3}", line):
        continue
    # continuation lines start with a number or "n 123"
    if buf and re.match(r"^(\d|n\s+\d|f\b|ff\b)", line):
        buf += " " + line
        continue
    if buf:
        rows.append(buf)
    buf = line
if buf:
    rows.append(buf)
PERSON = re.compile(r",\s*(?:B|M|P|A|D|Diakon|Bischof|König|Märtyrer|Mönch|Patriarch|Katholikos|Schreiber|Sohn|Tochter|Apostel|Manichäer|Notar|Feldherr|Magier|Mobedh|Mohpat)\b"
                    r"|\b(?:Sohn|Tochter|bin|bar|ibn|Mar|Mär|Rabban|Mart|König|Märtyrer|Apostel|Schule des|Coenobium des|Kloster des|Congregation des)\b|^(?:H\.|St\.)\s")
PLACE = re.compile(r"\b(?:Dair|Daira|Dairä|Kloster|Coenobium|Berg|Dorf|Fluss|Gabal|Öebel|Nahr|Tell|Tel|Ribät|Wädl|Wädi|Qasr|Kark\S*|Bet\S*|Beth|B[eä]th?|Mahoz\S*|Aqra|Akra|'Ain|Ain|Dast\S*|Karh|See|Insel|Provinz|Stadt|Burg|Brücke)\b"
                   r"|(?:äbädh?|äbäd|gerd|kert|qart|gird|än|ene|ija|Tja|stän|istän)$|^al-|^el-|^ed-")


def kind(name):
    """person / place / unknown, from the register wording only (Hoffmann marks B. = Bischof etc.)."""
    if PERSON.search(name):
        return "person" if not PLACE.search(name) or re.search(r",\s*(?:B|M|P|A)\b", name) else "unknown"
    if PLACE.search(name):
        return "place"
    return "unknown"


out = []
for r in rows:
    m = re.match(r"^(.*?[^\d\s])\s+((?:\d|n\s*\d|[hU]\s+\d).*)$", r)
    if not m:
        continue
    name, refs = m.group(1).strip(" ,.:;"), m.group(2)
    if len(name) < 3 or not re.search(r"[A-Za-zÄÖÜäöü]", name):
        continue
    notes = re.findall(r"\b[nhU]\s*(\d{2,4}a?)", refs)
    pages = re.findall(r"(?<![nhU\d]\s)(?<![nhU\d])\b(\d{1,3})\b(?!\d)", re.sub(r"\b[nhU]\s*\d{2,4}a?", " ", refs))
    # Hoffmann marks spirants as bh gh dh kh ph th; the OCR often gives l' or '' for the h.
    clean = re.sub(r"(?<=[bgdkptBGDKPT])(?:l'|l’|''|'|h)", "", name)
    clean = re.sub(r"\(.*?\)|\[|\]|\?", "", clean).strip()
    out.append({"hoffmann_form": name, "hoffmann_form_clean": clean, "hoffmann_kind": kind(name),
                "hoffmann_pages": "; ".join(dict.fromkeys(pages)),
                "hoffmann_notes": "; ".join(dict.fromkeys(notes))})
with open(ROOT / "data" / "hoffmann_register.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["hoffmann_form", "hoffmann_form_clean", "hoffmann_kind", "hoffmann_pages", "hoffmann_notes"])
    w.writeheader()
    w.writerows(out)
print(f"{len(out)} register entries")
