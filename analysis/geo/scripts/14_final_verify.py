"""Independent verification of every FINAL derived file against its full-resolution master.
Per file: is_valid for every geometry, empty geometries, pairwise overlap area, spurious internal holes (holes in the
simplified union that do not correspond to a master hole such as a cut-out lake), per-district area difference vs master,
districts outside +-1%, small districts (< 20 km2) present with one part, every master part >= 5 km2 still represented,
and file size. Also: label points inside every land_lakes file.
Out: out/final/FINAL_verification.json, out/final/FINAL_verification_per_district.csv"""
import glob, json, os
import geopandas as gpd, pandas as pd, numpy as np, shapely

F = "analysis/geo/out/final/"
masters = {v: gpd.read_file(F + f"FINAL_ed2023_{v}_3005.gpkg").sort_values("ed_code").reset_index(drop=True) for v in ["land_lakes", "land"]}
lab = pd.read_csv(F + "FINAL_ed2023_label_points.csv")
labpts = dict(zip(lab.ed_code, shapely.points(lab.label_x_3005, lab.label_y_3005)))
rep, per = {}, []
for fn in sorted(glob.glob(F + "FINAL_ed2023_land*_*.*json")):
    base = os.path.basename(fn)
    variant = "land_lakes" if "land_lakes" in base else "land"
    m = masters[variant]
    g = gpd.read_file(fn)
    g = g.set_crs(3005, allow_override=True) if "_3005." in base else g.set_crs(4326, allow_override=True)
    native_valid = bool(g.is_valid.all())
    native_invalid = g.ed_code[~g.is_valid].tolist()
    g3 = g.to_crs(3005).set_index("ed_code").loc[m.ed_code].reset_index()
    geo = g3.geometry.values
    a, b = shapely.STRtree(geo).query(geo, predicate="intersects")
    k = a < b
    ovl = [(g3.ed_code[i], g3.ed_code[j], shapely.intersection(geo[i], geo[j]).area) for i, j in zip(a[k], b[k])]
    ov = float(sum(x[2] for x in ovl))
    su, mu = shapely.union_all(geo), shapely.union_all(m.geometry.values)
    mholes = [shapely.Polygon(r) for p in shapely.get_parts(mu) for r in p.interiors]
    mpts = [h.representative_point() for h in mholes]
    holes = [shapely.Polygon(r) for p in shapely.get_parts(su) for r in p.interiors]
    spur = [h for h in holes if not any(h.contains(q) for q in mpts)]
    diff = (g3.area.values - m.area.values) / m.area.values * 100
    small = m.area.values < 20e6
    small_ok = all((not g3.geometry[i].is_empty) and g3.geometry[i].area > 0 for i in np.where(small)[0])
    miss = []
    for code, mg, sg in zip(m.ed_code, m.geometry, geo):
        for p in shapely.get_parts(mg):
            if p.area >= 5e6 and not sg.intersects(p.representative_point().buffer(250)):
                miss.append((code, round(p.area / 1e6, 2)))
    lab_in = int(sum(sg.contains(labpts[c]) for c, sg in zip(m.ed_code, geo)))
    rep[base] = {"bytes": os.path.getsize(fn), "n": len(g), "valid_native_crs": native_valid, "invalid": native_invalid,
                 "valid_in_3005": int(g3.is_valid.sum()), "empty": int(g3.is_empty.sum()),
                 "overlap_m2": round(ov, 3), "overlap_pairs_gt_1m2": [(x[0], x[1], round(x[2], 1)) for x in ovl if x[2] > 1],
                 "spurious_holes": len(spur), "spurious_hole_m2": round(float(sum(h.area for h in spur)), 1),
                 "lake_holes_master": len(mholes), "lake_holes_kept": len(holes) - len(spur),
                 "max_abs_area_diff_pct": round(float(np.abs(diff).max()), 3), "worst": m.ed_code[int(np.abs(diff).argmax())],
                 "districts_over_1pct": [(c, round(float(d), 3)) for c, d in zip(m.ed_code, diff) if abs(d) > 1],
                 "small_districts_lt20km2": int(small.sum()), "small_districts_present": small_ok,
                 "master_parts_ge5km2_missing": miss, "label_points_inside": lab_in,
                 "vertices": int(shapely.get_num_coordinates(geo).sum()), "parts": int(shapely.get_num_geometries(geo).sum())}
    per.append(pd.DataFrame({"file": base, "ed_code": m.ed_code, "area_master_km2": (m.area / 1e6).round(4).values,
                             "area_file_km2": (g3.area / 1e6).round(4).values, "diff_pct": diff.round(4),
                             "parts_master": shapely.get_num_geometries(m.geometry.values),
                             "parts_file": shapely.get_num_geometries(geo), "valid": g3.is_valid.values}))
    r = rep[base]
    print(base, r["bytes"], "valid", r["valid_native_crs"], "ovl", r["overlap_m2"], "spur", r["spurious_holes"], "maxdiff", r["max_abs_area_diff_pct"], r["worst"],
          ">1%", len(r["districts_over_1pct"]), "miss", len(r["master_parts_ge5km2_missing"]), "labels", r["label_points_inside"], flush=True)
json.dump(rep, open(F + "FINAL_verification.json", "w"), indent=1, default=str)
pd.concat(per).to_csv(F + "FINAL_verification_per_district.csv", index=False)
