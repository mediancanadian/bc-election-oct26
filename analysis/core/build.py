import pandas as pd, numpy as np
B='analysis/'
live=pd.read_csv(B+'live/latest.csv'); dist=pd.read_csv(B+'live/latest_districts.csv')
v26=live.pivot_table(index='district_code',columns='party_code',values='votes',aggfunc='sum').fillna(0)
t26=v26.sum(1); s26=v26.div(t26,axis=0)*100
r24=pd.read_csv(B+'results24/out/districts_2024.csv')
v24=r24.pivot_table(index='ed_code',columns='party',values='votes',aggfunc='sum').fillna(0)
s24=v24.div(v24.sum(1),axis=0)*100
summ24=pd.read_csv(B+'results24/out/districts_2024_summary.csv').set_index('ed_code')
c=pd.read_csv(B+'census/out/ed2023_profile.csv').set_index('ed_code')
fed=pd.read_csv(B+'federal25/fed2025_on_ed2023.csv').set_index('ed_code')
reg=pd.read_csv(B+'geo/out/ed2023_regions.csv'); print(reg.columns.tolist())
x=pd.DataFrame({'name':dist.set_index('district_code').district_name,
  'con26':s26.CON,'ndp26':s26.NDP,'grn26':s26.GRN,'votes26':t26,
  'con24':s24['CON'],'ndp24':s24['NDP'],'grn24':s24.get('GRN',0),
  'win24':summ24.winner_party,'reg24':summ24.registered_voters,'turn24':summ24.turnout_pct,
  'lead26':dist.set_index('district_code').leader,'margin26':dist.set_index('district_code').margin_pts,
  'cpc25':fed.CPC_share_pct,'lpc25':fed.LPC_share_pct})
x['con_swing']=x.con26-x.con24; x['ndp_swing']=x.ndp26-x.ndp24
x=x.join(c.drop(columns=['ed_name']))
x.to_csv(B+'core/out/joined.csv')
print(x[['con24','con26','con_swing','ndp_swing']].describe().round(1))
print('unweighted mean swing', x.con_swing.mean().round(2))
print(s24.columns.tolist())
