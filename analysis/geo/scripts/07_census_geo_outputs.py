"""StatCan 2021 census geography outputs for BC, EPSG:4326.
- db2021_digital_bc.geojson: digital boundary file dissemination blocks + GAF 2021 population, dwellings, DA, ED 2023 (main).
- da2021_digital_bc.geojson: digital DAs. From the StatCan digital DA layer if downloaded (raw/statcan/da_digital.geojson),
  otherwise dissolved from digital DBs (DAs are aggregates of whole DBs, so identical up to vertex order).
- da2021_cartographic_bc.geojson: cartographic DAs (shoreline-clipped), if downloaded.
DA files carry 2021 population and main 2023 district (largest pop_share)."""
import os
import geopandas as gpd, pandas as pd

R = "analysis/geo/"
O = R + "out/"
gaf = pd.read_csv(R + "raw/statcan/2021_92-151_x_bc.csv", dtype=str, encoding="latin-1",
                  usecols=["DBUID_IDIDU", "DBPOP2021_IDPOP2021", "DBTDWELL2021_IDTLOG2021", "DBURDWELL2021_IDRHLOG2021", "DAUID_ADIDU", "DADGUID_ADIDUGD"])
gaf.columns = ["DAUID", "DADGUID", "DBUID", "pop2021", "dwell2021", "urdwell2021"]
for c in ["pop2021", "dwell2021", "urdwell2021"]:
    gaf[c] = pd.to_numeric(gaf[c]).fillna(0).astype(int)
lk = pd.read_csv(O + "da_to_ed2023.csv")
main = lk.sort_values("pop_share", ascending=False).drop_duplicates("dguid").set_index("dguid")
nsplit = lk.groupby("dguid").size()

db = gpd.read_file(R + "raw/statcan/db_digital.geojson")[["DBUID", "DGUID", "LANDAREA", "geometry"]]
db = db.merge(gaf, on="DBUID", how="left", validate="1:1")
dbe = pd.read_csv(O + "db_to_ed2023.csv", dtype={"DBUID": str}).sort_values("frac", ascending=False).drop_duplicates("DBUID")
db = db.merge(dbe[["DBUID", "ED_ABBREVIATION"]].rename(columns={"ED_ABBREVIATION": "ed_code_main"}), on="DBUID", how="left")
out = db.rename(columns={"DGUID": "dguid", "LANDAREA": "landarea_km2", "DADGUID": "da_dguid"}).to_crs(4326)
fn = O + "db2021_digital_bc.geojson"
if os.path.exists(fn):
    os.remove(fn)
out.to_file(fn, driver="GeoJSON", COORDINATE_PRECISION=6)
print("db", len(out), round(os.path.getsize(fn) / 1e6, 1), "MB")

dapop = gaf.groupby("DADGUID").pop2021.sum()


def da_attrs(g):
    g["pop2021"] = g.dguid.map(dapop).fillna(0).astype(int)
    g["ed_code_main"] = g.dguid.map(main.ed_code)
    g["n_ed"] = g.dguid.map(nsplit).fillna(0).astype(int)
    return g


if os.path.exists(R + "raw/statcan/da_digital.geojson"):
    da = gpd.read_file(R + "raw/statcan/da_digital.geojson").rename(columns={"DGUID": "dguid", "LANDAREA": "landarea_km2"})
    src = "StatCan 2021 digital boundary file (DA layer)"
else:
    da = db[["DAUID", "DADGUID", "LANDAREA", "geometry"]].dissolve("DADGUID", aggfunc={"DAUID": "first", "LANDAREA": "sum"}).reset_index()
    da = da.rename(columns={"DADGUID": "dguid", "LANDAREA": "landarea_km2"})
    src = "dissolved from StatCan 2021 digital dissemination blocks"
da = da_attrs(da[["DAUID", "dguid", "landarea_km2", "geometry"]]).to_crs(4326)
fn = O + "da2021_digital_bc.geojson"
if os.path.exists(fn):
    os.remove(fn)
da.to_file(fn, driver="GeoJSON", COORDINATE_PRECISION=6)
print("da digital", len(da), src, round(os.path.getsize(fn) / 1e6, 1), "MB")
open(O + "da2021_digital_bc.source.txt", "w").write(src + "\n")

if os.path.exists(R + "raw/statcan/da_cartographic.geojson"):
    dc = gpd.read_file(R + "raw/statcan/da_cartographic.geojson").rename(columns={"DGUID": "dguid", "LANDAREA": "landarea_km2"})
    dc = da_attrs(dc[["DAUID", "dguid", "landarea_km2", "geometry"]]).to_crs(4326)
    fn = O + "da2021_cartographic_bc.geojson"
    if os.path.exists(fn):
        os.remove(fn)
    dc.to_file(fn, driver="GeoJSON", COORDINATE_PRECISION=6)
    print("da cartographic", len(dc), round(os.path.getsize(fn) / 1e6, 1), "MB")
