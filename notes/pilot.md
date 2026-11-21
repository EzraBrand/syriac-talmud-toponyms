# Pilot (21-Nov-2026)

Output: `out/pilot_matches.csv` (59 rows: 26 pilot toponyms + 33 controls; utf-8-sig;
columns `talmud_*`, `syriaca_*`, `attest_*`, `match_*`). Full candidate list:
`out/matches_all.csv` (top 8 per toponym, 140 toponyms).

## What was done

1. **Syriac side, three lists.**
   - Syriac Gazetteer: 3,485 TEI records → `data/syriaca_places.csv` (954 with Syriac
     names, 926 with coordinates). Kept for matching: places in the Sasanian core
     (lon 38–62°, lat 24–40°) or with no coordinates, and not later than 1000 CE, and not
     sourced only from Wilmshurst's 1318–1913 survey: 1,181 places.
   - Chabot, *Synodicon Orientale*: place forms from the French translation (498 forms
     with page numbers, `data/chabot_places.csv`) and Chabot's own place table, pp. 665–685
     (`data/chabot_table.csv`, parse is partial: 131 entries).
   - Hoffmann, *Auszüge* (1880): the name register, 2,324 entries with pages
     (`data/hoffmann_register.csv`). Persons and places are mixed in it.
2. **Talmudic side.** 149 Babylonian (and Median / Khuzistani) English forms picked by hand
   from the talmud-nlp-indexer toponym gazetteer; Aramaic form of each read from the
   Sefaria William Davidson text by English–Aramaic segment alignment
   (`data/talmud_toponyms.csv`; 8 forms corrected by hand, `data/talmud_form_overrides.csv`).
   Only 31 places east of 40° E have coordinates in the owner's Alma map, so most Babylonian
   toponyms have none.
3. **Matching** (`scripts/match_toponyms.py`): one consonant skeleton for Hebrew, Syriac and
   Latin transliterations; matres lectionis and final ה/א ignored; Beth-/בי prefix,
   linker ד/d-, final -n, and Persian elements handled as rules; letter confusions
   (d=r, b=k, k=q, t=T, s=S, s=z, h=H, p=b, g=k) cost 0.04 each; three-consonant names
   cost 0.05. Every rule that fired is in `match_rules`.
4. **Check against BJ.** Babylonia Judaica is on archive.org as a lending scan. Its
   "search inside" gives snippets with page numbers without a loan; that was used to find
   each BJ entry and BJ's verdict (`data/fts_bj_*.json`). Fiey's POCN is also there; its search works
   when it is called from the item's own archive.org page (`data/fts_pocn.json`). POCN
   covers sees only: it confirms Dasqarta d'Malka (Sasanian residence on the Diyala, about
   88 km NE of Baghdad, p. 75) and Maskin (one bishop, 900 CE; later joined with ʿUkbara,
   p. 111), and it has **no** entry for any weak-lead name (Karkhene, Espurgan, Sirakan,
   al-Sābusṭī, Tauk, Aghmā). Fiey's other works (*Assyrie chrétienne* III; *Sumer* 23, 1967)
   are **not** checked.

## Controls (known identifications)

Of 33 control toponyms, the matcher's top candidate is right for 13 (Meḥoza = Maḥoza,
Bei Lefet = Beth Lapaṭ, Bashkar = Kashkar, Meishan, Ḥamadan, Nesibin, Ḥadyab, Nihavnad,
Ginzak, Batzra = Baṣra, Bagda / Baghdad, Perat of Meishan). For 4 more the right place is
in the top 8 (Bei Ardeshir = Kokhe/Veh-Ardashir, rank 6; Bei Ḥozai = Beth Huzaye, rank 2;
Akhbaria = ʿUkbara, rank 3; Kerakh). It fails where the Syriac sources use another name
(Pumbedita, Sura, Mata Meḥasya, Neresh, Akistefon) and on short or generic names (Kafri,
Malka). One instructive false positive: **Neharde'a → Beth Nuhadra** (d=r), a see in the
far north.

## Pilot results (26 toponyms)

| Status | n | Toponyms |
|---|---|---|
| Restatement of a known identification | 8 | Mavrakhta, Drokart (+ variant Derokera), Mashhig, Diskarta, Hurmiz Ardeshid, Mushekanei, Sakistan |
| Rejected (false positive) | 6 | Parzina, Bei Torta, Pashronya, Vastanya, Masgariya, Gerofina |
| Weak lead (not in BJ or POCN; other Fiey works not checked) | 6 | Korkoneya, Asporak, Zerokinya, Bridge of Shabistana, Akra DeAgma, Tavakh |
| No Syriac candidate | 4 | Hagronya, Harpanya, Shekhantziv, Pappunya |
| Not checked / out of scope | 2 | Beit Shavor, Kan Nishrayya |

### Only restatements

Every strong match is already in the literature, mostly since the 19th century:

- **מברכתא Mavrakhta = Syriac Mabrakta** (near Maḥoze): Neubauer 1868 p. 357; Hoffmann
  1880 p. 110; Chabot 1902, table p. 676, prints the Talmudic form himself; Fiey 1967
  mapped it; BJ pp. 243–244.
- **דרוקרת Drokart = Darauqart**: Hoffmann 1880 n. 2152 already links the Talmudic form to
  Yāqūt and to a Syriac spelling; Obermeyer put it in Mesene; BJ p. 115 doubts that and puts
  it near Sura.
- **משהיג Mashhig = Mashmahig** (Bahrain): BJ titles its entry with the Syriac form (p. 240).
- **דסקרתא Diskarta = Dasqarta (d-Malka)**: Chabot 1902, table p. 671 ("Dastagird du
  Talmud").
- **הורמיז ארדשיר = Hormizd-Ardashir** (Ahwaz): BJ pp. 154–159, citing Hoffmann p. 34.
- **מושכני Mushkani = Maskene / Maskin**: Hoffmann 1880 n. 343 (p. 41) gives the Syriac,
  Talmudic and Arabic forms together; BJ pp. 260–261.

### Nothing new yet

No row is an identification that is new against BJ. The six "weak leads" have one or two
letter confusions, a generic word (agmā "marsh"), or a location that does not fit the
Talmudic context; none is checked against Fiey. The closest to something worth a look:

- **קורקוניא Qurqunya / Korkoneya ~ Karkhene** (Barhebraeus, "today called Karkhene", near
  Karka d-Beth Slokh / Daquqa; Hoffmann Excursus 19, p. 272f.). The consonants match exactly,
  BJ leaves Qurqunya unidentified (p. 391), and BJ uses Karhini/Karhine for another entry
  (p. 380). But BJ's reading of the source puts Qurqunya on R. Zera's way to Sura, far from
  Karkhene. Probably wrong.
- **Drokart**: not new, but Hoffmann's Syriac spelling of Darauqart has a source we have not
  found. A dated Syriac attestation with context could test BJ's objection to Obermeyer.

### Lessons for the full run

1. **The Gazetteer is the wrong main list for Beth Aramaye.** It covers sees, monasteries
   and (via Wilmshurst) modern villages. The villages of the Acts and of the chronicles are
   mostly not in it. Hoffmann's register and Chabot's tables gave more of the useful hits.
2. **Persons and places are mixed** in Hoffmann's register and in the Chabot form list
   (Parzina → "Burzen" is a royal official). A place/person flag is needed.
3. **Short skeletons** (three consonants or fewer) match by chance; the 0.05 penalty is not
   enough. Use them only with a second signal (region, a Beth- prefix on both sides).
4. **Prior art is dense.** Hoffmann 1880, Neubauer 1868, Obermeyer 1929, Chabot 1902 and
   Fiey 1967 already used most Syriac evidence for the well-attested places. The open BJ
   entries (Hagrunya, Harpanya, Sokansiv, Papuniya, the appendix places) gave no Syriac
   candidates at all. The realistic value of the project is (a) a reproducible table that
   shows for each place which Syriac evidence exists and who used it first, and (b) a small
   number of leads from texts that the 19th-century scholars did not have (Bedjan's AMS
   vols. 4–7, later chronicles), which means OCR of those texts, not more matching.

## Attestations (step 4)

See the `attest_*` columns. Chabot's Syriac is in **Estrangela** type. The Qoruyo East Syriac
model reads it only roughly (it found ܦܝܪܘ ܫܒܘܪ Pērōz-Šābūr on Syriac p. 79), so a
spelling counts as attested only after a check on the page image.

**Status: partly done.** Page references are in `data/attestations.csv` and the
`attest_*` columns: Chabot's French translation (pp. 272–662), Chabot's place table
(pp. 671, 676), Hoffmann (pp. 41, 271–273) and POCN (pp. 75, 111). **The Syriac spellings in
Chabot are not yet checked on the page images.** The Kraken run on Chabot's Syriac pp. 33–36
and 44–47 (leaves n51–54, n62–65, images in `work/chabot/`) crashed twice: first "The paging
file is too small", then exit 139 (the laptop ran out of memory). Only the test page, p. 79,
was read.

Bedjan, *AMS* II was **not** OCR'd: no surviving candidate needed it. The Acts that
Hoffmann used for Karkhene and Maskene are not identified with Bedjan pages yet.

## Round 2: BJ's own list of unidentified places (21-Nov-2026)

**The BJ list.** BJ's General Index (pp. 530–546) names the sub-sections of every entry, and
these show BJ's verdict: "Location" (located), "Already Proposed Location" (BJ weighs earlier
proposals), "Proposed Location" (BJ proposes), **"Attempts at Identification"** (unidentified
or disputed), and "(A)" (appendix). Searching the index labels with "search inside" gave 321
index snippets and 87 entries (`data/bj_entries.csv`, `scripts/build_bj_index.py`). The list
is **incomplete** (the search returns only short snippets), but it gives BJ's own targets:
17 places marked "Attempts at Identification" (`data/talmud_bj_targets.csv`; Hebrew forms from
the BJ headings, checked in the Sefaria Aramaic text).

**Matcher run on the 17** (`out/matches_bj_attempts.csv`, review in
`data/bj_attempts_review.csv`): 14 have no usable Syriac candidate, 2 are rejected
(Be Mikse → Beth Moksaye is Moxoene in Armenia; Nohar Poqod → Nahargur needs two
confusions), and **1 is a lead**:

- **Qartu, קרתויים / קרתויי (Yevamot 16a), = Syriac Qarṭwāyē, ܩܪܛܘܝܐ, the "Kartaw Kurds".**
  - Syriac side: Chabot p. 423 (synod of Ishoʿyahb I, 585: Kelilishoʿ, bishop "of Beth
    Tabyatē and of the Kartawayē"); Chabot's table p. 677 ("tribu kurde … à l'est du Petit
    Zab, au-dessus d'Arbèle"); Hoffmann p. 207 n. 1639 (Assemani, Wright's catalogue, Arabic
    geographers); Fiey, POCN p. 66 ("Beth Kartwayé … le Nord montagneux de l'Adiabène");
    Gazetteer records 1034 and 4464.
  - BJ (pp. 386–387) agrees with Rav Ashi that Qartu ≠ Qardu, but puts the Qartuans "according
    to Strabo, in southern Persia" (the Κύρτιοι). Jastrow (p. 1428) has Κόρτιοι, "mountaineers
    of Media". Neither cites the Syriac Qarṭwāyē, and Hoffmann's note and POCN do not cite the
    Talmud.
  - What the Syriac adds: a people called Qarṭwāyē (with ṭ; Talmudic ת = one t/ṭ confusion)
    in northern Adiabene, organised as a diocese by 585, separate from Qardu (Corduene). That
    supports Rav Ashi's distinction and points to northern Mesopotamia rather than southern Persia.
  - **Not yet a claim.** Still to check: Obermeyer p. 133, Neubauer p. 429, Fiey *Assyrie
    chrétienne* I (Kartaw pp. 152–153, 216–217; lending only), Weissbach RE s.v. Κύρτιοι.
    Caution: Chabot p. 630 equates "Qardewayē" with the Kartawayē, which blurs the very
    distinction.

**Coverage table** (`out/coverage.csv`, `scripts/build_coverage.py`): 166 Talmudic toponyms
(149 + the 17 BJ targets) with the BJ entry (found for 97), BJ's status where the index gave
it (71), the top Syriac candidate with score and rules, and the manual verdict where there is
one. This is the "systematic" table the project promised; it still has gaps in BJ status.

## Next steps

- Fiey, *Assyrie chrétienne* III (lending only) and *Sumer* 23 (1967): check the weak leads.
- Check the Qartu lead: Obermeyer p. 133, Neubauer p. 429, Fiey *AC* I, Weissbach RE.
- Complete the BJ index (more search terms, or the owner borrows BJ for an hour and reads pp. 530–546).
- Read BJ's verdicts for the entries whose verdict is "not read" (Diskarta, Papuniya).
- Add a place/person flag to the Hoffmann register; parse Chabot's table fully.
- Decide with the owner whether the next step is matching at scale (all 662 toponyms) or
  OCR of Bedjan AMS vols. 2–7 to build a new Syriac place list from the Acts themselves.
