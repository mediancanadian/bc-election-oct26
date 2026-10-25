"""Voting areas.
2024 (used in 2024 and, unless replaced, 2026): EBC_VOTING_AREAS_BS11_POLY_SVW, gazetted 2024-09-19, 93 EDs.
2020: EBC_VOTING_AREAS_BS10_POLY_SVW, gazetted 2017-02-23, used in 2017 and 2020 general elections (87 EDs).
Site-based voting areas (codes ending in S, e.g. ABS071S) are points (care facilities), not polygons.
Outputs:
  va2024.geojson, va2020.geojson (EPSG:4326, full), va2024_web.topojson, va2020_web.topojson (simplified, shared arcs)
  sva2024_points.geojson, sva2020_points.geojson
  va2020_to_ed2023.csv: each 2020 voting area -> share of its 2021 population in each 2023 district
     (dissemination-block populations; same 98% rule as da_to_ed2023), plus area share.
  sva2020_to_ed2023.csv: site-based 2020 voting areas -> 2023 district by point in polygon.
  va2024_check.csv: any 2024 VA whose polygon is not inside its own ED."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geopandas as gpd, pandas as pd, numpy as np
from simplify_lib import simplify, polygons_only, write_topojson
from shapely.geometry.polygon import orient
from shapely.geometry import MultiPolygon

R = "analysis/geo/"
O = R + "out/"


def rfc(g):
    g = polygons_only(g)
    return orient(g, 1.0) if g.geom_type == "Polygon" else MultiPolygon([orient(p, 1.0) for p in g.geoms])


def wgj(gdf, fn, dp, poly=True):
    g = gdf.to_crs(4326).copy()
    if poly:
        g["geometry"] = g.geometry.apply(rfc)
    if os.path.exists(fn):
        os.remove(fn)
    g.to_file(fn, driver="GeoJSON", COORDINATE_PRECISION=dp)


def load_va(key):
    v = gpd.read_file(R + f"raw/bcgw/{key}.geojson")
    v = v.rename(columns={"EDVA_CODE": "edva_code", "ED_ABBREVIATION": "ed_code", "VA_CODE": "va_code", "VA_TYPE": "va_type",
                          "GAZETTE_DATE": "gazette_date", "VOTING_AREA_POLY_ID": "ebc_va_poly_id"})
    v = v[["edva_code", "ed_code", "va_code", "va_type", "gazette_date", "ebc_va_poly_id", "geometry"]].to_crs(3005)
    v["gazette_date"] = v.gazette_date.astype(str).str[:10]
    v["geometry"] = v.geometry.make_valid().apply(polygons_only)
    assert v.edva_code.is_unique
    return v


def load_sva(key):
    s = gpd.read_file(R + f"raw/bcgw/{key}.geojson")
    s = s.rename(columns={"EDVA_CODE": "edva_code", "ED_ABBREVIATION": "ed_code", "VA_CODE": "va_code", "VA_TYPE": "va_type",
                          "BUILDING_NAME": "building_name", "LOCALITY": "locality"})
    return s[["edva_code", "ed_code", "va_code", "va_type", "building_name", "locality", "geometry"]].to_crs(3005)


report = {}
va24, va20 = load_va("va2024"), load_va("va2017")
sv24, sv20 = load_sva("sbva2024"), load_sva("sbva2017")
ed = gpd.read_file(R + "raw/bcgw/ed2023.geojson").to_crs(3005)[["ED_ABBREVIATION", "geometry"]].rename(columns={"ED_ABBREVIATION": "ed_code"})
e15 = gpd.read_file(R + "raw/bcgw/ed2015.geojson").to_crs(3005)[["ED_ABBREVIATION", "geometry"]].rename(columns={"ED_ABBREVIATION": "ed_code"})

for nm, v, s, e in [("va2024", va24, sv24, ed), ("va2020", va20, sv20, e15)]:
    wgj(v, O + f"{nm}.geojson", 6)
    wgj(s, O + f"s{nm}_points.geojson", 6, poly=False)
    g, _ = simplify(v.reset_index(drop=True), 0, 0, k=0.01, tmin=5, tmax=400)
    write_topojson(simplify.last_output, "EPSG:3005", O + f"{nm}_web.topojson", quant=1e6,
                   object_name="voting_areas", keep=["edva_code", "ed_code", "va_code"])
    # VA inside its ED?
    rp = v.copy()
    rp["geometry"] = rp.geometry.representative_point()
    j = gpd.sjoin(rp, e, how="left", predicate="within", rsuffix="ed")
    bad = j[j.ed_code_left != j.ed_code_ed]
    sj = gpd.sjoin(s, e, how="left", predicate="within", rsuffix="ed")
    sbad = sj[sj.ed_code_left != sj.ed_code_ed]
    report[nm] = {"polygons": len(v), "eds": v.ed_code.nunique(), "site_based_points": len(s),
                  "va_point_not_in_own_ed": len(bad), "sva_not_in_own_ed": len(sbad),
                  "kb_full": round(os.path.getsize(O + f"{nm}.geojson") / 1024), "kb_web_topojson": round(os.path.getsize(O + f"{nm}_web.topojson") / 1024),
                  "area_km2": round(v.area.sum() / 1e6)}
    if len(bad) or len(sbad):
        pd.concat([bad[["edva_code", "ed_code_left", "ed_code_ed"]].assign(kind="poly"),
                   sbad[["edva_code", "ed_code_left", "ed_code_ed"]].assign(kind="site")]).to_csv(O + f"{nm}_check.csv", index=False)

# ---- 2020 VA -> 2023 ED, population-weighted via dissemination blocks
db = gpd.read_file(R + "raw/statcan/db_digital.geojson")[["DBUID", "geometry"]].to_crs(3005)
db["geometry"] = db.geometry.make_valid()
gaf = pd.read_csv(R + "raw/statcan/2021_92-151_x_bc.csv", dtype=str, encoding="latin-1", usecols=["DBUID_IDIDU", "DBPOP2021_IDPOP2021"])
gaf.columns = ["DBUID", "pop"]
gaf["pop"] = pd.to_numeric(gaf["pop"]).fillna(0)
db = db.merge(gaf, on="DBUID")
cells = gpd.overlay(va20[["edva_code", "geometry"]], ed, how="intersection", keep_geom_type=True)
cells["cell"] = cells.edva_code + "|" + cells.ed_code
cells = cells.dissolve("cell", as_index=False)[["cell", "edva_code", "ed_code", "geometry"]]
cells["cell_area"] = cells.area
pc = gpd.overlay(db[["DBUID", "geometry"]], cells[["cell", "geometry"]], how="intersection", keep_geom_type=True)
pc["a"] = pc.area
pc = pc.groupby(["DBUID", "cell"], as_index=False).a.sum()
pc["frac"] = pc.a / pc.groupby("DBUID").a.transform("sum")
mx = pc.groupby("DBUID").frac.transform("max")
whole = pc[mx >= 0.98].sort_values("frac").groupby("DBUID").tail(1).assign(frac=1.0)
part = pc[(mx < 0.98) & (pc.frac >= 0.02)].copy()
part["frac"] = part.frac / part.groupby("DBUID").frac.transform("sum")
asg = pd.concat([whole, part]).merge(db[["DBUID", "pop"]], on="DBUID")
asg["pop_cell"] = asg["pop"] * asg.frac
cp = asg.groupby("cell").pop_cell.sum()
cells["pop2021"] = cells.cell.map(cp).fillna(0)
cells["va_pop"] = cells.groupby("edva_code").pop2021.transform("sum")
cells["va_area"] = cells.groupby("edva_code").cell_area.transform("sum")
cells["area_share"] = cells.cell_area / cells.va_area
cells["pop_share"] = np.where(cells.va_pop > 0, cells.pop2021 / cells.va_pop, cells.area_share)
cells["method"] = np.where(cells.groupby("edva_code").ed_code.transform("nunique") == 1, "whole",
                           np.where(cells.va_pop > 0, "db_pop", "area"))
cells = cells[(cells.pop_share > 0) | (cells.method == "whole")]
# drop sliver cells (< 0.5% of the VA area and no population): boundary misalignment
cells = cells[~((cells.area_share < 0.005) & (cells.pop2021 < 0.5) & (cells.method != "whole"))].copy()
cells["pop_share"] = cells.pop_share / cells.groupby("edva_code").pop_share.transform("sum")
cells["area_share"] = cells.area_share / cells.groupby("edva_code").area_share.transform("sum")
cells["method"] = np.where(cells.groupby("edva_code").ed_code.transform("nunique") == 1, "whole", cells.method)
cells.loc[cells.method == "whole", ["pop_share", "area_share"]] = 1.0
out = cells.rename(columns={"edva_code": "edva_code_2020", "ed_code": "ed_code_2023"})
out["ed_code_2020"] = out.edva_code_2020.str[:3]
out = out[["edva_code_2020", "ed_code_2020", "ed_code_2023", "pop_share", "area_share", "pop2021", "method"]].sort_values(["edva_code_2020", "pop_share"], ascending=[True, False])
out["pop_share"] = out.pop_share.round(6)
out["area_share"] = out.area_share.round(6)
out["pop2021"] = out.pop2021.round(1)
out.to_csv(O + "va2020_to_ed2023.csv", index=False)
missing = set(va20.edva_code) - set(out.edva_code_2020)
s20 = gpd.sjoin(sv20, ed.rename(columns={"ed_code": "ed_code_2023"}), how="left", predicate="within")
s20 = s20.rename(columns={"edva_code": "edva_code_2020", "ed_code": "ed_code_2020"})
s20[["edva_code_2020", "ed_code_2020", "ed_code_2023", "building_name", "locality"]].to_csv(O + "sva2020_to_ed2023.csv", index=False)
report["va2020_to_ed2023"] = {"vas": out.edva_code_2020.nunique(), "rows": len(out), "vas_missing": len(missing),
                              "split_vas": int(out[out.method != "whole"].edva_code_2020.nunique()),
                              "pop_total": round(out.pop2021.sum()), "sva_unmatched": int(s20.ed_code_2023.isna().sum())}
import json
json.dump(report, open(O + "va_report.json", "w"), indent=1)
print(json.dumps(report, indent=1))
