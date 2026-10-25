"""Project 2026 district vote shares from 2024 results + the poll average.

Parties modelled: NDP, CON, GRN, CENTRE (CentreBC), ONEBC, OTH (all others, incl. independents).

Regional targets (per party, % of valid votes):
  Metro Vancouver : regional poll average where >=2 pollsters publish it, else uniform provincial change
  Capital Region  : the change pollsters show for Vancouver Island (poll Island avg minus 2024 Island
                    result, both on the same set of Island districts) added to the 2024 Capital result
  Rest of BC      : residual, so the vote-weighted province total equals the provincial poll average
  OTH (others)    : 2024 regional share x (provincial poll avg / 2024 provincial share), all regions
  Weights = 2024 total valid votes per region.

District shares:
  uniform      : 2024 district share + (region target - 2024 region share)
  proportional : 2024 district share x (region target / 2024 region share)
  Negative values are set to 0.
  Party running in 2026 but not in 2024 in a district (incl. all CentreBC/OneBC districts): base =
    the party's average 2024 share in its region (0 for the new parties), and new parties get a flat
    share equal to their target among districts where they have a candidate.
  Party with no 2026 candidate in a district: share 0.
  Then repeat (50 rounds): scale each party so its vote-weighted total in each region hits the target
  over districts where it runs; scale each district to sum to 100. Converges to both conditions.
Margin = winner share - runner-up share; tiers: toss-up <3, lean <8, likely <15, safe >=15.
"""
import os, sys, json
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, OUT, read_csv, num, write_csv, tier

PARTIES = ["NDP", "CON", "GRN", "CENTRE", "ONEBC", "OTH"]
NEW = {"CENTRE", "ONEBC"}
REGIONS = ["Metro Vancouver", "Capital Region", "Rest of BC"]
ISLAND_CDS = {"5917", "5919", "5921", "5923", "5924", "5926", "5943"}  # census divisions on Vancouver Island


def p24(code):
    return code if code in ("NDP", "CON", "GRN") else "OTH"


def p26(aff):
    return {"BC NDP": "NDP", "Conservative Party": "CON", "BC Green Party": "GRN",
            "CentreBC": "CENTRE", "OneBC": "ONEBC"}.get(aff, "OTH")


# ---- inputs
region = {r["ed_code"]: r["region"] for r in read_csv(os.path.join(OUT, "regions.csv"))}
polls = json.load(open(os.path.join(OUT, "poll_average.json")))
prov_t = polls["province"]

v24 = defaultdict(lambda: defaultdict(float))
tot24 = {}
name = {}
for r in read_csv(os.path.join(ROOT, "results24/out/districts_2024.csv")):
    v24[r["ed_code"]][p24(r["party"])] += num(r["votes"])
    tot24[r["ed_code"]] = num(r["total_valid_votes"])
    name[r["ed_code"]] = r["ed_name"]
sh24 = {e: {p: 100 * v24[e][p] / tot24[e] for p in PARTIES} for e in tot24}

runs = defaultdict(set)
cands = defaultdict(list)
for r in read_csv(os.path.join(ROOT, "live/candidates_2026.csv")):
    runs[r["ed_code"]].add(p26(r["affiliation"]))
    if r["incumbent"] == "Y":
        cands[r["ed_code"]].append(f'{r["candidate"]} ({r["affiliation"]}; at dissolution {r["mla_lims_affiliation_at_dissolution"] or "n/a"})')
ran24 = {e: {p for p in PARTIES if v24[e][p] > 0} for e in tot24}

eds = sorted(tot24)
assert len(eds) == 93 and set(eds) == set(region), "district sets differ"

# Island districts (majority of 2021 population in an Island census division) for the Capital proxy
pop = defaultdict(lambda: defaultdict(float))
for r in read_csv(os.path.join(ROOT, "geo/out/da_to_ed2023_detail.csv")):
    pop[r["ed_code"]][r["DAUID"][:4] in ISLAND_CDS] += (num(r["da_pop_2021"]) or 0) * (num(r["pop_share"]) or 0)
island = {e for e in eds if pop[e][True] > pop[e][False]}


def wavg(es, p, sh):
    w = sum(tot24[e] for e in es)
    return sum(sh[e][p] * tot24[e] for e in es) / w


reg_eds = {R: [e for e in eds if region[e] == R] for R in REGIONS}
W = {R: sum(tot24[e] for e in reg_eds[R]) for R in REGIONS}
Wt = sum(W.values())
r24 = {R: {p: wavg(reg_eds[R], p, sh24) for p in PARTIES} for R in REGIONS}
prov24 = {p: wavg(eds, p, sh24) for p in PARTIES}
isl24 = {p: wavg(sorted(island), p, sh24) for p in PARTIES}

# ---- regional targets
target = {R: {} for R in REGIONS}
source = {R: {} for R in REGIONS}
regpoll = polls["regional"]
for p in PARTIES:
    if p == "OTH":  # small and mostly independents: scale 2024 regional share by the provincial ratio
        for R in REGIONS:
            target[R][p] = r24[R][p] * prov_t[p] / prov24[p]
            source[R][p] = "2024 x (poll avg / 2024), provincial ratio"
        continue
    dprov = prov_t[p] - prov24[p]
    mv = regpoll.get("Metro Vancouver", {}).get(p)
    if mv:
        target["Metro Vancouver"][p], source["Metro Vancouver"][p] = mv["avg"], f'poll avg (n={mv["n"]})'
    else:
        target["Metro Vancouver"][p], source["Metro Vancouver"][p] = r24["Metro Vancouver"][p] + dprov, "2024 + provincial change"
    cr = regpoll.get("Capital Region", {}).get(p)
    if cr:
        target["Capital Region"][p] = r24["Capital Region"][p] + (cr["avg"] - isl24[p])
        source["Capital Region"][p] = f'2024 + Vancouver Island poll change (n={cr["n"]})'
    else:
        target["Capital Region"][p], source["Capital Region"][p] = r24["Capital Region"][p] + dprov, "2024 + provincial change"
    rest = (prov_t[p] * Wt - target["Metro Vancouver"][p] * W["Metro Vancouver"]
            - target["Capital Region"][p] * W["Capital Region"]) / W["Rest of BC"]
    target["Rest of BC"][p], source["Rest of BC"][p] = rest, "residual to match province"
for R in REGIONS:
    for p in PARTIES:
        target[R][p] = max(target[R][p], 0.0)


def project(kind):
    sh = {}
    for e in eds:
        R = region[e]
        sh[e] = {}
        for p in PARTIES:
            if p not in runs[e]:
                sh[e][p] = 0.0
                continue
            if p in NEW:
                sh[e][p] = target[R][p]
                continue
            if p in ran24[e]:
                base = sh24[e][p]
            else:  # running now, did not run in 2024: regional average among districts it contested
                es = [x for x in reg_eds[R] if p in ran24[x]]
                base = wavg(es, p, sh24) if es else 0.0
            if kind == "uniform":
                v = base + target[R][p] - r24[R][p]
            else:
                v = base * (target[R][p] / r24[R][p]) if r24[R][p] > 0 else target[R][p]
            sh[e][p] = max(v, 0.0)
    for _ in range(50):
        for R in REGIONS:
            for p in PARTIES:
                es = [e for e in reg_eds[R] if sh[e][p] > 0]
                if not es:
                    continue
                cur = sum(sh[e][p] * tot24[e] for e in es) / W[R]
                if cur > 0:
                    for e in es:
                        sh[e][p] *= target[R][p] / cur
        for e in eds:
            s = sum(sh[e].values())
            for p in PARTIES:
                sh[e][p] *= 100 / s
    return sh


out_rows, seats, tossups, check = [], {}, {}, {}
results = {}
for kind in ("uniform", "proportional"):
    sh = project(kind)
    results[kind] = sh
    seats[kind] = Counter()
    for e in eds:
        order = sorted(PARTIES, key=lambda p: -sh[e][p])
        w, s = order[0], order[1]
        m = sh[e][w] - sh[e][s]
        seats[kind][w] += 1
        sh[e]["_w"], sh[e]["_s"], sh[e]["_m"], sh[e]["_t"] = w, s, m, tier(m)
    tossups[kind] = [e for e in eds if sh[e]["_t"] == "toss-up"]
    check[kind] = {p: round(wavg(eds, p, sh), 2) for p in PARTIES}

w24 = {e: max(PARTIES, key=lambda p: sh24[e][p]) for e in eds}
for e in eds:
    u, pr = results["uniform"][e], results["proportional"][e]
    row = {"ed_code": e, "district": name[e], "region": region[e], "winner_2024": w24[e],
           "parties_running_2026": " ".join(p for p in PARTIES if p in runs[e])}
    for p in PARTIES:
        row[f"sh24_{p}"] = round(sh24[e][p], 1)
    for k, d in (("uni", u), ("prop", pr)):
        for p in PARTIES:
            row[f"{k}_{p}"] = round(d[p], 1)
        row[f"{k}_winner"], row[f"{k}_second"] = d["_w"], d["_s"]
        row[f"{k}_margin"], row[f"{k}_tier"] = round(d["_m"], 1), d["_t"]
    row["variants_agree"] = u["_w"] == pr["_w"]
    row["incumbents_notes"] = "; ".join(cands[e])
    out_rows.append(row)

fields = list(out_rows[0].keys())
write_csv(os.path.join(OUT, "districts_projection.csv"), out_rows, fields)

summary = {
    "parties": PARTIES,
    "poll_average_province": prov_t,
    "result_2024_province": {p: round(v, 2) for p, v in prov24.items()},
    "regional_targets": {R: {p: round(target[R][p], 2) for p in PARTIES} for R in REGIONS},
    "regional_target_source": source,
    "result_2024_region": {R: {p: round(r24[R][p], 2) for p in PARTIES} for R in REGIONS},
    "island_2024_for_capital_proxy": {p: round(isl24[p], 2) for p in PARTIES},
    "island_districts": sorted(island),
    "region_weights_2024_valid_votes": W,
    "seats": {k: dict(sorted(v.items(), key=lambda kv: -kv[1])) for k, v in seats.items()},
    "tier_counts": {k: dict(Counter((results[k][e]["_w"], results[k][e]["_t"]) for e in eds).most_common()) for k in results},
    "tossups": {k: [{"ed_code": e, "district": name[e], "leader": results[k][e]["_w"],
                     "second": results[k][e]["_s"], "margin": round(results[k][e]["_m"], 1)} for e in v]
                for k, v in tossups.items()},
    "check_projected_province_share": check,
}
summary["tier_counts"] = {k: {f"{a}-{b}": n for (a, b), n in v.items()} for k, v in summary["tier_counts"].items()}
json.dump(summary, open(os.path.join(OUT, "projection_summary.json"), "w"), indent=1)
print(json.dumps({k: summary[k] for k in ("regional_targets", "seats", "tossups", "check_projected_province_share")}, indent=1))
print("disagree:", [(r["ed_code"], r["uni_winner"], r["prop_winner"]) for r in out_rows if not r["variants_agree"]])
