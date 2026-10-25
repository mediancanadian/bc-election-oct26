"""Merge download manifests into manifest.json with licences, and list outputs with sizes."""
import json, os, hashlib, datetime

R = "analysis/geo/"
EBC = {"name": "Elections BC Open Data Licence", "url": "https://www.elections.bc.ca/docs/EBC-Open-Data-Licence.pdf",
       "note": "Elections BC layers in the BC Data Catalogue are published under this licence (not OGL-BC); copy saved at raw/ebc/EBC-Open-Data-Licence.pdf"}
OGLBC = {"name": "Open Government Licence - British Columbia", "url": "https://www2.gov.bc.ca/gov/content/data/policy-standards/open-data/open-government-licence-bc"}
OGLC = {"name": "Open Government Licence - Canada", "url": "https://open.canada.ca/en/open-government-licence-canada"}
SCOL = {"name": "Statistics Canada Open Licence", "url": "https://www.statcan.gc.ca/en/reference/licence"}
CAT = {
    "ed2023": "provincial-electoral-districts-electoral-boundaries-redistribution-2023",
    "ed2015": "provincial-electoral-districts-electoral-boundaries-redistribution-2015",
    "va2024": "provincial-electoral-district-voting-areas-gazetted-09-19-2024",
    "va2017": "provincial-electoral-district-voting-areas-gazetted-02-23-2017",
    "sbva2024": "provincial-site-based-voting-areas-gazetted-09-19-2024",
    "sbva2017": "provincial-site-based-voting-areas-gazetted-02-23-2017",
    "vavp2024": "2024-provincial-general-election-voting-areas-to-voting-place-assignment",
    "regional_districts": "regional-districts-legally-defined-administrative-areas-of-bc",
}


def sha(fn):
    h = hashlib.sha256()
    with open(fn, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


src = []
for m in json.load(open(R + "raw/bcgw/manifest_bcgw.json")):
    key = os.path.basename(m["file"]).replace(".geojson", "")
    m["licence"] = OGLBC if key == "regional_districts" else EBC
    m["catalogue"] = "https://catalogue.data.gov.bc.ca/dataset/" + CAT[key]
    m["publisher"] = "BC Geographic Warehouse (openmaps.gov.bc.ca WFS)" + ("" if key == "regional_districts" else ", data from Elections BC")
    src.append(m)
for m in json.load(open(R + "raw/statcan/manifest_statcan.json")):
    m["licence"] = SCOL if m["file"].endswith(".csv") else OGLC
    m["publisher"] = "Statistics Canada" + (" (via BC Data Catalogue, dataset census-geographic-attribute-file)" if m["file"].endswith(".csv") else " (geo.statcan.gc.ca ArcGIS REST)")
    src.append(m)
for m in json.load(open(R + "raw/fwa/manifest_fwa.json")):
    m["licence"] = OGLBC
    m["publisher"] = "GeoBC Freshwater Atlas via BC Geographic Warehouse (openmaps.gov.bc.ca WFS)"
    src.append(m)
src.append({"file": "(read, not copied) analysis/census/maps/ed2023_full_clipped_3005.gpkg",
            "publisher": "census thread build: Elections BC 2023 districts (this thread's raw/bcgw/ed2023.geojson) clipped to the union of FWA watershed groups (WHSE_BASEMAPPING.FWA_WATERSHED_GROUPS_POLY, 1:20,000)",
            "licence": [EBC, OGLBC], "sha256": sha("analysis/census/maps/ed2023_full_clipped_3005.gpkg")})
t = open(R + "raw/bcdc/access_time.txt").read().strip()
for f, u in [("edva_conversiontable2017to2024.xlsx", "https://catalogue.data.gov.bc.ca/dataset/fb26db04-780c-4229-a147-da4fd5311d36/resource/7dec2191-33e8-46b6-83cc-ad773b57742d/download/edva_conversiontable2017to2024.xlsx"),
             ("edva_conversiontable2024to2017.xlsx", "https://catalogue.data.gov.bc.ca/dataset/fb26db04-780c-4229-a147-da4fd5311d36/resource/4d6da956-a849-48ea-a64e-cea0238c36c2/download/edva_conversiontable2024to2017.xlsx")]:
    src.append({"file": "raw/bcdc/" + f, "url": u, "accessed_utc": t, "licence": EBC, "publisher": "Elections BC via BC Data Catalogue (edva-conversion-tables)"})
src.append({"file": "raw/ebc/EBC-Open-Data-Licence.pdf", "url": EBC["url"], "accessed_utc": t, "publisher": "Elections BC"})
for s in src:
    fn = R + s["file"]
    if not s["file"].startswith("(") and os.path.exists(fn):
        s["bytes"] = os.path.getsize(fn)
        s["sha256"] = sha(fn)
blocked = [{"url": "https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/files-fichiers/lda_000b21a_e.zip (and other www12 zip downloads)",
            "result": "HTTP 403, Cloudflare browser challenge; not usable from a script. Same data taken from StatCan's geo.statcan.gc.ca ArcGIS REST service instead."},
           {"url": "https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21",
            "result": "Page fetch declined in this session; not used."}]
outs = []
for root, _, files in os.walk(R + "out"):
    for f in sorted(files):
        if f.startswith("_") or f.endswith(".log"):
            continue
        p = os.path.join(root, f)
        outs.append({"file": os.path.relpath(p, R), "kb": round(os.path.getsize(p) / 1024, 1)})
man = {"generated_utc": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
       "sources": src, "blocked_or_unused": blocked, "outputs": outs,
       "request_headers": "User-Agent: bc2026-geo only; no personal details sent."}
json.dump(man, open(R + "manifest.json", "w"), indent=1)
print(len(src), "sources,", len(outs), "outputs")
