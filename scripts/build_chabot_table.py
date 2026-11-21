"""Parse Chabot's "Table des noms de pays et de peuples" (Synodicon Orientale, pp. 665-685).

Each entry: name, Syriac form (garbled in the OCR), Arabic form, modern location, sources in
brackets ([H., p. 274] = Hoffmann, Auszüge; [N.] = Nöldeke, Tabari), then "— pages". Sees
are printed in capitals. Some entries already cite the Talmud (Mabrakta, Dasqarta de Malka).

Output: data/chabot_table.csv (chabot_entry, chabot_is_see, chabot_desc, chabot_pages,
chabot_hoffmann_ref, chabot_cites_talmud)
    py -3.13 -I scripts/build_chabot_table.py
"""
import csv, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
c = (ROOT / "sources" / "chabot_synodicon_djvu.txt").read_text(encoding="utf-8")
a = re.search(r"TABLE\s+DES\s+NOMS\s+DE\s+PAYS\s+ET\s+DE\s+PEUPLES", c).start()
b = re.search(r"TABLE\s+ANALYTIQUE\s+DES\s+MATIERES", c).start()
reg = c[a:b]
reg = re.sub(r"Digitized\s+by\s+Google", " ", reg)
reg = re.sub(r"SYNODES\s+NESTORIENS\.\s+\d+|\d{3}\s+J\.-B\.\s+CHABOT\.", " ", reg)
reg = re.sub(r"-\s*\n\s*", "", reg)          # de-hyphenate
reg = re.sub(r"\s+", " ", reg)
# an entry starts after the page list of the previous one ("— 376, 387." / "— 625.") or after "Voir X."
parts = re.split(r"(?<=[\d\)\]\.])\s+(?=(?:[A-Z][A-Za-zÀ-ÿ'’]+|[A-Z]{2,}[A-Z'’ ]*)(?:\s+(?:de|d['’]|el|al|[A-Z][A-Za-zÀ-ÿ'’\-]+)){0,4}\s?,)", reg)
rows = []
for p in parts[1:]:
    m = re.match(r"^([^,]{2,60}),\s*(.*)$", p)
    if not m:
        continue
    name, desc = m.group(1).strip(), m.group(2).strip()
    pages = ""
    pm = re.search(r"—\s*([\d\s,ion\.\*]+)\.?\s*(?:Ev[eêS]ques?|$)", desc)
    if pm:
        pages = re.sub(r"\s+", " ", pm.group(1)).strip(" ,.")
    href = "; ".join(re.findall(r"H\.,\s*p\.\s*([\diol]+)", desc))
    rows.append({
        "chabot_entry": name.title() if name.isupper() else name,
        "chabot_is_see": "yes" if name.isupper() and len(name) > 2 else "no",
        "chabot_desc": desc[:400],
        "chabot_pages": pages.replace("i", "1").replace("o", "0").replace("l", "1"),
        "chabot_hoffmann_ref": href.replace("i", "1").replace("o", "0").replace("l", "1"),
        "chabot_cites_talmud": "yes" if re.search(r"Talmud", desc) else "no",
    })
with open(ROOT / "data" / "chabot_table.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} entries; {sum(r['chabot_is_see'] == 'yes' for r in rows)} sees; "
      f"{sum(r['chabot_cites_talmud'] == 'yes' for r in rows)} cite the Talmud: "
      + ", ".join(r["chabot_entry"] for r in rows if r["chabot_cites_talmud"] == "yes"))
