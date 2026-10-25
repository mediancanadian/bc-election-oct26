"""Label anchors: pole of inaccessibility (shapely polylabel, 10 m tolerance) on the largest land part of each district
in FINAL_ed2023_land_lakes_3005 (lakes cut out, so no label falls in a lake). Checked inside the master and every simplified file.
Out: out/final/FINAL_ed2023_label_points.csv and .geojson (EPSG:4326) and _3005.geojson"""
import os, glob
import geopandas as gpd, pandas as pd, shapely
from shapely.ops import polylabel

F = "analysis/geo/out/final/"
m = gpd.read_file(F + "FINAL_ed2023_land_lakes_3005.gpkg")
rows = []
for code, name, g in zip(m.ed_code, m.ed_name, m.geometry):
    big = max(shapely.get_parts(g), key=lambda p: p.area)
    p = polylabel(big, tolerance=10)
    rows.append({"ed_code": code, "ed_name": name, "label_x_3005": round(p.x, 1), "label_y_3005": round(p.y, 1),
                 "dist_to_edge_m": round(big.exterior.distance(p) if not big.interiors else min(big.boundary.distance(p), big.exterior.distance(p)), 1),
                 "inside_master": bool(g.contains(p)), "geometry": p})
lab = gpd.GeoDataFrame(rows, crs=3005)
ll = lab.to_crs(4326)
lab["label_lon"], lab["label_lat"] = ll.geometry.x.round(6), ll.geometry.y.round(6)
for fn in sorted(glob.glob(F + "FINAL_ed2023_land_lakes_*_3005.geojson")):
    s = gpd.read_file(fn).set_crs(3005, allow_override=True).set_index("ed_code").loc[lab.ed_code]
    lab["inside_" + os.path.basename(fn).replace("FINAL_ed2023_land_lakes_", "").replace("_3005.geojson", "")] = \
        [bool(g.contains(p)) for g, p in zip(s.geometry, lab.geometry)]
lab.drop(columns="geometry").to_csv(F + "FINAL_ed2023_label_points.csv", index=False)
for crs, suf in [(4326, ""), (3005, "_3005")]:
    fn = F + f"FINAL_ed2023_label_points{suf}.geojson"
    if os.path.exists(fn):
        os.remove(fn)
    lab.to_crs(crs).to_file(fn, driver="GeoJSON", COORDINATE_PRECISION=6 if crs == 4326 else 1)
ins = [c for c in lab.columns if c.startswith("inside")]
print(lab[ins].all().to_dict(), "min dist to edge m", lab.dist_to_edge_m.min(), lab.loc[lab.dist_to_edge_m.idxmin(), "ed_code"])
