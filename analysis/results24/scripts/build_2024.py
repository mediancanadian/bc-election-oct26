"""Build 2024 BC general election tables from Elections BC open data.

Usage: python3 -I build_2024.py <results24_root>
Reads raw/ebc_vp_results, raw/ebc_regvoters, raw/bcgw_vavp2024, work/sov2024_*.csv
Writes out/districts_2024.csv, out/districts_2024_summary.csv, out/voting_places_2024.csv,
       out/va_to_voting_place_2024.csv, out/province_2024.csv, out/province_2024_by_opportunity.csv
"""
import sys, os
import pandas as pd

R = sys.argv[1]
OUT = os.path.join(R, "out")
EV = "2024 Provincial General Election"

vp = pd.read_csv(f"{R}/raw/ebc_vp_results/provincial_voting_results_by_voting_place.csv", dtype=str, encoding="utf-8-sig")
vp = vp[vp.EVENT_NAME == EV].copy()
vp["votes"] = vp.VOTES_CONSIDERED.astype(int)

PARTY_SHORT = {"BC NDP": "NDP", "Conservative Party": "CON", "BC Green Party": "GRN", "Independent": "IND",
               "Freedom Party of BC": "FPBC", "Libertarian": "LBN", "Communist Party of BC": "COMM",
               "Christian Heritage Party of B.C.": "CHP"}
valid = vp[vp.VOTE_CATEGORY == "Valid"].copy()
valid["AFFILIATION"] = valid.AFFILIATION.fillna("Unaffiliated")
valid["party"] = valid.AFFILIATION.map(PARTY_SHORT).fillna("UNAF")

# ---------- candidate level ----------
cand = (valid.groupby(["ED_ABBREVIATION", "ED_NAME", "CANDIDATE", "AFFILIATION", "party", "ELECTED"], dropna=False)
        .votes.sum().reset_index())
# vote-type splits per candidate
OPP = {"Advance voting": "adv", "Advance voting - out-of-district": "adv_ood", "Final voting": "final",
       "Final voting - out-of-district": "final_ood", "Special voting": "special", "DEO office voting": "deo",
       "Vote by mail": "mail", "Assisted telephone voting": "atv"}
valid["opp"] = valid.VOTING_OPPORTUNITY.map(OPP)
assert valid.opp.notna().all(), valid.VOTING_OPPORTUNITY.unique()
split = valid.pivot_table(index=["ED_ABBREVIATION", "CANDIDATE"], columns="opp", values="votes", aggfunc="sum", fill_value=0)
split.columns = [f"votes_{c}" for c in split.columns]
cand = cand.merge(split.reset_index(), on=["ED_ABBREVIATION", "CANDIDATE"])

rej = vp[vp.VOTE_CATEGORY == "Rejected"].groupby("ED_ABBREVIATION").votes.sum().rename("rejected_ballots")
tv = cand.groupby("ED_ABBREVIATION").votes.sum().rename("total_valid_votes")
reg = pd.read_csv(f"{R}/raw/ebc_regvoters/provincial_registered_voter_counts.csv", dtype=str, encoding="utf-8-sig")
reg = reg[reg.EVENT_NAME == "2024 General Election"].copy()
reg["n"] = reg.REGISTERED_VOTERS.astype(int)
regd = reg.groupby("ED_ABBREVIATION").n.sum().rename("registered_voters")

d = pd.concat([tv, rej, regd], axis=1).reset_index().rename(columns={"index": "ED_ABBREVIATION"})
d["ballots_considered"] = d.total_valid_votes + d.rejected_ballots
d["turnout_pct"] = (100 * d.ballots_considered / d.registered_voters).round(2)

cand = cand.merge(d, on="ED_ABBREVIATION")
cand["vote_share_pct"] = (100 * cand.votes / cand.total_valid_votes).round(2)
cand = cand.sort_values(["ED_ABBREVIATION", "votes"], ascending=[True, False])
cand["rank"] = cand.groupby("ED_ABBREVIATION").cumcount() + 1

# SOV cross-check + incumbency marker
sovc = pd.read_csv(f"{R}/work/sov2024_candidates.csv")
sovd = pd.read_csv(f"{R}/work/sov2024_district_summary.csv")
anoms = []
# match candidate by ED name + votes (SOV uses ballot names, open data uses "Last, First")
sovc_key = sovc.groupby(["ed_name", "votes"]).agg(list).reset_index()
m = cand.merge(sovc[["ed_name", "votes", "ballot_name", "member_of_previous_parliament"]],
               left_on=["ED_NAME", "votes"], right_on=["ed_name", "votes"], how="left")
dups = m.groupby(["ED_ABBREVIATION", "CANDIDATE"]).size()
if (dups > 1).any():
    anoms.append(f"ambiguous SOV vote match: {dups[dups > 1].index.tolist()}")
m = m.drop_duplicates(["ED_ABBREVIATION", "CANDIDATE"])
nomatch = m[m.ballot_name.isna()]
for _, r in nomatch.iterrows():
    anoms.append(f"open-data candidate not matched in SOV candidate table: {r.ED_NAME} {r.CANDIDATE} {r.votes}")
cand = m.drop(columns=["ed_name"])
sd = sovd[sovd.ed_name != "Total"].set_index("ed_name")
for _, r in d.merge(cand[["ED_ABBREVIATION", "ED_NAME"]].drop_duplicates(), on="ED_ABBREVIATION").iterrows():
    s = sd.loc[r.ED_NAME]
    for a, b in [("total_valid_votes", "total_valid"), ("rejected_ballots", "total_rejected"), ("registered_voters", "registered"), ("ballots_considered", "voters_who_voted")]:
        if int(r[a]) != int(s[b]):
            anoms.append(f"{r.ED_NAME}: open data {a}={r[a]} vs SOV {b}={s[b]}")

# margins
top = cand[cand["rank"] == 1].set_index("ED_ABBREVIATION")
sec = cand[cand["rank"] == 2].set_index("ED_ABBREVIATION")
mg = pd.DataFrame({"margin_votes": top.votes - sec.votes,
                   "margin_pts": (top.vote_share_pct - sec.vote_share_pct).round(2),
                   "margin_pts_exact": (100 * (top.votes - sec.votes) / top.total_valid_votes).round(3)})
cand = cand.merge(mg.reset_index(), on="ED_ABBREVIATION")
# elected flag check
chk = cand[(cand["rank"] == 1) != (cand.ELECTED == "Y")]
for _, r in chk.iterrows():
    anoms.append(f"ELECTED flag differs from top vote-getter: {r.ED_NAME} {r.CANDIDATE}")

cols = ["ED_ABBREVIATION", "ED_NAME", "CANDIDATE", "ballot_name", "AFFILIATION", "party", "votes", "vote_share_pct",
        "rank", "ELECTED", "member_of_previous_parliament",
        "votes_adv", "votes_adv_ood", "votes_final", "votes_final_ood", "votes_special", "votes_deo", "votes_mail", "votes_atv",
        "registered_voters", "total_valid_votes", "rejected_ballots", "ballots_considered", "turnout_pct",
        "margin_votes", "margin_pts", "margin_pts_exact"]
out = cand[cols].rename(columns={"ED_ABBREVIATION": "ed_code", "ED_NAME": "ed_name", "CANDIDATE": "candidate",
                                  "AFFILIATION": "affiliation", "ELECTED": "elected"})
out["elected"] = out.elected.eq("Y")
out.to_csv(f"{OUT}/districts_2024.csv", index=False)

# ---------- district summary ----------
RECOUNT = {  # source: Report of the CEO on the 2024 PGE, pp. 58-63
    "SRC": ("DEO full recount (automatic, margin <=100 at initial count); confirmed initial outcome", ""),
    "JFM": ("DEO full recount (automatic, margin <=100 at initial count); two uncounted quarantined boxes counted first under CEO Order; confirmed initial outcome", ""),
    "KEC": ("DEO partial recount (accepted request); judicial recount Nov 7-8 (Justice Beames); margin 38 -> 40", "judicial"),
    "SRG": ("Recount request declined; judicial recount Nov 7-8 (Justice Loo); margin 27 -> 22", "judicial"),
    "PRM": ("Partial judicial recount Nov 8 of one uncounted advance box (861 ballots) (Justice Tindale); margin 5,705 -> 6,068", "judicial"),
    "CRC": ("Recount request declined", ""), "MAE": ("Recount request declined", ""), "OBG": ("Recount request declined", ""),
}
CEO_ORDER = {"CQB": 76, "SRC": 214, "SWR": 441, "WVS": 22, "BDS": 28}
s = top[["ED_NAME", "party", "CANDIDATE", "votes", "vote_share_pct"]].rename(
    columns={"ED_NAME": "ed_name", "party": "winner_party", "CANDIDATE": "winner", "votes": "winner_votes", "vote_share_pct": "winner_share_pct"})
s = s.join(sec[["party", "CANDIDATE", "votes", "vote_share_pct"]].rename(
    columns={"party": "second_party", "CANDIDATE": "second", "votes": "second_votes", "vote_share_pct": "second_share_pct"}))
s = s.join(mg).join(d.set_index("ED_ABBREVIATION"))
inc = cand[cand.member_of_previous_parliament == True].groupby("ED_ABBREVIATION").apply(
    lambda g: "; ".join(f"{a} ({p})" for a, p in zip(g.ballot_name, g.party)), include_groups=False)
s["sitting_mla_candidates"] = inc
s["sitting_mla_won"] = cand[(cand.member_of_previous_parliament == True)].groupby("ED_ABBREVIATION").apply(
    lambda g: bool((g["rank"] == 1).any()), include_groups=False)
s["recount_note"] = [RECOUNT.get(k, ("", ""))[0] for k in s.index]
s["judicial_recount"] = [RECOUNT.get(k, ("", ""))[1] == "judicial" for k in s.index]
s["dEO_recount"] = s.index.isin(["SRC", "JFM", "KEC"])
s["ceo_order_unreported_ood_votes_added"] = [CEO_ORDER.get(k, 0) for k in s.index]
s["n_candidates"] = cand.groupby("ED_ABBREVIATION").size()
s.index.name = "ed_code"
s = s.rename(columns={"dEO_recount": "deo_recount"})
s.reset_index().to_csv(f"{OUT}/districts_2024_summary.csv", index=False)

# ---------- voting place level ----------
vpl = vp.copy()
vpl["AFFILIATION"] = vpl.AFFILIATION.fillna("")
vpl.loc[(vpl.VOTE_CATEGORY == "Valid") & (vpl.AFFILIATION == ""), "AFFILIATION"] = "Unaffiliated"
vpl["party"] = vpl.AFFILIATION.map(PARTY_SHORT)
vpl.loc[vpl.AFFILIATION == "Unaffiliated", "party"] = "UNAF"
vpl.loc[vpl.VOTE_CATEGORY == "Rejected", "party"] = "REJECTED"
vpl["vp_key"] = vpl.ID.str[:11]
keep = ["ID", "vp_key", "ED_ABBREVIATION", "ED_NAME", "VOTING_OPPORTUNITY", "VOTING_LOCATION", "ADDRESS_STANDARD_ID",
        "CANDIDATE", "AFFILIATION", "party", "ELECTED", "VOTE_CATEGORY", "votes", "COMBINED_INDICATOR", "RESULTS_REPORTED_UNDER"]
vpl[keep].rename(columns=str.lower).to_csv(f"{OUT}/voting_places_2024_long.csv", index=False)
# wide: one row per reporting unit (ED x opportunity x location)
w =vpl.groupby("vp_key").agg(ed_code=("ED_ABBREVIATION", "first"), ed_name=("ED_NAME", "first"),
                              voting_opportunity=("VOTING_OPPORTUNITY", "first"), voting_location=("VOTING_LOCATION", "first"),
                              address_standard_id=("ADDRESS_STANDARD_ID", "first"), combined=("COMBINED_INDICATOR", "first"),
                              reported_under=("RESULTS_REPORTED_UNDER", "first")).join(
    vpl.pivot_table(index="vp_key", columns="party", values="votes", aggfunc="sum", fill_value=0))
w["total_valid"] = w[[c for c in PARTY_SHORT.values() if c in w] + ["UNAF"]].sum(axis=1)
w.reset_index().to_csv(f"{OUT}/voting_places_2024_wide.csv", index=False)

# VA -> final voting place assignment (so voting-place results can be joined to VA polygons)
import json
gj = json.load(open(f"{R}/raw/bcgw_vavp2024/vavp_ge2024.geojson"))
a = pd.DataFrame([f["properties"] for f in gj["features"]])
a = a[["ED_ABBREVIATION", "EDVA_CODE", "VA_CODE", "ADDRESS_STANDARD_ID", "BUILDING_NAME", "STREET_ADDRESS", "LOCALITY", "FEATURE_AREA_SQM"]]
a["ADDRESS_STANDARD_ID"] = a.ADDRESS_STANDARD_ID.astype("Int64").astype(str)
rv = reg[["EDVA_CODE", "n", "VA_TYPE"]].rename(columns={"n": "registered_voters_2024"})
a = a.merge(rv, on="EDVA_CODE", how="left")
fk = w[w.voting_opportunity == "Final voting"].reset_index()[["vp_key", "ed_code", "address_standard_id"]]
a = a.merge(fk, left_on=["ED_ABBREVIATION", "ADDRESS_STANDARD_ID"], right_on=["ed_code", "address_standard_id"], how="left").drop(columns=["ed_code", "address_standard_id"])
a.rename(columns=str.lower).to_csv(f"{OUT}/va_to_voting_place_2024.csv", index=False)
na = a.vp_key.isna().sum()
if na:
    anoms.append(f"{na} 2024 areal VAs have no matching final-voting-place result row (assignment address not in results)")

# ---------- province ----------
P = valid.groupby("AFFILIATION").votes.sum()
seats = cand[cand["rank"] == 1].AFFILIATION.value_counts()
prov = pd.DataFrame({"valid_votes": P, "seats": seats}).fillna(0).astype(int)
prov["vote_share_pct"] = (100 * prov.valid_votes / prov.valid_votes.sum()).round(2)
prov = prov.sort_values("valid_votes", ascending=False)
tot_valid, tot_rej, tot_reg = int(P.sum()), int(d.rejected_ballots.sum()), int(d.registered_voters.sum())
prov.loc["TOTAL"] = [tot_valid, int(seats.sum()), 100.0]
prov[["valid_votes", "seats"]] = prov[["valid_votes", "seats"]].astype(int)
prov.index.name = "affiliation"
prov.reset_index().to_csv(f"{OUT}/province_2024.csv", index=False)
opp = vp.groupby(["VOTING_OPPORTUNITY", "VOTE_CATEGORY"]).votes.sum().unstack(fill_value=0)
opp["ballots_considered"] = opp.sum(axis=1)
opp["share_of_ballots_pct"] = (100 * opp.ballots_considered / opp.ballots_considered.sum()).round(2)
opp.loc["TOTAL"] = opp.sum()
opp.loc["TOTAL", "share_of_ballots_pct"] = 100
for c in ["Rejected", "Valid", "ballots_considered"]:
    opp[c] = opp[c].astype(int)
opp.reset_index().to_csv(f"{OUT}/province_2024_by_opportunity.csv", index=False)
stats = dict(total_valid=tot_valid, rejected=tot_rej, ballots=tot_valid + tot_rej, registered=tot_reg,
             turnout_pct=round(100 * (tot_valid + tot_rej) / tot_reg, 2),
             advance_share_pct=round(100 * opp.loc[["Advance voting", "Advance voting - out-of-district"], "ballots_considered"].sum() / (tot_valid + tot_rej), 2))
print(stats)
with open(f"{R}/work/anomalies_2024.txt", "w") as f:
    f.write("\n".join(anoms))
print("anomalies:", len(anoms)); print("\n".join(anoms[:30]))
