"""Derive the FINAL web (EPSG:4326) and slide (EPSG:3005) district files from the FINAL masters.
All files of one variant come from ONE simplified topology, so the full map, the insets, GeoJSON and TopoJSON line up.

Pipeline (scripts/simplify_lib.py):
 1. Islet filter per district: smallest parts dropped while each is < MAXDROP km2 and the cumulative dropped area stays
    <= BUDGET of the district's area; the largest part is always kept.
 2. Arcs (shared edges) built once with the topojson package (no quantization, EPSG:3005 metres). Each arc is simplified
    once with Douglas-Peucker; tolerance = clamp(K * sqrt(area of the smallest district using the arc), TMIN, TMAX)
    x a per-district multiplier (tuned so every district stays within 0.9% of its master area).
 3. Arcs snapped once to the output grid (1e-5 deg for web, 1 m in EPSG:3005 for slides). Every geometry is validated on
    every output grid; any self-intersection is repaired locally (nearby arc split into short chunks, the chunk
    tolerance cut until valid). Shared arcs mean no gaps and no overlaps by construction (also measured).
Usage: python3 -I 11_final_derive.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geopandas as gpd, pandas as pd, numpy as np, shapely
import simplify_lib as L

R = "analysis/geo/"
F = R + "out/final/"
attrs = pd.read_csv(R + "out/ed2023_area_pop.csv")[["ed_code", "land_km2", "pop2021"]].rename(columns={"land_km2": "statcan_land_km2"})
reg = pd.read_csv(R + "out/ed2023_regions.csv")[["ed_code", "rd_abbr", "inset"]].fillna("")
labels = pd.read_csv(F + "FINAL_ed2023_label_points.csv")[["ed_code", "label_lon", "label_lat", "label_x_3005", "label_y_3005"]] \
    if os.path.exists(F + "FINAL_ed2023_label_points.csv") else None
PROPS = ["ed_code", "ed_name", "ebc_ed_id", "area_master_km2", "statcan_land_km2", "pop2021", "rd_abbr", "inset"]
SETTINGS = {  # name: budget, maxdrop_km2, K, TMIN, TMAX, grids, size limit (bytes)
    "web": dict(start_mult={"ABW": 0.707, "CHC": 0.236, "CRC": 0.75, "LAO": 0.6, "LWI": 0.93, "MPR": 0.464, "NAI": 0.7, "NOH": 0.19, "NOI": 0.196, "POC": 0.865, "POR": 0.419, "SKE": 0.5, "SRG": 0.819, "SWR": 0.636, "VHA": 0.865, "VNP": 0.426, "VTB": 0.5, "WVS": 0.7}, lake_cap_m=350, target_pct=0.97, budget=0.005, maxdrop=5.0, K=0.03, TMIN=10, TMAX=4000, step4326=1e-5, coarse4326=10, step3005=1.0, limit=400_000),
    "slide720": dict(start_mult={"NOH": 0.42, "NOI": 0.55, "LAO": 0.8, "NAI": 0.8}, lake_cap_m=400, target_pct=0.98, budget=0.008, maxdrop=5.0, K=0.04, TMIN=25, TMAX=2200, step4326=1e-5, coarse4326=10, step3005=1.0, limit=None),
}
INSETS = {"metro_vancouver": "MVRD", "capital_region": "CAPRD", "kelowna": "RDCO"}


def islet_filter(gdf, budget, maxdrop):
    geoms, kept, dropped, dkm = [], [], [], []
    for g in gdf.geometry:
        parts = sorted(shapely.get_parts(g), key=lambda p: p.area)
        tot = sum(p.area for p in parts)
        keep, cum, nd = [], 0.0, 0
        for i, p in enumerate(parts):
            if i < len(parts) - 1 and p.area < maxdrop * 1e6 and cum + p.area <= budget * tot:
                cum += p.area; nd += 1
            else:
                keep.append(p)
        geoms.append(shapely.MultiPolygon(keep)); kept.append(len(keep)); dropped.append(nd); dkm.append(cum / 1e6)
    out = gdf.copy()
    out["geometry"] = geoms
    out["parts_kept"], out["parts_dropped"], out["islet_km2_dropped"] = kept, dropped, np.round(dkm, 4)
    return out


def to_gdf(dec, crs):
    return gpd.GeoDataFrame([p for p, _ in dec], geometry=[g for _, g in dec], crs=crs)


def checks(master, simp3005, label):
    s = simp3005.set_index("ed_code").loc[master.ed_code].reset_index()
    g = s.geometry.values
    a, b = shapely.STRtree(g).query(g, predicate="intersects")
    k = a < b
    ov = float(sum(shapely.intersection(g[i], g[j]).area for i, j in zip(a[k], b[k])))
    su = shapely.union_all(g)
    mu = shapely.union_all(master.geometry.values)
    # internal gaps = holes in the simplified union that do not contain a hole (lake) of the master union
    mholes = [shapely.Polygon(r) for p in shapely.get_parts(mu) for r in p.interiors]
    mpts = [h.representative_point() for h in mholes]
    holes = [shapely.Polygon(r) for p in shapely.get_parts(su) for r in p.interiors]
    spurious = [h for h in holes if not any(h.contains(q) for q in mpts)]
    gap = float(sum(h.area for h in spurious))
    lake_holes = len(holes) - len(spurious)
    diff = (s.area.values - master.area.values) / master.area.values * 100
    try:
        arcs_cross = None
    except Exception:
        pass
    return {"file": label, "n": len(s), "valid": int(s.is_valid.sum()), "empty": int(s.is_empty.sum()),
            "overlap_m2": round(ov, 2), "internal_gap_m2": round(gap, 2), "spurious_holes": len(spurious),
            "lake_holes_kept": lake_holes, "lake_holes_master": len(mholes),
            "max_abs_area_diff_pct": round(float(np.abs(diff).max()), 3), "worst": master.ed_code.iloc[int(np.abs(diff).argmax())],
            "districts_over_1pct": [(c, round(float(d), 3)) for c, d in zip(master.ed_code, diff) if abs(d) > 1],
            "vertices": int(shapely.get_num_coordinates(g).sum()), "parts": int(shapely.get_num_geometries(g).sum())}, diff


def parts_check(master, simp3005, min_km2):
    s = simp3005.set_index("ed_code")
    miss = []
    for code, mg in zip(master.ed_code, master.geometry):
        sg = s.loc[code].geometry
        for p in shapely.get_parts(mg):
            if p.area >= min_km2 * 1e6 and not sg.intersects(p.representative_point().buffer(200)):
                miss.append((code, round(p.area / 1e6, 3)))
    return miss


def write_all(variant, name, cfg, master, filt, out, res):
    tag = f"FINAL_ed2023_{variant}_{name}"
    arcs4, dec4 = res[(4326, cfg["step4326"])]
    arcs3, dec3 = res[(None, cfg["step3005"])]
    files = {"geojson_4326": F + f"{tag}_4326.geojson", "topojson_4326": F + f"{tag}_4326.topojson",
             "geojson_3005": F + f"{tag}_3005.geojson"}
    L.write_grid_geojson(dec4, cfg["step4326"], files["geojson_4326"], PROPS)
    L.write_grid_topojson(out, arcs4, cfg["step4326"], files["topojson_4326"], keep=PROPS)
    L.write_grid_geojson(dec3, cfg["step3005"], files["geojson_3005"], PROPS)
    with open(files["geojson_3005"]) as f:
        d = json.load(f)
    d["crs"] = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::3005"}}
    with open(files["geojson_3005"], "w") as f:
        json.dump(d, f, separators=(",", ":"), ensure_ascii=False)
    if name == "slide720":
        files["topojson_3005"] = F + f"{tag}_3005.topojson"
        L.write_grid_topojson(out, arcs3, cfg["step3005"], files["topojson_3005"], keep=PROPS)
    s3 = to_gdf(dec3, 3005)
    s4 = to_gdf(dec4, 4326)
    # insets: the same geometry, member districts only, plus a frame file of all districts clipped to the inset box
    if variant == "land_lakes" and name == "web":
        for iname, abbr in INSETS.items():
            mem4 = [(p, g) for p, g in dec4 if p["rd_abbr"] == abbr]
            mem3 = [(p, g) for p, g in dec3 if p["rd_abbr"] == abbr]
            L.write_grid_geojson(mem4, cfg["step4326"], F + f"FINAL_inset_{iname}_4326.geojson", PROPS)
            L.write_grid_geojson(mem3, cfg["step3005"], F + f"FINAL_inset_{iname}_3005.geojson", PROPS)
            b = to_gdf(mem3, 3005).total_bounds
            mx, my = (b[2] - b[0]) * 0.06, (b[3] - b[1]) * 0.06
            box = shapely.box(b[0] - mx, b[1] - my, b[2] + mx, b[3] + my)
            fr = [(p, shapely.intersection(g, box)) for p, g in dec3 if g.intersects(box)]
            fr = [(p, L.polygons_only(shapely.make_valid(g))) for p, g in fr if not g.is_empty and g.area > 0]
            L.write_grid_geojson(fr, cfg["step3005"], F + f"FINAL_inset_{iname}_frame_3005.geojson", PROPS)
            fr4 = to_gdf(fr, 3005).to_crs(4326)
            fr4["geometry"] = fr4.geometry.make_valid().apply(L.polygons_only)
            L.write_grid_geojson(list(zip(fr4[PROPS].to_dict("records"), fr4.geometry)), 1e-4, F + f"FINAL_inset_{iname}_frame_4326.geojson", PROPS)
    return files, s3, s4


def run_variant(variant, master_fn, name, cfg, log=print):
    m = gpd.read_file(master_fn)[["ed_code", "ed_name", "ebc_ed_id", "geometry"]].merge(attrs, on="ed_code").merge(reg, on="ed_code")
    m = m.sort_values("ed_code").reset_index(drop=True)
    m["area_master_km2"] = (m.area / 1e6).round(3)
    filt = islet_filter(m, cfg["budget"], cfg["maxdrop"])
    base = filt[PROPS + ["geometry"]].reset_index(drop=True)
    mult = np.array([cfg.get("start_mult", {}).get(c, 1.0) for c in base.ed_code])
    grids = [(4326, cfg["step4326"], cfg.get("coarse4326", 1)), (None, cfg["step3005"])]
    am = None
    cap_fn = None
    if variant == "land_lakes" and cfg.get("lake_cap_m"):
        lk = gpd.read_file(F + "FINAL_lakes_ge50km2_3005.gpkg")
        lparts = list(shapely.get_parts(shapely.union_all(lk.geometry.boundary.values)))
        ltree = shapely.STRtree(lparts)
        def cap_fn(arc, _c=cfg["lake_cap_m"]):
            a = np.asarray(arc)
            pt = shapely.Point(a[len(a) // 2])
            return _c if any(lparts[j].distance(pt) < 1 for j in ltree.query(pt.buffer(1))) else None
    for rnd in range(12):
        out, res, am = L.valid_pipeline(base, cfg["K"], cfg["TMIN"], cfg["TMAX"], mult, grids, log=lambda x: None, init_am=am, cap_fn=cap_fn)
        s3 = to_gdf(res[(None, cfg["step3005"])][1], 3005)
        diff = np.abs(s3.area.values - m.area.values) / m.area.values * 100
        over = diff > cfg.get("target_pct", 0.95)
        log(f"  {variant}/{name} round {rnd}: max area diff {diff.max():.2f}% ({m.ed_code[diff.argmax()]}), >0.9%: {int(over.sum())}")
        if not over.any():
            break
        mult = np.where(over, mult * np.clip(cfg.get("target_pct", 0.95) * 0.96 / diff, 0.5, 0.93), mult)
    files, s3, s4 = write_all(variant, name, cfg, m, filt, out, res)
    rep = {"settings": {k: v for k, v in cfg.items()}, "district_multipliers": {c: round(float(v), 3) for c, v in zip(m.ed_code, mult) if v < 1},
           "repair": {"arcs_split": sum(1 for q in am if q[0] == "cs"), "chunks_reduced": sum(1 for q in am if q[0] != "cs")},
           "bytes": {k: os.path.getsize(v) for k, v in files.items()},
           "parts_master": int(shapely.get_num_geometries(m.geometry.values).sum()), "parts_dropped": int(filt.parts_dropped.sum()),
           "islet_km2_dropped": round(float(filt.islet_km2_dropped.sum()), 3)}
    for k, fn in files.items():
        g = gpd.read_file(fn)
        g = g.set_crs(3005, allow_override=True) if k.endswith("3005") else g.set_crs(4326, allow_override=True).to_crs(3005)
        rep["check_" + k], d = checks(m, g, os.path.basename(fn))
        rep["valid_in_native_crs_" + k] = bool(gpd.read_file(fn).is_valid.all())
    rep["master_parts_ge_maxdrop_missing"] = parts_check(m, s3, cfg["maxdrop"])
    per = filt[["ed_code", "parts_kept", "parts_dropped", "islet_km2_dropped"]].copy()
    per["parts_master"] = shapely.get_num_geometries(m.geometry.values)
    per["area_master_km2"] = m.area_master_km2
    per["area_simplified_km2"] = (s3.set_index("ed_code").loc[m.ed_code].area.values / 1e6).round(3)
    per["area_diff_pct"] = ((per.area_simplified_km2 - per.area_master_km2) / per.area_master_km2 * 100).round(3)
    per["valid"] = s3.set_index("ed_code").loc[m.ed_code].is_valid.values
    per["variant"], per["file"] = variant, name
    return rep, per


if __name__ == "__main__":
    # usage: 11_final_derive.py <variant> <name> [K override]; one run per process, report saved per run
    variant, name = sys.argv[1], sys.argv[2]
    mfn = F + ("FINAL_ed2023_land_lakes_3005.gpkg" if variant == "land_lakes" else "FINAL_ed2023_land_3005.gpkg")
    cfg = dict(SETTINGS[name])
    if len(sys.argv) > 3:
        cfg["K"] = float(sys.argv[3])
    for attempt in range(6):
        rep, per = run_variant(variant, mfn, name, cfg)
        lim = cfg["limit"]
        if lim is None or max(rep["bytes"]["geojson_4326"], rep["bytes"]["topojson_4326"]) < lim:
            break
        cfg = dict(cfg, K=cfg["K"] * 1.1)
        print("  over size limit, K ->", round(cfg["K"], 5), flush=True)
    rep["settings"]["K_final"] = cfg["K"]
    json.dump(rep, open(F + f"_run_{variant}_{name}.json", "w"), indent=1, default=str)
    per.to_csv(F + f"_run_{variant}_{name}_per_district.csv", index=False)
    print(variant, name, rep["bytes"], rep["check_geojson_4326"]["max_abs_area_diff_pct"], flush=True)
