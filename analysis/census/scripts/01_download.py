"""Download official inputs for the census layer and land-clipped maps.
- BC Stats 2021 Census Profile for 93 PEDs (2023 Redistribution), BC Data Catalogue (CSV).
- FWA Watershed Groups (1:20,000, coastline-edged land polygons) via openmaps.gov.bc.ca WFS, EPSG:3005.
Records URL, UTC access time, sha256 and licence into raw/manifest_raw.json.
Sends no personal data: generic User-Agent, no cookies, no auth.
"""
import json, os, sys, time, hashlib, datetime, urllib.request, urllib.parse

ROOT = "analysis/census"
UA = {"User-Agent": "Mozilla/5.0"}
man_path = os.path.join(ROOT, "raw/manifest_raw.json")
man = json.load(open(man_path)) if os.path.exists(man_path) else []


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha(fn):
    h = hashlib.sha256()
    with open(fn, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def get(url, fn, timeout=600):
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r, open(fn, "wb") as f:
                f.write(r.read())
            return
        except Exception as e:
            print("retry", url, e); time.sleep(5)
    raise SystemExit("failed " + url)


def record(entry):
    global man
    man = [m for m in man if m["file"] != entry["file"]] + [entry]
    json.dump(man, open(man_path, "w"), indent=1)


BCSTATS = {
    "census_profile_2021_ped93_part1.csv": "a32273fb-0f47-4f11-a57d-49a20c398daa",
    "census_profile_2021_ped93_part2.csv": "3363ce8b-8f28-4ec0-be57-cefe0d178f6b",
    "98-401-x2021005_english_meta.txt": "47683f66-9d74-4104-87a7-66728136ccd7",
}
DS = "https://catalogue.data.gov.bc.ca/dataset/da0326f2-2191-4345-84d3-d14cd6ee76eb/resource/{}/download/{}"

if "bcstats" in sys.argv or len(sys.argv) == 1:
    os.makedirs(os.path.join(ROOT, "raw/bcstats"), exist_ok=True)
    for fn, rid in BCSTATS.items():
        url = DS.format(rid, fn)
        out = os.path.join(ROOT, "raw/bcstats", fn)
        t = now(); get(url, out)
        record({"file": "raw/bcstats/" + fn, "url": url, "accessed_utc": t, "sha256": sha(out),
                "publisher": "BC Stats (BC Data Catalogue: census-profiles-for-bc-provincial-electoral-districts)",
                "licence": "Statistics Canada Open Licence (as stated on the BC Data Catalogue record)"})

if "fwa" in sys.argv or len(sys.argv) == 1:
    os.makedirs(os.path.join(ROOT, "raw/bcgw"), exist_ok=True)
    layer = "WHSE_BASEMAPPING.FWA_WATERSHED_GROUPS_POLY"
    feats, start, t = [], 0, now()
    while True:
        q = dict(service="WFS", version="2.0.0", request="GetFeature", typeNames="pub:" + layer,
                 outputFormat="application/json", srsName="EPSG:3005", count=20, startIndex=start,
                 sortBy="OBJECTID", propertyName="WATERSHED_GROUP_ID,WATERSHED_GROUP_CODE,WATERSHED_GROUP_NAME,GEOMETRY")
        fn = os.path.join(ROOT, "raw/bcgw/_page.json")
        get("https://openmaps.gov.bc.ca/geo/pub/wfs?" + urllib.parse.urlencode(q), fn)
        d = json.load(open(fn)); feats += d["features"]; print("fwa", start, len(d["features"]), flush=True)
        if len(d["features"]) < 20:
            break
        start += 20
    os.remove(fn)
    out = os.path.join(ROOT, "raw/bcgw/fwa_watershed_groups.geojson")
    json.dump({"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::3005"}},
               "features": feats}, open(out, "w"))
    record({"file": "raw/bcgw/fwa_watershed_groups.geojson", "layer": layer, "features": len(feats),
            "url": "https://openmaps.gov.bc.ca/geo/pub/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=pub:" + layer +
                   "&outputFormat=application/json&srsName=EPSG:3005 (paged, count=20, sortBy=OBJECTID)",
            "accessed_utc": t, "sha256": sha(out), "publisher": "GeoBC, Freshwater Atlas (1:20,000)",
            "licence": "Open Government Licence - British Columbia"})
