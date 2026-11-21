"""Assemble the pilot table out/pilot_matches.csv (utf-8-sig).

Joins data/pilot_selection.csv (which candidate per toponym), data/talmud_toponyms.csv,
out/matches_all.csv (score and rules of that candidate), data/pilot_review.csv (manual check
against BJ, Hoffmann, Chabot) and data/attestations.csv (Syriac forms read on page images).
The control toponyms (known identifications) are added with their top match, for calibration.
    py -3.13 -I scripts/build_pilot.py
"""
import csv, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent


def rd(p):
    p = ROOT / p
    return list(csv.DictReader(open(p, encoding="utf-8-sig"))) if p.exists() else []


tal = {r["talmud_name_en"]: r for r in rd("data/talmud_toponyms.csv")}
matches = rd("out/matches_all.csv")
review = {r["talmud_name_en"]: r for r in rd("data/pilot_review.csv")}
att = {r["talmud_name_en"]: r for r in rd("data/attestations.csv")}
rows = []


def base(n):
    t = tal[n]
    return {"talmud_name_en": n, "talmud_form_he": t["talmud_form_he"], "talmud_form_source": t.get("talmud_form_source", ""),
            "talmud_region": t.get("talmud_region", ""), "talmud_refs": t["talmud_refs"], "talmud_group": t["talmud_group"]}


sys.path.insert(0, str(ROOT / "scripts"))
from match_toponyms import variants, compare  # noqa: E402


def hand_score(n, form):
    """Score a hand-picked candidate with the matcher's own rules (no short/beth penalties)."""
    best = None
    for tf in (tal[n]["talmud_form_he"], n):
        for ts, tr, _ in variants(tf):
            for ss, sr, _ in variants(form):
                if len(ts) < 2 or len(ss) < 2:
                    continue
                sc, conf = compare(ts, ss)
                if not best or sc > best[0]:
                    best = (sc, sorted(set(conf) | tr | sr))
    return best


for s in rd("data/pilot_selection.csv"):
    n = s["talmud_name_en"]
    m = next((x for x in matches if x["talmud_name_en"] == n and x["syriaca_id"] == s["candidate_id"]), None)
    if not m and s["candidate_id"]:
        hs = hand_score(n, s["candidate_id"].split(":", 1)[-1])
        if hs:
            m = {"syriaca_matched_name": s["candidate_id"].split(":", 1)[-1], "syriaca_names_syr": "", "syriaca_uri": "",
                 "syriaca_lat": "", "syriaca_lon": "", "match_score": round(hs[0], 3),
                 "match_rules": "; ".join(hs[1] + ["hand-scored"]), "match_rank": "", "match_ambiguity": ""}
    rv, a = review.get(n, {}), att.get(n, {})
    rows.append({**base(n),
        "syriaca_source": s["candidate_source"], "syriaca_id": s["candidate_id"], "syriaca_name": s["candidate_name"],
        "syriaca_matched_form": m["syriaca_matched_name"] if m else "", "syriaca_names_syr": m["syriaca_names_syr"] if m else "",
        "syriaca_uri": m["syriaca_uri"] if m else "", "syriaca_lat": m["syriaca_lat"] if m else "", "syriaca_lon": m["syriaca_lon"] if m else "",
        "match_score": m["match_score"] if m else "", "match_rules": m["match_rules"] if m else "",
        "match_rank": m["match_rank"] if m else "", "match_ambiguity": m["match_ambiguity"] if m else "",
        "match_selected_by": "" if not s["candidate_id"] else "matcher" if m and m["match_rank"] == "1" else
                             "matcher, picked from top 8" if m and m["match_rank"] else "hand (matcher missed it)",
        "match_status": rv.get("match_status", ""), "match_bj_entry": rv.get("match_bj_entry", ""),
        "match_bj_pages": rv.get("match_bj_pages", ""), "match_bj_view": rv.get("match_bj_view", ""),
        "match_prior_art": rv.get("match_prior_art", ""),
        "attest_source": a.get("attest_source") or rv.get("attest_source", ""), "attest_ref": a.get("attest_ref") or rv.get("attest_ref", ""),
        "attest_syriac_form": a.get("attest_syriac_form", ""), "attest_how_checked": a.get("attest_how_checked", ""),
        "match_note": rv.get("match_note", "")})

for n, t in tal.items():
    if t["talmud_group"] != "control":
        continue
    m = next((x for x in matches if x["talmud_name_en"] == n and x["match_rank"] == "1"), None)
    rows.append({**base(n), "syriaca_source": ("chabot" if m and m["syriaca_id"].startswith("chabot:") else "hoffmann" if m and m["syriaca_id"].startswith("hoffmann:") else "syriaca") if m else "",
        "syriaca_id": m["syriaca_id"] if m else "", "syriaca_name": m["syriaca_headword"] if m else "",
        "syriaca_matched_form": m["syriaca_matched_name"] if m else "", "syriaca_names_syr": m["syriaca_names_syr"] if m else "",
        "syriaca_uri": m["syriaca_uri"] if m else "", "syriaca_lat": m["syriaca_lat"] if m else "", "syriaca_lon": m["syriaca_lon"] if m else "",
        "match_score": m["match_score"] if m else "", "match_rules": m["match_rules"] if m else "", "match_rank": "1" if m else "",
        "match_ambiguity": m["match_ambiguity"] if m else "", "match_selected_by": "matcher (control: top match, not reviewed)" if m else "",
        "match_status": "control", "match_bj_entry": "", "match_bj_pages": "", "match_bj_view": "", "match_prior_art": "",
        "attest_source": "", "attest_ref": "", "attest_syriac_form": "", "attest_how_checked": "", "match_note": ""})

out = ROOT / "out" / "pilot_matches.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
from collections import Counter
print(f"wrote {out}: {len(rows)} rows;", dict(Counter(r["match_status"] for r in rows)))
