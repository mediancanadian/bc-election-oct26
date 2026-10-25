"""Borrowed post-election measures applied to B.C.: disproportionality, fragmentation, volatility, tipping point,
wasted votes, realignment (income x education), place typology, vote transitions (LP ecological inference)."""
import numpy as np, pandas as pd, json
B = 'analysis/'
h = pd.read_csv(B + 'history/province_series.csv')
fam = ['CON', 'SC', 'COAL', 'LIB', 'BCLIB', 'LEFT', 'GRN', 'REF', 'OTH']
x = pd.read_csv(B + 'core/out/ridings_2026_joined.csv', index_col=0)
live = pd.read_csv(B + 'live/latest.csv'); r24 = pd.read_csv(B + 'results24/out/districts_2024.csv')

# ---- 1-3. province-level indices by election
rows = []
for r in h.itertuples():
    v = np.array([getattr(r, 'share_' + f) if not pd.isna(getattr(r, 'share_' + f)) else 0 for f in fam], float)
    s = np.array([getattr(r, 'seats_' + f) if not pd.isna(getattr(r, 'seats_' + f)) else 0 for f in fam], float)
    if r.year == 1928: v[0] = 53.30
    s = 100 * s / s.sum(); v = 100 * v / v.sum()
    rows.append(dict(year=r.year, lsq=np.sqrt(0.5 * ((v - s) ** 2).sum()), env=1 / ((v / 100) ** 2).sum(), ens=1 / ((s / 100) ** 2).sum(),
                     top_share=v.max(), top_seats=s.max(), v=v, s=s))
v26 = live.groupby('party_code').votes.sum(); v26p = 100 * v26 / v26.sum()
seats = x.lead26.value_counts()
order = ['CON', 'NDP', 'GRN', 'CENTRE', 'ONEBC', 'OTH']
V = np.array([v26p.get(p, 0) for p in order]); Sx = np.array([100 * seats.get(p, 0) / 93 for p in order])
rows.append(dict(year=2026, lsq=np.sqrt(0.5 * ((V - Sx) ** 2).sum()), env=1 / ((V / 100) ** 2).sum(), ens=1 / ((Sx / 100) ** 2).sum(), top_share=V.max(), top_seats=Sx.max()))
I = pd.DataFrame(rows)[['year', 'lsq', 'env', 'ens', 'top_share', 'top_seats']].round(2)
# Pedersen volatility (party families; 2024->2026 with new parties)
vol = [None]
for a, b in zip(rows[:-2], rows[1:-1]):
    vol.append(0.5 * np.abs(b['v'] - a['v']).sum())
v24 = dict(zip(fam, rows[-2]['v'])); n24 = {'CON': v24['CON'], 'NDP': v24['LEFT'], 'GRN': v24['GRN'], 'CENTRE': 0, 'ONEBC': 0, 'OTH': 100 - v24['CON'] - v24['LEFT'] - v24['GRN']}
vol.append(0.5 * sum(abs(v26p.get(p, 0) - n24[p]) for p in order))
I['volatility'] = [None if v is None else round(v, 1) for v in vol]
print(I.to_string()); I.to_csv(B + 'core/meta/indices.csv', index=False)
print('LSq 2026 rank (higher = less proportional):', int((I.lsq >= I.lsq.iloc[-1]).sum()), 'of', len(I))

# ---- 4. tipping point: fewest votes switching CON->runner-up to cost the majority
con = x[x.lead26 == 'CON'].sort_values('margin26_votes')
need = int((x.lead26 == 'CON').sum() - 46)
tp = con.head(need)
print(f'\nCON leads {len(con)}; to fall to 46 needs {need} seats; votes switching = {int((tp.margin26_votes // 2 + 1).sum()):,} '
      f'in {need} ridings; of {int(v26.sum()):,} valid votes = {100 * (tp.margin26_votes // 2 + 1).sum() / v26.sum():.2f}%')
print('the tipping-point riding (47th easiest CON lead):', con.iloc[len(con) - 47 if False else 17]['name'], con.iloc[17].margin26_votes)

# ---- 5. wasted votes: votes cast in ridings where the party does not lead
lead_codes = x.lead26
w = {}
for p in ['CON', 'NDP', 'GRN']:
    tot = live[live.party_code == p].votes.sum()
    lost = live[(live.party_code == p) & (live.district_code.map(lead_codes) != p)].votes.sum()
    w[p] = round(100 * lost / tot, 1)
print('\nshare of each party\'s votes cast in ridings it does not lead:', w)

# ---- 6. realignment: income x education (Kitschelt & Rehm 2x2), 2024 vs 2026 two-party CON share
s = x[x.index != 'PCN'].copy()
s['inc_hi'] = s.hh_income_median >= s.hh_income_median.median(); s['edu_hi'] = s.pct_bachelor_plus_25_64 >= s.pct_bachelor_plus_25_64.median()
g = s.groupby(['inc_hi', 'edu_hi']).agg(n=('name', 'size'), tp24=('tp24', 'mean'), tp26=('tp26', 'mean'), swing=('tp_swing', 'mean'),
                                           ndp_ch=('ndp_swing', 'mean'), grn_ch=('grn_change', 'mean'), flips=('flip', 'sum')).round(1)
print('\nincome x education groups (median splits):'); print(g)
for v in ['hh_income_median', 'pct_bachelor_plus_25_64', 'density_per_km2', 'pct_hh_owner', 'pct_immigrants', 'median_age']:
    print(f'  r with CON two-party share: {v:26s} 2024 {s[v].corr(s.tp24):+.2f}  2026 {s[v].corr(s.tp26):+.2f}')

# ---- 7. place typology (Gordon / canadiansuburbs.ca transportation method, adapted to ridings)
bc_active = (s.commute_walk_bike / s.pop_2021).median() if 'commute_walk_bike' in s else None
ab = s['commute_walk_bike'] / (s['commute_car'] + s['commute_transit'] + s['commute_walk_bike'] + s['commute_other'])
tr = s['commute_transit'] / (s['commute_car'] + s['commute_transit'] + s['commute_walk_bike'] + s['commute_other'])
avg_ab = (s['commute_walk_bike'].sum()) / (s[['commute_car', 'commute_transit', 'commute_walk_bike', 'commute_other']].sum().sum())
avg_tr = (s['commute_transit'].sum()) / (s[['commute_car', 'commute_transit', 'commute_walk_bike', 'commute_other']].sum().sum())
def typ(i):
    # whole ridings: the density test comes first, so a large rural riding whose town people walk to work is not called an active core
    # (the project applies the walk-and-cycle test first, but only to census tracts inside metropolitan areas)
    if s.density_per_km2[i] < 150: return '4 Exurban and rural'
    if ab[i] >= 1.5 * avg_ab: return '1 Active core'
    if tr[i] > avg_tr: return '2 Transit suburb'
    return '3 Car suburb'
s['ptype'] = [typ(i) for i in s.index]
print(f'\nprovince averages: walk/bike {100*avg_ab:.1f}%, transit {100*avg_tr:.1f}%')
print(s.groupby('ptype').agg(n=('name', 'size'), tp24=('tp24', 'mean'), tp26=('tp26', 'mean'), swing=('tp_swing', 'mean'), ndp_ch=('ndp_swing', 'mean'),
                            flips=('flip', 'sum'), con26=('lead26', lambda q: (q == 'CON').sum())).round(1))
s[['name', 'region', 'ptype']].to_csv(B + 'core/meta/place_types.csv')

# ---- 8. vote transitions 2024 -> 2026 (lphom-style LP, homogeneity, votes only; 2024 rescaled to 2026 totals)
from scipy.optimize import linprog
P24 = ['CON', 'NDP', 'GRN', 'OTH']; P26 = ['CON', 'NDP', 'GRN', 'CENTRE', 'ONEBC', 'OTH']
r24['pc'] = r24.party.where(r24.party.isin(['CON', 'NDP', 'GRN']), 'OTH')
X = r24.pivot_table(index='ed_code', columns='pc', values='votes', aggfunc='sum').reindex(columns=P24).fillna(0)
Y = live.pivot_table(index='district_code', columns='party_code', values='votes', aggfunc='sum').reindex(columns=P26).fillna(0)
X = X.loc[Y.index]; X = X.mul(Y.sum(axis=1) / X.sum(axis=1), axis=0)
K, J, N = len(P24), len(P26), len(X)
nv = K * J + 2 * N * J
c = np.r_[np.zeros(K * J), np.ones(2 * N * J)]
Aeq, beq = [], []
for i in range(N):
    for j in range(J):
        row = np.zeros(nv)
        for k in range(K): row[k * J + j] = X.values[i, k]
        row[K * J + i * J + j] = 1; row[K * J + N * J + i * J + j] = -1
        Aeq.append(row); beq.append(Y.values[i, j])
for k in range(K):
    row = np.zeros(nv); row[k * J:(k + 1) * J] = 1; Aeq.append(row); beq.append(1)
res = linprog(c, A_eq=np.array(Aeq), b_eq=np.array(beq), bounds=[(0, None)] * nv, method='highs')
T = pd.DataFrame(res.x[:K * J].reshape(K, J), index=['from ' + p for p in P24], columns=P26)
print('\nestimated transitions, share of each 2024 party\'s voters by 2026 choice (votes only, homogeneity):'); print((100 * T).round(1))
print('fit: share of 2026 votes unexplained', round(100 * res.fun / 2 / Y.values.sum(), 1), '%')
(100 * T).round(1).to_csv(B + 'core/meta/transitions_2024_2026.csv')
