"""Build 2023 (93) and 2015 (87) electoral district outputs, web and slide simplifications, regions and insets.
Simplification works on shared arcs (simplify_lib), so neighbouring districts keep identical edges: no gaps
or overlaps. Per-arc Douglas-Peucker tolerance = clip(k * sqrt(area of smallest district on the arc), tmin, tmax)
in BC Albers metres, so small urban districts keep detail while large rural ones are thinned."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geopandas as gpd, pandas as pd, numpy as np
from shapely.geometry.polygon import orient
from shapely.geometry import MultiPolygon
from simplify_lib import simplify, polygons_only, write_topojson

R = "analysis/geo/"
O = R + "out/"
S = R + "out/_tmp.geojson"


def rfc_orient(g):
    g = polygons_only(g)
    if g.geom_type == "Polygon":
        return orient(g, 1.0)
    return MultiPolygon([orient(p, 1.0) for p in g.geoms])


def write_geojson(gdf, fn, dp):
    g = gdf.to_crs(4326).copy()
    g["geometry"] = g.geometry.apply(rfc_orient)
    if os.path.exists(fn):
        os.remove(fn)
    g.to_file(fn, driver="GeoJSON", COORDINATE_PRECISION=dp)


def kb(fn):
    return round(os.path.getsize(fn) / 1024, 1)


def check(gdf):
    g = gdf.to_crs(3005)
    o = gpd.overlay(g[["ed_code", "geometry"]], g[["ed_code", "geometry"]], keep_geom_type=True)
    o = o[o.ed_code_1 != o.ed_code_2]
    u = g.union_all()
    holes = sum(sum(p.__class__(r).area for r in p.interiors) for p in getattr(u, "geoms", [u]))
    return {"invalid": int((~g.is_valid).sum()), "overlap_m2": round(float(o.area.sum()), 1),
            "interior_gap_m2": round(float(holes), 1), "n": len(g)}


ed = gpd.read_file(R + "raw/bcgw/ed2023.geojson")
ed = ed.rename(columns={"ED_ABBREVIATION": "ed_code", "ED_NAME": "ed_name", "ELECTORAL_DISTRICT_ID": "ebc_ed_id"})
ed = ed[["ed_code", "ed_name", "ebc_ed_id", "geometry"]].sort_values("ed_code").reset_index(drop=True)
ed = ed.to_crs(3005)
assert len(ed) == 93 and ed.ed_code.is_unique and ed.is_valid.all()
ed["area_km2"] = (ed.area / 1e6).round(1)
pop = pd.read_csv(O + "ed2023_pop2021_from_db.csv").rename(columns={"ED_ABBREVIATION": "ed_code"})
ed = ed.merge(pop, on="ed_code", how="left")
ed["pop2021"] = ed.pop2021.round(0).astype(int)
# land area: StatCan 2021 block LANDAREA (km2) allocated with the same block-to-district fractions
_dbl = gpd.read_file(R + "raw/statcan/db_digital.geojson", ignore_geometry=True)[["DBUID", "LANDAREA"]]
_dba = pd.read_csv(O + "db_to_ed2023.csv", dtype={"DBUID": str}).merge(_dbl, on="DBUID")
ed["land_km2"] = ed.ed_code.map((_dba.LANDAREA * _dba.frac).groupby(_dba.ED_ABBREVIATION).sum().round(1))
ed["pop_per_land_km2"] = (ed.pop2021 / ed.land_km2).round(1)

# ---- regions: district representative point (always inside the district) within a regional district
rd = gpd.read_file(R + "raw/bcgw/regional_districts.geojson").to_crs(3005)[["ADMIN_AREA_NAME", "ADMIN_AREA_ABBREVIATION", "geometry"]]
pts = ed[["ed_code", "geometry"]].copy()
pts["geometry"] = pts.geometry.representative_point()
j = gpd.sjoin(pts, rd, how="left", predicate="within").drop_duplicates("ed_code")
ed = ed.merge(j[["ed_code", "ADMIN_AREA_NAME", "ADMIN_AREA_ABBREVIATION"]].rename(
    columns={"ADMIN_AREA_NAME": "regional_district", "ADMIN_AREA_ABBREVIATION": "rd_abbr"}), on="ed_code")
ov = gpd.overlay(ed[["ed_code", "geometry"]], rd, how="intersection", keep_geom_type=True)
ov["a"] = ov.area
ov = ov.groupby(["ed_code", "ADMIN_AREA_ABBREVIATION"]).a.sum().reset_index()
ov["share"] = ov.a / ov.groupby("ed_code").a.transform("sum")
ed = ed.merge(ov.rename(columns={"ADMIN_AREA_ABBREVIATION": "rd_abbr", "share": "area_share_in_rd"})[["ed_code", "rd_abbr", "area_share_in_rd"]],
              on=["ed_code", "rd_abbr"], how="left")
ed["area_share_in_rd"] = ed.area_share_in_rd.round(3)
# population share inside the assigned RD, from dissemination blocks (representative points)
dbp = pd.read_csv(O + "db_to_ed2023.csv", dtype={"DBUID": str})
dbg = gpd.read_file(R + "raw/statcan/db_digital.geojson")[["DBUID", "DBRPLAMX", "DBRPLAMY"]]
dbg = gpd.GeoDataFrame(dbg[["DBUID"]], geometry=gpd.points_from_xy(dbg.DBRPLAMX, dbg.DBRPLAMY), crs=3347).to_crs(3005)
dbg = gpd.sjoin(dbg, rd, how="left", predicate="within").drop_duplicates("DBUID")[["DBUID", "ADMIN_AREA_ABBREVIATION"]]
dbp = dbp.merge(dbg, on="DBUID", how="left")
ps = dbp.assign(inrd=dbp.pop_ed * 0).merge(ed[["ed_code", "rd_abbr"]], left_on="ED_ABBREVIATION", right_on="ed_code")
ps["inrd"] = np.where(ps.ADMIN_AREA_ABBREVIATION == ps.rd_abbr, ps.pop_ed, 0)
ps = ps.groupby("ed_code").agg(p=("pop_ed", "sum"), i=("inrd", "sum"))
ed["pop_share_in_rd"] = ed.ed_code.map((ps.i / ps.p).round(3))
REG = {"MVRD": "Metro Vancouver", "CAPRD": "Capital Region", "RDCO": "Central Okanagan (Kelowna)"}
ed["inset"] = ed.rd_abbr.map(REG).fillna("")
ed[["ed_code", "ed_name", "regional_district", "rd_abbr", "area_share_in_rd", "pop_share_in_rd", "inset"]] \
    .to_csv(O + "ed2023_regions.csv", index=False)
ed[["ed_code", "ed_name", "area_km2", "land_km2", "pop2021", "pop_per_land_km2", "regional_district", "inset"]].to_csv(O + "ed2023_area_pop.csv", index=False)

props = ["ed_code", "ed_name", "ebc_ed_id", "area_km2", "land_km2", "pop2021", "rd_abbr", "inset"]
report = {"full": {}, "web": {}, "slide": {}}

# ---- full resolution
write_geojson(ed[props + ["geometry"]], O + "ed2023.geojson", 6)
report["full"] = {"check": check(ed), "kb": kb(O + "ed2023.geojson")}


def simp(gdf, k, tmin, tmax):
    g, use = simplify(gdf.reset_index(drop=True), 0, 0, k=k, tmin=tmin, tmax=tmax)
    out = simplify.last_output
    g["geometry"] = g.geometry.apply(polygons_only)
    g = g.set_crs(3005, allow_override=True)
    return g, out


# ---- web: largest-detail setting that keeps both files under 400 KB
for k, tmin, tmax in [(0.003, 15, 1500), (0.0035, 15, 1750), (0.004, 15, 2000), (0.005, 20, 2500)]:
    web, wout = simp(ed[props + ["geometry"]], k, tmin, tmax)
    write_geojson(web, O + "ed2023_web.geojson", 5)
    write_topojson(wout, "EPSG:3005", O + "ed2023_web.topojson", quant=1e6, keep=props)
    if max(os.path.getsize(O + "ed2023_web.geojson"), os.path.getsize(O + "ed2023_web.topojson")) < 400_000:
        break
web = gpd.read_file(O + "ed2023_web.geojson").to_crs(3005)
err = (web.area.values - ed.area.values) / ed.area.values
report["web"] = {"k": k, "tmin_m": tmin, "tmax_m": tmax, "check": check(web), "kb_geojson": kb(O + "ed2023_web.geojson"),
                 "kb_topojson": kb(O + "ed2023_web.topojson"), "max_abs_area_err_pct": round(float(abs(err).max() * 100), 2)}

# ---- slide (720 px wide): province spans ~1,600 km east-west in BC Albers, ~2.2 km per pixel.
# Tolerance up to 1 km (half a pixel) for big districts, scaled down for small ones so they stay visible in insets.
slide, sout = simp(ed[props + ["geometry"]], 0.02, 30, 1000)
write_geojson(slide, O + "ed2023_slide720.geojson", 4)
write_topojson(sout, "EPSG:3005", O + "ed2023_slide720.topojson", quant=1e5, keep=props)
sl = gpd.read_file(O + "ed2023_slide720.geojson").to_crs(3005)
report["slide"] = {"k": 0.02, "tmin_m": 30, "tmax_m": 1000, "check": check(sl), "kb_geojson": kb(O + "ed2023_slide720.geojson"),
                   "kb_topojson": kb(O + "ed2023_slide720.topojson")}

# ---- insets
report["insets"] = {}
for name, abbr in {"metro_vancouver": "MVRD", "capital_region": "CAPRD", "kelowna": "RDCO"}.items():
    members = ed[ed.rd_abbr == abbr].ed_code.tolist()
    write_geojson(ed[ed.ed_code.isin(members)][props + ["geometry"]], O + f"inset_{name}.geojson", 6)
    write_geojson(web[web.ed_code.isin(members)], O + f"inset_{name}_web.geojson", 5)
    minx, miny, maxx, maxy = web[web.ed_code.isin(members)].total_bounds
    mx, my = (maxx - minx) * 0.05, (maxy - miny) * 0.05
    ctx = gpd.clip(web, (minx - mx, miny - my, maxx + mx, maxy + my))
    ctx = ctx[~ctx.is_empty & ctx.geom_type.isin(["Polygon", "MultiPolygon"])]
    write_geojson(ctx, O + f"inset_{name}_frame_web.geojson", 5)
    report["insets"][name] = {"rd": abbr, "districts": members, "frame_districts": len(ctx),
                              "kb": kb(O + f"inset_{name}_web.geojson"), "kb_frame": kb(O + f"inset_{name}_frame_web.geojson")}

# ---- 2015 redistribution, 87 districts (2017 and 2020 elections), reference
e15 = gpd.read_file(R + "raw/bcgw/ed2015.geojson").rename(
    columns={"ED_ABBREVIATION": "ed_code", "ED_NAME": "ed_name", "ELECTORAL_DISTRICT_ID": "ebc_ed_id"})
e15 = e15[["ed_code", "ed_name", "ebc_ed_id", "geometry"]].sort_values("ed_code").reset_index(drop=True).to_crs(3005)
assert len(e15) == 87 and e15.is_valid.all()
e15["area_km2"] = (e15.area / 1e6).round(1)
p15 = ["ed_code", "ed_name", "ebc_ed_id", "area_km2"]
write_geojson(e15, O + "ed2015.geojson", 6)
w15, o15 = simp(e15, report["web"]["k"], report["web"]["tmin_m"], report["web"]["tmax_m"])
write_geojson(w15, O + "ed2015_web.geojson", 5)
write_topojson(o15, "EPSG:3005", O + "ed2015_web.topojson", quant=1e6, keep=p15)
report["ed2015"] = {"check_full": check(e15), "check_web": check(gpd.read_file(O + "ed2015_web.geojson")),
                    "kb_web_geojson": kb(O + "ed2015_web.geojson"), "kb_web_topojson": kb(O + "ed2015_web.topojson")}

json.dump(report, open(O + "build_report.json", "w"), indent=1)
print(json.dumps(report, indent=1))
