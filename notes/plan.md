# Plan (updated 21-Nov-2026, after the pilot)

## Pilot steps: status

1. **Syriac place table** — done. `data/syriaca_places.csv` from the Gazetteer TEI
   (id, Syriac names, other names, coordinates, type, existence dates, bibliography).
   Fiey column is empty: no Gazetteer record cites Fiey. Added two more Syriac-side lists:
   Chabot (French forms + his place table) and Hoffmann's register.
2. **Talmudic toponym list** — done for 149 hand-picked Babylonian / Persian forms from the
   talmud-nlp-indexer gazetteer, with Aramaic forms from the Sefaria alignment. The BJ list
   of unidentified places could not be downloaded (BJ is a lending scan); instead each
   toponym's BJ entry and verdict were found with BJ's "search inside".
3. **Matching** — done; rules and costs in `scripts/match_toponyms.py`. Controls: top-1 right
   for 13 of 33, top-8 for 17 of 33.
4. **Attestation** — partly done: page references from Chabot's French translation, his place
   table, Hoffmann and POCN. Syriac spellings on Chabot's page images not yet checked (Kraken
   crashed: laptop out of memory). Bedjan not needed for any surviving candidate.
5. **Output** — `out/pilot_matches.csv`, `notes/pilot.md`.

## Round 2 (same day)

- BJ's index gives BJ's own statuses; 17 "Attempts at Identification" entries were matched.
  One lead: Qartu = Syriac Qarṭwāyē (see notes/pilot.md). Coverage table `out/coverage.csv`.

## Main finding

All strong matches restate known identifications. The useful Syriac evidence for Talmudic
places (Hoffmann 1880, Chabot 1902, Fiey 1967) was already used by Obermeyer and BJ. The
open BJ entries got no Syriac candidates.

## Options for the next step (owner to decide)

A. **Scale the matching** to all 662 gazetteer toponyms + Talmudic toponyms not on the list.
   Cheap, but the pilot says it will mostly restate.
B. **New Syriac text first**: OCR Bedjan *AMS* II, IV (Persian martyrs) and the Chronicle of
   Seert / Guidi's chronicle with Kraken (East Syriac model fits Bedjan), extract place names
   from the Syriac itself (patterns like ܩܪܝܬܐ ܕ… "village of", ܡܕܝܢܬܐ, ܒܝܬ …), and match those
   against the open BJ entries. This is where something new could appear. Roughly 700 pages
   per volume at ~1 page/min/worker (to be timed), in the background, resumable.
C. **Finish the checks**: the Qartu lead (Obermeyer p. 133, Fiey *AC* I),
   a complete BJ index (a one-hour loan would do it), BJ verdicts for Diskarta and Papuniya,
   Fiey *Assyrie chrétienne* III (lending only).

## Open questions

- Can the owner get Fiey, *Assyrie chrétienne* III, and Fiey, *Sumer* 23 (1967)?
- Should non-Babylonian Persian-Empire places (Media, Khuzistan, Adiabene) stay in scope?
