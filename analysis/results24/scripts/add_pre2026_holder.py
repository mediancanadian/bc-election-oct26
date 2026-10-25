"""Attach Legislative Assembly (LIMS API) 43rd Parliament member/party per district to districts_2024_summary.csv.

Usage: python3 -I add_pre2026_holder.py <results24_root>
Records the API values verbatim; no reconciliation is attempted (see results.md anomaly note).
"""
import sys, json
import pandas as pd

R = sys.argv[1]
d = json.load(open(f"{R}/raw/leg_bc/constituency_members.json"))["data"]["allConstituencies"]["nodes"]
rows = []
for c in d:
    m = [x for x in c["memberParliamentsByConstituencyId"]["nodes"] if x["parliamentByParliamentId"]["number"] == 43]
    rows.append({"ed_name": c["name"],
                 "lims_43rd_members": "; ".join(f'{x["memberByMemberId"]["firstName"]} {x["memberByMemberId"]["lastName"]} ({x["partyByPartyId"]["name"]}, active={x["active"]})' for x in m),
                 "lims_43rd_party_latest_active": "; ".join(x["partyByPartyId"]["name"] for x in m if x["active"]) or "none active (vacant)"})
L = pd.DataFrame(rows)
s = pd.read_csv(f"{R}/out/districts_2024_summary.csv")
s = s.drop(columns=[c for c in s.columns if c.startswith("lims_")]).merge(L, on="ed_name", how="left")
assert s.lims_43rd_members.notna().all(), s[s.lims_43rd_members.isna()].ed_name.tolist()
s.to_csv(f"{R}/out/districts_2024_summary.csv", index=False)
print(s.lims_43rd_party_latest_active.value_counts().to_string())
