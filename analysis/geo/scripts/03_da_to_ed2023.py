"""DA -> 2023 electoral district population-share lookup, built from 2021 dissemination blocks.
Inputs: raw/bcgw/ed2023.geojson (EPSG:3005), raw/statcan/db_digital.geojson (EPSG:3347),
        raw/statcan/2021_92-151_x_bc.csv (GAF, DB populations).
Rule per dissemination block (DB):
  - overlay DB with ED polygons in EPSG:3005 (BC Albers, equal area);
  - if one ED holds >= 98% of the DB's area that falls inside any ED, the whole DB goes to that ED
    (residue is boundary misalignment between StatCan and Elections BC linework);
  - otherwise the DB's population is split by area share among the EDs holding >= 2% each;
  - DBs not touching any ED (offshore slivers) go to the nearest ED.
Per DA: pop_share = sum of DB population in the ED / DA population.
method: 'whole' = every block of the DA lies in a single ED;
        'db_pop' = DA split, shares from whole-block populations only;
        'db_pop_area' = DA split, at least one populated block itself split by area;
        'area' = DA has 0 population, share by land area of its blocks.
Outputs: out/da_to_ed2023.csv, out/db_to_ed2023.csv"""
import geopandas as gpd, pandas as pd, numpy as np

R = "analysis/geo/"
ed = gpd.read_file(R + "raw/bcgw/ed2023.geojson")[["ED_ABBREVIATION", "ED_NAME", "geometry"]].to_crs(3005)
ed["geometry"] = ed.geometry.make_valid()
db = gpd.read_file(R + "raw/statcan/db_digital.geojson")[["DBUID", "geometry"]].to_crs(3005)
db["geometry"] = db.geometry.make_valid()
gaf = pd.read_csv(R + "raw/statcan/2021_92-151_x_bc.csv", dtype=str, encoding="latin-1",
                  usecols=["DBUID_IDIDU", "DBPOP2021_IDPOP2021", "DAUID_ADIDU", "DADGUID_ADIDUGD"])
gaf.columns = ["DAUID", "DADGUID", "DBUID", "pop"]
gaf["pop"] = pd.to_numeric(gaf["pop"]).fillna(0)
db = db.merge(gaf, on="DBUID", how="left", validate="1:1")
assert db["pop"].notna().all()

pieces = gpd.overlay(db[["DBUID", "geometry"]], ed[["ED_ABBREVIATION", "geometry"]], how="intersection",
                     keep_geom_type=True)
pieces["a"] = pieces.area
pieces = pieces.groupby(["DBUID", "ED_ABBREVIATION"], as_index=False)["a"].sum()
pieces["frac"] = pieces.a / pieces.groupby("DBUID").a.transform("sum")
mx = pieces.groupby("DBUID").frac.transform("max")
whole = pieces[mx >= 0.98].sort_values("frac").groupby("DBUID").tail(1).assign(frac=1.0, split=False)
part = pieces[(mx < 0.98) & (pieces.frac >= 0.02)].copy()
part["frac"] = part.frac / part.groupby("DBUID").frac.transform("sum")
part["split"] = True
asg = pd.concat([whole, part])[["DBUID", "ED_ABBREVIATION", "frac", "split"]]

miss = db[~db.DBUID.isin(asg.DBUID)]
if len(miss):
    nn = gpd.sjoin_nearest(miss[["DBUID", "geometry"]], ed[["ED_ABBREVIATION", "geometry"]], how="left")
    nn = nn.drop_duplicates("DBUID")[["DBUID", "ED_ABBREVIATION"]].assign(frac=1.0, split=False, nearest=True)
    asg = pd.concat([asg, nn])
asg["nearest"] = asg.get("nearest", False)
asg["nearest"] = asg["nearest"].fillna(False).astype(bool)
print("DBs:", db.DBUID.nunique(), "assigned:", asg.DBUID.nunique(), "split DBs:", asg[asg.split].DBUID.nunique(),
      "nearest:", int(asg.nearest.sum()))

db["landA"] = db.area
a = asg.merge(db[["DBUID", "DAUID", "DADGUID", "pop", "landA"]], on="DBUID")
a["pop_ed"] = a["pop"] * a.frac
a["area_ed"] = a.landA * a.frac
pop_split_db = a[a.split & (a["pop"] > 0)].DBUID.unique()
a.assign(pop_ed=a.pop_ed.round(3))[["DBUID", "DAUID", "ED_ABBREVIATION", "frac", "pop", "pop_ed", "split", "nearest"]] \
    .to_csv(R + "out/db_to_ed2023.csv", index=False)

g = a.groupby(["DADGUID", "DAUID", "ED_ABBREVIATION"], as_index=False).agg(pop=("pop_ed", "sum"), area=("area_ed", "sum"))
dapop = g.groupby("DADGUID")["pop"].transform("sum")
daarea = g.groupby("DADGUID")["area"].transform("sum")
g["pop_share"] = np.where(dapop > 0, g["pop"] / dapop, g["area"] / daarea)
g = g[g.pop_share > 0].copy()  # drop zero-pop pieces of populated DAs
n_ed = g.groupby("DADGUID").ED_ABBREVIATION.transform("nunique")
da_has_popsplit = g.DAUID.isin(a[a.DBUID.isin(pop_split_db)].DAUID)
g["method"] = np.select([n_ed == 1, dapop.loc[g.index] == 0, da_has_popsplit], ["whole", "area", "db_pop_area"], "db_pop")
g.loc[(n_ed == 1), "pop_share"] = 1.0
g = g.rename(columns={"DADGUID": "dguid", "ED_ABBREVIATION": "ed_code"})
g["pop_share"] = g.pop_share.round(6)
g["da_pop_2021"] = dapop.loc[g.index].round(0).astype(int)
g = g.sort_values(["dguid", "pop_share"], ascending=[True, False])
g[["dguid", "ed_code", "pop_share", "method"]].to_csv(R + "out/da_to_ed2023.csv", index=False)
g[["dguid", "DAUID", "ed_code", "pop_share", "method", "da_pop_2021"]].to_csv(R + "out/da_to_ed2023_detail.csv", index=False)

chk = g.groupby("dguid").pop_share.sum()
print("DAs:", g.dguid.nunique(), "rows:", len(g), "share sum min/max:", chk.min(), chk.max())
print(g.drop_duplicates("dguid").method.value_counts().to_dict(), "(per DA, first row)")
print(g.method.value_counts().to_dict(), "(rows)")
edpop = a.groupby("ED_ABBREVIATION").pop_ed.sum()
print("total pop", round(edpop.sum()), "EDs with pop", (edpop > 0).sum())
edpop.round(1).rename("pop2021").to_csv(R + "out/ed2023_pop2021_from_db.csv")
