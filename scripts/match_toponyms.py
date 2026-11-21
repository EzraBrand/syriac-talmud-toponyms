"""Match Talmudic toponyms against Syriac Gazetteer names with explicit orthographic rules.

    py -3.13 -I scripts/match_toponyms.py [--min-score 0.72] [--top 5]
Input:  data/talmud_toponyms.csv, data/syriaca_places.csv
Output: out/matches_all.csv  (top candidates per toponym, utf-8-sig)

Both sides are reduced to one Latin consonant alphabet ("strict" form):
  Hebrew/Aramaic and Syriac letters map 1:1; Latin transliterations are reduced the same way.
Rules (each one that changes the comparison is recorded in match_rules):
  matres      internal and final א ו י ע and final ה / ܐ ܗ ܘ ܝ ܥ (and Latin vowels, ʾ ʿ) are ignored
  final       final -ין / -ܝܢ / -in / -ān plural-type ending stripped
  beth        prefix בי / בית / ܒܝܬ / Beth- / Bei- stripped from both sides
  linker      ד / ܕ / d- / de between two words ignored
  persian:X   Persian element in variant spellings normalised (shapur, ardashir, peroz, hormizd, veh)
  d=r, b=k, k=q, t=T, s=S, s=z, H=k, p=b   letter confusions (cost each)
Score = SequenceMatcher ratio of the loose forms - 0.04 per confusion used
        - 0.03 if only one side had the beth prefix; pairs whose shorter skeleton is
        under 3 consonants are dropped.
"""
import argparse, csv, re, sys, unicodedata
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent

HEB = {"ה": "h", "ב": "b", "ג": "g", "ד": "d", "ז": "z", "ח": "H", "ט": "T", "כ": "k", "ך": "k", "ל": "l", "מ": "m",
       "ם": "m", "נ": "n", "ן": "n", "ס": "s", "פ": "p", "ף": "p", "צ": "Z", "ץ": "Z", "ק": "q", "ר": "r",
       "ש": "S", "ת": "t"}
SYR = {"ܗ": "h", "ܒ": "b", "ܓ": "g", "ܔ": "g", "ܕ": "d", "ܖ": "d", "ܙ": "z", "ܚ": "H", "ܛ": "T", "ܜ": "T", "ܟ": "k",
       "ܠ": "l", "ܡ": "m", "ܢ": "n", "ܣ": "s", "ܤ": "s", "ܦ": "p", "ܧ": "p", "ܨ": "Z", "ܩ": "q", "ܪ": "r",
       "ܫ": "S", "ܬ": "t"}
SYR2HEB = {"ܐ": "א", "ܒ": "ב", "ܓ": "ג", "ܔ": "ג", "ܕ": "ד", "ܗ": "ה", "ܘ": "ו", "ܙ": "ז", "ܚ": "ח", "ܛ": "ט",
           "ܝ": "י", "ܟ": "כ", "ܠ": "ל", "ܡ": "מ", "ܢ": "נ", "ܣ": "ס", "ܤ": "ס", "ܥ": "ע", "ܦ": "פ", "ܨ": "צ",
           "ܩ": "ק", "ܪ": "ר", "ܫ": "ש", "ܬ": "ת"}
# loose classes: letter -> (class, rule name)
LOOSE = {"d": ("R", "d=r"), "r": ("R", "d=r"), "b": ("B", "b=k"), "k": ("B", "b=k"), "q": ("B", "k=q"),
         "T": ("t", "t=T"), "t": ("t", "t=T"), "S": ("s", "s=S"), "s": ("s", "s=S"), "z": ("s", "s=z"),
         "Z": ("s", "s=Z"), "H": ("H", "h=H"), "h": ("H", "h=H"), "p": ("B", "p=b"), "g": ("B", "g=k")}

PERSIAN = [  # (rule, regex on strict skeleton, canonical)
    ("persian:shapur", r"S[bp]r", "Sbr"), ("persian:shapur", r"s[bp]r$", "Sbr"),
    ("persian:ardashir", r"[rd]?rdS[rd]", "rdSr"), ("persian:ardashir", r"rdSr", "rdSr"),
    ("persian:peroz", r"^[pb]rz", "prz"), ("persian:hormizd", r"^H?rmz?d?", "Hrmz"),
]


def strip_marks(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def lat_strict(word):
    """Latin transliteration -> strict consonant skeleton."""
    s = strip_marks(word).lower()
    raw = word  # keep dot-below info from the original
    # emphatics / gutturals from the original diacritics
    raw = unicodedata.normalize("NFC", raw)
    out = []
    i = 0
    w = unicodedata.normalize("NFC", word)
    while i < len(w):
        c = w[i]
        two = strip_marks(w[i:i + 2]).lower()
        if c in "ḥḤ":
            out.append("H")
        elif c in "ṭṬ":
            out.append("T")
        elif c in "ṣṢ":
            out.append("Z")
        elif c in "šŠ":
            out.append("S")
        elif two in ("sh", "kh", "th", "ph", "tz", "ts", "gh", "dh", "ch"):
            out.append({"sh": "S", "kh": "k", "th": "t", "ph": "p", "tz": "Z", "ts": "Z", "gh": "g",
                        "dh": "d", "ch": "k"}[two])
            i += 2
            continue
        else:
            b = strip_marks(c).lower()
            out.append({"b": "b", "v": "b", "w": "", "g": "g", "d": "d", "z": "z", "k": "k", "c": "k", "q": "q",
                        "l": "l", "m": "m", "n": "n", "s": "s", "p": "p", "f": "p", "r": "r", "t": "t",
                        "x": "ks", "j": "g", "h": "h"}.get(b, ""))
        i += 1
    return "".join(out)


def script_strict(word, table):
    return "".join(table.get(c, "") for c in word)


BETH_HEB = re.compile(r"^(בית|בי|ביה)(?=[א-ת]{2})")
BETH_SYR = re.compile(r"^(ܒܝܬ|ܒܝ)(?=\S{2})")
BETH_LAT = re.compile(r"^(beth?|bet|bei|bayt|beit|bēth|bēt|bē|bit)[\s\-‑]+", re.I)


def normalise(name, beth_strip=False):
    """Return (strict skeleton, rules fired, had_beth) for one name (any script).
    With beth_strip, return the form without a Beth-/Bei- prefix, or None if it has none."""
    rules, beth = set(), False
    name = re.sub(r"\(.*?\)|\[.*?\]", " ", name).strip()
    name = re.sub(r"[֑-ׇܰ-݊̃̄̈]", "", name)  # vowel points
    script = "heb" if re.search(r"[א-ת]", name) else "syr" if re.search(r"[ܐ-ܯ]", name) else "lat"
    words = [w for w in re.split(r"[\s\-‑]+", name) if w]
    if beth_strip:
        w0 = words[0]
        if len(words) > 1 and w0 in ("בי", "בית", "ביה", "ܒܝܬ", "ܒܝ") or (script == "lat" and len(words) > 1 and BETH_LAT.match(w0 + " ")):
            words, beth = words[1:], True
        elif script == "heb" and re.match(r"^(בית|בי)[א-ת]{3}", w0):
            words, beth = [re.sub(r"^(בית|בי)", "", w0)] + words[1:], True
        elif script == "syr" and re.match(r"^ܒܝܬ\S{2}", w0):
            words, beth = [w0[3:]] + words[1:], True
        else:
            return None
    sk = []
    for w in words:
        if script == "heb":
            if w in ("ד", "דה", "דבי") or (w.startswith("ד") and len(words) > 1 and w is not words[0] and len(w) > 3):
                if w in ("ד", "דה"):
                    rules.add("linker")
                    continue
                w = w[1:]
                rules.add("linker")
            s = script_strict(w, HEB)
        elif script == "syr":
            if w.startswith("ܕ") and w is not words[0]:
                w = w[1:]
                rules.add("linker")
            s = script_strict(w, SYR)
        else:
            lw = strip_marks(w).lower()
            if lw in ("d", "de", "da", "di", "of", "the", "al", "el"):
                rules.add("linker")
                continue
            if re.match(r"^d[e]?['’]", lw):
                w = re.sub(r"^[dD][eē]?['’]", "", w)
                rules.add("linker")
            s = lat_strict(w)
        # final plural/emphatic -in / -an
        if len(s) > 3 and s.endswith("n") and script != "lat":
            pass
        sk.append(s)
    s = "".join(sk)
    for rule, pat, canon in PERSIAN:
        if re.search(pat, s) and len(s) > len(canon):
            new = re.sub(pat, canon, s, count=1)
            if new != s:  # flag only when a variant spelling was actually normalised
                rules.add(rule)
            s = new
    s = re.sub(r"(.)\1", r"\1", s)
    s = re.sub(r"h$", "", s)  # final he = emphatic/feminine ending, like final aleph
    return s, rules, beth


def variants(name):
    out = [normalise(name)]
    b = normalise(name, beth_strip=True)
    if b:
        out.append(b)
    return out


def loose(s):
    return "".join(LOOSE.get(c, (c, ""))[0] for c in s)


def compare(a, b):
    """Score two strict skeletons; return (score, confusion rules)."""
    la, lb = loose(a), loose(b)
    sm = SequenceMatcher(None, la, lb, autojunk=False)
    ratio = sm.ratio()
    conf = set()
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            x, y = a[blk.a + k], b[blk.b + k]
            if x != y:
                r1, r2 = LOOSE.get(x, ("", ""))[1], LOOSE.get(y, ("", ""))[1]
                conf.add(r1 if r1 == r2 else f"{x}={y}")
    return ratio - 0.04 * len(conf), conf


def final_variants(s):
    """Final -n (plural / -ān) optional."""
    out = {s}
    if len(s) > 3 and s.endswith("n"):
        out.add(s[:-1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-score", type=float, default=0.72)
    ap.add_argument("--top", type=int, default=5)
    a = ap.parse_args()
    tal = [r for r in csv.DictReader(open(ROOT / "data" / "talmud_toponyms.csv", encoding="utf-8-sig"))]
    syr = list(csv.DictReader(open(ROOT / "data" / "syriaca_places.csv", encoding="utf-8-sig")))
    # region: the Sasanian core (Mesopotamia, Khuzistan, Media, Adiabene, Fars) = lon 38-62, lat 24-40.
    # Places with no coordinates are kept and flagged "unknown"; places outside are dropped.
    for p in syr:
        try:
            lat, lon = float(p["syriaca_lat"]), float(p["syriaca_lon"])
            p["syriaca_in_region"] = "yes" if 38 <= lon <= 62 and 24 <= lat <= 40 else "no"
        except ValueError:
            p["syriaca_in_region"] = "unknown"
    syr = [p for p in syr if p["syriaca_in_region"] != "no"]
    # period: drop places that the Gazetteer says came into existence after 1000 CE, and
    # records whose only source is Wilmshurst's 1318-1913 survey (modern villages).
    def early(p):
        y = re.match(r"-?\d+", p.get("syriaca_exist_from") or "")
        if y and int(y.group()) > 1000:
            return False
        return p.get("syriaca_wilmshurst_only") != "yes"
    n0 = len(syr)
    syr = [p for p in syr if early(p)]
    print(f"period filter: {n0} -> {len(syr)} Gazetteer places", flush=True)
    # Chabot's sees (French translation, data/chabot_places.csv) as a second Syriac-side list
    for c in csv.DictReader(open(ROOT / "data" / "chabot_places.csv", encoding="utf-8-sig")):
        syr.append({"syriaca_id": f"chabot:{c['chabot_form']}", "syriaca_uri": "", "syriaca_headword": c["chabot_form"],
                    "syriaca_names_syr": "", "syriaca_names_other": f"fr:{c['chabot_form']}", "syriaca_type": "chabot-form",
                    "syriaca_lat": "", "syriaca_lon": "", "syriaca_abstract": f"Chabot, Synodicon Orientale, pp. {c['chabot_pages']}",
                    "syriaca_in_region": "unknown"})
    # Hoffmann 1880 register (persons and places mixed; spirant h removed)
    for c in csv.DictReader(open(ROOT / "data" / "hoffmann_register.csv", encoding="utf-8-sig")):
        syr.append({"syriaca_id": f"hoffmann:{c['hoffmann_form_clean']}", "syriaca_uri": "", "syriaca_headword": c["hoffmann_form"],
                    "syriaca_names_syr": "", "syriaca_names_other": f"de:{c['hoffmann_form_clean']}", "syriaca_type": "hoffmann-register",
                    "syriaca_lat": "", "syriaca_lon": "",
                    "syriaca_abstract": f"Hoffmann, Auszüge (1880), pp. {c['hoffmann_pages']}" + (f"; nn. {c['hoffmann_notes']}" if c["hoffmann_notes"] else ""),
                    "syriaca_in_region": "unknown"})
    # every name of every place, normalised once
    snames = []
    for p in syr:
        names = [n for n in p["syriaca_names_syr"].split(" | ") if n]
        names += [n.split(":", 1)[1] for n in p["syriaca_names_other"].split(" | ") if n.startswith(("en", "fr", "de", "la"))]
        seen = set()
        for n in names:
            for s, rules, beth in variants(n):
                if len(s) < 3 or (s, beth) in seen:
                    continue
                seen.add((s, beth))
                snames.append((p, n, s, rules, beth))
    print(f"{len(tal)} Talmudic toponyms; {len(snames)} Syriac-side name forms", flush=True)
    rows = []
    for i, t in enumerate(tal, 1):
        forms = [f for f in [t["talmud_form_he"]] + [x.rsplit(" (", 1)[0] for x in t["talmud_other_forms"].split("; ") if x] if f]
        forms.append(t["talmud_name_en"])  # the English form is a transliteration too
        tn = []
        for f in dict.fromkeys(forms):
            for s, rules, beth in variants(f):
                if len(s) >= 3:
                    tn.append((f, s, rules, beth))
        best = {}
        for f, ts, trules, tbeth in tn:
            for p, n, ss, srules, sbeth in snames:
                if abs(len(ts) - len(ss)) > 3:
                    continue
                for v1 in final_variants(ts):
                    for v2 in final_variants(ss):
                        sc, conf = compare(v1, v2)
                        rules = set(conf) | trules | srules
                        if v1 != ts or v2 != ss:
                            rules.add("final")
                            sc -= 0.02
                        if tbeth or sbeth:
                            rules.add("beth")
                            if tbeth != sbeth:
                                sc -= 0.03  # one side keeps a Beth- the other side lacks
                        if f != t["talmud_name_en"] and re.search(r"[ܐ-ܯ]", n):
                            rules.add("script:aram-syr")
                        if min(len(v1), len(v2)) == 3 and not (tbeth and sbeth):  # Beth- on both sides = longer match
                            sc -= 0.05  # three consonants match by chance too easily
                            rules.add("short")
                        key = p["syriaca_id"]
                        if sc >= a.min_score and (key not in best or sc > best[key][0]):
                            best[key] = (sc, f, ts, n, ss, sorted(rules), p)
        ranked = sorted(best.values(), key=lambda x: -x[0])
        for rank, (sc, f, ts, n, ss, rules, p) in enumerate(ranked[: a.top], 1):
            rows.append({
                "talmud_name_en": t["talmud_name_en"], "talmud_group": t["talmud_group"],
                "talmud_form_he": t["talmud_form_he"], "talmud_refs": t["talmud_refs"],
                "match_talmud_form": f, "match_talmud_skeleton": ts,
                "syriaca_id": p["syriaca_id"], "syriaca_uri": p["syriaca_uri"], "syriaca_headword": p["syriaca_headword"],
                "syriaca_matched_name": n, "match_syriaca_skeleton": ss,
                "syriaca_names_syr": p["syriaca_names_syr"], "syriaca_type": p["syriaca_type"],
                "syriaca_lat": p["syriaca_lat"], "syriaca_lon": p["syriaca_lon"],
                "syriaca_abstract": p["syriaca_abstract"][:200],
                "syriaca_in_region": p["syriaca_in_region"],
                "match_score": round(sc, 3), "match_rules": "; ".join(rules), "match_rank": rank,
                # how many distinct places score within 0.02 of this one: high = weak evidence
                "match_ambiguity": sum(1 for x in ranked if x[0] >= sc - 0.02),
            })
        if i % 20 == 0:
            print(f"{i}/{len(tal)}", flush=True)
    out = ROOT / "out" / "matches_all.csv"
    with open(out, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out}: {len(rows)} rows for {len({r['talmud_name_en'] for r in rows})} toponyms")


if __name__ == "__main__":
    main()
