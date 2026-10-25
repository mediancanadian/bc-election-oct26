"""Build advance_turnout_2026_vs_2024.csv.
2026: Elections BC advance voting turnout PDF (voters counted in district where they voted; registered voters as of Oct 14).
2024: Statement of Votes 2024 (ballots considered at advance voting: in-district sub-total valid+rejected, plus out-of-district, credited to the voter's home district)."""
import re, csv, sys, subprocess
adv26_pdf, sov_txt, out = sys.argv[1], sys.argv[2], sys.argv[3]
num = lambda s: None if s.strip() in ('-', '---', '') else int(s.replace(',', ''))
t26 = subprocess.run(['pdftotext', '-layout', adv26_pdf, '-'], capture_output=True, text=True).stdout
rows26 = {}
pat = re.compile(r'^\s*(.+?)\s{2,}([A-Z]{3})\s+((?:[\d,]+|-)\s+){6}([\d,]+)\s+([\d,]+)\s*$')
for line in t26.splitlines():
    m = pat.match(line)
    if not m: continue
    parts = line.split()
    vals = parts[-8:]
    rows26[m.group(1).strip()] = dict(code=m.group(2), days=[num(v) for v in vals[:6]], total=num(vals[6]), reg=num(vals[7]))
tot = re.search(r'PROVINCIAL TOTAL\s+(.*)', t26).group(1).split()
sov = open(sov_txt, encoding='utf-8').read()
# 2024 registered voters per district from summary table: name ... registered  pct%
reg24 = {}
names26 = set(rows26)
for line in sov.splitlines()[:900]:
    m = re.match(r'^\s+(\S.*?)\s{2,}.*\s([\d,]+)\s+(\d+\.\d\d)%\s*$', line)
    if m and m.group(1).strip() in names26: reg24[m.group(1).strip()] = num(m.group(2))
adv24 = {}
lines = sov.splitlines()
cur = None
for k, line in enumerate(lines):
    m = re.match(r'^Elections BC \| Statement of Votes \| 2024 Provincial General Election\s{2,}(\S.*?)\s*$', line)
    if m and m.group(1).strip() in names26: cur = m.group(1).strip()
    if line.startswith('Advance voting - in-district') and cur and cur not in adv24:
        j = k + 1
        while not lines[j].startswith('Sub-totals'): j += 1
        sub = lines[j].split()
        adv24[cur] = dict(in_valid=num(sub[-2]), in_rej=num(sub[-1]), ood_valid=0, ood_rej=0)
    m2 = re.match(r'^Advance voting - out-of-district\s+(.*)$', line)
    if m2 and cur in adv24 and adv24[cur]['ood_valid'] == 0:
        v = m2.group(1).split(); adv24[cur]['ood_valid'] = num(v[-2]); adv24[cur]['ood_rej'] = num(v[-1])
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['ed_code', 'district', 'adv2026_oct16', 'adv2026_oct17', 'adv2026_oct18', 'adv2026_oct19', 'adv2026_oct20', 'adv2026_oct21',
                'adv2026_total_voters', 'registered_2026_oct14', 'adv2026_pct_of_registered',
                'adv2024_ballots_in_district', 'adv2024_ballots_out_of_district', 'adv2024_ballots_total', 'registered_2024_final', 'adv2024_pct_of_registered', 'note'])
    for name, r in sorted(rows26.items()):
        a = adv24.get(name); rg = reg24.get(name)
        a_in = a['in_valid'] + a['in_rej'] if a else None
        a_ood = a['ood_valid'] + a['ood_rej'] if a else None
        a_tot = a_in + a_ood if a else None
        note = 'blank day cell(s) in 2026 PDF' if None in r['days'] else ''
        w.writerow([r['code'], name] + ['' if d is None else d for d in r['days']] + [r['total'], r['reg'], f"{100*r['total']/r['reg']:.2f}",
                   a_in, a_ood, a_tot, rg, f"{100*a_tot/rg:.2f}" if a_tot and rg else '', note])
    w.writerow(['', 'PROVINCIAL TOTAL'] + [num(x) for x in tot[:6]] + [num(tot[6]), num(tot[7]), f"{100*num(tot[6])/num(tot[7]):.2f}",
               sum(v['in_valid'] + v['in_rej'] for v in adv24.values()), sum(v['ood_valid'] + v['ood_rej'] for v in adv24.values()),
               sum(v['in_valid'] + v['in_rej'] + v['ood_valid'] + v['ood_rej'] for v in adv24.values()), sum(reg24.values()), '', ''])
print('2026 rows', len(rows26), '2024 sov blocks', len(adv24), '2024 reg', len(reg24))
print('missing 2024 match:', [n for n in rows26 if n not in adv24 or n not in reg24])
