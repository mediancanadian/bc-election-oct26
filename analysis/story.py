#!/usr/bin/env python3
"""Every number the story uses, for the slides and the website: writes data/story.json.

Reads the analysis outputs (2026 results as of October 25, 2026, 1:49 a.m. Pacific, 2024 and 2020 results, 2025 federal vote on provincial ridings,
2021 Census by riding, history 1928 to 2024, polls) and the platform research. Run after analysis/core/full.py.
"""
import json, os
import numpy as np, pandas as pd
from scipy.optimize import nnls

# research threads sit next to this file: analysis/<thread>/, with the core analysis in analysis/core/
B = os.environ.get('BC_ANALYSIS', os.path.dirname(os.path.abspath(__file__))) + '/'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'story.json')
x = pd.read_csv(B + 'core/out/ridings_2026_joined.csv', index_col=0)
live = pd.read_csv(B + 'live/latest.csv')
dist = pd.read_csv(B + 'live/latest_districts.csv')
h = pd.read_csv(B + 'history/province_series.csv')
t20 = pd.read_csv(B + 'results24/out/transposed_2020_on_2023_eds.csv').set_index('ed_code')
fed = pd.read_csv(B + 'federal25/fed2025_on_ed2023.csv', index_col=0).reindex(x.index)
place = pd.read_csv(B + 'core/meta/place_types.csv', index_col=0)
idx = pd.read_csv(B + 'core/meta/indices.csv')
polls = pd.read_csv(B + 'polls/polls.csv')
S = {}

# ---------------------------------------------------------------- meta and result
v26 = live.groupby('party_code').votes.sum()
S['meta'] = dict(snapshot_utc=live.snapshot_utc.iloc[0], boxes=int(dist.boxes_reported.sum()), boxes_total=int(dist.boxes_total.sum()),
                 source_time=dist.source_time.iloc[0], valid_votes=int(v26.sum()))
S['n_ridings'] = len(x); S['majority'] = len(x) // 2 + 1
S['seats'] = {p: int((x.lead26 == p).sum()) for p in ('CON', 'NDP', 'GRN')}
S['seats24'] = {p: int((x.win24 == p).sum()) for p in ('CON', 'NDP', 'GRN')}
S['share'] = {p: round(float(100 * v26.get(p, 0) / v26.sum()), 2) for p in ('CON', 'NDP', 'GRN', 'CENTRE', 'ONEBC', 'OTH')}

# ---------------------------------------------------------------- 2. how: the Conservatives replaced the BC Liberals
rise = []
for yr in (2017, 2020, 2024):
    r = h[h.year == yr].iloc[0]
    rise.append(dict(year=yr, BCLIB=float(r.share_BCLIB or 0), CON=float(r.share_CON or 0), NDP=float(r.share_LEFT), GRN=float(r.share_GRN or 0)))
rise.append(dict(year=2026, BCLIB=0.0, CON=S['share']['CON'], NDP=S['share']['NDP'], GRN=S['share']['GRN'], initial=True))

rl = []
# 2001: the series files the BC Conservative (CP) vote under "Other"; take it from the district file instead
d01 = pd.read_csv(B + 'history/districts_2001_2017.csv'); d01 = d01[d01.year == 2001]
con01 = round(float(100 * d01[d01.party == 'CP'].votes.sum() / d01.drop_duplicates('ed_code').total_valid_votes.sum()), 2)
for yr in (2001, 2005, 2009, 2013, 2017, 2020, 2024):
    r = h[h.year == yr].iloc[0]
    rl.append(dict(year=yr, BCLIB=float(r.share_BCLIB or 0), CON=con01 if yr == 2001 else float(r.share_CON or 0), NDP=float(r.share_LEFT)))
rl.append(dict(year=2026, BCLIB=0.0, CON=S['share']['CON'], NDP=S['share']['NDP'], initial=True))
S['rise_long'] = rl
x['nw20'] = t20.notional_winner_2020
S['rise'] = dict(years=rise, lib_ridings_2020=int((x.nw20 == 'LIB').sum()),
                 lib_ridings_2020_con_lead=int(((x.nw20 == 'LIB') & (x.lead26 == 'CON')).sum()),
                 ndp_ridings_2020_con_lead=int(((x.nw20 == 'NDP') & (x.lead26 == 'CON')).sum()),
                 ndp_ridings_2020=int((x.nw20 == 'NDP').sum()),
                 corr_right2020_con2024=round(float((t20.LIB_pct + t20.CON_pct).reindex(x.index).corr(x.con24)), 2),
                 bcunited_candidates_2024=0)

# ---------------------------------------------------------------- 3. where: the suburbs switched
AREA = {'SRC': 'Surrey', 'SRF': 'Surrey', 'SRG': 'Surrey', 'SRN': 'Surrey', 'BNC': 'Burnaby', 'BNO': 'Burnaby',
        'CQB': 'Coquitlam', 'CQM': 'Coquitlam', 'POM': 'Port Moody', 'RCS': 'Richmond', 'DLN': 'Delta',
        'NVS': 'North Vancouver', 'MAP': 'Maple Ridge', 'VFV': 'Vancouver', 'VLA': 'Vancouver', 'VNY': 'Vancouver',
        'SAS': 'Saanich', 'JFM': 'Juan de Fuca', 'CWV': 'Cowichan Valley', 'LAO': 'Ladysmith', 'VRL': 'Vernon', 'CRC': 'Courtenay-Comox'}
sw = x[x.win24 != x.lead26]
S['switched'] = [dict(code=c, name=r['name'], region=r.region, area=AREA.get(c, r['name']), from_=r.win24, to=r.lead26,
                      margin=int(r.margin26_votes)) for c, r in sw.iterrows()]
S['n_switched'] = len(sw)
S['n_switched_metro'] = int((sw.region == 'Metro Vancouver').sum())
areas = sw[sw.region == 'Metro Vancouver'].index.map(AREA).value_counts()
S['switched_metro_areas'] = {k: int(v) for k, v in areas.items()}
x['ptype'] = place.ptype
pt = x[x.index != 'PCN'].groupby('ptype').agg(n=('name', 'size'), swing=('tp_swing', 'mean'), switched=('flip', 'sum'))
S['place_types'] = [dict(type=k[2:], n=int(r.n), swing=round(float(r.swing), 1), switched=int(r.switched)) for k, r in pt.iterrows()]
sub = pt.loc[['2 Transit suburb', '3 Car suburb']]; oth = pt.loc[['1 Active core', '4 Exurban and rural']]
S['suburb_swing'] = round(float((sub.swing * sub.n).sum() / sub.n.sum()), 1)
S['core_rural_swing'] = round(float((oth.swing * oth.n).sum() / oth.n.sum()), 1)
S['suburb_switched'] = int(sub.switched.sum())
# Vancouver's suburbs: Metro Vancouver ridings outside the City of Vancouver (riding names that do not start with "Vancouver-")
mvs = x[(x.region == 'Metro Vancouver') & ~x['name'].str.startswith('Vancouver-')]
sy = x[x['name'].str.startswith('Surrey')]
S['surrey'] = dict(n=len(sy), con24=int((sy.win24 == 'CON').sum()), con26=int((sy.lead26 == 'CON').sum()))
S['vancouver_suburbs'] = dict(n=len(mvs), con24=int((mvs.win24 == 'CON').sum()), con26=int((mvs.lead26 == 'CON').sum()),
                              ndp24=int((mvs.win24 == 'NDP').sum()), ndp26=int((mvs.lead26 == 'NDP').sum()))

# ---------------------------------------------------------------- 4. who lives there (riding medians; 2021 Census)
# 'switched' = a new Conservative lead (the one riding that moved to the NDP, Courtenay-Comox, is left out as 'other')
x['grp'] = np.where((x.win24 != x.lead26) & (x.lead26 == 'CON'), 'switched',
                    np.where(x.win24 != x.lead26, 'other', np.where(x.lead26 == 'NDP', 'stayed_ndp', np.where(x.lead26 == 'CON', 'stayed_con', 'other'))))
cols = dict(own='pct_hh_owner', drive='pct_commute_car', vismin='pct_vm_total', income='hh_income_median', immig='pct_immigrants',
            degree='pct_bachelor_plus_25_64', kids='pct_age_0_14', renters='pct_hh_renter')
S['who'] = {g: {k: round(float(x[x.grp == g][c].median()), 1) for k, c in cols.items()} | {'n': int((x.grp == g).sum())}
            for g in ('switched', 'stayed_ndp', 'stayed_con')}


# pooled shares across the ridings in each group, each over its own census universe, plus the typical riding's median income:
# owners over private households; car commuters (driver or passenger) over all commuters; visible minorities and immigrants
# over the population in private households (25% sample), recovered from each riding's count and published share
def pooled(d):
    hh = d.hh_owner.sum() + d.hh_renter.sum()
    com = d[['commute_car', 'commute_transit', 'commute_walk_bike', 'commute_other']].sum().sum()
    priv = (100 * d.vm_total / d.pct_vm_total).sum()
    # kept at four decimals so that pages rounding to whole percentages round once (28.48 shows as 28%, not 29%)
    return dict(own=round(100 * d.hh_owner.sum() / hh, 4), drive=round(100 * d.commute_car.sum() / com, 4),
                vismin=round(100 * d.vm_total.sum() / priv, 4), immig=round(100 * d.immigrants.sum() / priv, 4),
                income=float(d.hh_income_median.median()), n=int(len(d)))
S['who_pooled'] = {g: pooled(x[x.grp == g]) for g in ('switched', 'stayed_ndp', 'stayed_con')}

# ---------------------------------------------------------------- 5. the middle ground (federal 2025 plurality on provincial ridings)
fw = fed[['LPC_share_pct', 'CPC_share_pct', 'NDP_share_pct', 'GPC_share_pct']].idxmax(axis=1).str[:3]
x['fedwin'] = fw
mid = {}
for g in ('NDP', 'LPC', 'CPC', 'GPC'):
    d = x[x.fedwin == g]
    mid[g] = dict(n=len(d), y2024={p: int((d.win24 == p).sum()) for p in ('NDP', 'CON', 'GRN')},
                  y2026={p: int((d.lead26 == p).sum()) for p in ('NDP', 'CON', 'GRN')}, switched=int((d.win24 != d.lead26).sum()))
S['middle'] = mid
# average two-party swing toward the Conservatives by 2025 federal group (Peace River North, with no NDP candidate, left out)
sx = x[x.index != 'PCN']
# NDP share of the provincial vote, average riding, by 2025 federal group (Peace River North, with no NDP candidate, left out)
S['middle_ndp'] = {g: dict(y2024=round(float(sx[m].ndp24.mean()), 1), y2026=round(float(sx[m].ndp26.mean()), 1),
                           con2024=round(float(sx[m].con24.mean()), 1), con2026=round(float(sx[m].con26.mean()), 1), n=int(m.sum()))
                   for g, m in (('LPC', sx.fedwin == 'LPC'), ('CPC', sx.fedwin == 'CPC'), ('NDP_GPC', sx.fedwin.isin(['NDP', 'GPC'])))}
# provincial vote pooled over each federal group's ridings (party votes over all valid votes), 2024 final and 2026,
# with the provincial seats each group elected
_d24 = pd.read_csv(B + 'results24/out/districts_2024.csv').pivot_table(index='ed_code', columns='party', values='votes', aggfunc='sum').fillna(0)
_p26 = live.pivot_table(index='district_code', columns='party_code', values='votes', aggfunc='sum').fillna(0)
def _pool(codes):
    a = _d24.reindex(codes).sum(); b = _p26.reindex(codes).sum()
    return dict(n=len(codes), y2024={k: round(float(100 * a.get(k, 0) / a.sum()), 1) for k in ('NDP', 'CON', 'GRN')},
                y2026={k: round(float(100 * b.get(k, 0) / b.sum()), 1) for k in ('NDP', 'CON', 'GRN')},
                seats24={k: int((x.loc[codes].win24 == k).sum()) for k in ('NDP', 'CON', 'GRN')},
                seats26={k: int((x.loc[codes].lead26 == k).sum()) for k in ('NDP', 'CON', 'GRN')})
S['middle_pooled'] = {g: _pool(x.index[m]) for g, m in (('LPC', x.fedwin == 'LPC'), ('CPC', x.fedwin == 'CPC'), ('NDP_GPC', x.fedwin.isin(['NDP', 'GPC'])))}
# swing by riding income: ridings ranked by median household income (2021 Census, 2020 incomes) and cut into four groups of 23,
# Peace River North (no NDP candidate in 2026) left out; each group's mean two-party swing and median income
_s = x[x.index != 'PCN']
_q = pd.qcut(_s.hh_income_median.rank(method='first'), 4, labels=False)
S['income_groups'] = [dict(n=int((_q == k).sum()), swing=round(float(_s.tp_swing[_q == k].mean()), 1), income=float(_s.hh_income_median[_q == k].median()))
                      for k in range(4)]
S['income_r'] = round(float(_s.hh_income_median.corr(_s.tp_swing)), 2)
S['middle_swing'] = dict(LPC=round(float(sx[sx.fedwin == 'LPC'].tp_swing.mean()), 1), CPC=round(float(sx[sx.fedwin == 'CPC'].tp_swing.mean()), 1),
                         NDP_GPC=round(float(sx[sx.fedwin.isin(['NDP', 'GPC'])].tp_swing.mean()), 1),
                         NDP=round(float(sx[sx.fedwin == 'NDP'].tp_swing.mean()), 1), GPC=round(float(sx[sx.fedwin == 'GPC'].tp_swing.mean()), 1))
# each riding's swing in its income group, for the dots on slide 5
for k, grp in enumerate(S['income_groups']):
    grp['swings'] = sorted(round(float(v), 2) for v in _s.tp_swing[_q == k])
# the last Conservative majority before 2026 (seats by party after each general election since 1928)
_maj = h[(h.seats_CON.fillna(0) > h.seats_in_house / 2) & (h.year < 2026)]
_ly = int(_maj.year.max()); _lr = h[h.year == _ly].iloc[0]
# 1928: the Conservative Party's own share is 53.30% (Electoral History of BC 1871-1986, p.159); the series' 53.60 adds Independent Conservatives
S['last_con_majority'] = dict(year=_ly, seats=int(_lr.seats_CON), of=int(_lr.seats_in_house), share=53.30 if _ly == 1928 else float(_lr.share_CON),
                              n_after=int(((h.year > _ly) & (h.year < 2026)).sum()))

flows = {}
for g in ('NDP', 'LPC', 'CPC', 'GPC'):
    d = x[x.fedwin == g]
    flows[g] = {f'{a}>{b}': int(n) for (a, b), n in d.groupby(['win24', 'lead26']).size().items()}
S['middle_flows'] = flows
# riding-level estimate (Goodman regression, non-negative) of where each federal party's voters went provincially, with bootstrap ranges
F = fed[['LPC_share_pct', 'CPC_share_pct', 'NDP_share_pct', 'GPC_share_pct', 'OTH_share_pct']].values / 100
rng = np.random.default_rng(7); est = {}
for yr in ('24', '26'):
    for party in ('con', 'ndp', 'grn'):
        y = x[f'{party}{yr}'].values / 100
        point = nnls(F, y)[0]
        boots = np.array([nnls(F[i], y[i])[0] for i in [rng.integers(0, len(y), len(y)) for _ in range(400)]])
        est[f'{party}{yr}'] = dict(LPC=[round(100 * point[0]), round(100 * np.percentile(boots[:, 0], 5)), round(100 * np.percentile(boots[:, 0], 95))],
                                   CPC=[round(100 * point[1]), round(100 * np.percentile(boots[:, 1], 5)), round(100 * np.percentile(boots[:, 1], 95))],
                                   NDP=[round(100 * point[2]), round(100 * np.percentile(boots[:, 2], 5)), round(100 * np.percentile(boots[:, 2], 95))])
S['flows'] = est

# ---------------------------------------------------------------- 6. why: what voters said (pollster releases)
ar = polls[(polls.pollster == 'Angus Reid Institute') & (polls.field_end == '2026-10-19')].iloc[0]
ir = polls[(polls.pollster == 'Innovative Research Group') & (polls.field_end == '2026-10-19')].iloc[0]
ip = polls[(polls.pollster == 'Ipsos') & (polls.field_end == '2026-10-22')].iloc[0]
S['why'] = dict(
    issues=[dict(issue='Cost of living', pct=58, best=dict(CON=33, NDP=26)), dict(issue='Health care', pct=44, best=dict(NDP=30, CON=28)),
            dict(issue='Housing', pct=28, best=dict(CON=28, NDP=27))],
    issues_source=dict(pollster='Angus Reid Institute', field=f'{ar.field_start} to {ar.field_end}', url=ar.source_url,
                       question='Top issues facing the province (choose up to three)'),
    best_source=dict(pollster='Innovative Research Group', field=f'{ir.field_start} to {ir.field_end}', url=ir.source_url,
                     question='Which party is best on each issue'),
    time_for_change=dict(pct=53, reelect=31, pollster='Ipsos', field=f'{ip.field_start} to {ip.field_end}', url=ip.source_url))
# a lead on "best party" counts only when the gap is larger than the 95% margin of error of the gap between two shares
# of one sample (weighted n from the release); smaller gaps are shown as about even
n_best = int(str(ir.sample_size).split()[0]); S['why']['best_source']['n'] = n_best
for it in S['why']['issues']:
    (a, pa), (b, pb) = sorted(it['best'].items(), key=lambda kv: -kv[1])
    moe = 100 * 1.96 * ((pa / 100 + pb / 100 - (pa / 100 - pb / 100) ** 2) / n_best) ** 0.5
    it.update(gap=pa - pb, moe=round(moe, 1), lead=a if pa - pb > moe else 'even')

# ---------------------------------------------------------------- 7. what the majority means
S['votes_seats'] = {p: dict(votes=S['share'][p], seats=round(100 * S['seats'][p] / len(x), 1)) for p in ('CON', 'NDP', 'GRN')}
con = x[x.lead26 == 'CON'].sort_values('margin26_votes'); need = S['seats']['CON'] - (S['majority'] - 1)
S['tipping'] = dict(seats_to_lose=int(need), voters=int((con.head(need).margin26_votes // 2 + 1).sum()),
                    pct_of_votes=round(float(100 * (con.head(need).margin26_votes // 2 + 1).sum() / v26.sum()), 2),
                    tipping_riding=con.iloc[need - 1]['name'])
S['indices'] = json.loads(idx.to_json(orient='records'))
wasted = {}
for p in ('CON', 'NDP', 'GRN'):
    tot = live[live.party_code == p].votes.sum()
    wasted[p] = round(float(100 * live[(live.party_code == p) & (live.district_code.map(x.lead26) != p)].votes.sum() / tot), 1)
S['votes_where_trailing'] = wasted

# ---------------------------------------------------------------- 8. promises matched to the top worries (Conservative platform)
PL = 'https://conservativebc.ca/wp-content/uploads/2026/10/20261016_BCC_Platform2026_8-5x11-Draft-18_compressed.pdf'
S['promises'] = [
    dict(worry='Cost of living', items=[
        dict(short='$1,000 a year in income-tax relief per person, from the 2027 tax year', detail='"Provide $1,000 a year in income-tax relief per person, or $2,000 for a couple" (page 5): basic personal amount raised from $13,216 to $32,000, from the 2027 tax year, cutting tax "by $1,000 or a little more for people who owe at least that much" (page 59); people who owe less save less. About $2.9 billion a year.', page='5, 59 to 60', url=PL),
        dict(short='Up to $150 million a year for family benefits and child care', detail='24-hour child care spaces, a higher BC Family Benefit and Affordable Child Care Benefit, and a multigenerational home renovation credit; phased in from $15 million in 2027/28 to the full amount from 2030/31 (costing table B1, page 64)', page='7, 61, 64', url=PL),
        dict(short='No tax increases while in government (party plan page)', detail='"Throughout the entirety of our government, we will not raise taxes on British Columbians." The pledge comes from the party\'s plan page and its September 27, 2026 release.', page='plan page', url='https://conservativebc.ca/plan/')]),
    dict(worry='Health care', items=[
        dict(short='Publicly paid surgery elsewhere when waits pass set limits', detail='"Universal Health-Care Guarantee": treatment through another qualified provider when surgical wait benchmarks are exceeded', page='32, 61', url=PL),
        dict(short='$50 million to keep rural ERs and maternity wards open', detail='Rural Health Emergency Fund', page='32, 61', url=PL),
        dict(short='A 100-day review of reforms from other public systems to cut waits', detail='"Launch the 100-day Patients First review to identify reforms from other universal public systems that cut waits, expand capacity, keep ERs open, and strengthen rural services, without user fees."', page='32', url=PL)]),
    dict(worry='Housing', items=[
        dict(short='Faster approvals for new homes', detail='"Approve homes in months, not years"; zoning to match community plans', page='6', url=PL),
        dict(short='Cut construction charges and fix the building code', detail='No charges named; step code overhaul', page='5 to 6', url=PL),
        dict(short='No target for homes built, rents or prices', detail='The platform sets no number of homes and no target for rents or prices; its timeline is for approvals ("Approve homes in months, not years", page 6).', page='5 to 7', url=PL)])]
S['platform'] = dict(title="Lorne Doerkson's Plan for a Stronger BC, 2026", url=PL, new_spending_full_year_billion=1.425, tax_relief_four_years_billion=11.1,
                     deficit_2029_30_billion=10.8)
S['next'] = dict(final_count='November 6 to 10, 2026 (planned)', return_day='November 18, 2026', swearing_in='not announced',
                 source='https://elections.bc.ca/2026-provincial-election/', premier='Lorne Doerkson (interim leader)')
cl = x.sort_values('margin26_votes')
S['close'] = [dict(name=r['name'], lead=r.lead26, second=r.second26, votes=int(r.margin26_votes)) for _, r in cl.head(8).iterrows()]
S['n_within_150'] = int((x.margin26_votes <= 150).sum())

# ---------------------------------------------------------------- website extras: income x education, gender gap in final polls
s = x[x.index != 'PCN'].copy()
s['inc'] = np.where(s.hh_income_median >= s.hh_income_median.median(), 'Higher income', 'Lower income')
s['edu'] = np.where(s.pct_bachelor_plus_25_64 >= s.pct_bachelor_plus_25_64.median(), 'more degrees', 'fewer degrees')
g = s.groupby(['inc', 'edu']).agg(n=('name', 'size'), swing=('tp_swing', 'mean'), ndp=('ndp_swing', 'mean'), grn=('grn_change', 'mean'), switched=('flip', 'sum'))
S['income_education'] = [dict(income=a, education=b, n=int(r.n), swing=round(float(r.swing), 1), ndp_change=round(float(r.ndp), 1),
                              grn_change=round(float(r.grn), 1), switched=int(r.switched)) for (a, b), r in g.iterrows()]
S['realignment'] = {v: dict(r2024=round(float(s[v].corr(s.tp24)), 2), r2026=round(float(s[v].corr(s.tp26)), 2))
                    for v in ('hh_income_median', 'pct_bachelor_plus_25_64', 'density_per_km2', 'pct_hh_owner', 'pct_immigrants')}

json.dump(S, open(OUT, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps({k: S[k] for k in ('seats', 'n_switched', 'n_switched_metro', 'switched_metro_areas', 'suburb_swing', 'core_rural_swing', 'suburb_switched',
                                    'who', 'middle', 'votes_seats', 'tipping', 'n_within_150')}, indent=0)[:3000])
print(S['rise'])
