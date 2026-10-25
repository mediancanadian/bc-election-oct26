"""Download BC Geographic Warehouse layers via openmaps.gov.bc.ca WFS (GeoJSON, EPSG:3005), paged.
Writes raw/bcgw/<layer>.geojson and appends entries to manifest_bcgw.json."""
import json, os, sys, time, urllib.request, urllib.parse, datetime

BASE = "https://openmaps.gov.bc.ca/geo/pub/wfs"
ROOT = "analysis/geo"
LAYERS = {
    "ed2023": "WHSE_ADMIN_BOUNDARIES.EBC_ELECTORAL_DISTS_BS11_SVW",
    "ed2015": "WHSE_ADMIN_BOUNDARIES.EBC_ELECTORAL_DISTS_BS10_SVW",
    "va2024": "WHSE_ADMIN_BOUNDARIES.EBC_VOTING_AREAS_BS11_POLY_SVW",
    "va2017": "WHSE_ADMIN_BOUNDARIES.EBC_VOTING_AREAS_BS10_POLY_SVW",
    "sbva2024": "WHSE_ADMIN_BOUNDARIES.EBC_SBP_VOTING_AREAS_BS11_SVW",
    "sbva2017": "WHSE_ADMIN_BOUNDARIES.EBC_SBP_VOTING_AREAS_BS10_SVW",
    "vavp2024": "WHSE_HUMAN_CULTURAL_ECONOMIC.EBC_VAVP_GE2024_SV",
    "regional_districts": "WHSE_LEGAL_ADMIN_BOUNDARIES.ABMS_REGIONAL_DISTRICTS_SP",
}
PAGE = 1000
out = os.path.join(ROOT, "raw/bcgw")
man = []
for key, layer in LAYERS.items():
    if len(sys.argv) > 1 and key not in sys.argv[1:]:
        continue
    feats, start = [], 0
    while True:
        q = dict(service="WFS", version="2.0.0", request="GetFeature", typeNames="pub:" + layer,
                 outputFormat="application/json", srsName="EPSG:3005", count=PAGE, startIndex=start,
                 sortBy="OBJECTID")
        url = BASE + "?" + urllib.parse.urlencode(q)
        req = urllib.request.Request(url, headers={"User-Agent": "bc2026-geo"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    d = json.load(r)
                break
            except Exception as e:
                print("retry", key, start, e); time.sleep(5)
        else:
            raise SystemExit("failed " + key)
        feats += d["features"]
        print(key, start, len(d["features"]), flush=True)
        if len(d["features"]) < PAGE:
            break
        start += PAGE
    fc = {"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::3005"}},
          "features": feats}
    fn = os.path.join(out, key + ".geojson")
    json.dump(fc, open(fn, "w"))
    man.append({"file": "raw/bcgw/" + key + ".geojson", "layer": layer, "features": len(feats),
                "url": BASE + "?service=WFS&version=2.0.0&request=GetFeature&typeNames=pub:" + layer +
                       "&outputFormat=application/json&srsName=EPSG:3005 (paged, count=1000, sortBy=OBJECTID)",
                "accessed_utc": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "licence": "Open Government Licence - British Columbia"})
mf = os.path.join(out, "manifest_bcgw.json")
old = json.load(open(mf)) if os.path.exists(mf) else []
old = [m for m in old if m["file"] not in {x["file"] for x in man}] + man
json.dump(old, open(mf, "w"), indent=1)
