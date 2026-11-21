"""Parse the Syriac Gazetteer TEI records into one CSV row per place.

    py -3.13 -I scripts/build_syriaca_places.py
Input:  sources/syriaca-places-tei/*.xml (scripts/fetch_syriaca_places.py)
Output: data/syriaca_places.csv (utf-8-sig)
"""
import csv, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "syriaca-places-tei"
NS = {"t": "http://www.tei-c.org/ns/1.0"}
XL = "{http://www.w3.org/XML/1998/namespace}lang"
XID = "{http://www.w3.org/XML/1998/namespace}id"


def text(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip() if el is not None else ""


def main():
    rows = []
    files = sorted(SRC.glob("[0-9]*.xml"), key=lambda p: int(p.stem))
    for i, f in enumerate(files, 1):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as e:
            print(f"PARSE FAIL {f.name}: {e}", flush=True)
            continue
        place = root.find(".//t:listPlace/t:place", NS)
        if place is None:
            continue
        bibl = {}
        for b in place.findall("t:bibl", NS):
            ptr = b.find("t:ptr", NS)
            title = b.find("t:title", NS)
            auth = b.find(".//t:persName", NS)
            rng = "; ".join(f"{c.get('unit')} {text(c)}" for c in b.findall("t:citedRange", NS))
            bibl[b.get(XID)] = {"ptr": (ptr.get("target") if ptr is not None else "").split("/")[-1],
                                "title": text(title), "author": text(auth), "range": rng}
        names = place.findall("t:placeName", NS)
        syr, other, en_head = [], [], ""
        for n in names:
            lang, val = n.get(XL, ""), text(n)
            if not val:
                continue
            if lang.startswith("syr"):
                if val not in syr:
                    syr.append(val)
            else:
                if lang == "en" and "#syriaca-headword" in (n.get("{https://srophe.app}tags") or "") and not en_head:
                    en_head = val
                other.append(f"{lang}:{val}")
        loc = place.find("t:location[@subtype='preferred']/t:geo", NS)
        if loc is None:
            loc = place.find(".//t:location/t:geo", NS)
        lat = lon = ""
        if loc is not None and text(loc):
            parts = text(loc).split()
            if len(parts) == 2:
                lat, lon = parts
        loc_text = "; ".join(text(l) for l in place.findall("t:location", NS) if l.get("type") != "gps" and text(l))
        abstract = text(place.find("t:desc[@type='abstract']", NS))
        ex_from = ex_to = ""
        st = place.find("t:state[@type='existence']", NS)
        if st is not None:
            ex_from = st.get("from") or st.get("notBefore") or ""
            ex_to = st.get("to") or st.get("notAfter") or ""
        att = [e.get("notBefore") or e.get("when") or e.get("from") or "" for e in place.findall("t:event[@type='attestation']", NS)]
        att = sorted(a for a in att if a)
        alltext = text(place)
        fiey = [f"{b['author']} {b['title']} {b['range']}".strip() for b in bibl.values()
                if "fiey" in (b["author"] + b["title"]).lower()]
        if "Fiey" in alltext and not fiey:
            fiey = ["(Fiey named in record text)"]
        rows.append({
            "syriaca_id": f.stem,
            "syriaca_uri": f"http://syriaca.org/place/{f.stem}",
            "syriaca_headword": en_head or (other[0].split(":", 1)[1] if other else ""),
            "syriaca_names_syr": " | ".join(syr),
            "syriaca_names_other": " | ".join(other),
            "syriaca_type": place.get("type", ""),
            "syriaca_lat": lat,
            "syriaca_lon": lon,
            "syriaca_location_text": loc_text,
            "syriaca_abstract": abstract,
            "syriaca_exist_from": ex_from,
            "syriaca_exist_to": ex_to,
            "syriaca_first_attestation": att[0] if att else "",
            "syriaca_wilmshurst_only": "yes" if bibl and all(b["ptr"] in ("LBS5EGWD", "") for b in bibl.values()) else "no",
            "syriaca_fiey_refs": " | ".join(fiey),
            "syriaca_bibl": " | ".join(sorted({b["ptr"] for b in bibl.values() if b["ptr"]})),
            "syriaca_idnos": " | ".join(text(x) for x in place.findall("t:idno", NS) if "syriaca.org/place" not in text(x)),
        })
        if i % 500 == 0:
            print(f"{i}/{len(files)}", flush=True)
    out = ROOT / "data" / "syriaca_places.csv"
    with open(out, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out}: {len(rows)} places, {sum(1 for r in rows if r['syriaca_names_syr'])} with Syriac names, "
          f"{sum(1 for r in rows if r['syriaca_lat'])} with coordinates, {sum(1 for r in rows if r['syriaca_fiey_refs'])} with Fiey refs")


if __name__ == "__main__":
    main()
