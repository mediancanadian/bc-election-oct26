"""Polls vs the count.

Usage: python3 compare.py [results.csv]   (default analysis/live/latest.csv)
Input columns: district code, party, votes (column names detected loosely: ed_code/district_code/
code/district; party/affiliation; votes). Party names are mapped to NDP/CON/GRN/CENTRE/ONEBC/OTH.
Rows for the same district+party are summed. Works on partial counts: only districts present are compared.

Writes to model/out/compare/:
  district_miss.csv  per district: counted share vs uniform and proportional projections, miss per party
                     (count minus projection, points), projected vs actual leader, hit/miss
  party_gap.csv      per party: poll average vs counted share (counted districts only, and all), gap,
                     plus projected vs actual leading-in seats
  compare_summary.json
Reads only the frozen projection (model/out/districts_projection.csv, poll_average.json).
"""
import os, sys, json, datetime
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, OUT, read_csv, pick, num, write_csv, norm_party

PARTIES = ["NDP", "CON", "GRN", "CENTRE", "ONEBC", "OTH"]
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "live/latest.csv")
dest = os.path.join(OUT, "compare")
os.makedirs(dest, exist_ok=True)

proj = {r["ed_code"]: r for r in read_csv(os.path.join(OUT, "districts_projection.csv"))}
byname = {r["district"].lower().replace("–", "-"): c for c, r in proj.items()}
polls = json.load(open(os.path.join(OUT, "poll_average.json")))["province"]

rows = read_csv(src)
if not rows:
    sys.exit(f"no rows in {src}")
cols = rows[0].keys()
c_ed = pick(cols, "ed_code", "district_code", "ed_abbreviation", "code", "district")
c_p = pick(cols, "party", "party_code", "affiliation")
c_v = pick(cols, "votes", "vote", "total_votes")

AFF = {"bc ndp": "NDP", "conservative party": "CON", "bc green party": "GRN", "centrebc": "CENTRE", "onebc": "ONEBC"}
votes = defaultdict(lambda: defaultdict(float))
unknown = set()
for r in rows:
    k = str(r[c_ed]).strip()
    ed = k.upper() if k.upper() in proj else byname.get(k.lower().replace("–", "-"))
    if not ed:
        unknown.add(k)
        continue
    p = AFF.get(str(r[c_p]).strip().lower()) or norm_party(r[c_p])
    votes[ed][p] += num(r[c_v]) or 0

counted = sorted(e for e in votes if sum(votes[e].values()) > 0)
out, seats_actual = [], Counter()
for e in counted:
    tot = sum(votes[e].values())
    act = {p: 100 * votes[e].get(p, 0) / tot for p in PARTIES}
    lead = max(PARTIES, key=lambda p: act[p])
    seats_actual[lead] += 1
    pr = proj[e]
    row = {"ed_code": e, "district": pr["district"], "region": pr["region"], "votes_counted": int(tot),
           "actual_leader": lead}
    for p in PARTIES:
        row[f"act_{p}"] = round(act[p], 1)
    for k in ("uni", "prop"):
        row[f"{k}_leader"] = pr[f"{k}_winner"]
        row[f"{k}_tier"] = pr[f"{k}_tier"]
        row[f"{k}_hit"] = pr[f"{k}_winner"] == lead
        for p in PARTIES:
            row[f"{k}_miss_{p}"] = round(act[p] - float(pr[f"{k}_{p}"]), 1)
        row[f"{k}_abs_miss_sum"] = round(sum(abs(row[f"{k}_miss_{p}"]) for p in PARTIES) / 2, 1)
    out.append(row)
write_csv(os.path.join(dest, "district_miss.csv"), out, list(out[0].keys()) if out else ["ed_code"])

# party-level gap: counted share in reported districts vs poll avg; also projection on same districts
gap = []
tot_all = sum(sum(votes[e].values()) for e in counted)
for p in PARTIES:
    cs = 100 * sum(votes[e].get(p, 0) for e in counted) / tot_all if tot_all else 0
    w = {e: sum(votes[e].values()) for e in counted}
    pu = sum(float(proj[e][f"uni_{p}"]) * w[e] for e in counted) / tot_all if tot_all else 0
    pp = sum(float(proj[e][f"prop_{p}"]) * w[e] for e in counted) / tot_all if tot_all else 0
    gap.append({"party": p, "poll_average": polls.get(p), "counted_share": round(cs, 2),
                "gap_count_minus_polls": round(cs - polls.get(p, 0), 2),
                "projected_share_same_districts_uniform": round(pu, 2),
                "gap_count_minus_projection_uniform": round(cs - pu, 2),
                "projected_share_same_districts_prop": round(pp, 2),
                "seats_leading_counted": seats_actual.get(p, 0),
                "seats_projected_uniform_same_districts": sum(proj[e]["uni_winner"] == p for e in counted),
                "seats_projected_prop_same_districts": sum(proj[e]["prop_winner"] == p for e in counted)})
write_csv(os.path.join(dest, "party_gap.csv"), gap, list(gap[0].keys()))

summ = {"run_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": src, "districts_with_votes": len(counted), "of": len(proj),
        "note": "counted_share covers only districts with votes; partial counts are not province-wide",
        "uniform_hits": sum(r["uni_hit"] for r in out), "prop_hits": sum(r["prop_hit"] for r in out),
        "unmatched_district_keys": sorted(unknown),
        "misses_uniform": [(r["ed_code"], r["uni_leader"], r["actual_leader"], r["uni_tier"]) for r in out if not r["uni_hit"]],
        "party_gap": gap}
json.dump(summ, open(os.path.join(dest, "compare_summary.json"), "w"), indent=1)

print(f"{len(counted)}/{len(proj)} districts with votes | uniform right {summ['uniform_hits']}, proportional right {summ['prop_hits']}")
print(f"{'party':7}{'polls':>7}{'count':>7}{'gap':>7}{'seats':>6}{'proj':>6}")
for g in gap:
    print(f"{g['party']:7}{g['poll_average'] or 0:7.1f}{g['counted_share']:7.1f}{g['gap_count_minus_polls']:7.1f}"
          f"{g['seats_leading_counted']:6d}{g['seats_projected_uniform_same_districts']:6d}")
if unknown:
    print("unmatched district keys:", sorted(unknown))
