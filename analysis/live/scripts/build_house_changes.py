"""house_changes_2024_2026.csv: compare each MLA's 2024 election party (LIMS allMemberElections, year 2024) with their
record at dissolution (LIMS allMemberParliaments, parliament 43, active flag). Both are Legislative Assembly of BC records
(api.lims.leg.bc.ca, the GraphQL API behind leg.bc.ca member pages). Event dates are NOT in LIMS: the date/detail columns come
from Wikipedia's '43rd Parliament of British Columbia' page and are marked secondary/unverified.
Usage: build_house_changes.py <mp43.json> <resign_elect.json> <out.csv> <standings_out.csv>"""
import json, sys, csv, collections
mp = json.load(open(sys.argv[1]))['data']['allMemberParliaments']['nodes']
el = json.load(open(sys.argv[2]))['data']['allMemberElections']['nodes']
nm = lambda m: f"{m['firstName']} {m['lastName']}"
elected = {(nm(e['memberByMemberId']), e['constituencyByConstituencyId']['name']): e['partyByPartyId']['name'] for e in el}
SECONDARY = {  # name: (date(s), detail) from Wikipedia, unverified against an official dated record
 'Dallas Brodie': ('2025-03-07; 2025-06-09; 2025-12-13; 2025-12-21', 'Removed from Conservative caucus; co-founded OneBC; removed as OneBC interim leader then rejoined OneBC caucus'),
 'Jordan Kealy': ('2025-03-07', 'Left Conservative caucus'),
 'Tara Armstrong': ('2025-03-07; 2025-06-09; 2025-12-16', 'Left Conservative caucus; co-founded OneBC; left OneBC caucus'),
 'Elenore Sturko': ('2025-09-22; 2026-09-18', 'Removed from Conservative caucus; joined CentreBC (sat as Independent)'),
 'Amelia Boultbee': ('2025-10-20; 2026-07-03', 'Left Conservative caucus; crossed floor to NDP'),
 'Hon Chan': ('2026-03-26', 'Removed from Conservative caucus'),
 'Peter Milobar': ('2026-08-14; 2026-09-18', 'Left Conservative caucus; CentreBC leader (sat as Independent)'),
 'Reann Gasper': ('2026-08-22', 'Resigned seat; by-election called for 2026-09-26 superseded by dissolution'),
 'Ian Paton': ('2026-08-24; 2026-09-18', 'Left Conservative caucus; joined CentreBC; rejoined Conservatives after election call'),
 'Rosalyn Bird': ('2026-08-25; 2026-09-18', 'Left Conservative caucus; joined CentreBC'),
 'Teresa Wat': ('2026-08-26; 2026-09-18', 'Left Conservative caucus; joined CentreBC'),
 'Brennan Day': ('2026-08-26', 'Left Conservative caucus; rejoined Conservatives after election call'),
 'Bruce Banman': ('2026-08-27; 2026-09-18', 'Left Conservative caucus; joined CentreBC; running 2026 as Conservative'),
 'Amshen - Joan Phillip': ('2026-08-28', 'Died in office; seat vacant at dissolution'),
 "Á'a:líya Warbus": ('2026-08-31; 2026-09-18', 'Left Conservative caucus; joined CentreBC; running 2026 as Conservative'),
 'Donegal Wilson': ('2026-09-02; 2026-09-18', 'Left Conservative caucus; joined CentreBC; running 2026 as Conservative'),
 'Brent Chapman': ('2026-09-22', 'Wikipedia: left Conservatives for OneBC on dissolution day; LIMS still lists Conservative'),
}
TEMP = ['Scott McInnis', 'Claire Rattée', 'Trevor Halford', 'John Rustad', 'Linda Hepner']  # left/removed and rejoined before dissolution (secondary)
rows = []
for m in mp:
    who = nm(m['memberByMemberId']); dist = m['constituencyByConstituencyId']['name']
    if who == 'Vacant Seat':
        continue
    p24 = elected.get((who, dist), '')
    pd = m['partyByPartyId']['name'] if m['active'] else ('VACATED' if who in ('Reann Gasper', 'Amshen - Joan Phillip') else m['partyByPartyId']['name'])
    if not p24 and who not in SECONDARY:
        continue  # LIMS lacks a 2024 election record (Jodie Wickens, Coquitlam-Burke Mountain, NDP); not a change
    if p24 != pd or who in SECONDARY:
        d, det = SECONDARY.get(who, ('', ''))
        rows.append([dist, who, p24, pd, 'Y' if m['active'] else 'N', d, det])
for who in TEMP:
    m = next(x for x in mp if nm(x['memberByMemberId']) == who)
    rows.append([m['constituencyByConstituencyId']['name'], who, elected.get((who, m['constituencyByConstituencyId']['name'])), m['partyByPartyId']['name'], 'Y',
                 '2026-09 (see detail)', 'Temporarily left/removed from Conservative caucus, rejoined 2026-09-21 (secondary); no net change'])
rows.sort(key=lambda r: r[0])
with open(sys.argv[3], 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['district', 'mla', 'party_elected_2024_LIMS', 'party_at_dissolution_LIMS', 'seated_at_dissolution_LIMS', 'event_dates_SECONDARY_unverified', 'detail_SECONDARY_unverified'])
    w.writerows(rows)
c = collections.Counter(m['partyByPartyId']['name'] for m in mp if m['active'])
vac = sum(1 for m in mp if nm(m['memberByMemberId']) == 'Vacant Seat')
with open(sys.argv[4], 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['party', 'seats_2024_election_LIMS', 'seats_at_dissolution_LIMS_2026-09-22'])
    e24 = collections.Counter(elected.values()); e24['British Columbia New Democratic Party'] += 1  # Wickens missing in LIMS; 2024 SOV: NDP 47
    for p in sorted(set(c) | set(e24), key=lambda p: -c.get(p, 0)):
        w.writerow([p, e24.get(p, 0), c.get(p, 0)])
    w.writerow(['Vacant', 0, vac]); w.writerow(['Total', sum(e24.values()), sum(c.values()) + vac])
print(len(rows), 'rows;', dict(c), 'vacant', vac)
