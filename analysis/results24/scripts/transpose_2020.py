"""Transpose 2020 BC election results (87 EDs, 2015 boundaries) onto the 93 EDs of the 2023 redistribution.

Usage: python3 -I transpose_2020.py <results24_root>

Method
1. Weights. For each 2020 (2017-gazetted) areal voting area (VA) polygon, intersect with the 2024 VA polygons
   (BS11). Each 2024 VA carries its 2024 registered-voter count (Elections BC open data). The weight of the piece
   (2020 VA x 2024 VA) = 2024 registered voters of that 2024 VA x (piece area / 2024 VA area), i.e. voters are
   assumed uniform only inside a ~700-voter 2024 VA. The piece belongs to the 2023 ED of its 2024 VA.
   2020 site-based VAs (care homes; points) go wholly to the 2023 ED containing the point.
   A 2020 VA whose intersecting 2024 VAs have zero registered voters falls back to pure area share.
2. Election-day ("General voting") votes, reported per 2020 VA, are split across 2023 EDs by those weights
   (fractional split). A largest-share assignment is also saved for reference.
3. Advance (by voting place), mail, absentee, special and DEO votes are reported only by 2020 ED. For each 2020
   ED and party, they are split across 2023 EDs in proportion to that party's election-day votes transposed from
   that 2020 ED in step 2 (party-specific). Rejected ballots and registered voters are split the same way using
   rejected election-day ballots and 2020 VA registered-voter counts respectively.
Outputs: out/transposed_2020_on_2023_eds.csv (district x party), out/transposed_2020_summary.csv,
         out/va2020_to_ed2023_weights.csv
"""
import sys, io, json
import numpy as np, pandas as pd, geopandas as gpd

R = sys.argv[1]
OUT = f"{R}/out"
v17 = gpd.read_file(f"{R}/raw/ebc_va_shp_2017/x/edvas02232017.shp").set_crs(3005, allow_override=True)
s17 = gpd.read_file(f"{R}/raw/ebc_sva_shp_2017/x/svas02232017.shp").set_crs(3005, allow_override=True)
v24 = gpd.read_file(f"{R}/raw/bcgw_va2024/va2024_bs11.geojson").set_crs(3005, allow_override=True)
ed23 = gpd.read_file(f"{R}/raw/bcgw_ed2023/ed2023_bs11.geojson").set_crs(3005, allow_override=True)
reg = pd.read_csv(f"{R}/raw/ebc_regvoters/provincial_registered_voter_counts.csv", dtype=str, encoding="utf-8-sig")
reg["n"] = reg.REGISTERED_VOTERS.astype(int)
r24 = reg[reg.EVENT_NAME == "2024 General Election"].set_index("EDVA_CODE").n
r20 = reg[reg.EVENT_NAME == "2020 General Election"].set_index("EDVA_CODE").n

v24 = v24[["EDVA_CODE", "ED_ABBREVIATION", "geometry"]].rename(columns={"EDVA_CODE": "va24", "ED_ABBREVIATION": "ed23"})
v24["reg24"] = v24.va24.map(r24).fillna(0)
miss24 = int(v24.reg24.eq(0).sum())
v24["a24"] = v24.area
v17 = v17[["EDVA_CODE", "ED_ABBREV", "geometry"]].rename(columns={"EDVA_CODE": "va20", "ED_ABBREV": "ed20"})
pcs = gpd.overlay(v17, v24, how="intersection", keep_geom_type=True)
pcs["a"] = pcs.area
pcs = pcs[pcs.a > 1.0]  # drop sliver pieces < 1 m2 (digitising noise along shared edges)
pcs["w_reg"] = pcs.reg24 * pcs.a / pcs.a24
W = pcs.groupby(["va20", "ed20", "ed23"]).agg(w_reg=("w_reg", "sum"), area=("a", "sum")).reset_index()
tot = W.groupby("va20")[["w_reg", "area"]].transform("sum")
W["share"] = np.where(tot.w_reg > 0, W.w_reg / tot.w_reg, W.area / tot.area)
W["basis"] = np.where(tot.w_reg > 0, "reg24_weighted", "area_only")
# site-based VAs
s = s17[["EDVA_CODE", "ED_ABBR", "geometry"]].rename(columns={"EDVA_CODE": "va20", "ED_ABBR": "ed20"}).drop_duplicates("va20")
sj = gpd.sjoin(s, ed23[["ED_ABBREVIATION", "geometry"]], how="left", predicate="within")
nearest_used = int(sj.ED_ABBREVIATION.isna().sum())
if nearest_used:
    nn = gpd.sjoin_nearest(s[s.va20.isin(sj[sj.ED_ABBREVIATION.isna()].va20)], ed23[["ED_ABBREVIATION", "geometry"]])
    sj = pd.concat([sj[sj.ED_ABBREVIATION.notna()], nn])
sj = sj.drop_duplicates("va20")
SW = pd.DataFrame({"va20": sj.va20, "ed20": sj.ed20, "ed23": sj.ED_ABBREVIATION, "w_reg": np.nan, "area": 0.0, "share": 1.0, "basis": "site_point"})
W = pd.concat([W, SW], ignore_index=True)
W["is_largest"] = W.share.eq(W.groupby("va20").share.transform("max"))
W.to_csv(f"{OUT}/va2020_to_ed2023_weights.csv", index=False)

# ---------- 2020 votes ----------
b = open(f"{R}/raw/ebc_va_results/provincial_voting_results_by_va.csv", "rb").read()
b = b[3:] if b[:3] == b"\xef\xbb\xbf" else b
va = pd.read_csv(io.StringIO(b.decode("latin-1")), dtype=str)
va = va[va.EVENT_NAME == "2020 General Election"].copy()
va["votes"] = va.VOTES_CONSIDERED.astype(int)
PS = {"BC NDP": "NDP", "BC Liberal Party": "LIB", "BC Green Party": "GRN", "Conservative": "CON"}
va["party"] = np.where(va.VOTE_CATEGORY == "Rejected", "REJECTED", va.AFFILIATION.map(PS).fillna("OTH"))
gen = va[va.VOTING_OPPORTUNITY == "General voting"].groupby(["EDVA_CODE", "ED_ABBREVIATION", "party"]).votes.sum().reset_index()
oth = va[va.VOTING_OPPORTUNITY != "General voting"].groupby(["ED_ABBREVIATION", "party"]).votes.sum().reset_index()
miss = set(gen.EDVA_CODE) - set(W.va20)
assert not miss, f"VAs without weights: {sorted(miss)[:10]}"
g = gen.merge(W[["va20", "ed23", "share"]], left_on="EDVA_CODE", right_on="va20")
g["v"] = g.votes * g.share
gt = g.groupby(["ED_ABBREVIATION", "ed23", "party"]).v.sum().reset_index()
# party-specific split of non-VA votes; fallback to all-party election-day split if a party had 0 election-day votes in the old ED
allp = gt.groupby(["ED_ABBREVIATION", "ed23"]).v.sum()
allp = (allp / allp.groupby(level=0).transform("sum")).rename("fs_all").reset_index()
gt["fs"] = gt.v / gt.groupby(["ED_ABBREVIATION", "party"]).v.transform("sum")
fallback = []
rows = []
for _, r in oth.iterrows():
    sub = gt[(gt.ED_ABBREVIATION == r.ED_ABBREVIATION) & (gt.party == r.party)]
    if len(sub) == 0 or sub.v.sum() == 0:
        sub = allp[allp.ED_ABBREVIATION == r.ED_ABBREVIATION].rename(columns={"fs_all": "fs"})
        fallback.append(f"{r.ED_ABBREVIATION}/{r.party}")
    for _, q in sub.iterrows():
        rows.append((r.ED_ABBREVIATION, q.ed23, r.party, r.votes * q.fs))
ot = pd.DataFrame(rows, columns=["ED_ABBREVIATION", "ed23", "party", "v"])
T = pd.concat([gt[["ED_ABBREVIATION", "ed23", "party", "v"]].assign(kind="election_day"), ot.assign(kind="other")])
T.groupby(["ed23", "ED_ABBREVIATION"]).v.sum().reset_index().rename(columns={"ED_ABBREVIATION": "ed20", "v": "votes_incl_rejected"}).to_csv(
    f"{OUT}/transposed_2020_flows_ed20_to_ed23.csv", index=False)
X = T.groupby(["ed23", "party"]).v.sum().unstack(fill_value=0)
# registered voters 2020 by VA
rr = W.merge(r20.rename("reg20"), left_on="va20", right_index=True, how="left")
X["registered_2020"] = (rr.reg20 * rr.share).groupby(rr.ed23).sum()
vcols = ["NDP", "LIB", "GRN", "CON", "OTH"]
X["total_valid"] = X[vcols].sum(axis=1)
for c in vcols:
    X[f"{c}_pct"] = (100 * X[c] / X.total_valid).round(2)
X["turnout_pct"] = (100 * (X.total_valid + X.REJECTED) / X.registered_2020).round(2)
srt = X[vcols].apply(lambda r: r.sort_values(ascending=False).index.tolist(), axis=1)
X["notional_winner_2020"] = srt.str[0]
X["notional_second_2020"] = srt.str[1]
X["notional_margin_pts_2020"] = X.apply(lambda r: round(r[f"{r.notional_winner_2020}_pct"] - r[f"{r.notional_second_2020}_pct"], 2), axis=1)
X["election_day_share_of_votes"] = (T[T.kind == "election_day"].groupby("ed23").v.sum() / T.groupby("ed23").v.sum()).round(3)
X = X.join(ed23.set_index("ED_ABBREVIATION").ED_NAME)
X.index.name = "ed_code"
X = X.reset_index()
X = X[["ed_code", "ED_NAME"] + vcols + ["REJECTED", "total_valid", "registered_2020"] + [f"{c}_pct" for c in vcols] +
      ["turnout_pct", "notional_winner_2020", "notional_second_2020", "notional_margin_pts_2020", "election_day_share_of_votes"]]
X = X.rename(columns={"ED_NAME": "ed_name"})
for c in vcols + ["REJECTED", "total_valid", "registered_2020"]:
    X[c] = X[c].round(1)
X.to_csv(f"{OUT}/transposed_2020_on_2023_eds.csv", index=False)

# checks
tv = va[va.VOTE_CATEGORY == "Valid"].votes.sum()
print("valid 2020", tv, "transposed", round(X.total_valid.sum(), 2), "eds", len(X))
print("notional seats", X.notional_winner_2020.value_counts().to_dict())
print("2024 VAs with 0 registered voters:", miss24, "| site VAs placed by nearest:", nearest_used, "| fallbacks:", len(fallback))
print("area_only VAs:", W[W.basis == "area_only"].va20.nunique())
json.dump({"site_nearest": nearest_used, "fallback_party_split": fallback, "zero_reg_2024_vas": miss24,
           "area_only_2020_vas": int(W[W.basis == "area_only"].va20.nunique())}, open(f"{R}/work/transpose_diag.json", "w"), indent=1)
