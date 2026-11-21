"""One row per Talmudic toponym: its Babylonia Judaica entry and status, and its best Syriac candidate.

Inputs: data/talmud_toponyms.csv, data/talmud_bj_targets.csv (BJ "Attempts" entries),
data/fts_bj_heads.json (BJ headings found by searching the Hebrew form; local only),
data/bj_entries.csv (BJ index statuses), out/matches_all.csv, out/matches_bj_attempts.csv,
data/pilot_review.csv, data/bj_attempts_review.csv (manual verdicts).
Output: out/coverage.csv (utf-8-sig)
    py -3.13 -I scripts/build_coverage.py
"""
import csv, json, re, sys, unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent


def rd(p):
    p = ROOT / p
    return list(csv.DictReader(open(p, encoding="utf-8-sig"))) if p.exists() else []


def key(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z]", "", s.replace("&", "s"))
    for a, b in (("kh", "k"), ("sh", "s"), ("tz", "s"), ("ts", "s"), ("v", "b"), ("w", "b"), ("q", "k"), ("ei", "e")):
        s = s.replace(a, b)
    s = re.sub(r"[aeiouy]", "", s)
    return re.sub(r"(.)\1", r"\1", s)


heads = json.load(open(ROOT / "data" / "fts_bj_heads.json", encoding="utf-8")) if (ROOT / "data" / "fts_bj_heads.json").exists() else {}
bj = {key(r["bj_entry"]): r for r in rd("data/bj_entries.csv")}
top = {}
for r in rd("out/matches_all.csv") + rd("out/matches_bj_attempts.csv"):
    if r["match_rank"] == "1":
        top[r["talmud_name_en"]] = r
review = {r["talmud_name_en"]: r for r in rd("data/pilot_review.csv")}
review.update({r["bj_entry"]: {**r, "match_bj_entry": r["bj_entry"], "match_bj_pages": r["bj_pages"]} for r in rd("data/bj_attempts_review.csv")})
rows = []
for t in rd("data/talmud_toponyms.csv") + rd("data/talmud_bj_targets.csv"):
    n = t["talmud_name_en"]
    rv = review.get(n, {})
    head = rv.get("match_bj_entry") or next((h for p, h in heads.get(n, {}).get("heads", []) if len(h) > 2 and h[0].isupper() and " " not in h.strip() or h.startswith(("Be ", "Nohar", "Harta", "Porat", "Pum", "Mata"))), "")
    if t["talmud_group"] == "bj-attempts":
        head = n
    b = bj.get(key(head)) or bj.get(key(n)) or {}
    m = top.get(n, {})
    rows.append({
        "talmud_name_en": n, "talmud_form_he": t["talmud_form_he"], "talmud_group": t["talmud_group"],
        "talmud_region": t.get("talmud_region", ""), "talmud_refs": t["talmud_refs"],
        "match_bj_entry": head or b.get("bj_entry", ""), "match_bj_pages": rv.get("match_bj_pages") or b.get("bj_pages", "") or t.get("talmud_bj_pages", ""),
        "match_bj_status": b.get("bj_status", "attempts" if t["talmud_group"] == "bj-attempts" else ""),
        "syriaca_top_candidate": m.get("syriaca_headword", ""), "syriaca_top_id": m.get("syriaca_id", ""),
        "match_top_score": m.get("match_score", ""), "match_top_rules": m.get("match_rules", ""),
        "match_reviewed_status": rv.get("match_status", ""), "match_note": rv.get("match_note", ""),
    })
with open(ROOT / "out" / "coverage.csv", "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
from collections import Counter
print(f"{len(rows)} rows; BJ entry found for {sum(1 for r in rows if r['match_bj_entry'])}; "
      f"BJ status: {dict(Counter(r['match_bj_status'] for r in rows))}; reviewed: {dict(Counter(r['match_reviewed_status'] for r in rows if r['match_reviewed_status']))}")
