# Sources

Status: **have** = data on disk in `sources/`; **checked** = link and content
checked, not downloaded; **missing** = not found or not in reach.
Checked 21-Nov-2026.

## Syriac data

| Source | Where | Licence | Status | Notes |
|---|---|---|---|---|
| Syriac Gazetteer (Syriaca.org), place records | [srophe/syriaca-data](https://github.com/srophe/syriaca-data) `data/places/tei/` | CC BY 4.0 (stated in each record's `<licence>`; some records also incorporate other works under CC BY) | **have** (TEI in `sources/syriaca-places-tei/`, commit 05d74c295a of 30-Oct-2026 in `_manifest.json`) | **Newest and active:** repo pushed 20-Nov-2026; last commit on `data/places` 21-Nov-2025 (issue #1230). 3,485 records; 954 with Syriac names, 926 with coordinates; 1,583 sourced only from Wilmshurst (1318–1913). **No record cites Fiey** in its bibliography (checked by parsing all `<bibl>`). |
| — old repo `srophe/places` | [GitHub](https://github.com/srophe/places) | — | checked, **not used** | Archived 16-Jul-2026, but already deprecated since 31-Jul-2014 ("Deprecate repository"). Stale. |
| — `srophe/srophe-eXist-app` | [GitHub](https://github.com/srophe/srophe-eXist-app) | GPL-3.0 (code) | checked, **not used** | Archived 21-Jul-2026. Has **no** `data/places` folder; it is the app code. Its data repo is `syriaca-data` (README: "srophe-app-data … used by srophe-eXist-app"). |
| Chabot, *Synodicon Orientale ou Recueil de synodes nestoriens* (Paris 1902 = *Notices et extraits* 37), Syriac + French | archive.org [`ChabotSynodiconOrientale`](https://archive.org/details/ChabotSynodiconOrientale) (PDF 27.6 MB, page images 1.1 GB) | public domain (1902) | **have** text layer (`sources/chabot_synodicon_djvu.txt`, 1.9 MB); page images fetched as needed into `work/chabot/` | The French translation in the text layer is good OCR, so place names are found in French and then checked on the Syriac page image. Syriac text pp. 1–252 (archive.org leaf n = page + 18, e.g. n97 = p. 79), French translation from p. 253. Syriac type is **Estrangela**; the Qoruyo East Syriac Kraken model reads it only roughly. Chabot's "Table des noms de pays" (pp. 665–685) gives Syriac and Arabic forms and sources, and already cites the Talmud for Mabrakta and Dasqarta de Malka. |
| — HathiTrust copies | [catalog](https://catalog.hathitrust.org/Search/Home?lookfor=synodicon%20orientale%20chabot) (hvd.32044012610838, uiug.30112075972296, …) | — | checked | "Limited (search only)" from this laptop (non-US access rule for 1902 non-US books). The archive.org copy is enough. |
| — Penn Online Books Page | | | checked | No Synodicon entry found under Chabot. |
| — Gallica (*Notices et extraits* 37) | | | not checked | Gallica's SRU did not answer from the agent's browser. Not needed while archive.org works. |
| Braun, *Das Buch der Synhados* (Stuttgart/Wien 1900), German translation of the same Synodicon | archive.org [`DasBuchDerSynhados`](https://archive.org/details/DasBuchDerSynhados) | Public Domain Mark | **have** text layer (`sources/braun_synhados_djvu.txt`) | Second, independent transliteration of the sees. |
| Bedjan, *Acta Martyrum et Sanctorum* II (Paris 1891) | archive.org [`Bedjan1892ActaMartyrumEtSanctorumVol.2`](https://archive.org/details/Bedjan1892ActaMartyrumEtSanctorumVol.2) (PDF 78 MB, jp2 170 MB, 300 ppi); second copy `ActaMartyrumEtSanctorumvolume4Ed.PaulBedjan` | public domain | checked | Text layer is garbage (Latin-script OCR of Syriac). Needs Kraken OCR of the pages we need. Vols. 1–6 also on archive.org (`ActaMartyrumEtSanctorumvolume{2,3,5,6}Ed.PaulBedjan`, `…volume4Ed.PaulBedjan_807`; note that the archive.org titles give wrong volume numbers for some items; check the title page), and as one set `ActaMartyrumEtSanctorumPaulBedjanSyriacVol1-6`. Vol. 7 not yet looked for. |

## Talmudic data (owner's earlier projects, reused)

| Source | Path | Notes |
|---|---|---|
| talmud-nlp-indexer toponym gazetteer (662 entries, English) | `C:\Users\ezrab\Ezra Brandt\Claude\talmud-names-discovery\data\talmud_toponyms_gazetteer.txt` | English forms of the William Davidson (Steinsaltz) translation. |
| Alma place map (373 places with coordinates; only 31 east of 40° E) | `C:\Users\ezrab\Ezra Brandt\Claude\talmud-names-discovery\alma\alma_places.csv` | So most Babylonian toponyms have **no** coordinates in the owner's lists. |
| Sefaria William Davidson English + Aramaic | `C:\Users\ezrab\Ezra Brandt\Claude\talmud-names-discovery\sefaria\` | Used to get the Aramaic spelling of each English toponym. |

## Reference works (to cite and check against)

| Work | Status | Use |
|---|---|---|
| A. Oppenheimer (with B. Isaac and M. Lecker), *Babylonia Judaica in the Talmudic Period* (Wiesbaden 1983) | **checked (search only)**: archive.org [`babyloniajudaica0000oppe`](https://archive.org/details/babyloniajudaica0000oppe), lending library. Its "search inside" (server `ia600806`, `fulltext/inside.php`) returns snippets with page numbers without a loan. Results in `data/fts_bj_*.json`. | The baseline. Its General Index (pp. 530–546) names each entry's sub-sections, including "Attempts at Identification" = unidentified/disputed; searching those labels rebuilds a partial list of entries with BJ's status (`data/bj_entries.csv`). Entries and verdicts were also found per toponym (Hebrew forms work well as search terms). BJ uses Hoffmann, Obermeyer, Fiey (*Sumer* 23, 1967) and Nöldeke. |
| J. M. Fiey, *Assyrie chrétienne* I–III (Beirut 1965–68) | vol. II **have** text layer (`sources/fiey_assyrie_djvu.txt`, from the open Beth Mardutho copy `assyriechrtienne0003jmfi`); vols. I and III only as lending scans (`assyriechretienn0000fiey`, `assyriechretienn0001fiey`, `bwb_C0-ATP-677_3`) | Vol. II is the north (not Beth Aramaye). **Vol. III (Bēth Garmai, Bēth Aramāyē, Maišān) is the one we need**: lending only. |
| J. M. Fiey, *Pour un Oriens Christianus Novus* (Beirut/Stuttgart 1993) | **checked (search only)**: lending scan `bwb_T5-DIB-779`; search inside works when called from the item's own archive.org page (server `ia800600`). Results in `data/fts_pocn.json`. | Sees only. Not cited in the Gazetteer records. |
| J. M. Fiey, "Topographie chrétienne de Mahozé", *Sumer* 23 (1967) | missing | BJ relies on it for the Mahoza area (Mavrakta, Gisra do-Sabistana). |
| J. Obermeyer (1929) | not on archive.org under that name; needed for the Qartu lead (p. 133) | BJ discusses his identifications entry by entry. |
| A. Neubauer, *La géographie du Talmud* (1868) | **have** text layer (`sources/neubauer_geographie_djvu.txt`, archive.org `lagographiedutal00neub`, public domain) | Cited by Chabot for Mabrakta. p. 398: Kerkounya = a Kerkounah in Kurdistan; p. 429: Karthoï = Kurtioi. |
| F. Jullien, studies of the historical geography of the Persian Martyr Acts | missing | Exact titles to fix. |
| A. H. Becker, *The Invention of the Persian Martyr Acts* (2020) | missing | Dating and nature of the Acts. |
| J. L. Rubenstein, on the Persian Martyr Acts and the Bavli | missing | Exact titles to fix. |
| G. Hoffmann, *Auszüge aus syrischen Akten persischer Märtyrer* (Leipzig 1880) | **have** text layer (`sources/hoffmann_auszuege_djvu.txt`, archive.org `auszgeaussyris00hoff`, Toronto, open) | The classic historical geography of the Acts. Its register (pp. 298 ff.) is parsed into `data/hoffmann_register.csv`. Hoffmann already cites the Talmud for several places (Maskene n. 343, Darauqart n. 2152). Syriac and Hebrew in the OCR are garbled. |
| J. Obermeyer, *Die Landschaft Babylonien im Zeitalter des Talmuds und des Gaonats* (Frankfurt 1929) | missing (not found on archive.org) | Talmudic geography with Syriac and Arabic evidence. |
| M. Streck, *Die alte Landschaft Babylonien nach den arabischen Geographen* (1900–01) | checked: several open copies on archive.org (`diealtelandschaf00stre` etc.) | Arabic side; cited by BJ. Not used yet. |

## Dictionaries

| Work | Where | Use |
|---|---|---|
| M. Jastrow, *Dictionary of the Targumim, the Talmud Babli and Yerushalmi* (1903) | Sefaria API `/api/words/<word>` (public) | Checked for קרתויים (p. 1428: Κόρτιοι, "mountaineers of Media"). |
