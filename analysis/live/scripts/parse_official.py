"""Rebuild clean results from Elections BC's own results CSVs in the newest snapshot.

Reads raw/snapshots/<latest>/GE-2026-10-24_Candidate.csv and _Party.csv (official files),
writes latest.csv (one row per district and candidate), latest_districts.csv and latest_summary.csv.
"""
import csv, glob, io, json, os, re

BASE = 'analysis/live'
CODE = {'conservative party': 'CON', 'bc ndp': 'NDP', 'bc green party': 'GRN', 'centrebc': 'CENTRE', 'onebc': 'ONEBC'}


def of(s):
    m = re.match(r'\s*(\d+)\s+of\s+(\d+)', s or '')
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def read(path):
    with open(path, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


snaps = sorted(d for d in glob.glob(BASE + '/raw/snapshots/*') if glob.glob(d + '/GE-*_Candidate.csv'))
if not snaps:
    raise SystemExit('no official candidate CSV yet')
snap = snaps[-1]
rows = read(glob.glob(snap + '/GE-*_Candidate.csv')[0])

cands, rejected, dist = [], {}, {}
for r in rows:
    code, name, cand = r['Electoral District Code'], r['Electoral District Name'], r["Candidate's Ballot Name"]
    votes = int(str(r['Total Valid Votes']).replace(',', '') or 0)
    boxes, boxes_t = of(r['In-district Ballot Box count'])
    adv, adv_t = of(r['AdvanceTotals'])
    fin, fin_t = of(r['FinalTotals'])
    d = dist.setdefault(code, dict(district_code=code, district_name=name, boxes_reported=boxes, boxes_total=boxes_t,
                                   adv_reported=adv, adv_total=adv_t, final_reported=fin, final_total=fin_t,
                                   status=r['Initial Count Status'], source_time=f"{r['Date']} {r['Time']}"))
    if cand.strip().lower() == 'rejected ballots':
        rejected[code] = votes
        continue
    aff = (r['Affiliation'] or '').strip()
    cands.append(dict(district_code=code, district_name=name, candidate=cand, party=aff or 'Unaffiliated',
                      party_code=CODE.get(aff.lower(), 'OTH'), votes=votes))

valid = {}
for c in cands:
    valid[c['district_code']] = valid.get(c['district_code'], 0) + c['votes']
lead = {}
for c in cands:
    t = valid[c['district_code']]
    c['share_pct'] = round(100 * c['votes'] / t, 2) if t else 0.0
    if t and (c['district_code'] not in lead or c['votes'] > lead[c['district_code']]['votes']):
        lead[c['district_code']] = c
for c in cands:
    c['leading'] = 'Y' if lead.get(c['district_code']) is c else 'N'
    c.update({k: dist[c['district_code']][k] for k in ('boxes_reported', 'boxes_total', 'status', 'source_time')})

snap_time = os.path.basename(snap)
cols = ['district_code', 'district_name', 'candidate', 'party', 'party_code', 'votes', 'share_pct', 'leading',
        'boxes_reported', 'boxes_total', 'status', 'source_time']
with open(BASE + '/latest.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, cols + ['snapshot_utc']); w.writeheader()
    for c in cands:
        w.writerow({**{k: c[k] for k in cols}, 'snapshot_utc': snap_time})

for code, d in dist.items():
    t = valid.get(code, 0)
    ranked = sorted([c for c in cands if c['district_code'] == code], key=lambda c: -c['votes'])
    d.update(valid_votes=t, rejected=rejected.get(code, 0),
             leader=ranked[0]['party_code'] if t else '', second=ranked[1]['party_code'] if t and len(ranked) > 1 else '',
             margin_votes=(ranked[0]['votes'] - ranked[1]['votes']) if t and len(ranked) > 1 else '',
             margin_pts=round(ranked[0]['share_pct'] - ranked[1]['share_pct'], 2) if t and len(ranked) > 1 else '')
dcols = list(next(iter(dist.values())).keys())
with open(BASE + '/latest_districts.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, dcols); w.writeheader(); w.writerows(dist.values())

tot = sum(valid.values())
parties = sorted({c['party_code'] for c in cands})
summ = []
for p in parties:
    v = sum(c['votes'] for c in cands if c['party_code'] == p)
    summ.append(dict(party=p, votes=v, share_pct=round(100 * v / tot, 2) if tot else 0.0,
                     leading=sum(1 for d in dist.values() if d['leader'] == p)))
with open(BASE + '/latest_summary.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, ['party', 'votes', 'share_pct', 'leading']); w.writeheader(); w.writerows(summ)

rep = sum(1 for d in dist.values() if valid.get(d['district_code']))
boxes = sum(d['boxes_reported'] or 0 for d in dist.values()); boxes_t = sum(d['boxes_total'] or 0 for d in dist.values())
adv = sum(d['adv_reported'] or 0 for d in dist.values()); adv_t = sum(d['adv_total'] or 0 for d in dist.values())
print(f"{snap_time}: {tot:,} votes, {rep} districts with votes, advance boxes {adv}/{adv_t}, all boxes {boxes}/{boxes_t}, "
      + ', '.join(f"{s['party']} {s['share_pct']}% lead {s['leading']}" for s in summ if s['votes']))
