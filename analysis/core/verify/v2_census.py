"""Independent verification, part 2: census quartiles, correlations, regressions,
same-field ridings, independent/Green distortion. Needs ridings_wide.csv from v1_core.py."""
import pandas as pd, numpy as np
B = 'analysis/'; OUT = B + 'core/verify/'
W = pd.read_csv(OUT + 'ridings_wide.csv', index_col=0)
cen = pd.read_csv(B + 'census/out/ed2023_profile.csv').set_index('ed_code')
d = pd.read_csv(B + 'results24/out/districts_2024.csv')
c = pd.read_csv(B + 'live/raw/snapshots/20261025T115814Z/GE-2026-10-24_Candidate.csv', encoding='utf-8-sig')
c.columns = ['ed', 'ed_name', 'name', 'aff', 'votes', 'pct', 'boxes', 'date', 'time', 'adv', 'fin', 'status']
c = c[c.name.str.strip() != 'Rejected Ballots']
c['aff'] = c.aff.fillna('').str.strip()

traits = {
    'income': 'hh_income_median', 'home value': 'median_dwelling_value', 'indigenous': 'pct_indigenous',
    'immigrants': 'pct_immigrants', 'univ 25-64': 'pct_bachelor_plus_25_64', 'univ 15+': 'pct_bachelor_plus_15plus',
    'vis min': 'pct_vm_total', 'south asian': 'pct_vm_south_asian', 'chinese': 'pct_vm_chinese',
    'renters': 'pct_hh_renter', 'median age': 'median_age', 'men+': 'pct_men_plus'}
X = W.join(cen[list(traits.values())])
print('2-party swing summary', X.swing.describe().round(2).to_dict())
rows = []
for k, col in traits.items():
    q = pd.qcut(X[col], 4, labels=False)
    lo, hi = X[q == 0], X[q == 3]
    rows.append([k, round(lo[col].mean(), 1), round(hi[col].mean(), 1), round(lo[col].median(), 1), round(hi[col].median(), 1),
                 round(lo.swing.mean(), 1), round(hi.swing.mean(), 1), round(X[col].corr(X.swing), 2), len(lo), len(hi)])
qt = pd.DataFrame(rows, columns=['trait', 'lo_mean', 'hi_mean', 'lo_med', 'hi_med', 'swing_lo', 'swing_hi', 'r', 'n_lo', 'n_hi'])
print(qt.to_string())

# Same-field definitions
p24 = d.groupby('ed_code').party.apply(lambda s: frozenset(s))
pm = {'Conservative Party': 'CON', 'BC NDP': 'NDP', 'BC Green Party': 'GRN'}
p26 = c.groupby('ed').aff.apply(lambda s: frozenset(pm.get(a, 'X') for a in s))
f24 = p24.apply(lambda s: frozenset(x for x in s if x in ('CON', 'NDP', 'GRN')))
f26 = p26.apply(lambda s: frozenset(x for x in s if x in ('CON', 'NDP', 'GRN')))
ind24 = d[d.party.isin(['IND', 'UNAF'])].groupby('ed_code').vote_share_pct.sum().reindex(W.index).fillna(0)
X['ind24'] = ind24
defs = {
    'same CON/NDP/GRN set': (f24 == f26.reindex(f24.index)),
    'same set and no 2024 IND/UNAF': (f24 == f26.reindex(f24.index)) & (ind24 == 0),
    'same set and 2024 IND/UNAF<5': (f24 == f26.reindex(f24.index)) & (ind24 < 5),
    'same set and 2024 IND/UNAF<10': (f24 == f26.reindex(f24.index)) & (ind24 < 10),
}
for k, m in defs.items():
    m = m.reindex(X.index).fillna(False).astype(bool)
    print(k, m.sum(), 'r income', round(X[m].hh_income_median.corr(X[m].swing), 3))
mv = X[X.region == 'Metro Vancouver']
print('r income in Metro', round(mv.hh_income_median.corr(mv.swing), 3), len(mv))

def ols(y, Xm):
    Xm = np.column_stack([np.ones(len(y)), Xm]); b, *_ = np.linalg.lstsq(Xm, y, rcond=None)
    e = y - Xm @ b; s2 = e @ e / (len(y) - Xm.shape[1]); se = np.sqrt(np.diag(s2 * np.linalg.inv(Xm.T @ Xm)))
    return b[1:], (b / se)[1:]
z = lambda s: (s - s.mean()) / s.std()
regd = pd.get_dummies(X.region, drop_first=True).astype(float).values
for edu in ['pct_bachelor_plus_25_64', 'pct_bachelor_plus_15plus']:
    cols = ['hh_income_median', 'pct_immigrants', 'pct_hh_renter', 'median_age', edu]
    b, t = ols(X.swing.values, np.column_stack([z(X[cc]).values for cc in cols] + [regd]))
    print('full model', edu, 'income b', round(b[0], 2), 't', round(t[0], 2), 'others t', np.round(t[1:5], 2))
    b, t = ols(X.swing.values, np.column_stack([z(X[cc]).values for cc in cols]))
    print(' no region', 'income b', round(b[0], 2), 't', round(t[0], 2))
same = defs['same CON/NDP/GRN set'].reindex(X.index).fillna(False).astype(bool)
for v in ['pct_immigrants', 'pct_vm_total', 'pct_vm_chinese', 'pct_bachelor_plus_25_64', 'pct_vm_south_asian', 'pct_men_plus']:
    for lab, sub in [('all', X), ('same-field', X[same])]:
        rd = pd.get_dummies(sub.region, drop_first=True).astype(float).values
        b, t = ols(sub.swing.values, np.column_stack([z(sub.hh_income_median).values, z(sub[v]).values]))
        b2, t2 = ols(sub.swing.values, np.column_stack([z(sub.hh_income_median).values, z(sub[v]).values, rd]))
        print(v, lab, len(sub), 'with income: t', round(t[1], 2), '| +region t', round(t2[1], 2))
# level and Green change
X['tp26'] = X.CON26 / (X.CON26 + X.NDP26) * 100
print('r renters vs 2026 two-party CON level', round(X.pct_hh_renter.corr(X.tp26), 3))
X['dGRN'] = X.GRN26 / X.T26 * 100 - X.GRN24 / X.T24 * 100
X['dCON'] = X.CON26 / X.T26 * 100 - X.CON24 / X.T24 * 100
X['dNDP'] = X.NDP26 / X.T26 * 100 - X.NDP24 / X.T24 * 100
for col in ['pct_bachelor_plus_25_64', 'pct_bachelor_plus_15plus', 'median_dwelling_value', 'hh_income_median']:
    print(col, 'r dGRN', round(X[col].corr(X.dGRN), 3), 'r dCON', round(X[col].corr(X.dCON), 3), 'r dNDP', round(X[col].corr(X.dNDP), 3))
both_grn = X.grn24_ran & X.grn26_ran
print('dGRN r univ, Green ran both', both_grn.sum(), round(X[both_grn].pct_bachelor_plus_25_64.corr(X[both_grn].dGRN), 3))
print('r men+ swing', round(X.pct_men_plus.corr(X.swing), 3))
# turnout links
for col in ['dturnA', 'dturnB']:
    print(col, 'r swing', round(X[col].corr(X.swing), 3), 'r dCON', round(X[col].corr(X.dCON), 3), 'r dNDP', round(X[col].corr(X.dNDP), 3))

# Independent / Green distortion of raw swings
X['rawCONch'] = X.dCON
big = X.reindex(X.rawCONch.abs().sort_values(ascending=False).index)[['name', 'win24', 'lead26', 'dCON', 'dNDP', 'swing', 'ind24', 'grn24_ran', 'grn26_ran']].head(15)
print(big.round(1).to_string())
print('ridings with 2024 IND/UNAF >= 5%:'); print(X[X.ind24 >= 5][['name', 'ind24', 'dCON', 'dNDP', 'swing', 'lead26']].round(1).to_string())
# Green entry/exit
ge = X[X.grn24_ran != X.grn26_ran][['name', 'region', 'grn24_ran', 'grn26_ran', 'GRN24', 'T24', 'GRN26', 'T26', 'dNDP', 'swing', 'win24', 'lead26']]
ge['g24'] = ge.GRN24 / ge.T24 * 100; ge['g26'] = ge.GRN26 / ge.T26 * 100
print('Green entry/exit ridings', len(ge)); print(ge[['name', 'region', 'g24', 'g26', 'dNDP', 'swing', 'win24', 'lead26']].round(1).to_string())
# flips where Green entry/exit or 2024 IND
fl = X[X.win24 != X.lead26]
print('flips with Green entry/exit:', fl[fl.grn24_ran != fl.grn26_ran].name.tolist())
print('flips with 2024 IND>=3:', fl[fl.ind24 >= 3][['name', 'ind24']].values.tolist())
X.to_csv(OUT + 'ridings_with_census.csv')
