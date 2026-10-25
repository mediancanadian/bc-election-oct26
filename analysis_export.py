"""Copy the analysis outputs the slides and site read into data/ (run after analysis/core/full.py)."""
import json, os, shutil, pandas as pd
ROOT = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(ROOT, 'analysis') + '/'; D = os.path.join(ROOT, 'data') + '/'
x = pd.read_csv(B + 'core/out/ridings_2026_joined.csv', index_col=0)
f = pd.read_csv(B + 'federal25/fed2025_on_ed2023.csv', index_col=0)
x['gpc25'] = f.GPC_share_pct
# fed_lead25 (Liberal or Conservative only, used inside the analysis) is left out: the published grouping is the party with the
# most federal votes among all four (lpc25, cpc25, ndp25, gpc25), which puts Vancouver-Strathcona with the NDP
x = x.drop(columns=['fed_lead25'])
x.to_csv(D + 'ridings.csv')
for f, t in (('province.csv', 'province.csv'), ('regions6.csv', 'regions.csv'), ('close_races.csv', 'close_races.csv')):
    shutil.copy(B + 'core/out/' + f, D + t)
pd.read_csv(B + 'model/out/polls_used.csv').to_csv(D + 'polls_used.csv', index=False)
h = pd.read_csv(B + 'history/province_series.csv')
sc = [c for c in h.columns if c.startswith('share_')]
out = pd.DataFrame({'year': h.year, 'share': h[sc].max(axis=1), 'party': h[sc].idxmax(axis=1).str[6:]})
# 1928: the Conservative Party itself had 53.30% (Electoral History of BC 1871-1986, p.159); 53.60 adds Independent Conservatives
out.loc[out.year == 1928, 'share'] = 53.30
out.to_csv(D + 'history.csv', index=False)
live = pd.read_csv(B + 'live/latest.csv')
snap = live.snapshot_utc.iloc[0]
dist = pd.read_csv(B + 'live/latest_districts.csv')
json.dump(dict(snapshot_utc=snap, boxes=int(dist.boxes_reported.sum()), boxes_total=int(dist.boxes_total.sum()),
               source_time=dist.source_time.iloc[0]), open(D + 'meta.json', 'w'), indent=1)
live.to_csv(D + 'candidates_2026_as_of_2026-10-25_0149_PT.csv', index=False)
print('exported', snap)
