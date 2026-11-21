"""Build the Talmudic (Babylonian) toponym list with Aramaic spellings.

Input (not re-derived; from the owner's earlier projects):
  - data/talmud_babylonian_selection.csv: English forms from the talmud-nlp-indexer toponym
    gazetteer (talmud-names-discovery/data/talmud_toponyms_gazetteer.txt) that are Babylonian
    or Persian-Empire places, picked by hand, with a `talmud_group` (pilot / control).
  - talmud-names-discovery/alma/alma_places.csv: Alma map places with coordinates.
  - talmud-names-discovery/sefaria/*_{en,he}.json: William Davidson English + Aramaic, aligned
    segment by segment.

For each English form: find every Bavli segment whose English has the form (whole words),
then in the parallel Aramaic segment choose the word (or two-word span) whose consonant
skeleton is closest to the English skeleton. The most frequent choice is the Aramaic form.

Output: data/talmud_toponyms.csv (utf-8-sig)
    py -3.13 -I scripts/build_talmud_toponyms.py
"""
import csv, json, re, sys, unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
TND = ROOT.parent / "talmud-names-discovery"
SEF = TND / "sefaria"
NIKUD = re.compile(r"[֑-ׇ]")
PREFIX = "ובדשלמכה"
H2L = {"ב": "b", "ג": "g", "ד": "d", "ז": "z", "ט": "t", "כ": "k", "ך": "k", "ל": "l", "מ": "m",
       "ם": "m", "נ": "n", "ן": "n", "ס": "s", "פ": "p", "ף": "p", "צ": "z", "ץ": "z", "ק": "k",
       "ר": "r", "ש": "s", "ת": "t"}   # א ה ו ח י ע dropped on both sides


def heb_skel(w):
    s = "".join(H2L.get(c, "") for c in w)
    return re.sub(r"(.)\1", r"\1", s)


def lat_skel(name):
    s = unicodedata.normalize("NFKD", name.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"^(the|river|bridge of|fortress( of)?|city of|valley of|village of)\s+", "", s)
    s = re.sub(r"\s+river$", "", s)
    for a, b in (("tz", "z"), ("ts", "z"), ("sh", "s"), ("kh", "k"), ("ch", "k"), ("ph", "p"),
                 ("th", "t"), ("c", "k"), ("q", "k"), ("f", "p"), ("v", "b"), ("w", "b"), ("x", "ks")):
        s = s.replace(a, b)
    s = re.sub(r"[^bdgklmnprstz]", "", s)
    return re.sub(r"(.)\1", r"\1", s)


def heb_tokens(s):
    s = NIKUD.sub("", re.sub(r"<[^>]+>", " ", s or "")).replace("״", "").replace('"', "")
    return re.findall(r"[א-ת׳']+", s)


def unprefix(tok, target):
    """Drop up to two proclitic letters if that brings the skeleton closer."""
    best = tok
    for k in (1, 2):
        if len(tok) - k >= 2 and all(c in PREFIX for c in tok[:k]):
            cand = tok[k:]
            if SequenceMatcher(None, heb_skel(cand), target).ratio() > SequenceMatcher(None, heb_skel(best), target).ratio():
                best = cand
    return best


def clean_en(s):
    return re.sub(r"<[^>]+>", "", s or "")


def main():
    sel = list(csv.DictReader(open(ROOT / "data" / "talmud_babylonian_selection.csv", encoding="utf-8-sig")))
    alma = {r["alma_place_english"]: r for r in csv.DictReader(open(TND / "alma" / "alma_places.csv", encoding="utf-8-sig"))}
    segs = []  # (ref, en, he)
    for fe in sorted(SEF.glob("*_en.json")):
        tr = fe.name[:-8]
        fh = SEF / f"{tr}_he.json"
        en = json.loads(fe.read_text(encoding="utf-8"))["text"]
        he = json.loads(fh.read_text(encoding="utf-8"))["text"]
        for i, (ae, ah) in enumerate(zip(en, he)):
            for j, (se, sh) in enumerate(zip(ae or [], ah or [])):
                segs.append((f"{tr.replace('_', ' ')} {i // 2 + 1}{'ab'[i % 2]}:{j + 1}", clean_en(se), sh))
    print(f"{len(segs)} segments", flush=True)
    rows = []
    for n, r in enumerate(sel, 1):
        name = r["talmud_name_en"]
        pat = re.compile(r"(?<![\w’'])" + re.escape(name) + r"(?![\w’'])")
        target = lat_skel(name)
        nwords = len(lat_skel_words := [w for w in re.split(r"\s+", name) if lat_skel(w)])
        forms, refs = Counter(), defaultdict(list)
        hits = 0
        for ref, en, he in segs:
            if not pat.search(en):
                continue
            hits += 1
            toks = heb_tokens(he)
            best, bs = None, 0.0
            for L in sorted({max(1, nwords), max(1, nwords) + 1, max(1, nwords - 1)}):
                for k in range(len(toks) - L + 1):
                    span = toks[k:k + L]
                    span = [unprefix(span[0], target)] + span[1:]
                    sk = heb_skel("".join(span))
                    sc = SequenceMatcher(None, sk, target).ratio()
                    if sc > bs:
                        best, bs = " ".join(span), sc
            if best and bs >= 0.6:
                forms[best] += 1
                if len(refs[best]) < 5:
                    refs[best].append(ref)
        top = forms.most_common(3)
        a = alma.get(r.get("alma_match") or name, {})
        rows.append({
            "talmud_name_en": name,
            "talmud_group": r["talmud_group"],
            "talmud_note": r.get("talmud_note", ""),
            "talmud_form_he": top[0][0] if top else "",
            "talmud_form_count": top[0][1] if top else 0,
            "talmud_other_forms": "; ".join(f"{f} ({c})" for f, c in top[1:]),
            "talmud_segments_with_en": hits,
            "talmud_refs": "; ".join(refs[top[0][0]]) if top else "",
            "talmud_alma_lon": a.get("alma_longitude", ""),
            "talmud_alma_lat": a.get("alma_latitude", ""),
        })
        if n % 10 == 0:
            print(f"{n}/{len(sel)}", flush=True)
    out = ROOT / "data" / "talmud_toponyms.csv"
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows; {sum(1 for x in rows if not x['talmud_form_he'])} without Aramaic form)")


if __name__ == "__main__":
    main()
