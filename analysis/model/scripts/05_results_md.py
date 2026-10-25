"""Write model/results.md from the model outputs (numbers are never typed by hand)."""
import os, sys, json, csv
sys.path.insert(0, os.path.dirname(__file__))
from common import MODEL, OUT, read_csv

pa = json.load(open(os.path.join(OUT, "poll_average.json")))
s = json.load(open(os.path.join(OUT, "projection_summary.json")))
rows = read_csv(os.path.join(OUT, "districts_projection.csv"))
fz_path = os.path.join(MODEL, "model_frozen.json")
fz = json.load(open(fz_path)) if os.path.exists(fz_path) else None
P = ["NDP", "CON", "GRN", "CENTRE", "ONEBC", "OTH"]
LBL = {"NDP": "NDP", "CON": "Conservative", "GRN": "Green", "CENTRE": "CentreBC", "ONEBC": "OneBC", "OTH": "Other"}
pu = read_csv(os.path.join(OUT, "polls_used.csv"))

L = []
a = L.append
a("# BC 2026: pre-results seat estimate (polls vs the count)\n")
if fz:
    a(f"**Frozen {fz['frozen_utc']} UTC ({fz['frozen_pacific']}), {fz['minutes_before_close']} minutes before polls closed "
      f"(8 p.m. Pacific, 03:00 UTC Oct 25).** Hashes of inputs, outputs and scripts are in `model_frozen.json`.\n")
a("## Method in plain words\n")
a("1. **Poll average.** For each pollster, take its last poll with fieldwork ending on or after Sept 22, 2026 "
  "(election call). Average them with equal weight. No adjustments for sample size, mode or house effects.")
a("2. **Regions.** Each of the 93 districts goes to Metro Vancouver, the Capital Region or the rest of BC, by where most of "
  "its 2021 census population lives (census divisions 5915 and 5917). Metro Vancouver uses the regional poll average "
  "where at least 2 pollsters publish that region. No pollster publishes the Capital Region alone, so it gets the "
  "change pollsters show for Vancouver Island. The rest of BC is whatever keeps the province total equal to the poll average.")
a("3. **Swing.** Uniform: each party's 2024 district share plus the change in its regional share. Proportional: the 2024 "
  "district share multiplied by the ratio of new to old regional share. Parties are then scaled so each region's total "
  "matches its target and each district adds to 100.")
a("4. **New parties and gaps.** CentreBC and OneBC ran nowhere in 2024. Their poll share is spread evenly over only the "
  "districts where they have a 2026 candidate, scaled so the regional total still matches the poll. A party with no "
  "2026 candidate in a district gets 0 and its share is spread over the other parties there by rescaling (NDP has no "
  "candidate in Peace River North). A party running where it did not run in 2024 starts from its 2024 regional average.")
a("5. **Tiers** (lead over second place): toss-up under 3 points, lean under 8, likely under 15, safe 15 or more.\n")

a("## Poll average\n")
a("| Party | Average | Pollsters |\n|---|---|---|")
for p in P:
    a(f"| {LBL[p]} | {pa['province'][p]:.1f} | {pa['n_pollsters'].get(p, '-') if p != 'OTH' else 'remainder'} |")
a("\nPolls used: " + "; ".join(f"{r['pollster']} ({r['field_end']})" for r in pu) + ".\n")
a("Regional targets (% of valid votes) vs 2024:\n")
a("| Region | " + " | ".join(LBL[p] for p in P[:3]) + " | Basis |\n|---|---|---|---|---|")
for R, t in s["regional_targets"].items():
    o = s["result_2024_region"][R]
    a(f"| {R} | " + " | ".join(f"{t[p]:.1f} ({t[p]-o[p]:+.1f})" for p in P[:3]) + f" | {s['regional_target_source'][R]['NDP']} |")
a("")

a("## Projected seats (47 for a majority)\n")
a("| Party | Uniform swing | Proportional swing | 2024 result |\n|---|---|---|---|")
w24 = {p: sum(r["winner_2024"] == p for r in rows) for p in P}
for p in P:
    u, pr = s["seats"]["uniform"].get(p, 0), s["seats"]["proportional"].get(p, 0)
    if u or pr or w24[p]:
        a(f"| {LBL[p]} | {u} | {pr} | {w24[p]} |")
a("")
for k in ("uniform", "proportional"):
    tc = s["tier_counts"][k]
    a(f"- **{k.capitalize()}** tiers: " + ", ".join(f"{key} {n}" for key, n in sorted(tc.items())))
a("")

a("## Toss-ups (lead under 3 points)\n")
a("| District | Region | Uniform | Proportional |\n|---|---|---|---|")
for r in rows:
    if r["uni_tier"] == "toss-up" or r["prop_tier"] == "toss-up":
        a(f"| {r['district']} | {r['region']} | {r['uni_winner']} +{r['uni_margin']} ({r['uni_tier']}) | "
          f"{r['prop_winner']} +{r['prop_margin']} ({r['prop_tier']}) |")
dis = [r for r in rows if r["variants_agree"] == "False"]
a("\nVariants disagree on: " + (", ".join(f"{r['district']} (uniform {r['uni_winner']}, proportional {r['prop_winner']})" for r in dis) or "none") + ".\n")

a("## Limits\n")
a("- Swing models carry 2024 patterns forward. They ignore candidate effects: Conservatives who sat as independents or "
  "joined CentreBC and are now running again as Conservatives, Elenore Sturko (CentreBC leader, Surrey South), "
  "Dallas Brodie (OneBC, Vancouver-Quilchena), Jordan Kealy (independent incumbent, Peace River North), and open seats.")
a("- CentreBC and OneBC get a flat share where they run; real support will be lumpy. Their poll shares come from only 7 "
  "of 10 pollsters (Pallas, Forum and Innovative do not report them separately).")
a("- The Capital Region uses Vancouver Island poll numbers as a proxy. Regional subsamples are small (often 150 to 300 "
  "people) and pollsters define regions differently; only exactly matching labels are used.")
a("- Rest of BC is a residual, so any error in the Metro or Island figures lands there.")
a("- Simple average: no weighting by recency, sample size or pollster track record. One poll per pollster.")
a("- No uncertainty interval. The toss-up list is where a normal polling miss (2 to 3 points) flips the seat.")
a("- 2024 shares are on the same 2023 boundaries, so no transposition is needed.\n")
a("## Files\n")
a("- `out/poll_average.json`, `out/polls_used.csv`: poll average and the polls in it")
a("- `out/regions.csv`: district to region")
a("- `out/districts_projection.csv`: every district, 2024 shares, both variants, winner, margin, tier")
a("- `out/projection_summary.json`: seats, targets, tiers, toss-ups")
a("- `model_frozen.json`: freeze time and SHA-256 hashes")
a("- `scripts/run_all.sh` rebuilds; `scripts/compare.py [results.csv]` runs polls vs the count "
  "(default `analysis/live/latest.csv`, columns district code, party, votes) into `out/compare/`.")
open(os.path.join(MODEL, "results.md"), "w").write("\n".join(L) + "\n")
print("wrote results.md")
