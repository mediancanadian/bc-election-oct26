"""Build 2020 BC general election tables (87 districts, 2015 boundaries) from Elections BC open data.

Usage: python3 -I build_2020.py <results24_root>
Writes out/districts_2020.csv, out/districts_2020_summary.csv, out/voting_areas_2020.csv,
       out/province_2020.csv, out/province_2020_by_opportunity.csv
"""
import sys, io
import pandas as pd

R = sys.argv[1]
OUT = f"{R}/out"
b = open(f"{R}/raw/ebc_va_results/provincial_voting_results_by_va.csv", "rb").read()
b = b[3:] if b[:3] == b"\xef\xbb\xbf" else b
va = pd.read_csv(io.StringIO(b.decode("latin-1")), dtype=str)  # file body is Latin-1 despite a UTF-8 BOM
va = va[va.EVENT_NAME == "2020 General Election"].copy()
va["votes"] = va.VOTES_CONSIDERED.astype(int)
PARTY_SHORT = {"BC NDP": "NDP", "BC Liberal Party": "LIB", "BC Green Party": "GRN", "Conservative": "CON",
               "Independent": "IND", "Libertarian": "LBN", "Christian Heritage Party of B.C.": "CHP",
               "Communist Party of BC": "COMM", "B.C. Vision": "BCV", "Wexit BC": "WEXIT", "Rural BC Party": "RURAL"}
OPP = {"General voting": "general", "Advance voting": "adv", "s. 98 Special": "special", "s. 99 Absentee - in ED": "absentee_in_ed",
       "s. 100 Absentee - out of ED": "absentee_out_ed", "s. 101 Absentee - advance": "absentee_adv",
       "s. 104 Voting in DEO office": "deo", "s. 106 Voting by mail": "mail"}
va["opp"] = va.VOTING_OPPORTUNITY.map(OPP)
assert va.opp.notna().all()
valid = va[va.VOTE_CATEGORY == "Valid"].copy()
valid["party"] = valid.AFFILIATION.map(PARTY_SHORT)
assert valid.party.notna().all(), valid.AFFILIATION.unique()

cand = valid.groupby(["ED_ABBREVIATION", "ED_NAME", "CANDIDATE", "AFFILIATION", "party", "ELECTED"]).votes.sum().reset_index()
split = valid.pivot_table(index=["ED_ABBREVIATION", "CANDIDATE"], columns="opp", values="votes", aggfunc="sum", fill_value=0)
split.columns = [f"votes_{c}" for c in split.columns]
cand = cand.merge(split.reset_index(), on=["ED_ABBREVIATION", "CANDIDATE"])
rej = va[va.VOTE_CATEGORY == "Rejected"].groupby("ED_ABBREVIATION").votes.sum().rename("rejected_ballots")
tv = cand.groupby("ED_ABBREVIATION").votes.sum().rename("total_valid_votes")
reg = pd.read_csv(f"{R}/raw/ebc_regvoters/provincial_registered_voter_counts.csv", dtype=str, encoding="utf-8-sig")
reg = reg[reg.EVENT_NAME == "2020 General Election"].copy()
reg["n"] = reg.REGISTERED_VOTERS.astype(int)
d = pd.concat([tv, rej, reg.groupby("ED_ABBREVIATION").n.sum().rename("registered_voters")], axis=1)
d.index.name = "ED_ABBREVIATION"
d = d.reset_index()
d["ballots_considered"] = d.total_valid_votes + d.rejected_ballots
d["turnout_pct"] = (100 * d.ballots_considered / d.registered_voters).round(2)
cand = cand.merge(d, on="ED_ABBREVIATION")
cand["vote_share_pct"] = (100 * cand.votes / cand.total_valid_votes).round(2)
cand = cand.sort_values(["ED_ABBREVIATION", "votes"], ascending=[True, False])
cand["rank"] = cand.groupby("ED_ABBREVIATION").cumcount() + 1

anoms = []
sovc = pd.read_csv(f"{R}/work/sov2020_candidates.csv")
sovd = pd.read_csv(f"{R}/work/sov2020_district_summary.csv")
m = cand.merge(sovc[["ed_name", "votes", "ballot_name", "member_of_previous_parliament"]], left_on=["ED_NAME", "votes"],
               right_on=["ed_name", "votes"], how="left").drop_duplicates(["ED_ABBREVIATION", "CANDIDATE"])
for _, r in m[m.ballot_name.isna()].iterrows():
    anoms.append(f"2020 candidate not matched in SOV: {r.ED_NAME} {r.CANDIDATE} {r.votes}")
cand = m.drop(columns="ed_name")
sd = sovd[sovd.ed_name != "Total"].set_index("ed_name")
for _, r in d.merge(cand[["ED_ABBREVIATION", "ED_NAME"]].drop_duplicates(), on="ED_ABBREVIATION").iterrows():
    if r.ED_NAME not in sd.index:
        anoms.append(f"2020 SOV district row missing for {r.ED_NAME}")
        continue
    s = sd.loc[r.ED_NAME]
    for a, bb in [("total_valid_votes", "total_valid"), ("rejected_ballots", "total_rejected"), ("registered_voters", "registered"), ("ballots_considered", "voters_who_voted")]:
        if int(r[a]) != int(s[bb]):
            anoms.append(f"2020 {r.ED_NAME}: open data {a}={r[a]} vs SOV {bb}={s[bb]}")
top = cand[cand["rank"] == 1].set_index("ED_ABBREVIATION")
sec = cand[cand["rank"] == 2].set_index("ED_ABBREVIATION")
mg = pd.DataFrame({"margin_votes": top.votes - sec.votes, "margin_pts": (top.vote_share_pct - sec.vote_share_pct).round(2)})
cand = cand.merge(mg.reset_index(), on="ED_ABBREVIATION")
for _, r in cand[(cand["rank"] == 1) != (cand.ELECTED == "Y")].iterrows():
    anoms.append(f"2020 ELECTED flag differs from top vote-getter: {r.ED_NAME} {r.CANDIDATE}")

vcols = [c for c in cand.columns if c.startswith("votes_")]
out = cand[["ED_ABBREVIATION", "ED_NAME", "CANDIDATE", "ballot_name", "AFFILIATION", "party", "votes", "vote_share_pct", "rank",
            "ELECTED", "member_of_previous_parliament"] + vcols + ["registered_voters", "total_valid_votes", "rejected_ballots",
                                                                  "ballots_considered", "turnout_pct", "margin_votes", "margin_pts"]]
out = out.rename(columns={"ED_ABBREVIATION": "ed_code", "ED_NAME": "ed_name", "CANDIDATE": "candidate", "AFFILIATION": "affiliation", "ELECTED": "elected"})
out["elected"] = out.elected.eq("Y")
out.to_csv(f"{OUT}/districts_2020.csv", index=False)

s = top[["ED_NAME", "party", "CANDIDATE", "votes", "vote_share_pct"]].rename(columns={"ED_NAME": "ed_name", "party": "winner_party", "CANDIDATE": "winner", "votes": "winner_votes", "vote_share_pct": "winner_share_pct"})
s = s.join(sec[["party", "CANDIDATE", "votes", "vote_share_pct"]].rename(columns={"party": "second_party", "CANDIDATE": "second", "votes": "second_votes", "vote_share_pct": "second_share_pct"}))
s = s.join(mg).join(d.set_index("ED_ABBREVIATION"))
s["sitting_mla_candidates"] = cand[cand.member_of_previous_parliament == True].groupby("ED_ABBREVIATION").apply(
    lambda g: "; ".join(f"{a} ({p})" for a, p in zip(g.ballot_name, g.party)), include_groups=False)
s["recount_note"] = ""
s.loc["WVS", "recount_note"] = "Judicial recount Nov 16-17 2020 (Justice Crerar); margin 41 -> 60 (2020 CEO report)"
s["judicial_recount"] = s.index == "WVS"
s.index.name = "ed_code"
s.reset_index().to_csv(f"{OUT}/districts_2020_summary.csv", index=False)

# voting-area level (general voting day only; advance by voting place; other opportunities ED-wide)
g = va[va.opp == "general"].copy()
g["party"] = g.AFFILIATION.map(PARTY_SHORT).fillna("REJECTED")
w = g.pivot_table(index=["ED_ABBREVIATION", "EDVA_CODE", "VA_CODE"], columns="party", values="votes", aggfunc="sum", fill_value=0)
flags = g.groupby("EDVA_CODE").agg(combined=("COMBINED_INDICATOR", "first"), reported_under=("RESULTS_REPORTED_UNDER", "first"))
w = w.reset_index().merge(flags.reset_index(), on="EDVA_CODE").merge(
    reg[["EDVA_CODE", "VA_TYPE", "n"]].rename(columns={"n": "registered_voters"}), on="EDVA_CODE", how="left")
w["total_valid"] = w[[c for c in PARTY_SHORT.values() if c in w]].sum(axis=1)
w.rename(columns={"ED_ABBREVIATION": "ed_code", "EDVA_CODE": "edva_code", "VA_CODE": "va_code", "VA_TYPE": "va_type"}).to_csv(f"{OUT}/voting_areas_2020.csv", index=False)
# advance voting by voting place
a = va[va.opp == "adv"].copy()
a["party"] = a.AFFILIATION.map(PARTY_SHORT).fillna("REJECTED")
aw = a.pivot_table(index=["ED_ABBREVIATION", "VOTING_LOCATION"], columns="party", values="votes", aggfunc="sum", fill_value=0).reset_index()
aw.rename(columns={"ED_ABBREVIATION": "ed_code", "VOTING_LOCATION": "voting_location"}).to_csv(f"{OUT}/advance_places_2020.csv", index=False)

P = valid.groupby("AFFILIATION").votes.sum()
seats = cand[cand["rank"] == 1].AFFILIATION.value_counts()
prov = pd.DataFrame({"valid_votes": P, "seats": seats}).fillna(0).astype(int)
prov["vote_share_pct"] = (100 * prov.valid_votes / prov.valid_votes.sum()).round(2)
prov = prov.sort_values("valid_votes", ascending=False)
prov.loc["TOTAL"] = [int(P.sum()), int(seats.sum()), 100.0]
prov[["valid_votes", "seats"]] = prov[["valid_votes", "seats"]].astype(int)
prov.index.name = "affiliation"
prov.reset_index().to_csv(f"{OUT}/province_2020.csv", index=False)
opp = va.groupby(["VOTING_OPPORTUNITY", "VOTE_CATEGORY"]).votes.sum().unstack(fill_value=0)
opp["ballots_considered"] = opp.sum(axis=1)
opp["share_of_ballots_pct"] = (100 * opp.ballots_considered / opp.ballots_considered.sum()).round(2)
opp.loc["TOTAL"] = opp.sum()
opp.loc["TOTAL", "share_of_ballots_pct"] = 100
for c in ["Rejected", "Valid", "ballots_considered"]:
    opp[c] = opp[c].astype(int)
opp.reset_index().to_csv(f"{OUT}/province_2020_by_opportunity.csv", index=False)
T = int(d.ballots_considered.sum())
print(dict(valid=int(P.sum()), rejected=int(d.rejected_ballots.sum()), registered=int(d.registered_voters.sum()),
           turnout=round(100 * T / d.registered_voters.sum(), 2),
           advance_share=round(100 * opp.loc["Advance voting", "ballots_considered"] / T, 2),
           mail_share=round(100 * opp.loc["s. 106 Voting by mail", "ballots_considered"] / T, 2)))
open(f"{R}/work/anomalies_2020.txt", "w").write("\n".join(anoms))
print("anomalies", len(anoms), anoms[:20])
