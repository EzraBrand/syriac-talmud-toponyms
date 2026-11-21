# Syriac sources for Talmudic toponyms

A project to identify unidentified or disputed Babylonian toponyms of the
Babylonian Talmud with East Syriac sources.

Started 21-Nov-2026. Repository: https://github.com/EzraBrand/syriac-talmud-toponyms

## The idea

The Babylonian Talmud and the Church of the East come from the same region
(Beth Aramaye, Mesene, Khuzistan, Adiabene) and the same centuries (4th–7th c.),
and both write Eastern Aramaic. So many Talmudic place names should appear in
Syriac in near-identical spelling. Two known examples:

- Talmudic מחוזא (Meḥoza) = Syriac ܡܚܘܙܐ (Māḥōzē), the Ctesiphon / Veh-Ardashir
  conurbation.
- פומבדיתא (Pumbedita) is near Pērōz-Šābūr / Anbar, a see of the Church of the East.

Oppenheimer, *Babylonia Judaica in the Talmudic Period* (1983), leaves many places
unidentified or disputed.

## What is new here, and what is not

**Not new:** the method. Oppenheimer used Syriac evidence, much of it through
Fiey (*Assyrie chrétienne*; *Pour un Oriens Christianus Novus*, 1993), and earlier
scholars (Hoffmann 1880, Obermeyer 1929, Funk) did the same. Many matches that
this project finds will only restate their identifications.

**New (if it works):** *systematic* coverage. Every Talmudic toponym is matched
against every place in the Syriac Gazetteer (Syriaca.org) with explicit,
recorded orthographic rules, and the best candidates are checked in dated
Syriac texts (the synodal signature lists in Chabot's *Synodicon Orientale*,
the Persian Martyr Acts in Bedjan). Each match keeps its score and the rule that
fired, so a reader can see why it was proposed and reject it.

**Rule:** no identification is called new until it is checked against BJ and
Fiey. Until then a row is a *candidate*.

## Status (21-Nov-2026)

- Sources checked and recorded in [SOURCES.md](SOURCES.md). Syriac Gazetteer: all 3,485
  place records from `srophe/syriaca-data` (the old `srophe/places` repo was stale since 2014).
- **Pilot done (draft):** [notes/pilot.md](notes/pilot.md), `out/pilot_matches.csv`.
  26 toponyms + 33 controls. Result: every strong match is a **restatement** of a
  19th–20th-century identification (Neubauer, Hoffmann, Chabot, Obermeyer, Fiey, BJ).
  **Nothing new against BJ.** Six weak leads; none checked against Fiey yet.
- Main lesson: the Syriac Gazetteer covers sees and monasteries, not the villages of Beth
  Aramaye. Hoffmann's register (1880) and Chabot's tables gave the useful hits, and they are
  exactly the sources BJ already used. New evidence would need new Syriac text (OCR of
  Bedjan's Acts), not more matching.
- **Round 2:** BJ's own index marks 17 places "Attempts at Identification" (unidentified or
  disputed); list rebuilt from BJ's index (`data/bj_entries.csv`, incomplete). On those 17 the
  matcher found **one lead: Talmudic Qartu (קרתויים, Yevamot 16a) = Syriac Qarṭwāyē**, a Kurdish
  people and diocese north of Arbela (Chabot p. 423, synod of 585; Hoffmann n. 1639; Fiey POCN
  p. 66). BJ puts the Qartuans in southern Persia (Strabo's Κύρτιοι) and cites no Syriac.
  Not yet checked against Obermeyer, Neubauer and Fiey *Assyrie chrétienne* I, so **not a
  claim yet**.
- Coverage table for 166 toponyms: `out/coverage.csv`.
- BJ itself is on archive.org (lending); its "search inside" works without a loan and was
  used for the BJ check. Fiey's POCN is there too, but not yet searchable from here.

## Layout

| Path | What |
|---|---|
| `SOURCES.md` | Every source: edition, link, licence, status |
| `notes/plan.md` | Method, pilot steps, open questions |
| `scripts/` | All code (run with `py -3.13 -I`) |
| `sources/` | Downloaded data and text layers (large files not in git) |
| `data/` | Built tables (Syriac places, Talmudic toponyms) |
| `out/` | Pilot outputs: `pilot_matches.csv`, `matches_all.csv`, `matches_bj_attempts.csv`, `coverage.csv` |
| `logs/` | Logs of long jobs |
| `work/` | Page images and OCR scratch (not in git) |

## Run (in order)

```
py -3.13 -I scripts/fetch_syriaca_places.py      # Gazetteer TEI via gh api (resumable)
py -3.13 -I scripts/build_syriaca_places.py      # -> data/syriaca_places.csv
py -3.13 -I scripts/build_chabot_index.py        # -> data/chabot_places.csv
py -3.13 -I scripts/build_chabot_table.py        # -> data/chabot_table.csv
py -3.13 -I scripts/build_hoffmann_register.py   # -> data/hoffmann_register.csv
py -3.13 -I scripts/build_talmud_toponyms.py     # -> data/talmud_toponyms.csv (~12 min)
py -3.13 -I scripts/apply_overrides.py           # hand corrections, in place
py -3.13 -I scripts/match_toponyms.py --top 8    # -> out/matches_all.csv
py -3.13 -I scripts/build_pilot.py               # -> out/pilot_matches.csv
py -3.13 -I scripts/build_bj_index.py            # -> data/bj_entries.csv (needs local data/fts_bj_index*.json)
py -3.13 -I scripts/match_toponyms.py --talmud data/talmud_bj_targets.csv --out out/matches_bj_attempts.csv --top 8 --min-score 0.70
py -3.13 -I scripts/build_coverage.py            # -> out/coverage.csv
```

The text layers in `sources/*.txt` and the BJ search results (`data/fts_*.json`) were
fetched in the browser (shell downloads are blocked); see SOURCES.md.

## Licence

Code: MIT (see `LICENSE`). `data/syriaca_places.csv` is derived from the Syriac Gazetteer
(Syriaca.org), CC BY 4.0; credit Syriaca.org when you reuse it. The Chabot, Braun and Hoffmann
text layers (public domain, archive.org) are not in the repository. Raw "search inside"
snippets from Babylonia Judaica and Fiey's POCN are kept local only (in copyright); the
repository has only page numbers and short summaries of them (`data/pilot_review.csv`).
