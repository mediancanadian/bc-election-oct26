"""Poll average: last poll per pollster with field end on/after Sept 22 2026 (campaign),
simple (unweighted) average. Province-wide for all parties; regional where pollsters
publish a region matching ours.

Region matching (strict, labels must match exactly after lower-casing):
  Metro Vancouver  <- "Metro Vancouver", "Metro Van", "Vancouver metro area"
  Capital Region   <- "Vancouver Island", "Van Island" (no pollster publishes the Capital
                      Region alone; Vancouver Island is the closest published unit and is
                      used as a proxy)
  Rest of BC       <- not taken from polls; solved as the residual in 03_project.py so that
                      the province-wide total equals the province-wide poll average.
Labels such as "Lower Mainland", "Island/North Coast", "Island/Sunshine Coast" are not used
because their boundaries differ from ours.
A regional party figure is used only if at least 2 pollsters publish it.
"""
import os, re, sys, json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, OUT, read_csv, num, write_csv

CAMPAIGN_START = "2026-09-22"
COLS = {"NDP": "NDP", "CON": "Conservative", "GRN": "Green", "CENTRE": "CentreBC", "ONEBC": "OneBC"}
REGION_LABELS = {
    "metro vancouver": "Metro Vancouver", "metro van": "Metro Vancouver",
    "vancouver metro area": "Metro Vancouver",
    "vancouver island": "Capital Region", "van island": "Capital Region",
}
TOK = {"ndp": "NDP", "cpc": "CON", "con": "CON", "grn": "GRN", "green": "GRN",
       "onebc": "ONEBC", "centrebc": "CENTRE"}

rows = [r for r in read_csv(os.path.join(ROOT, "polls/polls.csv"))
        if r["field_end"] >= CAMPAIGN_START and num(r["NDP"]) is not None]


def firm(name):
    return re.sub(r"\s*\(.*\)", "", name).replace(" Institute", "").replace(" Group", "").strip()


last = {}
for r in sorted(rows, key=lambda r: (r["field_end"], r["release_date"])):
    last[firm(r["pollster"])] = r
used = sorted(last.values(), key=lambda r: r["field_end"])


def parse_regions(text):
    out = {}
    for part in (text or "").split(";"):
        if ":" not in part:
            continue
        label, vals = part.split(":", 1)
        reg = REGION_LABELS.get(label.strip().lower())
        if not reg:
            continue
        d = {}
        for t, v in re.findall(r"([A-Za-z]+)\s+(\d+(?:\.\d+)?)", vals):
            if t.lower() in TOK:
                d[TOK[t.lower()]] = float(v)
        out[reg] = d
    return out


prov = defaultdict(list)
reg = defaultdict(lambda: defaultdict(list))
table = []
for r in used:
    row = {"pollster": firm(r["pollster"]), "field_start": r["field_start"], "field_end": r["field_end"],
           "population": r["population"]}
    for p, c in COLS.items():
        v = num(r[c])
        row[p] = v if v is not None else ""
        if v is not None:
            prov[p].append(v)
    rs = parse_regions(r["regional_splits"])
    for rg, d in rs.items():
        for p, v in d.items():
            reg[rg][p].append((row["pollster"], v))
            row[f"{rg}:{p}"] = v
    table.append(row)

avg = {p: round(sum(v) / len(v), 2) for p, v in prov.items()}
avg["OTH"] = round(100 - sum(avg.values()), 2)
n = {p: len(v) for p, v in prov.items()}

regional = {}
for rg, d in reg.items():
    regional[rg] = {p: {"avg": round(sum(x for _, x in v) / len(v), 2), "n": len(v),
                        "pollsters": [k for k, _ in v]} for p, v in d.items() if len(v) >= 2}

res = {"rule": "last poll per pollster, field end >= 2026-09-22, simple average",
       "province": avg, "n_pollsters": n, "regional": regional,
       "polls_used": [{k: t[k] for k in ("pollster", "field_start", "field_end")} for t in table]}
with open(os.path.join(OUT, "poll_average.json"), "w") as f:
    json.dump(res, f, indent=1)
fields = ["pollster", "field_start", "field_end", "population", *COLS] + sorted(
    {k for t in table for k in t if ":" in k})
write_csv(os.path.join(OUT, "polls_used.csv"), table, fields)
print(json.dumps({"province": avg, "n": n,
                  "regional": {r: {p: (v["avg"], v["n"]) for p, v in d.items()} for r, d in regional.items()}}, indent=1))
for t in table:
    print(t["pollster"], t["field_end"])
