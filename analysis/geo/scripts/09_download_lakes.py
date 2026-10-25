"""Download Freshwater Atlas lakes (1:20,000) >= 100 ha from the BC Geographic Warehouse WFS (EPSG:3005).
Lakes are split by watershed group in FWA, so pieces are fetched at >= 100 ha and later dissolved by WATERBODY_KEY
before the 50 km2 threshold is applied. Also fetches man-made waterbodies >= 100 ha (none reach 50 km2; for completeness)."""
import json, os, time, urllib.request, urllib.parse, datetime

R = "analysis/geo/"
OUT = R + "raw/fwa/"
os.makedirs(OUT, exist_ok=True)
BASE = "https://openmaps.gov.bc.ca/geo/pub/wfs"
man = []
for key, layer in [("fwa_lakes_ge100ha", "WHSE_BASEMAPPING.FWA_LAKES_POLY"),
                   ("fwa_manmade_ge100ha", "WHSE_BASEMAPPING.FWA_MANMADE_WATERBODIES_POLY")]:
    feats, start = [], 0
    while True:
        q = dict(service="WFS", version="2.0.0", request="GetFeature", typeNames="pub:" + layer,
                 outputFormat="application/json", srsName="EPSG:3005", count=200, startIndex=start, sortBy="OBJECTID",
                 CQL_FILTER="AREA_HA>=100",
                 propertyName="WATERBODY_POLY_ID,WATERBODY_KEY,WATERBODY_TYPE,AREA_HA,GNIS_NAME_1,GNIS_NAME_2,WATERSHED_GROUP_CODE,FEATURE_CODE,GEOMETRY")
        url = BASE + "?" + urllib.parse.urlencode(q)
        for a in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "bc2026-geo"}), timeout=600) as r:
                    d = json.load(r)
                break
            except Exception as e:
                print("retry", e); time.sleep(5)
        else:
            raise SystemExit("failed")
        feats += d["features"]
        print(key, start, len(d["features"]), flush=True)
        if len(d["features"]) < 200:
            break
        start += 200
    json.dump({"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::3005"}},
               "features": feats}, open(OUT + key + ".geojson", "w"))
    man.append({"file": "raw/fwa/" + key + ".geojson", "layer": layer, "features": len(feats),
                "url": BASE + "?service=WFS&version=2.0.0&request=GetFeature&typeNames=pub:" + layer +
                       "&CQL_FILTER=AREA_HA>=100&outputFormat=application/json&srsName=EPSG:3005 (paged, 200)",
                "accessed_utc": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
                "licence": "Open Government Licence - British Columbia",
                "catalogue": "https://catalogue.data.gov.bc.ca/dataset/freshwater-atlas-lakes" if "LAKES" in layer else
                             "https://catalogue.data.gov.bc.ca/dataset/freshwater-atlas-manmade-waterbodies"})
json.dump(man, open(OUT + "manifest_fwa.json", "w"), indent=1)
