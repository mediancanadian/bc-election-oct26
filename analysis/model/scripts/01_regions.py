"""Assign each 2023-boundary district to a region using 2021 census populations.

Source: geo/out/da_to_ed2023_detail.csv (DA -> district with population share).
Census division = first 4 digits of DAUID: 5915 Greater Vancouver (Metro Vancouver),
5917 Capital (Capital Region). A district goes to the region holding the majority
of its 2021 population; everything else is 'Rest of BC'.
"""
import glob, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, OUT, read_csv, pick, num, write_csv

REG = {"5915": "Metro Vancouver", "5917": "Capital Region"}

# Note: geo/out/ed2023_regions.csv holds regional districts (by area), not these three regions,
# so it is not used. Population-majority rule here differs from it for Maple Ridge East (MAE),
# which is 89% Metro Vancouver by population but 60% Fraser Valley by area.

rows = read_csv(os.path.join(ROOT, "geo/out/da_to_ed2023_detail.csv"))
pop = defaultdict(lambda: defaultdict(float))
for r in rows:
    p = (num(r["da_pop_2021"]) or 0) * (num(r["pop_share"]) or 0)
    pop[r["ed_code"]][REG.get(r["DAUID"][:4], "Rest of BC")] += p

out = []
for ed, d in sorted(pop.items()):
    tot = sum(d.values()) or 1
    reg, p = max(d.items(), key=lambda kv: kv[1])
    out.append({"ed_code": ed, "region": reg, "share_in_region": round(p / tot, 3),
                "source": "geo/out/da_to_ed2023_detail.csv (DAUID census division)"})
write_csv(os.path.join(OUT, "regions.csv"), out, ["ed_code", "region", "share_in_region", "source"])
from collections import Counter
print(len(out), Counter(o["region"] for o in out))
print("split districts:", [(o["ed_code"], o["region"], o["share_in_region"]) for o in out if o["share_in_region"] < 0.95])
