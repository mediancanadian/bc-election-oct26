import pandas as pd, numpy as np
B='analysis/'
x=pd.read_csv(B+'core/out/joined.csv',index_col=0)
reg=pd.read_csv(B+'model/out/regions.csv'); print(reg.columns.tolist()[:6])
x=x.join(reg.set_index(reg.columns[0])[[c for c in reg.columns if 'region' in c.lower()][:1]].rename(columns=lambda c:'region'))
# vote-weighted regional shares
live=pd.read_csv(B+'live/latest.csv'); r24=pd.read_csv(B+'results24/out/districts_2024.csv')
live['region']=live.district_code.map(x.region); r24['region']=r24.ed_code.map(x.region)
def sh(df,pc,code):
    t=df.groupby('region').votes.sum(); return (df[df[pc]==code].groupby('region').votes.sum()/t*100).round(1)
R=pd.DataFrame({'CON24':sh(r24,'party','CON'),'CON26':sh(live,'party_code','CON'),'NDP24':sh(r24,'party','NDP'),'NDP26':sh(live,'party_code','NDP'),
  'seats':x.groupby('region').size(),'CON_lead26':x[x.lead26=='CON'].groupby('region').size(),'CON_won24':x[x.win24=='CON'].groupby('region').size()})
print(R); R.to_csv(B+'core/out/regions.csv')
V={'Median household income':'hh_income_median','University degree (25-64)':'pct_bachelor_plus_25_64','Median age':'median_age',
 'Renters':'pct_hh_renter','Median home value':'median_dwelling_value','Visible minority':'pct_vm_total','South Asian':'pct_vm_south_asian',
 'Chinese':'pct_vm_chinese','Filipino':'pct_vm_filipino','Indigenous':'pct_indigenous','Immigrants':'pct_immigrants','Recent immigrants':'pct_recent_immigrants_2016_2021',
 'Punjabi at home':'pct_lang_home_punjabi_panjabi','Mandarin at home':'pct_lang_home_mandarin','Cantonese at home':'pct_lang_home_yue_cantonese',
 'Men':'pct_men_plus','No religion':'pct_rel_none_secular','Christian':'pct_rel_christian','Sikh':'pct_rel_sikh','Low income':'pct_low_income_lim_at',
 'Transit commute':'pct_commute_transit','Density':'density_per_km2'}
rows=[]
for k,v in V.items():
    if v not in x: print('missing',v); continue
    q=pd.qcut(x[v].rank(method='first'),4,labels=False)
    g=x.groupby(q)
    rows.append(dict(measure=k,low_q_value=round(x[v][q==0].median(),1),high_q_value=round(x[v][q==3].median(),1),
      con26_low=round(g.con26.mean()[0],1),con26_high=round(g.con26.mean()[3],1),
      swing_low=round(g.con_swing.mean()[0],1),swing_high=round(g.con_swing.mean()[3],1),
      r_con26=round(x[v].corr(x.con26),2),r_swing=round(x[v].corr(x.con_swing),2)))
T=pd.DataFrame(rows).sort_values('r_swing',key=abs,ascending=False); T.to_csv(B+'core/out/demographics.csv',index=False)
pd.set_option('display.width',250); print(T.to_string(index=False))
