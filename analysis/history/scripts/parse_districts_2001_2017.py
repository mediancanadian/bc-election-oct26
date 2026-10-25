"""Build districts_2001_2017.csv from Elections BC Statement of Votes spreadsheets (voting-area results by district).
Usage: python3 -I parse_districts_2001_2017.py <raw_dir> <out_csv>
Reads the 'Grand Totals' row of each district sheet (all voting opportunities), plus rejected ballots,
registered voters who voted, registered voters, and the 'Candidate elected' line."""
import sys, re, csv
import pandas as pd

raw, out = sys.argv[1], sys.argv[2]
FILES = {
    2001: (f'{raw}/ge2001_xls/2001ResultsxED.xls', 'GE 2001-05-16'),
    2005: (f'{raw}/ge2005_xls/2005GE_Results_Excel.xls', 'GE 2005-05-17'),
    2009: (f'{raw}/ge2009_xls/2009GE-Results-Excel.xls', 'GE 2009-05-12'),
    2013: (f'{raw}/ge2013_xls/2013GE-Results-Excel.xls', 'GE 2013-05-14'),
    2017: (f'{raw}/ge2017_xlsx/2017-provincial-general-election-sov.xlsx', 'GE 2017-05-09'),
}
DATES = {2001: '2001-05-16', 2005: '2005-05-17', 2009: '2009-05-12', 2013: '2013-05-14', 2017: '2017-05-09'}

def num(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return None
    if isinstance(v, (int, float)): return v
    s = str(v).replace(',', '').strip()
    try: return float(s)
    except ValueError: return None

def clean(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return ''
    return re.sub(r'\s+', ' ', str(v)).strip()

def code_names(year, xf):
    names = {}
    if year == 2005:
        d = pd.read_excel(xf, 'ED Codes', header=None)
        for _, r in d.iterrows():
            if clean(r[1]) and clean(r[1]) != 'Code': names[clean(r[1])] = clean(r[0])
    elif year == 2009:
        d = pd.read_excel(xf, 'ED Codes', header=None)
        for _, r in d.iterrows():
            if clean(r[0]): names[clean(r[0])] = clean(r[1])
    elif year in (2013, 2017):
        d = pd.read_excel(xf, 'ED List' if year == 2013 else 'ED_List', header=None)
        for _, r in d.iterrows():
            for nc, cc in ((1, 2), (4, 5)):
                n, c = clean(r[nc]), clean(r[cc])
                if n and re.fullmatch(r'[A-Z]{3}', c): names[c] = n
    if year == 2001:
        # 2001 workbook has codes only. 2001 and 2005 used the same 79 districts (1999 redistribution); take names from the
        # 2005 'ED Codes' sheet. Only code difference: 2001 PKV = 2005 PEN (Penticton-Okanagan Valley), verified from the
        # Electoral History 1987-2001 results (Barisoff/Gidda/Goldstone/Naegel/Terada under Penticton-Okanagan Valley).
        d = pd.read_excel(FILES[2005][0], 'ED Codes', header=None)
        for _, r in d.iterrows():
            if clean(r[1]) and clean(r[1]) != 'Code': names[clean(r[1])] = clean(r[0])
        names['PKV'] = names.pop('PEN')
    return names

rows = []
for year, (path, _) in FILES.items():
    xf = pd.ExcelFile(path)
    names = code_names(year, xf)
    sheets = [s for s in xf.sheet_names if s not in ('ED Codes', 'ED List', 'ED_List')]
    for s in sheets:
        code = s.replace('_2001', '').replace(f'{year}-', '')
        d = pd.read_excel(xf, s, header=None)
        lab = d[0].map(clean)
        # locate party row: the row whose cells are short uppercase party codes
        tot_col = None
        for r in range(0, 8):
            for c in range(d.shape[1]):
                if re.match(r'(?i)^total( valid)?', clean(d.iat[r, c])) and tot_col is None:
                    tot_col = c
        # candidate columns lie between first data column and tot_col
        party_row = None
        first_data = next(r for r in range(d.shape[0]) if re.match(r'(?i)(advance voting|general voting)', clean(d.iat[r, 0])))
        for r in range(first_data - 1, -1, -1):
            vals = [clean(d.iat[r, c]) for c in range(1, tot_col)]
            if sum(bool(re.fullmatch(r'[A-Z]{2,5}', v)) for v in vals) >= max(1, len([v for v in vals if v]) - 1) and any(vals):
                party_row = r; break
        if party_row is None:
            raise SystemExit(f'{year} {s}: no party row; first_data={first_data}\n' + d.head(first_data + 1).to_string())
        cand_cols = [c for c in range(1, tot_col) if any(clean(d.iat[r, c]) for r in range(0, party_row + 1))
                     and not clean(d.iat[0, c]).startswith('*')]
        name_rows = [r for r in range(0, party_row) if any(clean(d.iat[r, c]) for c in cand_cols)]
        gt = [i for i, v in enumerate(lab) if v.lower().startswith('grand total')]
        if len(gt) != 1:
            raise SystemExit(f'{year} {s}: grand totals rows {gt}')
        gt = gt[0]
        # 2001 sheets have candidate data shifted: check where numbers sit in grand totals
        def find(label):
            for i, v in enumerate(lab):
                if v.lower().rstrip(':') == label.lower():
                    for c in range(1, d.shape[1]):
                        x = num(d.iat[i, c])
                        if x is not None: return x
            return None
        total_valid = find('Total valid votes')
        rejected = find('Rejected ballots')
        voted = find('Registered voters who voted')
        registered = find('Registered voters')
        elected = ''
        for i, v in enumerate(lab):
            if v.lower().startswith('candidate elected'):
                elected = next(clean(d.iat[i, c]) for c in range(1, d.shape[1]) if clean(d.iat[i, c]))
        # grand total values per candidate: some 2001 sheets place values one column left of names
        vals = {c: num(d.iat[gt, c]) for c in range(1, d.shape[1])}
        gt_reg = None
        cands = []
        for c in cand_cols:
            nm = ' '.join(clean(d.iat[r, c]) for r in name_rows if clean(d.iat[r, c]))
            pty = clean(d.iat[party_row, c])
            cands.append([c, nm, pty])
        # determine alignment: sum of candidate votes should equal total valid in grand totals
        gt_total = vals.get(tot_col)
        def cand_sum(shift):
            try: return sum(vals.get(c + shift) or 0 for c, _, _ in cands)
            except TypeError: return None
        shift = 0
        if gt_total is None or abs(cand_sum(0) - gt_total) > 0.5:
            for sh in (-1, 1):
                if vals.get(tot_col + sh) is not None and abs(cand_sum(sh) - vals[tot_col + sh]) < 0.5:
                    shift = sh; gt_total = vals[tot_col + sh]; break
            else:
                raise SystemExit(f'{year} {s}: candidate sum {cand_sum(0)} != total {gt_total}')
        if registered is None:  # 2001: registered voters sit in grand totals, last numeric column
            registered = [v for v in vals.values() if v is not None][-1]
        if total_valid is None: total_valid = gt_total
        if abs(total_valid - gt_total) > 0.5:
            raise SystemExit(f'{year} {s}: summary total {total_valid} != grand total {gt_total}')
        votes = [(nm, pty, vals.get(c + shift) or 0) for c, nm, pty in cands]
        ranked = sorted(votes, key=lambda x: -x[2])
        win, second = ranked[0], (ranked[1] if len(ranked) > 1 else ('', '', 0))
        el_name = re.sub(r'\s*\(.*\)$', '', elected)
        el_party = re.search(r'\(([^)]*)\)', elected).group(1) if '(' in elected else ''
        for nm, pty, v in votes:
            rows.append(dict(
                year=year, election_date=DATES[year], district_count=len(sheets), ed_code=code,
                electoral_district=names.get(code, ''), candidate=nm, party=pty or 'NA/IND(blank)', votes=int(v),
                vote_share_pct=round(100 * v / total_valid, 2), rank=[x[0] for x in ranked].index(nm) + 1,
                is_winner=int(nm == win[0]), district_winner=win[0], district_winner_party=win[1],
                winning_margin_votes=int(win[2] - second[2]), winning_margin_pct_pts=round(100 * (win[2] - second[2]) / total_valid, 2),
                total_valid_votes=int(total_valid), rejected_ballots=int(rejected) if rejected is not None else '',
                registered_voters_who_voted=int(voted) if voted is not None else '',
                registered_voters=int(registered), turnout_pct_registered=round(100 * voted / registered, 2) if voted else '',
                official_elected_line=elected, winner_matches_official=int(el_name.split()[-1].lower() in win[0].lower()),
            ))
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), 'rows')
