"""Parse Elections BC Statement of Votes text (pdftotext -layout) for cross-checks.

Usage: python3 -I parse_sov.py <sov_txt> <year> <out_dir>
Outputs:
  sov<year>_district_summary.csv  (district summary table: party columns, valid, rejected, voted, registered, pct)
  sov<year>_candidates.csv        (candidate summary: district, ballot name, incumbent asterisk, affiliation, votes, pct)
"""
import re, sys, csv

src, year, out = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(src, encoding="utf-8", errors="replace").read().splitlines()

num = r"(?:[\d,]+|---)"
# District summary rows: name followed by numeric columns and a percentage
cols = {"2024": ["NDP", "CP", "GP", "OTHER"], "2020": ["NDP", "LIB", "GP", "CP", "OTHER"]}[year]
pat = re.compile(r"^\s{5,}([A-Z][A-Za-z'.\- ]+?)\s{2,}((?:" + num + r"\s+){" + str(len(cols) + 4) + r"})(\d+\.\d+)%\s*$")
rows = []
for ln in lines:
    m = pat.match(ln)
    if not m:
        continue
    name = m.group(1).strip()
    vals = m.group(2).split()
    if name == "Total" or len(vals) != len(cols) + 4:
        if name == "Total":
            rows.append([name] + vals + [m.group(3)])
        continue
    rows.append([name] + vals + [m.group(3)])
with open(f"{out}/sov{year}_district_summary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ed_name"] + cols + ["total_valid", "total_rejected", "voters_who_voted", "registered", "pct_voted"])
    for r in rows:
        w.writerow([r[0]] + [v.replace(",", "").replace("---", "0") for v in r[1:-1]] + [r[-1]])
print("district rows", len(rows))

# Candidate summary section (between 'Summary of results by candidate' header pages and the district summary)
start = [i for i, l in enumerate(lines) if "Candidate ballot name" in l][0] - 2
end = [i for i, l in enumerate(lines) if "Summary of results by electoral district" in l and i > start][0]
cand = []
cur = None
cpat = re.compile(r"^(.*?)\s{2,}(\S.*?\S\*?)\s{2,}(\S.*?)\s{2,}([\d,]+)\s+(\d+\.\d+)%\s*$")
for ln in lines[start:end]:
    m = cpat.match(ln)
    if not m:
        continue
    d, nm, aff, v, p = [x.strip() for x in m.groups()]
    if d:
        cur = d
    cand.append([cur, nm.rstrip("*"), nm.endswith("*"), aff, v.replace(",", ""), p])
with open(f"{out}/sov{year}_candidates.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ed_name", "ballot_name", "member_of_previous_parliament", "affiliation_sov", "votes", "pct"])
    w.writerows(cand)
print("candidate rows", len(cand))
