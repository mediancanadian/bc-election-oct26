# Downloads 2021 census dissemination block polygons (BC Geographic Warehouse WFS), paged.
import json, sys, urllib.request, datetime, os
out = sys.argv[1]
layer = "pub:WHSE_HUMAN_CULTURAL_ECONOMIC.CEN_CENSUS_DISSEM_BLOCKS_SVW"
base = ("https://openmaps.gov.bc.ca/geo/pub/wfs?service=WFS&version=2.0.0&request=GetFeature"
        f"&typeNames={layer}&outputFormat=application/json&srsName=EPSG:3005&sortBy=OBJECTID&count=10000")
feats = []; start = 0
while True:
    with urllib.request.urlopen(base + f"&startIndex={start}", timeout=600) as r:
        d = json.load(r)
    feats += d["features"]; print(start, len(d["features"]), flush=True)
    if len(d["features"]) < 10000: break
    start += 10000
json.dump({"type": "FeatureCollection", "features": feats,
           "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::3005"}}}, open(out, "w"))
print("total", len(feats), datetime.datetime.now(datetime.timezone.utc).isoformat())
