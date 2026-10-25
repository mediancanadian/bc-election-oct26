# Re-allocate 2025 federal poll-by-poll results (BC) onto the 93 BC provincial electoral districts (2023 boundaries).
# Run: python3 -I scripts/02_allocate.py   (from analysis/federal25)
import glob, json, re, sys
import numpy as np, pandas as pd, geopandas as gpd

ROOT = "analysis/federal25"
ED_PATH = "analysis/geo/raw/bcgw/ed2023.geojson"
CRS = 3005
PARTIES = {"Liberal": "LPC", "Conservative": "CPC", "NDP-New Democratic Party": "NDP", "Green Party": "GPC"}
PCOLS = ["LPC", "CPC", "NDP", "GPC", "OTH"]
log = {}

# ---------- 1. poll results ----------
fs = sorted(glob.glob(f"{ROOT}/raw/ec_results/pr/pollresults_resultatsbureau59*.csv"))
assert len(fs) == 43
df = pd.concat([pd.read_csv(f, encoding="utf-8-sig", dtype=str, keep_default_na=False) for f in fs])
df.columns = ['fed', 'fedname', 'fedname_f', 'pd', 'pdname', 'void', 'nopoll', 'combined', 'rej', 'electors', 'fam',
              'mid', 'first', 'party', 'party_f', 'inc', 'elected', 'votes']
df["pd"] = df.pd.str.strip(); df["combined"] = df.combined.str.strip()
df["fed"] = df.fed.astype(int); df["votes"] = df.votes.astype(int)
df["rej"] = df.rej.astype(int); df["electors"] = df.electors.astype(int)
df["p"] = df.party.map(PARTIES).fillna("OTH")

# one row per poll (fed, pd)
polls = df.drop_duplicates(["fed", "pd"])[["fed", "fedname", "pd", "pdname", "void", "nopoll", "combined", "rej", "electors"]].copy()
v = df.pivot_table(index=["fed", "pd"], columns="p", values="votes", aggfunc="sum", fill_value=0).reindex(columns=PCOLS, fill_value=0)
polls = polls.merge(v.reset_index(), on=["fed", "pd"])
m = polls.pd.str.extract(r"^(\d+)(?:-(\d+))?([A-Z]?)$")
polls["base"] = pd.to_numeric(m[0]); polls["sfx"] = pd.to_numeric(m[1]).fillna(0)
def kind(r):
    if r.pd.startswith("S/R"): return "svr"          # special voting rules (special ballots)
    b = r.base
    if b < 400: return "ordinary"
    if b < 500: return "special_pd"                  # 400-series: single-building polling divisions (type S)
    if b < 600: return "mobile"                      # 500-series: mobile polls (type M)
    return "advance"                                 # 600-series: advance polls
polls["kind"] = polls.apply(kind, axis=1)
log["polls_by_kind"] = polls.kind.value_counts().to_dict()

# resolve 'combined with' chains to the poll that actually reports the votes
pset = set(zip(polls.fed, polls.pd))
def resolve(fed, pdn, seen=()):
    row = comb.get((fed, pdn), "")
    if row == "" or (fed, row) in seen: return pdn
    assert (fed, row) in pset, (fed, pdn, row)
    return resolve(fed, row, seen + ((fed, pdn),))
comb = dict(zip(zip(polls.fed, polls.pd), polls.combined))
polls["unit"] = [resolve(f, p) for f, p in zip(polls.fed, polls.pd)]
# votes sit on the reporting poll; sources of a combination should carry zero
src = polls[polls.unit != polls.pd]
log["combined_source_polls"] = int(len(src)); log["combined_source_votes_nonzero"] = int(src[PCOLS].sum().sum())

# ---------- 2. official totals for checks ----------
t8 = pd.read_csv(f"{ROOT}/raw/ec_results/table_tableau08.csv", encoding="utf-8-sig")
bc_col = [c for c in t8.columns if c.startswith("B.C.")][0]
t8["party"] = t8.iloc[:, 0].str.split("/").str[0]
off = {"LPC": int(t8.loc[t8.party == "Liberal Party of Canada", bc_col].iloc[0]),
       "CPC": int(t8.loc[t8.party == "Conservative Party of Canada", bc_col].iloc[0]),
       "NDP": int(t8.loc[t8.party == "New Democratic Party", bc_col].iloc[0]),
       "GPC": int(t8.loc[t8.party == "Green Party of Canada", bc_col].iloc[0])}
t3 = pd.read_csv(f"{ROOT}/raw/ec_results/table_tableau03.csv", encoding="utf-8-sig")
bc3 = t3[t3.iloc[:, 0].str.startswith("British Columbia")].iloc[0]
off_valid = int(bc3.iloc[3]); off_rej = int(bc3.iloc[5]); off_elect = int(bc3.iloc[2])
off["OTH"] = off_valid - sum(off.values())
log["official_bc"] = {**off, "valid": off_valid, "rejected": off_rej, "electors": off_elect}
raw_tot = polls[PCOLS].sum().to_dict()
log["pollfile_bc"] = {k: int(v) for k, v in raw_tot.items()} | {"rejected": int(polls.rej.sum()), "electors": int(polls.electors.sum())}
for k in PCOLS: assert raw_tot[k] == off[k], (k, raw_tot[k], off[k])
# riding-level check against table 12 (votes per riding)
t12 = pd.read_csv(f"{ROOT}/raw/ec_results/table_tableau12.csv", encoding="utf-8-sig", dtype=str)
t12 = t12[t12.iloc[:, 2].str.startswith("59")]
rv = t12.groupby(t12.iloc[:, 2].astype(int))[t12.columns[6]].apply(lambda s: s.astype(int).sum())
pv = polls.groupby("fed")[PCOLS].sum().sum(axis=1)
log["riding_valid_mismatches_vs_table12"] = int((rv.reindex(pv.index) != pv).sum())

# ---------- 3. geography ----------
ed = gpd.read_file(ED_PATH).to_crs(CRS)[["ED_ABBREVIATION", "ED_NAME", "geometry"]].rename(columns={"ED_ABBREVIATION": "ed", "ED_NAME": "ed_name"})
ed["geometry"] = ed.geometry.make_valid()
pdg = gpd.read_file(f"{ROOT}/raw/ec_geo/shp/SHP/PD_CA_2025_EN.shp", where="FED_NUM >= 59000 AND FED_NUM < 60000").to_crs(CRS)
pdg["fed"] = pdg.FED_NUM.astype(int); pdg["base"] = pdg.PD_NUM.astype(int); pdg["sfx"] = pdg.PD_NBR_SFX.astype(int)
pdg = pdg.dissolve(by=["fed", "base", "sfx"], as_index=False)[["fed", "base", "sfx", "PD_TYPE", "geometry"]]
pdg["geometry"] = pdg.geometry.make_valid()
pdg["gid"] = np.arange(len(pdg))

db = gpd.read_file(f"{ROOT}/raw/bcgw/db2021.geojson").set_crs(CRS, allow_override=True)
gaf = pd.read_csv(f"{ROOT}/raw/statcan/2021_92-151_x_bc.csv", encoding="latin1", dtype={"DBUID_IDIDU": str},
                  usecols=["DBUID_IDIDU", "DBPOP2021_IDPOP2021"])
db = db[["DISSEMINATION_BLOCK_ID", "geometry"]].merge(gaf, left_on="DISSEMINATION_BLOCK_ID", right_on="DBUID_IDIDU", how="left")
log["db_count"] = int(len(db)); log["db_blank_population_in_gaf"] = int(db.DBPOP2021_IDPOP2021.isna().sum())
db["pop"] = db.DBPOP2021_IDPOP2021.fillna(0).astype(float)
log["db_pop_total"] = float(db["pop"].sum())
db["geometry"] = db.geometry.make_valid(); db["db_area"] = db.area
db = db[db["pop"] > 0][["DISSEMINATION_BLOCK_ID", "pop", "db_area", "geometry"]]

print("overlay PD x ED", flush=True)
pe = gpd.overlay(pdg[["gid", "geometry"]], ed[["ed", "geometry"]], how="intersection", keep_geom_type=True)
pe["a"] = pe.area
pe = pe[pe.a > 0.01].reset_index(drop=True); pe["pid"] = np.arange(len(pe))
print("overlay DB x piece", len(pe), flush=True)
dp = gpd.overlay(db, pe[["pid", "geometry"]], how="intersection", keep_geom_type=True)
dp["popw"] = dp["pop"] * dp.area / dp.db_area
piece_pop = dp.groupby("pid").popw.sum()
pe["pop"] = pe.pid.map(piece_pop).fillna(0)
log["db_pop_captured_in_pd_ed_pieces"] = float(pe["pop"].sum())
# per geometry id: pop and area by ED
gw = pe.groupby(["gid", "ed"]).agg(pop=("pop", "sum"), a=("a", "sum")).reset_index()
# PD polygons not touching any ED polygon (offshore slivers): nearest ED
missing = set(pdg.gid) - set(gw.gid)
if missing:
    mm = pdg[pdg.gid.isin(missing)].copy(); mm["geometry"] = mm.representative_point()
    nn = gpd.sjoin_nearest(mm[["gid", "geometry"]], ed[["ed", "geometry"]])
    gw = pd.concat([gw, pd.DataFrame({"gid": nn.gid, "ed": nn.ed, "pop": 0.0, "a": 1.0})])
log["pd_polygons_no_ed_overlap_nearest"] = len(missing)
gkey = {(r.fed, r.base, r.sfx): r.gid for r in pdg.itertuples()}

# ---------- 4. allocation of geographic polls ----------
geo_kinds = {"ordinary", "special_pd", "mobile"}
polls["gid"] = [gkey.get((f, int(b), int(s))) if k in geo_kinds else None
                for f, b, s, k in zip(polls.fed, polls.base.fillna(-1), polls.sfx, polls.kind)]
gp = polls[polls.kind.isin(geo_kinds)]
log["geo_polls_without_polygon"] = int(gp.gid.isna().sum())
nog = gp.gid.isna()
log["mobile_polls_without_polygon"] = [f"{r.fed}-{r.pd} ({int(sum(getattr(r,k) for k in PCOLS))} votes)" for r in gp[nog].itertuples()]
assert set(gp[nog].kind) <= {"mobile"} and (gp[nog].unit == gp[nog].pd).all()
polls.loc[polls.kind.isin(geo_kinds) & polls.gid.isna(), "kind"] = "mobile_nopolygon"
gp = polls[polls.kind.isin(geo_kinds)]
assert gp.gid.notna().all()
# a reporting unit's footprint = its own PD plus every PD combined into it
foot = gp.groupby(["fed", "unit"]).gid.apply(lambda s: sorted(set(int(x) for x in s))).to_dict()

def weights(gids):
    w = gw[gw.gid.isin(gids)].groupby("ed")[["pop", "a"]].sum()
    if w["pop"].sum() > 0: return w["pop"] / w["pop"].sum(), "population"
    return w["a"] / w["a"].sum(), "area"

rows = []; method_count = {"population": 0, "area": 0}; area_polls = []
units = polls[(polls.pd == polls.unit) & polls.kind.isin(geo_kinds)]
for r in units.itertuples():
    gids = foot[(r.fed, r.unit)]
    w, how = weights(gids); method_count[how] += 1
    if how == "area": area_polls.append(f"{r.fed}-{r.pd}")
    for e, s in w.items():
        rows.append({"fed": r.fed, "pd": r.pd, "kind": r.kind, "ed": e, "w": s, "how": how,
                     **{k: getattr(r, k) * s for k in PCOLS}, "rej": r.rej * s})
log["geo_reporting_units_by_weight_method"] = method_count
log["area_fallback_units"] = area_polls
alloc = pd.DataFrame(rows)
# electors: each poll row's electors allocated by its own PD footprint (sources of combinations included)
er = []
for r in polls[polls.kind.isin(geo_kinds)].itertuples():
    w, _ = weights([int(r.gid)])
    for e, s in w.items(): er.append({"fed": r.fed, "ed": e, "electors": r.electors * s})
elect = pd.DataFrame(er)
# electors listed on non-geographic rows (SVR Group 1 = electors on the special-ballot list, mobile polls without polygon):
# spread within the riding in proportion to that riding's mapped electors
ngE = polls[~polls.kind.isin(geo_kinds)].groupby("fed").electors.sum()
eb = elect.groupby(["fed", "ed"]).electors.sum().reset_index()
eb["share"] = eb.electors / eb.groupby("fed").electors.transform("sum")
eb["electors"] = eb.fed.map(ngE).fillna(0) * eb.share
elect = pd.concat([elect, eb[["fed", "ed", "electors"]]])
nongeo_electors = int(polls.loc[~polls.kind.isin(geo_kinds), "electors"].sum())
log["electors_on_advance_or_svr_rows"] = nongeo_electors

# ---------- 5. advance + special-ballot (SVR): within-riding proportional allocation ----------
geo_fed_ed = alloc.groupby(["fed", "ed"])[PCOLS + ["rej"]].sum()
ng = polls[~polls.kind.isin(geo_kinds)].groupby("fed")[PCOLS + ["rej"]].sum()
nrows = []; party_fallback = 0
for fed, tot in ng.iterrows():
    base = geo_fed_ed.loc[fed]
    allv = base[PCOLS].sum(axis=1)
    for k in PCOLS + ["rej"]:
        if tot[k] == 0: continue
        col = base[k] if k != "rej" else base["rej"]
        if col.sum() <= 0:
            col = allv; party_fallback += 1
        share = col / col.sum()
        for e, s in share.items(): nrows.append({"fed": fed, "ed": e, "k": k, "v": tot[k] * s})
log["advance_svr_party_fallback_to_all_votes"] = party_fallback
adv = pd.DataFrame(nrows).pivot_table(index=["fed", "ed"], columns="k", values="v", aggfunc="sum", fill_value=0)

# ---------- 6. assemble per ED ----------
fe = geo_fed_ed.add(adv.reindex(columns=PCOLS + ["rej"], fill_value=0), fill_value=0)
out = fe.groupby("ed")[PCOLS + ["rej"]].sum()
out["electors"] = elect.groupby("ed").electors.sum()
out = ed[["ed", "ed_name"]].set_index("ed").join(out).fillna(0)
out["valid"] = out[PCOLS].sum(axis=1)
# checks
for k in PCOLS: assert abs(out[k].sum() - off[k]) < 1e-6 * max(off[k], 1) + 1e-3, (k, out[k].sum(), off[k])
log["alloc_totals"] = {k: round(float(out[k].sum()), 3) for k in PCOLS + ["rej", "electors", "valid"]}
log["n_feds_contributing"] = fe.reset_index().groupby("ed").fed.nunique().describe().to_dict()

res = pd.DataFrame(index=out.index)
res["ed_name"] = out.ed_name
for k in PCOLS: res[f"{k}_votes"] = out[k].round(0).astype(int)
res["total_valid_votes"] = out.valid.round(0).astype(int)
res["rejected_ballots"] = out.rej.round(0).astype(int)
for k in PCOLS: res[f"{k}_share_pct"] = (100 * out[k] / out.valid).round(2)
res["electors_est"] = out.electors.round(0).astype(int)
res["turnout_est_pct"] = (100 * (out.valid + out.rej) / out.electors).round(1)
res["fed_winner"] = out[PCOLS].idxmax(axis=1)
srt = np.sort(out[PCOLS].values, axis=1)
res["margin_pts"] = (100 * (srt[:, -1] - srt[:, -2]) / out.valid.values).round(2)
ridings = fe.reset_index()
ridings["v"] = ridings[PCOLS].sum(axis=1)
ridings = ridings[ridings.v >= 0.5]
fedmap = dict(zip(polls.fed, polls.fedname))
res["federal_ridings_overlapping"] = ridings.sort_values("v", ascending=False).groupby("ed").apply(
    lambda g: "; ".join(f"{fedmap[f]} ({100*v/g.v.sum():.0f}%)" for f, v in zip(g.fed, g.v) if 100*v/g.v.sum() >= 1))
res.index.name = "ed_code"
res.reset_index().to_csv(f"{ROOT}/fed2025_on_ed2023.csv", index=False)
log["rounded_totals"] = {k: int(res[f"{k}_votes"].sum()) for k in PCOLS}
log["eds_led"] = res.fed_winner.value_counts().to_dict()
json.dump(log, open(f"{ROOT}/scripts/allocation_log.json", "w"), indent=1, default=str)
print(json.dumps(log, indent=1, default=str))
