"""candidates_2026.csv from Elections BC candidate CSV + LIMS (Legislative Assembly) member records for the 43rd Parliament.
Usage: build_candidates.py <ebc_candidates.csv> <lims_mp43.json> <out.csv>"""
import csv, json, sys, unicodedata, re
def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z ]', '', s.replace('-', ' ')).split()
cands = list(csv.DictReader(open(sys.argv[1], encoding='cp1252')))
mps = json.load(open(sys.argv[2]))['data']['allMemberParliaments']['nodes']
active = [m for m in mps if m['active'] and m['memberByMemberId']['lastName'] != 'Seat']
def key(m): return (norm(m['memberByMemberId']['firstName'])[-1], norm(m['memberByMemberId']['lastName'])[-1])
mp_by_key = {key(m): m for m in active}
used = set()
out = open(sys.argv[3], 'w', newline='', encoding='utf-8'); w = csv.writer(out)
w.writerow(['ed_code', 'district', 'candidate', 'affiliation', 'incumbent', 'incumbent_same_district', 'mla_district_at_dissolution', 'mla_lims_affiliation_at_dissolution'])
for c in cands:
    n = norm(c['Candidate Ballot Name']); k = (n[0] if n else '', n[-1] if n else '')
    m = next((mp for kk, mp in mp_by_key.items() if kk[1] == k[1] and (kk[0] == k[0] or kk[0] in n)), None)
    if m: used.add(key(m))
    w.writerow([c['ED Code'], c['Electoral District'], c['Candidate Ballot Name'], c['Affiliation'],
                'Y' if m else 'N',
                ('Y' if m['constituencyByConstituencyId']['name'] == c['Electoral District'] else 'N') if m else '',
                m['constituencyByConstituencyId']['name'] if m else '', m['partyByPartyId']['name'] if m else ''])
out.close()
print('incumbents running:', len(used), 'of', len(active), 'sitting MLAs at dissolution')
print('not running:', sorted(f"{m['memberByMemberId']['firstName']} {m['memberByMemberId']['lastName']} ({m['constituencyByConstituencyId']['name']})" for k, m in mp_by_key.items() if k not in used))
