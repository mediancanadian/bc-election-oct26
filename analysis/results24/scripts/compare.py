"""Close 2024 races and seat changes 2020 (notional, transposed) -> 2024.

Usage: python3 -I compare.py <results24_root>
Party lineage note: BC Liberal Party renamed BC United (2023); BC United suspended its 2024 campaign and its
candidates ran as Unaffiliated or withdrew. A LIB(2020) -> CON(2024) change is therefore recorded as a change of
party label; column `change_type` separates that case.
"""
import sys
import pandas as pd

R = sys.argv[1]
s24 = pd.read_csv(f"{R}/out/districts_2024_summary.csv")
x = pd.read_csv(f"{R}/out/transposed_2020_on_2023_eds.csv")
close = s24[s24.margin_pts < 5].sort_values("margin_pts")[
    ["ed_code", "ed_name", "winner_party", "winner", "second_party", "second", "margin_votes", "margin_pts", "turnout_pct", "judicial_recount", "recount_note"]]
close.to_csv(f"{R}/out/close_races_2024.csv", index=False)
m = s24[["ed_code", "ed_name", "winner_party", "second_party", "margin_pts", "winner_share_pct"]].merge(
    x[["ed_code", "notional_winner_2020", "notional_second_2020", "notional_margin_pts_2020", "NDP_pct", "LIB_pct", "GRN_pct", "CON_pct"]], on="ed_code")
m["changed"] = m.winner_party != m.notional_winner_2020
m["change_type"] = ""
m.loc[m.changed & (m.notional_winner_2020 == "LIB") & (m.winner_party == "CON"), "change_type"] = "LIB->CON (right-of-centre label change)"
m.loc[m.changed & (m.change_type == ""), "change_type"] = m.notional_winner_2020 + "->" + m.winner_party
m.rename(columns={"winner_party": "winner_2024", "second_party": "second_2024", "margin_pts": "margin_pts_2024",
                  "NDP_pct": "NDP_pct_2020n", "LIB_pct": "LIB_pct_2020n", "GRN_pct": "GRN_pct_2020n", "CON_pct": "CON_pct_2020n"}
         ).to_csv(f"{R}/out/seat_changes_2020n_2024_all.csv", index=False)
ch = m[m.changed]
ch.to_csv(f"{R}/out/seat_changes_2020n_2024.csv", index=False)
print("close", len(close)); print(close[["ed_name", "winner_party", "second_party", "margin_votes", "margin_pts"]].to_string())
print("changed", len(ch)); print(ch.change_type.value_counts().to_string())
print(ch[["ed_name", "notional_winner_2020", "notional_margin_pts_2020", "winner_2024" if "winner_2024" in ch else "winner_party"]].to_string())
