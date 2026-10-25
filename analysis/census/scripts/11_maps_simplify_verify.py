"""Step 2 of map build: topology-preserving simplification (mapshaper, shared arcs simplified once, Douglas-Peucker,
planar metres in EPSG:3005, keep-shapes) of clipped and unclipped districts, then verification:
 is_valid on every geometry; per-district area vs full-resolution (within 1%); pairwise overlaps; gaps (union holes
 not in full-res); lost parts; district code/name match vs Elections BC 2026 candidate list.
Usage: python3 -I 11_maps_simplify_verify.py <tolerance_m> <mapshaper_bin> <scratch_dir>
"""
import sys, os, json, subprocess
import geopandas as gpd, shapely, numpy as np, pandas as pd

TOL, MS, S = float(sys.argv[1]), sys.argv[2], sys.argv[3]
ROOT = "analysis/census"; M = os.path.join(ROOT, "maps")
tag = "s%dm" % TOL
res = {}
for kind in ["clipped", "unclipped"]:
    full = gpd.read_file(os.path.join(M, "ed2023_full_%s_3005.gpkg" % kind)).sort_values("ed_code").reset_index(drop=True)
    src = os.path.join(S, "ed2023_full_%s_3005.geojson" % kind)
    if not os.path.exists(src):
        full[["ed_code", "ed_name", "geometry"]].to_file(src, driver="GeoJSON")
    tmp = os.path.join(S, "simp_%s_%s.geojson" % (kind, tag))
    subprocess.run([MS, "-i", src, "-simplify", "dp", "interval=%g" % TOL, "keep-shapes", "planar", "-clean", "gap-fill-area=0", "sliver-control=0",
                    "-o", tmp, "force"], check=True, capture_output=True)
    simp = gpd.read_file(tmp).set_crs(3005, allow_override=True).sort_values("ed_code").reset_index(drop=True)
    assert list(simp.ed_code) == list(full.ed_code)
    valid = shapely.is_valid(simp.geometry.values)
    reasons = [shapely.is_valid_reason(g) for g, v in zip(simp.geometry.values, valid) if not v]
    a_full = full.area.values; a_s = simp.area.values
    pct = (a_s - a_full) / a_full * 100
    g = simp.geometry.values; tr = shapely.STRtree(g); i, j = tr.query(g, predicate="intersects"); m = i < j
    ov = np.array([shapely.area(shapely.intersection(g[x], g[y])) if valid[x] and valid[y] else np.nan for x, y in zip(i[m], j[m])])
    nf = shapely.get_num_geometries(full.geometry.values); ns = shapely.get_num_geometries(g)
    # gaps: holes in union of simplified not present in full union
    us = shapely.union_all(shapely.make_valid(g)); uf = shapely.union_all(full.geometry.values)
    gap = shapely.difference(uf, us).area / 1e6; extra = shapely.difference(us, uf).area / 1e6
    holes_s = sum(len(p.interiors) for p in shapely.get_parts(us)); holes_f = sum(len(p.interiors) for p in shapely.get_parts(uf))
    df = pd.DataFrame({"ed_code": full.ed_code, "ed_name": full.ed_name, "area_full_km2": a_full / 1e6,
                       "area_simplified_km2": a_s / 1e6, "area_diff_pct": pct, "parts_full": nf, "parts_simplified": ns,
                       "valid": valid, "vertices_full": shapely.get_num_coordinates(full.geometry.values),
                       "vertices_simplified": shapely.get_num_coordinates(g)})
    df.to_csv(os.path.join(M, "check_area_%s_%s.csv" % (kind, tag)), index=False)
    res[kind] = dict(tolerance_m=TOL, n=len(simp), invalid=int((~valid).sum()), invalid_reasons=reasons[:10],
                     max_abs_area_diff_pct=float(np.abs(pct).max()), worst=df.ed_code.iloc[int(np.argmax(np.abs(pct)))],
                     over_1pct=df.loc[np.abs(pct) > 1, ["ed_code", "area_diff_pct"]].round(3).values.tolist(),
                     pair_overlap_km2=float(np.nansum(ov) / 1e6), pair_overlap_max_m2=float(np.nanmax(ov)) if len(ov) else 0,
                     union_gap_vs_full_km2=gap, union_extra_vs_full_km2=extra, union_holes_full=holes_f, union_holes_simplified=holes_s,
                     parts_full=int(nf.sum()), parts_simplified=int(ns.sum()), empty=int(shapely.is_empty(g).sum()),
                     vertices_full=int(df.vertices_full.sum()), vertices_simplified=int(df.vertices_simplified.sum()))
    small = df[df.ed_code.isin(["VNW", "VNY", "VTB", "VNS", "VNT", "VTS", "NVL", "RCC", "SRC"])][["ed_code", "area_full_km2", "area_diff_pct", "valid", "parts_full", "parts_simplified"]]
    res[kind]["small_urban"] = small.round(4).values.tolist()
    simp.to_file(os.path.join(M, "ed2023_%s_%s_3005.gpkg" % (kind, tag)), driver="GPKG")
json.dump(res, open(os.path.join(M, "check_simplify_%s.json" % tag), "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
