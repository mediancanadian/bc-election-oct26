"""Download StatCan 2021 DA/DB boundaries for BC (PRUID=59) from StatCan's official ArcGIS REST services
(geo.statcan.gc.ca; the www12 zip downloads are behind a browser challenge), plus the 2021 Geographic
Attribute File (BC extract, republished on the BC Data Catalogue) for DB populations.
Usage: python3 -I 02_download_statcan.py [db_digital] [da_cartographic] [da_digital] [gaf]"""
import json, os, sys, time, urllib.request, urllib.parse, datetime

ROOT = "analysis/geo"
OUT = os.path.join(ROOT, "raw/statcan")
os.makedirs(OUT, exist_ok=True)
SVC = "https://geo.statcan.gc.ca/geo_wa/rest/services/2021/"
JOBS = {
    "db_digital": (SVC + "Digital_boundary_files/MapServer/13", "DBUID,DGUID,DBRPLAMX,DBRPLAMY,LANDAREA,PRUID"),
    "da_cartographic": (SVC + "Cartographic_boundary_files/MapServer/12", "DAUID,DGUID,LANDAREA,PRUID"),
    "da_digital": (SVC + "Digital_boundary_files/MapServer/12", "DAUID,DGUID,LANDAREA,PRUID"),
}
GAF = "https://catalogue.data.gov.bc.ca/dataset/4ed0c389-43ed-4b00-b1be-7c259f47b6a0/resource/6c8eeb86-bb56-48e8-b734-0d25d6a51a7b/download/2021_92-151_x_bc.csv"
PAGE = int(os.environ.get("PAGE", "1000"))
UA = {"User-Agent": "bc2026-geo"}


def get(url, tries=40):
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
                b = r.read()
            d = json.loads(b)
            if "error" in d:
                raise ValueError(str(d["error"])[:200])
            return d
        except Exception as e:
            print("  retry", a, str(e)[:120], flush=True)
            time.sleep(min(20, 2 * (a + 1)))
    raise SystemExit("failed " + url)


man = []
want = sys.argv[1:] or list(JOBS) + ["gaf"]
for key in want:
    now = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    if key == "gaf":
        fn = os.path.join(OUT, "2021_92-151_x_bc.csv")
        urllib.request.urlretrieve(GAF, fn) if False else None
        with urllib.request.urlopen(urllib.request.Request(GAF, headers=UA), timeout=600) as r, open(fn, "wb") as f:
            f.write(r.read())
        man.append({"file": "raw/statcan/2021_92-151_x_bc.csv", "url": GAF, "accessed_utc": now,
                    "description": "Statistics Canada 2021 Census Geographic Attribute File (92-151-X), filtered to B.C., republished on BC Data Catalogue (dataset census-geographic-attribute-file)",
                    "licence": "Statistics Canada Open Licence"})
        continue
    base, fields = JOBS[key]
    # fetch OBJECTIDs first, then batches by objectIds (offset paging hits random server 500s)
    ids = sorted(get(base + "/query?" + urllib.parse.urlencode(dict(where="PRUID='59'", returnIdsOnly="true", f="json")))["objectIds"])
    print(key, "ids", len(ids), flush=True)
    feats = []
    for i in range(0, len(ids), PAGE):
        chunk = ids[i:i + PAGE]
        cdir = os.path.join(OUT, "_cache_" + key)
        os.makedirs(cdir, exist_ok=True)
        cfn = os.path.join(cdir, "%d_%d.json" % (chunk[0], chunk[-1]))
        if os.path.exists(cfn):
            feats += json.load(open(cfn))
            continue
        for fmt_try in range(6):
            q = dict(objectIds=",".join(map(str, chunk)), outFields=fields, returnGeometry="true", outSR="3347", f="geojson")
            try:
                d = get(base + "/query?" + urllib.parse.urlencode(q), tries=15)
                break
            except SystemExit:
                print("  chunk retry", i, fmt_try, flush=True)
                time.sleep(30)
        else:
            raise SystemExit("failed chunk %d" % i)
        assert len(d["features"]) == len(chunk), (len(d["features"]), len(chunk))
        feats += d["features"]
        json.dump(d["features"], open(cfn, "w"))
        print(key, i, len(d["features"]), flush=True)
    fc = {"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::3347"}},
          "features": feats}
    json.dump(fc, open(os.path.join(OUT, key + ".geojson"), "w"))
    man.append({"file": "raw/statcan/" + key + ".geojson", "features": len(feats),
                "url": base + "/query?where=PRUID='59'&outFields=" + fields + "&outSR=3347&f=geojson (OBJECTIDs from returnIdsOnly, fetched in batches via objectIds)",
                "accessed_utc": now, "licence": "Open Government Licence - Canada (Statistics Canada)",
                "description": "Statistics Canada 2021 Census boundary file, " + key.replace("_", " ")})
mf = os.path.join(OUT, "manifest_statcan.json")
old = json.load(open(mf)) if os.path.exists(mf) else []
old = [m for m in old if m["file"] not in {x["file"] for x in man}] + man
json.dump(old, open(mf, "w"), indent=1)
