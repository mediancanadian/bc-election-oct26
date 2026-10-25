"""FINAL master build (EPSG:3005).
Start: census thread's land-clipped full-resolution districts (analysis/census/maps/ed2023_full_clipped_3005.gpkg;
Elections BC 2023 boundaries from BCGW clipped to the union of GeoBC Freshwater Atlas watershed groups, 1:20,000).
1. Codes/names/ids checked against geo/out/ed2023.geojson (Elections BC as published).
2. Artifact removal: interior rings < 1 m2 (one found: a 0.003 m2 triangular gap in the FWA watershed-group union where
   four groups meet (MFRT, SAHT, LFRT, TSEA) at 59.371 N, 122.125 W; no lake there; not in the Elections BC polygon).
3. Lakes: FWA lakes (1:20,000) pieces dissolved by WATERBODY_KEY; every lake >= 50 km2 is cut out
   (islands in lakes are holes in FWA lake polygons, so they stay with the district).
Outputs (out/final/):
  FINAL_ed2023_land_3005.gpkg          land-clipped, no lake cut-outs
  FINAL_ed2023_land_lakes_3005.gpkg    land-clipped, lakes >= 50 km2 removed  (master for all derived files)
  FINAL_lakes_ge50km2_3005.gpkg        the lakes removed (dissolved, clipped to BC districts), for display
  final_lakes_by_district.csv          lake area removed per district"""
import os
import geopandas as gpd, pandas as pd, numpy as np, shapely

R = "analysis/geo/"
F = R + "out/final/"
os.makedirs(F, exist_ok=True)
src = gpd.read_file("analysis/census/maps/ed2023_full_clipped_3005.gpkg")
ref = gpd.read_file(R + "out/ed2023.geojson")
j = ref[["ed_code", "ed_name", "ebc_ed_id"]].merge(src[["ed_code", "ed_name", "ebc_ed_id"]], on="ed_code", how="outer",
                                                   suffixes=("", "_census"), indicator=True)
assert (j._merge == "both").all() and (j.ed_name == j.ed_name_census).all() and (j.ebc_ed_id == j.ebc_ed_id_census).all()
print("codes/names/ids identical for", len(j))


def drop_tiny_holes(g, min_area=1.0):
    out, removed = [], []
    for p in shapely.get_parts(g):
        keep = [r for r in p.interiors if shapely.Polygon(r).area >= min_area]
        removed += [shapely.Polygon(r) for r in p.interiors if shapely.Polygon(r).area < min_area]
        out.append(shapely.Polygon(p.exterior, keep))
    return shapely.MultiPolygon(out), removed


land = src[["ed_code", "ed_name", "ebc_ed_id", "geometry"]].copy()
art = []
geoms = []
for c, g in zip(land.ed_code, land.geometry):
    ng, rem = drop_tiny_holes(g)
    art += [(c, r.area, *gpd.GeoSeries([r.centroid], crs=3005).to_crs(4326).iloc[0].coords[0]) for r in rem]
    geoms.append(ng)
land["geometry"] = geoms
pd.DataFrame(art, columns=["ed_code", "area_m2", "lon", "lat"]).to_csv(F + "final_artifacts_removed.csv", index=False)
print("artifacts removed:", art)
assert land.is_valid.all()
land["area_land_km2"] = land.area / 1e6
land["n_parts"] = shapely.get_num_geometries(land.geometry.values)
land.to_file(F + "FINAL_ed2023_land_3005.gpkg", driver="GPKG")

# ---- lakes
lk = gpd.read_file(R + "raw/fwa/fwa_lakes_ge100ha.geojson").to_crs(3005)
lk["geometry"] = lk.geometry.make_valid()
d = lk.dissolve("WATERBODY_KEY", aggfunc={"AREA_HA": "sum", "GNIS_NAME_1": "first", "WATERSHED_GROUP_CODE": lambda s: ",".join(sorted(set(s)))}).reset_index()
d["area_km2_fwa"] = d.AREA_HA / 100
big = d[d.area_km2_fwa >= 50].copy()
big["geometry"] = big.geometry.make_valid()
big = big.rename(columns={"GNIS_NAME_1": "lake_name", "WATERBODY_KEY": "waterbody_key", "WATERSHED_GROUP_CODE": "wsg"})
print("lakes >= 50 km2:", len(big))
lakes_u = shapely.union_all(big.geometry.values)
geoms, rows = [], []
for c, g in zip(land.ed_code, land.geometry):
    ng = shapely.make_valid(shapely.difference(g, lakes_u))
    polys = [q for q in shapely.get_parts(ng) if q.geom_type == "Polygon" and q.area > 0]
    polys = [q for p in polys for q in ([p] if p.geom_type == "Polygon" else shapely.get_parts(p))]
    geoms.append(shapely.MultiPolygon(polys))
    rows.append((c, (g.area - shapely.MultiPolygon(polys).area) / 1e6))
ll = land.copy()
ll["geometry"] = geoms
assert ll.is_valid.all()
ll["area_land_km2"] = land.area / 1e6
ll["area_land_nolakes_km2"] = ll.area / 1e6
ll["n_parts"] = shapely.get_num_geometries(ll.geometry.values)
ll.to_file(F + "FINAL_ed2023_land_lakes_3005.gpkg", driver="GPKG")
pd.DataFrame(rows, columns=["ed_code", "lake_km2_removed"]).merge(ll[["ed_code", "ed_name", "area_land_km2", "area_land_nolakes_km2"]]) \
    .round(3).to_csv(F + "final_lakes_by_district.csv", index=False)
# lakes for display, clipped to the district union (drops parts of Atlin/Tagish/Teslin in Yukon, Koocanusa in Montana)
bcu = shapely.union_all(land.geometry.values)
big["geometry"] = [shapely.make_valid(shapely.intersection(g, bcu)) for g in big.geometry]
big["area_km2_in_bc"] = big.area / 1e6
big[["waterbody_key", "lake_name", "wsg", "area_km2_fwa", "area_km2_in_bc", "geometry"]].sort_values("area_km2_fwa", ascending=False) \
    .to_file(F + "FINAL_lakes_ge50km2_3005.gpkg", driver="GPKG")
# overlap check
g = ll.geometry.values
a, b = shapely.STRtree(g).query(g, predicate="intersects")
m = a < b
ov = sum(shapely.intersection(g[i], g[k]).area for i, k in zip(a[m], b[m]))
print("land_lakes valid", ll.is_valid.all(), "overlap m2", ov, "total km2", round(ll.area.sum() / 1e6), "lakes km2 removed", round(sum(r[1] for r in rows)))
