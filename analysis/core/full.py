"""Full analysis of the 2026 BC general election (results as of October 25, 2026, 1:49 a.m. Pacific) against 2024, 2025 federal,
2021 Census, polls and the 1928-2024 history. Writes tables to analysis/out/ and prints findings."""
import json, numpy as np, pandas as pd
pd.set_option('display.width', 400); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 200)
B = 'analysis/'; O = B + 'core/out/'

# ---------- inputs ----------
live = pd.read_csv(B + 'live/latest.csv')
dist = pd.read_csv(B + 'live/latest_districts.csv').set_index('district_code')
r24 = pd.read_csv(B + 'results24/out/districts_2024.csv')
s24 = pd.read_csv(B + 'results24/out/districts_2024_summary.csv').set_index('ed_code')
cen = pd.read_csv(B + 'census/out/ed2023_profile.csv').set_index('ed_code')
fed = pd.read_csv(B + 'federal25/fed2025_on_ed2023.csv').set_index('ed_code')
cands = pd.read_csv(B + 'live/candidates_2026.csv')
adv = pd.read_csv(B + 'live/advance_turnout_2026_vs_2024.csv').set_index('ed_code')
hist = pd.read_csv(B + 'history/province_series.csv')
rd = pd.read_csv(B + 'geo/out/ed2023_regions.csv').set_index('ed_code')
reg3 = pd.read_csv(B + 'model/out/regions.csv').set_index('ed_code').region
pavg = json.load(open(B + 'model/out/poll_average.json'))
snap = live.snapshot_utc.iloc[0]

P = ['CON', 'NDP', 'GRN', 'CENTRE', 'ONEBC', 'OTH']
v26 = live.pivot_table(index='district_code', columns='party_code', values='votes', aggfunc='sum').reindex(columns=P).fillna(0)
r24['pc'] = r24.party.where(r24.party.isin(['CON', 'NDP', 'GRN']), 'OTH')
v24 = r24.pivot_table(index='ed_code', columns='pc', values='votes', aggfunc='sum').reindex(columns=['CON', 'NDP', 'GRN', 'OTH']).fillna(0)
sh26 = v26.div(v26.sum(axis=1), axis=0) * 100
sh24 = v24.div(v24.sum(axis=1), axis=0) * 100

# finer regions from regional districts (documented rule: the district's regional district by population share)
# the island outside the Capital Region, with the mainland coast across the strait (qathet: Powell River and the Sunshine Coast;
# Squamish-Lillooet: Squamish and Whistler, where most of West Vancouver-Sea to Sky's people live)
VIC = 'Rest of Vancouver Island and Coast'
RDMAP = {'Metro Vancouver': 'Metro Vancouver', 'Capital': 'Capital Region (Victoria)', 'Fraser Valley': 'Fraser Valley',
         'Central Okanagan': 'Okanagan', 'North Okanagan': 'Okanagan', 'Okanagan-Similkameen': 'Okanagan',
         'Cowichan Valley': VIC, 'Nanaimo': VIC, 'Comox Valley': VIC, 'Strathcona': VIC, 'Mount Waddington': VIC, 'Alberni-Clayoquot': VIC,
         'qathet': VIC, 'Squamish-Lillooet': VIC}
def region6(r):
    for k, v in RDMAP.items():
        if k.lower() in str(r).lower(): return v
    return 'Interior and North'
x = pd.DataFrame(index=dist.index)
x['name'] = dist.district_name
x['region3'] = reg3
x['region'] = rd.regional_district.map(region6)
x.loc[x.index.isin(['MAP', 'MRP']) | x.name.str.contains('Maple Ridge'), 'region'] = 'Metro Vancouver'
x['win24'] = s24.winner_party; x['lead26'] = dist.leader; x['second26'] = dist.second
x['margin26_votes'] = dist.margin_votes; x['margin26_pts'] = dist.margin_pts
x['margin24_pts'] = s24.margin_pts
for p in P: x[f'{p.lower()}26'] = sh26[p]
for p in ['CON', 'NDP', 'GRN']: x[f'{p.lower()}24'] = sh24[p]
x['con_swing'] = x.con26 - x.con24; x['ndp_swing'] = x.ndp26 - x.ndp24; x['grn_change'] = x.grn26 - x.grn24
x['votes26'] = v26.sum(axis=1); x['reg26'] = adv.registered_2026_oct14
x['reg24'] = s24.registered_voters
r24i = r24.groupby('ed_code')[['votes_adv', 'votes_final']].sum().sum(axis=1)   # 2024 in-district advance + voting day = comparable to election-night count
x['votes24_night'] = r24i; x['turn24_final'] = s24.turnout_pct
x['night_turn24'] = 100 * x.votes24_night / x.reg24; x['night_turn26'] = 100 * x.votes26 / x.reg26
x['cpc25'] = fed.CPC_share_pct; x['lpc25'] = fed.LPC_share_pct; x['ndp25'] = fed.NDP_share_pct
x['fed_lead25'] = np.where(x.cpc25 > x.lpc25, 'CPC', 'LPC')
x['flip'] = x.win24 != x.lead26
x = x.join(cen.drop(columns=['ed_name']))
x.to_csv(O + 'ridings_2026_joined.csv')

out = {}
# ---------- 1. province ----------
tot26 = v26.sum(); tot24 = v24.sum()
prov = pd.DataFrame({'votes26': tot26, 'share26': (100 * tot26 / tot26.sum()).round(2),
                     'share24': (100 * tot24 / tot24.sum()).reindex(P).round(2),
                     'lead26': x.lead26.value_counts().reindex(P).fillna(0).astype(int),
                     'seats24': x.win24.value_counts().reindex(P).fillna(0).astype(int),
                     'polls': pd.Series(pavg['province']).reindex(P)})
prov['change'] = prov.share26 - prov.share24; prov['count_minus_polls'] = prov.share26 - prov.polls
prov.to_csv(O + 'province.csv'); out['province'] = prov
# votes per seat
prov['votes_per_seat'] = (prov.votes26 / prov.lead26.replace(0, np.nan)).round(0)
# seat bonus
print('== PROVINCE (initial count', snap, ')'); print(prov.round(2))
print('total valid', int(tot26.sum()), '| boxes', int(dist.boxes_reported.sum()), '/', int(dist.boxes_total.sum()))

# ---------- 2. flips ----------
fl = x[x.flip][['name', 'region', 'win24', 'lead26', 'margin24_pts', 'margin26_pts', 'margin26_votes', 'con_swing', 'ndp_swing']].sort_values(['lead26', 'region'])
fl.to_csv(O + 'flips.csv'); print('\n== FLIPS', len(fl)); print(fl.round(1).to_string())
print(fl.groupby(['win24', 'lead26', 'region']).size())

# ---------- 3. regions ----------
def regtab(col):
    g = x.groupby(col)
    rv26 = v26.groupby(x[col]).sum(); rv24 = v24.groupby(x[col]).sum()
    t = pd.DataFrame({'ridings': g.size(),
        'CON24': (100 * rv24.CON / rv24.sum(axis=1)).round(1), 'CON26': (100 * rv26.CON / rv26.sum(axis=1)).round(1),
        'NDP24': (100 * rv24.NDP / rv24.sum(axis=1)).round(1), 'NDP26': (100 * rv26.NDP / rv26.sum(axis=1)).round(1),
        'GRN24': (100 * rv24.GRN / rv24.sum(axis=1)).round(1), 'GRN26': (100 * rv26.GRN / rv26.sum(axis=1)).round(1),
        'CON_seats24': g.win24.apply(lambda s: (s == 'CON').sum()), 'CON_seats26': g.lead26.apply(lambda s: (s == 'CON').sum()),
        'NDP_seats24': g.win24.apply(lambda s: (s == 'NDP').sum()), 'NDP_seats26': g.lead26.apply(lambda s: (s == 'NDP').sum()),
        'GRN_seats26': g.lead26.apply(lambda s: (s == 'GRN').sum())})
    return t
R6 = regtab('region'); R6.to_csv(O + 'regions6.csv'); print('\n== REGIONS'); print(R6)

# ---------- 4. turnout ----------
tn = pd.DataFrame({'registered': [x.reg24.sum(), x.reg26.sum()], 'votes_counted_on_night': [x.votes24_night.sum(), x.votes26.sum()]}, index=['2024', '2026'])
tn['pct'] = (100 * tn.votes_counted_on_night / tn.registered).round(2)
tn.to_csv(O + 'turnout.csv'); print('\n== TURNOUT (election-night comparable)'); print(tn)
x['night_turn_change'] = x.night_turn26 - x.night_turn24
print('turnout change: median', round(x.night_turn_change.median(), 1), 'by region'); print(x.groupby('region').night_turn_change.median().round(1))
print('rose in', (x.night_turn_change > 0).sum(), 'ridings')
print('corr turnout change vs con swing', round(x.night_turn_change.corr(x.con_swing), 2))

# ---------- 5. demographics ----------
V = {'Median household income': 'hh_income_median', 'University degree (25-64)': 'pct_bachelor_plus_25_64', 'Median age': 'median_age',
     'Age 65+': 'pct_age_65_plus', 'Age 20-34': 'pct_age_20_34', 'Renters': 'pct_hh_renter', 'Median home value': 'median_dwelling_value',
     'Shelter cost 30%+': 'pct_hh_shelter_30plus', 'Visible minority': 'pct_vm_total', 'South Asian': 'pct_vm_south_asian', 'Chinese': 'pct_vm_chinese',
     'Filipino': 'pct_vm_filipino', 'Indigenous': 'pct_indigenous', 'Immigrants': 'pct_immigrants', 'Recent immigrants': 'pct_recent_immigrants_2016_2021',
     'Punjabi at home': 'pct_lang_home_punjabi_panjabi', 'Mandarin at home': 'pct_lang_home_mandarin', 'Cantonese at home': 'pct_lang_home_yue_cantonese',
     'English at home': 'pct_lang_home_english', 'Men': 'pct_men_plus', 'No religion': 'pct_rel_none_secular', 'Christian': 'pct_rel_christian',
     'Sikh': 'pct_rel_sikh', 'Low income': 'pct_low_income_lim_at', 'Unemployment': 'unemployment_rate', 'Transit commute': 'pct_commute_transit',
     'Density': 'density_per_km2', 'Population growth 2016-21': 'pop_growth_2016_2021_pct_approx'}
rows = []
for k, v in V.items():
    if v not in x: print('missing', v); continue
    q = pd.qcut(x[v].rank(method='first'), 4, labels=False)
    g = x.groupby(q)
    rows.append(dict(measure=k, column=v, low_quarter_median=x[v][q == 0].median(), high_quarter_median=x[v][q == 3].median(),
        con26_low=g.con26.mean()[0], con26_high=g.con26.mean()[3], ndp26_low=g.ndp26.mean()[0], ndp26_high=g.ndp26.mean()[3],
        con_swing_low=g.con_swing.mean()[0], con_swing_high=g.con_swing.mean()[3], ndp_swing_low=g.ndp_swing.mean()[0], ndp_swing_high=g.ndp_swing.mean()[3],
        r_con26=x[v].corr(x.con26), r_con_swing=x[v].corr(x.con_swing), r_ndp_swing=x[v].corr(x.ndp_swing),
        r_con_swing_metro=x[x.region == 'Metro Vancouver'][v].corr(x[x.region == 'Metro Vancouver'].con_swing)))
D = pd.DataFrame(rows).round(2).sort_values('r_ndp_swing', key=abs, ascending=False)
D.to_csv(O + 'demographics.csv', index=False)
print('\n== DEMOGRAPHICS (quartiles of ridings, unweighted means)')
print(D[['measure', 'low_quarter_median', 'high_quarter_median', 'con26_low', 'con26_high', 'con_swing_low', 'con_swing_high', 'ndp_swing_low', 'ndp_swing_high', 'r_con_swing', 'r_ndp_swing', 'r_con_swing_metro']].to_string(index=False))

# multivariate: which links hold jointly (standardised OLS, numpy)
def ols(y, cols, df):
    d = df[[y] + cols].dropna(); Z = (d[cols] - d[cols].mean()) / d[cols].std()
    X = np.column_stack([np.ones(len(d)), Z.values]); b, *_ = np.linalg.lstsq(X, d[y].values, rcond=None)
    res = d[y].values - X @ b; r2 = 1 - (res ** 2).sum() / ((d[y] - d[y].mean()) ** 2).sum()
    s2 = (res ** 2).sum() / (len(d) - X.shape[1]); se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return pd.DataFrame({'coef_pts_per_sd': b[1:], 't': b[1:] / se[1:]}, index=cols).round(2), round(r2, 2), len(d)
x['metro'] = (x.region == 'Metro Vancouver').astype(int); x['fed_lib'] = (x.fed_lead25 == 'LPC').astype(int)
for y in ['ndp_swing', 'con_swing']:
    m, r2, n = ols(y, ['hh_income_median', 'pct_immigrants', 'pct_hh_renter', 'pct_indigenous', 'pct_rel_none_secular', 'median_age', 'metro', 'ndp24'], x)
    print(f'\n== OLS {y} (n={n}, R2={r2})'); print(m); m.to_csv(O + f'ols_{y}.csv')

# ---------- 6. federal ----------
F = x.groupby('fed_lead25').agg(ridings=('name', 'size'), ndp_swing=('ndp_swing', 'mean'), con_swing=('con_swing', 'mean'),
    con_lead26=('lead26', lambda s: (s == 'CON').sum()), ndp_lead26=('lead26', lambda s: (s == 'NDP').sum()), flips=('flip', 'sum')).round(1)
F.to_csv(O + 'federal.csv'); print('\n== FEDERAL 2025 LEAD'); print(F)
ct = pd.crosstab(x.fed_lead25, x.lead26); print(ct); ct.to_csv(O + 'federal_crosstab.csv')
print('corr LPC25 share vs NDP swing', round(x.lpc25.corr(x.ndp_swing), 2), '| NDP25 share vs ndp swing', round(x.ndp25.corr(x.ndp_swing), 2))

# ---------- 7. history ----------
h = hist.copy(); print('\n== HISTORY columns', h.columns.tolist()[:12])

# ---------- 8. polls vs count by region ----------
rows = []
for reg, d in pavg['regional'].items():
    for p, v in d.items():
        rows.append(dict(region=reg, party=p, poll=v['avg'], n_pollsters=v['n']))
PR = pd.DataFrame(rows)
cnt = {'Metro Vancouver': x.region3 == 'Metro Vancouver', 'Capital Region': x.region.isin(['Capital Region (Victoria)', VIC]) & ~x.index.isin(['POR', 'WVS']), 'Rest of BC': x.region3 == 'Rest of BC'}  # pollsters publish Vancouver Island, stored under the Capital Region key
def cshare(mask, p):
    vv = v26[mask.reindex(v26.index).fillna(False)]; return 100 * vv[p].sum() / vv.sum().sum()
PR['count'] = [cshare(cnt[r], p) if r in cnt else np.nan for r, p in zip(PR.region, PR.party)]
PR['count_minus_poll'] = PR['count'] - PR.poll
PR.round(1).to_csv(O + 'polls_vs_count_regions.csv', index=False); print('\n== POLLS VS COUNT BY REGION'); print(PR.round(1))
fz = pd.read_csv(B + 'model/out/districts_projection.csv').set_index('ed_code')
x['proj_uni'] = fz.uni_winner; x['proj_prop'] = fz.prop_winner
print('estimate right: uniform', (x.proj_uni == x.lead26).sum(), 'proportional', (x.proj_prop == x.lead26).sum())
print('missed (uniform):'); print(x[x.proj_uni != x.lead26][['name', 'proj_uni', 'lead26', 'margin26_pts']].round(1).to_string())
toss = fz[fz.uni_tier == 'toss-up'].index; print('toss-ups went', x.loc[toss].lead26.value_counts().to_dict())

# ---------- 9. new parties and leaders ----------
for p in ['CENTRE', 'ONEBC']:
    ran = v26[p] > 0
    print(f'\n== {p}: ran in', int(ran.sum()), 'ridings, share where ran', round(100 * v26.loc[ran, p].sum() / v26.loc[ran].sum().sum(), 2),
          '| best:', x.loc[ran, f'{p.lower()}26'].sort_values(ascending=False).head(3).round(1).to_dict())
    # would their votes have changed the winner? (upper bound: all their votes to the runner-up)
    z = x[ran & (x.lead26 == 'CON')]; changed = z[v26.loc[z.index, p] > z.margin26_votes]
    zn = x[ran & (x.lead26 == 'NDP')]; changedn = zn[v26.loc[zn.index, p] > zn.margin26_votes]
    print('  ridings where its vote exceeded the winning margin: CON-led', list(changed.name), '| NDP-led', list(changedn.name))
lead = {'Eby (NDP)': 'VNP', 'Doerkson (CON)': 'CBC', 'Lowan (GRN)': 'SAN', 'Sturko (CentreBC)': 'SUS', 'Brodie (OneBC)': 'VNQ', 'Kealy (Ind)': 'PCN'}
L = live[live.district_code.isin(lead.values())].sort_values(['district_code', 'votes'], ascending=[True, False])
L.to_csv(O + 'leaders_ridings.csv', index=False)
print('\n== LEADERS RIDINGS'); print(L.groupby('district_code').head(3)[['district_name', 'candidate', 'party', 'votes', 'share_pct', 'leading']].to_string(index=False))

# ---------- 10. incumbents ----------
inc = cands[cands.incumbent == 'Y'][['ed_code', 'candidate', 'affiliation', 'incumbent_same_district', 'mla_lims_affiliation_at_dissolution']]
lv = live.set_index(['district_code', 'candidate'])
inc['leading'] = [lv.leading.get((e, c), 'N/A') for e, c in zip(inc.ed_code, inc.candidate)]
inc.to_csv(O + 'incumbents.csv', index=False)
print('\n== INCUMBENTS running', len(inc), 'leading', (inc.leading == 'Y').sum(), 'not', (inc.leading == 'N').sum(), 'unmatched', (inc.leading == 'N/A').sum())
print(inc.groupby('affiliation').leading.value_counts().unstack(fill_value=0))
print('incumbents trailing:'); print(inc[inc.leading == 'N'][['ed_code', 'candidate', 'affiliation']].to_string(index=False))

# ---------- 11. close races ----------
C = x.sort_values('margin26_votes')[['name', 'lead26', 'second26', 'margin26_votes', 'margin26_pts', 'win24']].head(12)
C.to_csv(O + 'close_races.csv'); print('\n== CLOSEST'); print(C.round(2).to_string())
print('under 1 pt', (x.margin26_pts < 1).sum(), '| under 5 pts', (x.margin26_pts < 5).sum(), '| 2024 under 5 pts', (x.margin24_pts < 5).sum())
print('largest wins'); print(x.sort_values('margin26_pts', ascending=False)[['name', 'lead26', 'margin26_pts']].head(5).round(1).to_string())
print('\n== BIGGEST CON SWINGS'); print(x.sort_values('con_swing', ascending=False)[['name', 'region', 'con24', 'con26', 'con_swing', 'ndp_swing', 'win24', 'lead26']].head(10).round(1).to_string())
print('\n== BIGGEST NDP DROPS'); print(x.sort_values('ndp_swing')[['name', 'region', 'ndp24', 'ndp26', 'ndp_swing', 'con_swing', 'grn_change']].head(10).round(1).to_string())
print('\n== GREEN'); print(x.sort_values('grn26', ascending=False)[['name', 'grn24', 'grn26', 'lead26']].head(6).round(1).to_string())
print('ridings where CON vote fell', (x.con_swing < 0).sum(), '| NDP vote rose', (x.ndp_swing > 0).sum())

# ---------- 12. like-for-like: two-party swing (CON share of CON+NDP), robust to independents and Green entry/exit ----------
print('\n== TWO-PARTY SWING (CON / (CON+NDP))')
x['tp24'] = 100 * x.con24 / (x.con24 + x.ndp24); x['tp26'] = 100 * x.con26 / (x.con26 + x.ndp26); x['tp_swing'] = x.tp26 - x.tp24
o24 = r24[~r24.party.isin(['CON', 'NDP', 'GRN'])].groupby('ed_code').vote_share_pct.max()
g24 = set(r24[r24.party == 'GRN'].ed_code); g26 = set(live[live.party_code == 'GRN'].district_code)
x['same_field'] = (o24.reindex(x.index).fillna(0) < 5) & (x.index.isin(g24) == x.index.isin(g26))
print('province two-party: 2024', round(100 * tot24.CON / (tot24.CON + tot24.NDP), 1), '2026', round(100 * tot26.CON / (tot26.CON + tot26.NDP), 1))
print('ridings with comparable field', int(x.same_field.sum()))
print(x.groupby('region').tp_swing.describe()[['count', 'mean', 'min', 'max']].round(1))
rows = []
for k, v in V.items():
    if v not in x: continue
    q = pd.qcut(x[v].rank(method='first'), 4, labels=False); g = x.groupby(q)
    sf = x[x.same_field]
    rows.append(dict(measure=k, low_quarter_median=x[v][q == 0].median(), high_quarter_median=x[v][q == 3].median(),
                     tp_swing_low=g.tp_swing.mean()[0], tp_swing_high=g.tp_swing.mean()[3],
                     r_tp_swing=x[v].corr(x.tp_swing), r_tp_swing_same_field=sf[v].corr(sf.tp_swing),
                     r_tp_swing_metro=x[x.region == 'Metro Vancouver'][v].corr(x[x.region == 'Metro Vancouver'].tp_swing),
                     r_tp26_level=x[v].corr(x.tp26)))
T = pd.DataFrame(rows).round(2).sort_values('r_tp_swing', key=abs, ascending=False)
T.to_csv(O + 'demographics_two_party.csv', index=False); print(T.to_string(index=False))
for cols in (['hh_income_median', 'pct_immigrants', 'pct_hh_renter', 'median_age', 'pct_bachelor_plus_25_64', 'metro'],
             ['hh_income_median', 'pct_vm_south_asian', 'pct_vm_chinese', 'pct_hh_renter', 'median_age', 'metro']):
    m, r2, n = ols('tp_swing', cols, x); print(f'\nOLS tp_swing (n={n}, R2={r2})'); print(m)
    m2, r22, n2 = ols('tp_swing', cols, x[x.same_field]); print(f'same-field only (n={n2}, R2={r22})'); print(m2)
print(x.groupby('fed_lead25').tp_swing.mean().round(1))
print('top two-party swings'); print(x.sort_values('tp_swing', ascending=False)[['name', 'region', 'tp24', 'tp26', 'tp_swing', 'same_field', 'lead26']].head(12).round(1).to_string())
print('smallest'); print(x.sort_values('tp_swing')[['name', 'region', 'tp24', 'tp26', 'tp_swing', 'same_field']].head(8).round(1).to_string())
x.to_csv(O + 'ridings_2026_joined.csv')
