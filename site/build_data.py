#!/usr/bin/env python3
"""Build data/site.json for the explorer from the analysis files in data/ (and the poll table)."""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, '..', 'data')
AN = os.path.join(HERE, '..', 'analysis') + '/'   # research threads; the core analysis is in analysis/core/
x = pd.read_csv(os.path.join(D, 'ridings.csv'), index_col=0)
live = pd.read_csv(os.path.join(D, 'candidates_2026_as_of_2026-10-25_0149_PT.csv'))
r24 = pd.read_csv(AN + 'results24/out/districts_2024.csv')
polls = pd.read_csv(AN + 'polls/polls.csv')
hist = pd.read_csv(AN + 'history/province_series.csv')
meta = json.load(open(os.path.join(D, 'meta.json')))

CENSUS = [  # key, label, unit, group
    ('hh_income_median', 'Median household income', '$', 'Income'), ('pct_low_income_lim_at', 'Low income', '%', 'Income'),
    ('pct_hh_inc_200k_plus', 'Households earning $200k+', '%', 'Income'),
    ('median_age', 'Median age', 'yrs', 'Age'), ('pct_age_65_plus', 'Age 65 and over', '%', 'Age'), ('pct_age_20_34', 'Age 20 to 34', '%', 'Age'),
    ('pct_women_plus', 'Women', '%', 'Gender'),
    ('pct_bachelor_plus_25_64', 'University degree (age 25 to 64)', '%', 'Education'),
    ('pct_vm_total', 'Visible minority', '%', 'Ethnicity'), ('pct_vm_south_asian', 'South Asian', '%', 'Ethnicity'), ('pct_vm_chinese', 'Chinese', '%', 'Ethnicity'),
    ('pct_vm_filipino', 'Filipino', '%', 'Ethnicity'), ('pct_vm_black', 'Black', '%', 'Ethnicity'), ('pct_indigenous', 'Indigenous', '%', 'Ethnicity'),
    ('pct_immigrants', 'Immigrants', '%', 'Immigration'), ('pct_recent_immigrants_2016_2021', 'Recent immigrants (2016 to 2021)', '%', 'Immigration'),
    ('pct_lang_home_english', 'English spoken at home', '%', 'Language'), ('pct_lang_home_punjabi_panjabi', 'Punjabi spoken at home', '%', 'Language'),
    ('pct_lang_home_mandarin', 'Mandarin spoken at home', '%', 'Language'), ('pct_lang_home_yue_cantonese', 'Cantonese spoken at home', '%', 'Language'),
    ('pct_lang_home_tagalog_pilipino_filipino', 'Tagalog spoken at home', '%', 'Language'),
    ('pct_rel_christian', 'Christian', '%', 'Religion'), ('pct_rel_sikh', 'Sikh', '%', 'Religion'), ('pct_rel_none_secular', 'No religion', '%', 'Religion'),
    ('pct_hh_owner', 'Households that own their home', '%', 'Housing'), ('pct_hh_renter', 'Renters', '%', 'Housing'), ('median_dwelling_value', 'Median home value', '$', 'Housing'),
    ('pct_hh_shelter_30plus', 'Spending 30%+ of income on housing', '%', 'Housing'),
    ('unemployment_rate', 'Unemployment rate', '%', 'Work'), ('pct_commute_car', 'Commuters who go to work by car', '%', 'Work'), ('pct_commute_transit', 'Transit to work', '%', 'Work'),
    ('density_per_km2', 'People per km²', '', 'Place'),
]
CENSUS = [c for c in CENSUS if c[0] in x.columns]

def f(v, d=2):
    return None if pd.isna(v) else round(float(v), d)


def hu(v):
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(repr(float(v))).quantize(Decimal('0.1'), ROUND_HALF_UP))

# place type (Canadian Suburbs commuting method adapted to ridings; same rule and averages as analysis/meta/meta.py)
pt = pd.read_csv(AN + 'core/meta/place_types.csv', index_col=0).ptype
cm = ['commute_car', 'commute_transit', 'commute_walk_bike', 'commute_other']
base = x.drop(index=[c for c in ('PCN',) if c in x.index])
avg_ab = base.commute_walk_bike.sum() / base[cm].sum().sum(); avg_tr = base.commute_transit.sum() / base[cm].sum().sum()
def ptype(code):
    if code in pt.index: return pt[code][2:]
    r = x.loc[code]; tot = r[cm].sum()
    if r.density_per_km2 < 150: return 'Exurban and rural'   # density first for whole ridings
    if r.commute_walk_bike / tot >= 1.5 * avg_ab: return 'Active core'
    return 'Transit suburb' if r.commute_transit / tot > avg_tr else 'Car suburb'
# 2020 result moved onto the 2023 ridings (Elections BC 2020 voting areas, transposed in results24)
t20 = pd.read_csv(AN + 'results24/out/transposed_2020_on_2023_eds.csv').set_index('ed_code')
# federal 2025 plurality on the provincial riding
fedwin = x[['lpc25', 'cpc25', 'ndp25', 'gpc25']].idxmax(axis=1).str[:3].str.upper()

# the results file files every smaller party and independent under OTH; keep the label the ballot showed
PARTY_CODE = {'Independent': 'IND', 'Unaffiliated': 'UNAF', 'Libertarian': 'LBN', 'Christian Heritage Party of BC': 'CHP',
              'Communist Party of BC': 'COMM', 'Freedom Party of BC': 'FPBC'}
def pcode(code, party):
    return PARTY_CODE.get(party, code) if code == 'OTH' else code
rid = {}
for code, r in x.iterrows():
    c26 = live[live.district_code == code].sort_values('votes', ascending=False)
    c24 = r24[r24.ed_code == code].sort_values('votes', ascending=False)
    rid[code] = dict(
        name=r['name'], region=r.region, lead=r.lead26, win24=r.win24, flip=bool(r.lead26 != r.win24),
        margin=int(r.margin26_votes), margin_pts=f(r.margin26_pts), boxes=[int(c26.boxes_reported.iloc[0]), int(c26.boxes_total.iloc[0])],
        c26=[[n, pcode(p, pa), int(v), hu(100 * v / c26.votes.sum())] for n, p, pa, v in zip(c26.candidate, c26.party_code, c26.party, c26.votes)],   # shares from votes, rounded once, half up
        c24=[[n, p, int(v), f(s, 1)] for n, p, v, s in zip(c24.candidate, c24.party, c24.votes, c24.vote_share_pct)],
        s26={p: f(r[f'{p.lower()}26'], 4) for p in ('CON', 'NDP', 'GRN')}, s24={p: f(r[f'{p.lower()}24'], 4) for p in ('CON', 'NDP', 'GRN')},
        tp=f(r.tp_swing, 4) if code != 'PCN' else None, con_swing=f(r.con_swing, 4), ndp_swing=f(r.ndp_swing, 4),
        fed={'LPC': f(r.lpc25, 2), 'CPC': f(r.cpc25, 2), 'NDP': f(r.ndp25, 2), 'GPC': f(r.gpc25, 2)},   # as published in the allocation file
        same_field=bool(r.same_field), pop=int(r.pop_2021) if not pd.isna(r.pop_2021) else None,
        census={k: f(r[k], 4) for k, *_ in CENSUS},
        ptype=ptype(code), fedwin=fedwin[code], nw20=t20.notional_winner_2020.get(code),
        s20={k: f(t20[f'{k}_pct'].get(code), 1) for k in ('LIB', 'CON', 'NDP', 'GRN')},
        tp24=f(r.tp24, 4), tp26=f(r.tp26, 4), grn_change=f(r.grn_change, 4))

# income group of each riding: the same rule as analysis/story.py (rank by median household income, ties in file order,
# four groups of 23; Peace River North, with no NDP candidate in 2026, left out), checked against story.json
_s = x[x.index != 'PCN']
_q = pd.qcut(_s.hh_income_median.rank(method='first'), 4, labels=False)
for code, q in _q.items(): rid[code]['incq'] = int(q)
_story = json.load(open(os.path.join(D, 'story.json')))
for k, g in enumerate(_story['income_groups']):
    assert round(float(_s.tp_swing[_q == k].mean()), 1) == g['swing'] and int((_q == k).sum()) == g['n'], ('income group mismatch', k)

# history: every party family's share and seats
fam = {'CON': 'Conservative', 'SC': 'Social Credit', 'COAL': 'Coalition', 'LIB': 'Liberal', 'BCLIB': 'BC Liberal', 'LEFT': 'CCF / NDP', 'GRN': 'Green', 'REF': 'Reform', 'OTH': 'Other'}
import re
MONTHS = {m[:3]: m for m in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']}
def full_dates(t):   # "18 Jul 2017" -> "July 18, 2017"
    return t if not isinstance(t, str) else re.sub(r'\b(\d{1,2}) ([A-Z][a-z]{2}) (\d{4})\b', lambda m: f'{MONTHS[m.group(2)]} {int(m.group(1))}, {m.group(3)}', t)
H = []
for r in hist.itertuples():
    H.append(dict(year=int(r.year), seats=int(r.seats_in_house), turnout=f(r.turnout_pct_registered, 1), premier=full_dates(r.premier),
                  gov=full_dates(r.governing_party_after_vote), share={k: f(getattr(r, f'share_{k}'), 2) for k in fam if not pd.isna(getattr(r, f'share_{k}'))},
                  won={k: int(getattr(r, f'seats_{k}')) for k in fam if not pd.isna(getattr(r, f'seats_{k}')) and getattr(r, f'seats_{k}') > 0}))
H[0]['share']['CON'] = 53.30   # Conservative Party alone (Electoral History of BC 1871-1986, p.159)
d01 = pd.read_csv(AN + 'history/districts_2001_2017.csv'); d01 = d01[d01.year == 2001]
con01 = round(float(100 * d01[d01.party == 'CP'].votes.sum() / d01.drop_duplicates('ed_code').total_valid_votes.sum()), 2)
h01 = next(h for h in H if h['year'] == 2001); h01['share']['CON'] = con01; h01['share']['OTH'] = round(h01['share']['OTH'] - con01, 2)
prov = pd.read_csv(os.path.join(D, 'province.csv'), index_col=0)
H.append(dict(year=2026, seats=93, turnout=None, premier=None, gov=None, initial=True,
              share={'CON': f(prov.loc['CON', 'share26']), 'LEFT': f(prov.loc['NDP', 'share26']), 'GRN': f(prov.loc['GRN', 'share26']),
                     'OTH': f(prov.loc[['CENTRE', 'ONEBC', 'OTH'], 'share26'].sum())},
              won={'CON': int((x.lead26 == 'CON').sum()), 'LEFT': int((x.lead26 == 'NDP').sum()), 'GRN': int((x.lead26 == 'GRN').sum())}))

P = []
for r in polls.itertuples():
    if pd.isna(r.Conservative): continue
    P.append(dict(pollster=r.pollster, end=r.field_end, n=None if pd.isna(r.sample_size) else str(r.sample_size), mode=r.mode,
                  NDP=f(r.NDP, 1), CON=f(r.Conservative, 1), GRN=f(r.Green, 1), opened=str(r.release_status).startswith('opened'),
                  url=r.source_url if isinstance(r.source_url, str) and r.source_url.startswith('http') else None))
used = pd.read_csv(os.path.join(D, 'polls_used.csv'))
# match each final poll to its own release row (names differ slightly between the two tables)
def match(row):
    m = polls[(polls.field_end == row.field_end) & polls.pollster.str.startswith(row.pollster.split()[0])]
    return (m.iloc[0].pollster, m.iloc[0].source_url) if len(m) else (row.pollster, None)
used['full_name'], used['url'] = zip(*[match(r) for r in used.itertuples()])
# 2024 ballots counted at the final count (vote-by-mail, assisted telephone, absentee on final voting day): how they leaned
late_cols = ['votes_mail', 'votes_atv', 'votes_final_ood']
all_cols = ['votes_adv', 'votes_adv_ood', 'votes_final', 'votes_final_ood', 'votes_special', 'votes_deo', 'votes_mail', 'votes_atv']
g24 = r24[r24.party.isin(['CON', 'NDP'])].groupby('party')[all_cols].sum()
L = g24[late_cols].sum(axis=1); A = g24[all_cols].sum(axis=1) - L
late2024 = dict(con_two_party_late=round(float(100 * L['CON'] / L.sum()), 1), con_two_party_rest=round(float(100 * A['CON'] / A.sum()), 1),
                late_share=round(float(100 * L.sum() / g24[all_cols].sum().sum()), 1))

# places for "Find your riding": every municipality and designated place in B.C. (2021 Census geographic attribute file),
# with the ridings its people live in, from 2021 dissemination-block populations allocated to the 2023 ridings
GAF = AN + 'geo/raw/statcan/2021_92-151_x_bc.csv'   # a raw download (see REPRODUCE.md); without it the published place index is reused
CSDT = {'CY': 'city', 'DM': 'district', 'T': 'town', 'VL': 'village', 'RGM': 'regional municipality', 'IM': 'island municipality',
        'NL': "Nisga'a lands", 'IGD': 'government district', 'TWL': 'Tsawwassen lands', 'TAL': "Tla'amin lands"}
places = []
if os.path.exists(GAF):
    gaf = pd.read_csv(GAF, encoding='latin-1', dtype=str, usecols=['DBUID_IDIDU', 'CSDNAME_SDRNOM', 'CSDTYPE_SDRGENRE', 'DPLNAME_LDNOM'])
    dbe = pd.read_csv(AN + 'geo/out/db_to_ed2023.csv', dtype={'DBUID': str}).merge(gaf, left_on='DBUID', right_on='DBUID_IDIDU', how='left')
def add(name, kind, d):
    s = d.groupby('ED_ABBREVIATION').pop_ed.sum(); tot = s.sum()
    if tot < 50: return
    s = s[(s >= 200) | (s / tot >= 0.02)].sort_values(ascending=False)
    places.append([name, kind, [[c, round(float(100 * v / tot), 1)] for c, v in s.items()], int(round(tot))])
if os.path.exists(GAF):
    for (n, t), d in dbe[dbe.CSDTYPE_SDRGENRE.isin(list(CSDT))].groupby(['CSDNAME_SDRNOM', 'CSDTYPE_SDRGENRE']):
        add(n, CSDT[t], d)
    for n, d in dbe[dbe.DPLNAME_LDNOM.notna()].groupby('DPLNAME_LDNOM'):
        add(n, 'community', d)
    json.dump(places, open(os.path.join(D, 'places.json'), 'w', encoding='utf-8'), separators=(',', ':'), ensure_ascii=False)
else:
    places = json.load(open(os.path.join(D, 'places.json'), encoding='utf-8'))

regions = pd.read_csv(os.path.join(D, 'regions.csv'), index_col=0)
out = dict(meta=meta, census=[dict(k=k, label=l, unit=u, group=g) for k, l, u, g in CENSUS], ridings=rid, history=H, families=fam,
           polls=P, final_polls=used[['pollster', 'full_name', 'url', 'field_end', 'CON', 'NDP', 'GRN']].to_dict('records'), late2024=late2024,
           province={p: dict(share26=f(prov.loc[p, 'share26']), share24=f(prov.loc[p, 'share24']), votes=int(prov.loc[p, 'votes26']),
                             lead=int((x.lead26 == p).sum()), seats24=int((x.win24 == p).sum())) for p in prov.index},
           regions=json.loads(regions.reset_index().to_json(orient='records')), places=places)
json.dump(out, open(os.path.join(D, 'site.json'), 'w'), separators=(',', ':'), default=lambda o: None if (isinstance(o, float) and np.isnan(o)) else str(o))
print('site.json', os.path.getsize(os.path.join(D, 'site.json')) // 1024, 'KB', len(rid), 'ridings', len(P), 'polls')
