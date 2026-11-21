"""Parse Chabot's "Table des noms de pays et de peuples" (Synodicon Orientale, pp. 665-685).

Each entry: name, Syriac form (garbled in the OCR), Arabic form, modern location, sources in
brackets ([H., p. 274] = Hoffmann, Auszüge; [N.] = Nöldeke, Tabari; [M.] = Marquart,
Ērānšahr), then "— pages", then the list of bishops with dates. Sees are printed in capitals.
Some entries already cite the Talmud (Mabrakta, Dasqarta de Malka).

Line-based parse: an entry starts on a line that begins with a capitalised name followed by
",", "." or "(" and that is not a bishop line ("Yohannan (544).").

Output: data/chabot_table.csv (chabot_entry, chabot_is_see, chabot_desc, chabot_pages,
chabot_hoffmann_ref, chabot_bishop_dates, chabot_cites_talmud)
    py -3.13 -I scripts/build_chabot_table.py
"""
import csv, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
c = (ROOT / "sources" / "chabot_synodicon_djvu.txt").read_text(encoding="utf-8")
a = re.search(r"TABLE\s+DES\s+NOMS\s+DE\s+PAYS\s+ET\s+DE\s+PEUPLES", c).end()
b = re.search(r"TABLE\s+ANALYTIQUE\s+DES\s+MATIERES", c).start()
reg = c[a:b]
reg = reg[reg.index("sujet"):]  # skip the preface
lines = [re.sub(r"[ \t]+", " ", l).strip() for l in reg.splitlines()]
NOISE = re.compile(r"^(Digitized by|Google|SYNODES NESTORIENS|\d{3} J\.-B\. CHABOT|[A-Z\. ]{1,12}$|E\S{0,3}v\S{0,3}ques?\s*:?$|\S{1,3}$)")
START = re.compile(r"^(?:\d?['’1]?[A-ZÉ][\w'’\-]*|Beit|Kabka|Kamka)(?:\s+(?:de|d['’]|el|ou|des|[A-ZÉ][\w'’\-]*|[a-z]{1,3}\b)){0,5}\s*(?:,|\.|\(|—|;)")
BISHOP = re.compile(r"^[A-ZÉ][\w'’\-\. ]{1,30}\s*\(\s*[\do]{3}\s*\)\s*[\.\?;,]*\s*$|\(\s*[\dio]{3}\s*\)\s*\.\s*$")
entries, cur = [], None
for l in lines:
    if not l or NOISE.match(l):
        continue
    if START.match(l) and not BISHOP.search(l) and not l.startswith(("Voir", "Eveque", "Ev")):
        if cur:
            entries.append(cur)
        cur = [l]
    elif cur is not None:
        cur.append(l)
if cur:
    entries.append(cur)


def num(s):
    return s.replace("i", "1").replace("o", "0").replace("l", "1").replace("a", "2").replace("S", "5")


rows = []
for e in entries:
    text = re.sub(r"-\s+(?=[a-zé])", "", " ".join(e))
    m = re.match(r"^(.*?)\s*(?:,|\.|\(|—|;)", text)
    name = m.group(1).strip() if m else text[:30]
    pages = ""
    pm = re.search(r"—\s*([\dioa\*S ,n\.]+?)\s*\.?\s*(?:Ev\S*ques?|Voir|$)", text)
    if pm:
        pages = num(re.sub(r"\s+", " ", pm.group(1)).strip(" ,."))
    rows.append({
        "chabot_entry": name.title() if name.isupper() and len(name) > 3 else name,
        "chabot_is_see": "yes" if re.sub(r"[^A-Za-z]", "", name).isupper() and len(name) > 3 else "no",
        "chabot_desc": text[:600],
        "chabot_pages": pages,
        "chabot_hoffmann_ref": "; ".join(num(x) for x in re.findall(r"H\.\s*,\s*p\.\s*([\dioa\- ]+)", text)),
        "chabot_bishop_dates": "; ".join(num(x) for x in re.findall(r"\(\s*([\dio]{3})\s*\)", text)),
        "chabot_cites_talmud": "yes" if "Talmud" in text else "no",
    })
with open(ROOT / "data" / "chabot_table.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} entries; {sum(r['chabot_is_see'] == 'yes' for r in rows)} sees (capitals); "
      f"{sum(1 for r in rows if r['chabot_hoffmann_ref'])} cite Hoffmann; "
      f"cite the Talmud: " + ", ".join(r["chabot_entry"] for r in rows if r["chabot_cites_talmud"] == "yes"))
