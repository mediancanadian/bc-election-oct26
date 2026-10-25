"""Parse Table 2 (40th GE compared to previous general elections) from the 2013 Statement of Votes.
The page is rotated; pdfplumber returns each cell's text reversed. Tokens per election appear in the order:
cost, rejected %, rejected votes, valid votes, % registered who voted, voters who voted, registered voters,
estimated eligible voters, candidates, members, districts, election date, nomination, writ, dissolution, year(+footnote).
Usage: python3 -I parse_sov2013_comparison.py <pdf> <out_csv>"""
import sys, csv, re, pdfplumber
pdf, out = sys.argv[1], sys.argv[2]
with pdfplumber.open(pdf) as p:
    toks = [t[::-1] for t in p.pages[14].extract_text().split('\n')]
rows = []
i = toks.index('$0.70') if '$0.70' in toks else None
# find start: first token that looks like cost
start = next(k for k, t in enumerate(toks) if re.fullmatch(r'\$?[0-9]+\.[0-9]+\$?|–9|9–', t))
k = start
while k + 15 < len(toks):
    grp = toks[k:k+16]
    yr = grp[15]
    m = re.match(r'(19|20)\d\d', yr)
    if not m:
        break
    rows.append(dict(year=yr[:4], year_footnote=yr[4:], cost_per_registered_voter=grp[0], rejected_pct=grp[1],
                     rejected_votes=grp[2], valid_votes=grp[3], pct_registered_who_voted=grp[4], voters_who_voted=grp[5],
                     registered_voters=grp[6], estimated_eligible_voters=grp[7], candidates=grp[8], members=grp[9],
                     districts=grp[10], election_date=grp[11], nomination=grp[12], writ=grp[13], dissolution=grp[14]))
    k += 16
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
