"""Independent verification, part 1: result, history, flips, regions, incumbents,
new parties, leaders, close races, turnout, polls. Run: python3 -I v1_core.py"""
import pandas as pd, numpy as np, json, re, unicodedata
B = 'analysis/'
S = B + 'live/raw/snapshots/20261025T115814Z/'
OUT = B + 'core/verify/'

def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z]', '', s)

# ---------- 2026 ----------
c = pd.read_csv(S + 'GE-2026-10-24_Candidate.csv', encoding='utf-8-sig')
c.columns = ['ed', 'ed_name', 'name', 'aff', 'votes', 'pct', 'boxes', 'date', 'time', 'adv', 'fin', 'status']
rej = c[c.name.str.strip() == 'Rejected Ballots'].copy()
c = c[c.name.str.strip() != 'Rejected Ballots'].copy()
pmap = {'Conservative Party': 'CON', 'BC NDP': 'NDP', 'BC Green Party': 'GRN', 'CentreBC': 'CENTRE', 'OneBC': 'ONEBC'}
c['aff'] = c.aff.fillna('').str.strip()
c['p'] = c.aff.map(pmap).fillna('OTH')
c['votes'] = c.votes.astype(int)
print('2026 candidates', len(c), 'ridings', c.ed.nunique())
tot = c.groupby('p').votes.sum(); T = tot.sum()
print('2026 total valid', T); print((tot / T * 100).round(2))
c = c.sort_values(['ed', 'votes'], ascending=[True, False])
c['rank'] = c.groupby('ed').votes.rank(ascending=False, method='first')
dv = c.groupby('ed').votes.sum().rename('tv')
c = c.join(dv, on='ed'); c['sh'] = c.votes / c.tv * 100
lead = c[c['rank'] == 1].set_index('ed'); sec = c[c['rank'] == 2].set_index('ed')
lead = lead.assign(margin=lead.votes - sec.votes, mpts=lead.sh - sec.sh, second=sec.p, second_name=sec.name)
seats26 = lead.p.value_counts(); print('leading', seats26.to_dict())
print('votes per riding led', (tot[seats26.index] / seats26).round(0).to_dict())
print('two-party CON share 2026', round(tot.CON / (tot.CON + tot.NDP) * 100, 2))
# boxes
bx = c.groupby('ed').boxes.first().str.extract(r'(\d+) of (\d+)').astype(int)
print('boxes', bx[0].sum(), 'of', bx[1].sum())
adv = c.groupby('ed').adv.first().str.extract(r'(\d+) of (\d+)').astype(int)
print('adv boxes', adv[0].sum(), 'of', adv[1].sum())
inc = bx[bx[0] < bx[1]].copy(); inc['left'] = inc[1] - inc[0]
inc = inc.join(lead[['p', 'margin', 'mpts']])
print('incomplete ridings\n', inc)
# party file cross-check
pf = pd.read_csv(S + 'GE-2026-10-24_Party.csv', encoding='utf-8-sig')
pf.columns = [x.strip() for x in pf.columns]
print('party file sums', pf[['GP', 'NDP', 'CP', 'OTHER', 'Total Valid Votes', 'Rejected Ballots', 'Total Votes Considered']].sum().to_dict())

# ---------- 2024 ----------
d = pd.read_csv(B + 'results24/out/districts_2024.csv')
s24 = pd.read_csv(B + 'results24/out/districts_2024_summary.csv').set_index('ed_code')
t24 = d.groupby('party').votes.sum(); T24 = t24.sum()
sh24 = (t24 / T24 * 100).round(2); print('2024 shares', sh24.to_dict())
print('2024 other share (not CON/NDP/GRN)', round(100 - sh24.CON - sh24.NDP - sh24.GRN, 2))
print('2024 seats', s24.winner_party.value_counts().to_dict())
print('2024 two-party CON', round(t24.CON / (t24.CON + t24.NDP) * 100, 2))

# ---------- History ----------
h = pd.read_csv(B + 'history/province_series.csv')
fams = ['CON', 'SC', 'COAL', 'LIB', 'BCLIB', 'LEFT', 'GRN', 'REF']
h['maxshare'] = h[['share_' + f for f in fams]].max(axis=1)
h['maxseats'] = h[['seats_' + f for f in fams]].max(axis=1)
print(h[h.year >= 1996][['year', 'seats_in_house', 'maxshare', 'maxseats', 'share_BCLIB', 'seats_BCLIB', 'share_LEFT', 'share_CON']])
print('years with any party share >= 48.05:', h[h.maxshare >= 48.05].year.tolist())
print('years with any party seats >= 64:', h[h.maxseats >= 64].year.tolist())
print('CON-family share by year >= 43:', h[h.share_CON >= 43][['year', 'share_CON']].values.tolist())
print('LEFT share < 37.38:', h[(h.share_LEFT < 37.38) & (h.year >= 1963)][['year', 'share_LEFT']].values.tolist())
det = pd.read_csv(B + 'history/province_party_detail.csv')
print(det[(det.iloc[:, 0] == 1928)].iloc[:, 2:8])

# ---------- Regions ----------
r = pd.read_csv(B + 'geo/out/ed2023_regions.csv').set_index('ed_code')
isl = ['Cowichan Valley', 'Nanaimo', 'Comox Valley', 'Strathcona', 'Mount Waddington', 'Alberni-Clayoquot', 'qathet']
def reg(row):
    rd = row.regional_district
    if rd.startswith('Metro Vancouver') or 'Maple Ridge' in row.ed_name: return 'Metro Vancouver'
    if rd.startswith('Capital'): return 'Capital Region'
    if any(k in rd for k in isl): return 'Rest of Vancouver Island'
    if rd.startswith('Fraser Valley'): return 'Fraser Valley'
    if any(k in rd for k in ['Central Okanagan', 'North Okanagan', 'Okanagan-Similkameen']): return 'Okanagan'
    return 'Interior and North'
r['region'] = r.apply(reg, axis=1)
print(r.region.value_counts().to_dict())

# party votes wide
w26 = c.pivot_table(index='ed', columns='p', values='votes', aggfunc='sum', fill_value=0)
d['p'] = d.party.where(d.party.isin(['CON', 'NDP', 'GRN']), 'OTH')
w24 = d.pivot_table(index='ed_code', columns='p', values='votes', aggfunc='sum', fill_value=0)
W = pd.DataFrame(index=r.index)
for p in ['CON', 'NDP', 'GRN']:
    W[p + '24'] = w24[p]; W[p + '26'] = w26[p]
W['T24'] = w24.sum(axis=1); W['T26'] = w26.sum(axis=1)
W['win24'] = s24.winner_party; W['lead26'] = lead.p; W['region'] = r.region; W['name'] = r.ed_name
W['tp24'] = W.CON24 / (W.CON24 + W.NDP24) * 100; W['tp26'] = W.CON26 / (W.CON26 + W.NDP26) * 100
W['swing'] = W.tp26 - W.tp24
rows = []
for g, x in W.groupby('region'):
    rows.append([g, len(x)] + [round(x[p + y].sum() / x['T' + y].sum() * 100, 1) for p in ['CON', 'NDP', 'GRN'] for y in ['24', '26']]
                + [(x.win24 == 'CON').sum(), (x.lead26 == 'CON').sum(), (x.win24 == 'NDP').sum(), (x.lead26 == 'NDP').sum(),
                   round(x.swing.mean(), 1), round(x.swing.min(), 1), round(x.swing.max(), 1), (x.swing > 0).sum(),
                   round((x.CON26.sum() / (x.CON26.sum() + x.NDP26.sum()) - x.CON24.sum() / (x.CON24.sum() + x.NDP24.sum())) * 100, 1)])
reg_t = pd.DataFrame(rows, columns=['region', 'n', 'CON24', 'CON26', 'NDP24', 'NDP26', 'GRN24', 'GRN26', 'CONs24', 'CONs26', 'NDPs24', 'NDPs26', 'swing_mean', 'swing_min', 'swing_max', 'n_toward_CON', 'swing_pooled'])
print(reg_t.to_string())
# Green running counts per region
grn_run = c[c.p == 'GRN'].groupby('ed').size(); W['grn26_ran'] = W.index.isin(grn_run.index)
W['grn24_ran'] = W.index.isin(d[d.party == 'GRN'].ed_code)
print('Green ran by region 2024/2026', W.groupby('region')[['grn24_ran', 'grn26_ran']].sum().to_dict())
W.to_csv(OUT + 'ridings_wide.csv')

# ---------- Flips ----------
fl = W[W.win24 != W.lead26][['name', 'region', 'win24', 'lead26']]
print('flips', len(fl)); print(fl.sort_values(['win24', 'region']).to_string())

# ---------- Incumbents ----------
k = pd.read_csv(B + 'live/candidates_2026.csv')
k['key'] = k.ed_code + k.candidate.map(norm)
c['key'] = c.ed + c.name.map(norm)
lk = set(lead.reset_index().ed + lead.name.map(norm).values)
ki = k[k.incumbent == 'Y'].copy()
ki['matched'] = ki.key.isin(c.key)
ki['leading'] = ki.key.isin(lk)
print('incumbents', len(ki), 'unmatched', (~ki.matched).sum(), ki[~ki.matched][['ed_code', 'candidate']].values.tolist())
tr = ki[~ki.leading]
print('incumbents trailing', len(tr)); print(tr[['ed_code', 'candidate', 'affiliation', 'incumbent_same_district', 'mla_lims_affiliation_at_dissolution']].to_string())
print(tr.affiliation.value_counts().to_dict())

# ---------- New parties ----------
for p in ['CENTRE', 'ONEBC']:
    x = c[c.p == p]
    eds = x.ed.unique()
    share_where = x.votes.sum() / dv[eds].sum() * 100
    print(p, 'ridings', len(eds), 'votes', x.votes.sum(), 'share where ran', round(share_where, 2))
    print(x.sort_values('sh', ascending=False)[['ed_name', 'name', 'sh', 'rank']].head(4).round(2).to_string())
    bigger = x[(x.votes > x.ed.map(lead.margin)) & (x['rank'] > 2)]
    print(' vote > margin', len(bigger), bigger.ed_name.tolist())
for nm in ['Sturko', 'Brodie', 'Eby', 'Doerkson', 'Lowan', 'Kealy']:
    x = c[c.name.str.contains(nm)]
    for _, rr in x.iterrows():
        print(nm, rr.ed_name, rr.aff, round(rr.sh, 2), int(rr['rank']), 'lead margin', int(lead.loc[rr.ed, 'margin']), round(lead.loc[rr.ed, 'mpts'], 2))
print(c[c.ed == c[c.name.str.contains('Eby')].ed.iloc[0]][['name', 'p', 'votes', 'sh']].round(2))

# ---------- Close races ----------
cl = lead.sort_values('margin')[['ed_name', 'p', 'second', 'margin', 'mpts']]
print(cl.head(12).round(2).to_string())
print('under 1pt', (lead.mpts < 1).sum(), 'under 5pt', (lead.mpts < 5).sum(), '2024 under 5', (s24.margin_pts_exact < 5).sum())

# ---------- Federal ----------
f = pd.read_csv(B + 'federal25/fed2025_on_ed2023.csv').set_index('ed_code')
W['fed'] = f.fed_winner; W['LPC'] = f.LPC_share_pct
W['dNDP'] = W.NDP26 / W.T26 * 100 - W.NDP24 / W.T24 * 100
W['dCON'] = W.CON26 / W.T26 * 100 - W.CON24 / W.T24 * 100
print(W.fed.value_counts().to_dict())
for g, x in W.groupby('fed'):
    print(g, len(x), 'dNDP', round(x.dNDP.mean(), 1), 'dCON', round(x.dCON.mean(), 1), 'swing', round(x.swing.mean(), 1),
          'CON lead', (x.lead26 == 'CON').sum(), 'NDP lead', (x.lead26 == 'NDP').sum(), 'other', ((x.lead26 != 'CON') & (x.lead26 != 'NDP')).sum(),
          'flips', (x.win24 != x.lead26).sum(),
          'pooled dNDP', round(x.NDP26.sum() / x.T26.sum() * 100 - x.NDP24.sum() / x.T24.sum() * 100, 1))
print('r(LPC share, dNDP)', round(W.LPC.corr(W.dNDP), 3))

# ---------- Polls vs count ----------
pa = json.load(open(B + 'model/out/poll_average.json'))
for p in ['CON', 'NDP', 'GRN']:
    print('poll', p, pa['province'][p], 'count', round(tot[p] / T * 100, 2), 'diff', round(tot[p] / T * 100 - pa['province'][p], 2))
for p in ['CENTRE', 'ONEBC']:
    print('poll', p, pa['province'][p], 'count', round(tot[p] / T * 100, 2))
mv = W[W.region == 'Metro Vancouver']
print('Metro count', {p: round(mv[p + '26'].sum() / mv.T26.sum() * 100, 1) for p in ['CON', 'NDP', 'GRN']}, 'polled', {p: pa['regional']['Metro Vancouver'][p]['avg'] for p in ['CON', 'NDP', 'GRN']})
vi = W[W.region.isin(['Capital Region', 'Rest of Vancouver Island'])]
vi_true = vi[~vi.index.isin(r[r.regional_district.str.startswith('qathet')].index)]
for lab, x in [('Island incl qathet', vi), ('Island excl qathet', vi_true), ('Capital only', W[W.region == 'Capital Region'])]:
    print(lab, len(x), {p: round(x[p + '26'].sum() / x.T26.sum() * 100, 1) for p in ['CON', 'NDP', 'GRN']}, 'polled(Island cols)', {p: pa['regional']['Capital Region'][p]['avg'] for p in ['CON', 'NDP', 'GRN']})
m = json.load(open(B + 'model/model_frozen.json'))
print('frozen', m['frozen_pacific'], m['seats'])
pj = pd.read_csv(B + 'model/out/districts_projection.csv').set_index('ed_code')
for v in ['uni', 'prop']:
    print(v, 'right', (pj[v + '_winner'] == lead.p).sum())
for v in ['uniform', 'proportional']:
    tu = m['tossups'][v]
    print(v, 'tossups', len(tu), lead.loc[tu].p.value_counts().to_dict())

# ---------- Turnout ----------
a = pd.read_csv(B + 'live/advance_turnout_2026_vs_2024.csv').set_index('ed_code')
reg26 = a.registered_2026_oct14
pfx = pf.set_index('Electoral District Code')
bal26 = pfx['Total Votes Considered']
val26 = pfx['Total Valid Votes']
print('2026 ballots considered', bal26.sum(), 'valid', val26.sum(), 'registered', reg26.sum(), round(bal26.sum() / reg26.sum() * 100, 2))
g = d.groupby('ed_code')[['votes_adv', 'votes_adv_ood', 'votes_final', 'votes_final_ood', 'votes_special', 'votes_deo', 'votes_mail', 'votes_atv']].sum()
reg24 = s24.registered_voters
print('2024 registered', reg24.sum())
v_a = g.votes_adv + g.votes_final
v_b = g.votes_adv + g.votes_adv_ood + g.votes_final + g.votes_deo + g.votes_special
print('2024 adv+final valid', v_a.sum(), round(v_a.sum() / reg24.sum() * 100, 2))
print('2024 adv+adv_ood+final+deo+special valid', v_b.sum(), round(v_b.sum() / reg24.sum() * 100, 2))
print('2024 all valid', g.sum().sum(), 'ballots considered', s24.ballots_considered.sum())
for lab, v24 in [('A', v_a), ('B', v_b)]:
    t24p = v24 / reg24 * 100; t26p = val26 / reg26 * 100
    dt = (t26p - t24p)
    W['dturn' + lab] = dt
    print(lab, 'down in', (dt < 0).sum(), 'median', round(dt.median(), 2), W.groupby('region')['dturn' + lab].median().round(1).to_dict(),
          'r(dturn, swing)', round(dt.corr(W.swing), 3))
    # also using ballots considered 2026
    dt2 = bal26 / reg26 * 100 - t24p
    print(lab, '(2026 ballots incl rejected) down in', (dt2 < 0).sum(), 'median', round(dt2.median(), 2), W.assign(x=dt2).groupby('region').x.median().round(1).to_dict(), round(dt2.corr(W.swing), 3))
W.to_csv(OUT + 'ridings_wide.csv')
lead.to_csv(OUT + 'leaders_2026.csv')
