"""Step 1 of map build: full-resolution 2023 electoral districts (Elections BC via BCGW, EPSG:3005), unclipped and
land-clipped with the GeoBC Freshwater Atlas Watershed Groups (1:20,000; coastal groups are bounded by the FWA
coastline, so their union is BC land incl. lakes/rivers, excluding ocean).
Outputs (maps/):
  ed2023_full_unclipped_3005.gpkg  ed2023_full_clipped_3005.gpkg  bc_land_fwa_3005.gpkg
"""
import geopandas as gpd, shapely, numpy as np, os, sys, json

ROOT = "analysis/census"
M = os.path.join(ROOT, "maps"); os.makedirs(M, exist_ok=True)
ed = gpd.read_file("analysis/geo/raw/bcgw/ed2023.geojson").to_crs(3005)
ed = ed[["ED_ABBREVIATION", "ED_NAME", "ELECTORAL_DISTRICT_ID", "FEATURE_AREA_SQM", "geometry"]].rename(
    columns={"ED_ABBREVIATION": "ed_code", "ED_NAME": "ed_name", "ELECTORAL_DISTRICT_ID": "ebc_ed_id"})
ed = ed.sort_values("ed_code").reset_index(drop=True)
assert len(ed) == 93 and ed.is_valid.all()
ed.to_file(os.path.join(M, "ed2023_full_unclipped_3005.gpkg"), driver="GPKG")

ws = gpd.read_file(os.path.join(ROOT, "raw/bcgw/fwa_watershed_groups.geojson")).to_crs(3005)
land = shapely.union_all(shapely.make_valid(ws.geometry.values))
gpd.GeoDataFrame({"src": ["FWA_WATERSHED_GROUPS_POLY union"]}, geometry=[land], crs=3005).to_file(
    os.path.join(M, "bc_land_fwa_3005.gpkg"), driver="GPKG")
parts = shapely.get_parts(land)
tree = shapely.STRtree(parts)
out = []
for g in ed.geometry.values:
    idx = tree.query(g, predicate="intersects")
    cand = shapely.union_all(parts[idx]) if len(idx) else shapely.Polygon()
    c = shapely.make_valid(shapely.intersection(g, cand))
    polys = [p for p in shapely.get_parts(c) if p.geom_type == "Polygon" and p.area > 0]
    if c.geom_type == "GeometryCollection":
        polys = [q for p in shapely.get_parts(c) for q in shapely.get_parts(p) if q.geom_type == "Polygon"]
    out.append(shapely.MultiPolygon(polys))
cl = ed.copy(); cl["geometry"] = out
assert cl.is_valid.all(), "invalid clipped"
cl["area_unclipped_km2"] = ed.area / 1e6
cl["area_land_km2"] = cl.area / 1e6
cl["n_parts"] = shapely.get_num_geometries(cl.geometry.values)
cl.to_file(os.path.join(M, "ed2023_full_clipped_3005.gpkg"), driver="GPKG")
# overlap check
g = cl.geometry.values; a, b = shapely.STRtree(g).query(g, predicate="intersects"); m = a < b
ov = np.array([shapely.intersection(g[i], g[j]).area for i, j in zip(a[m], b[m])])
print("clipped: valid", cl.is_valid.all(), "pairwise overlap m2 total", ov.sum(), "max", ov.max())
print(cl[["ed_code", "area_unclipped_km2", "area_land_km2", "n_parts"]].sort_values("n_parts").tail(8))
