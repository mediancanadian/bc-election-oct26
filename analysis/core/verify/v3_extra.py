"""Part 3: sensitivity checks (quartile tie handling, PCN exclusion, federal grouping, model variants)."""
import pandas as pd, numpy as np
B='analysis/'; OUT=B+'core/verify/'
X=pd.read_csv(OUT+'ridings_with_census.csv',index_col=0)
f=pd.read_csv(B+'federal25/fed2025_on_ed2023.csv').set_index('ed_code')
print('PCN', X.loc['PCN',['CON24','NDP24','CON26','NDP26','tp24','tp26','swing']].to_dict())
for col in ['pct_indigenous','pct_immigrants','median_age','hh_income_median']:
    q=pd.qcut(X[col].rank(method='first'),4,labels=False)
    print(col,'rank-split lo/hi swing',round(X[q==0].swing.mean(),2),round(X[q==3].swing.mean(),2), (q==0).sum(),(q==3).sum())
    Y=X.drop('PCN'); q=pd.qcut(Y[col],4,labels=False)
    print(col,'excl PCN',round(Y[q==0].swing.mean(),2),round(Y[q==3].swing.mean(),2), round(Y[col].corr(Y.swing),3))
def ols(y,Xm):
    Xm=np.column_stack([np.ones(len(y)),Xm]); b,*_=np.linalg.lstsq(Xm,y,rcond=None)
    e=y-Xm@b; s2=e@e/(len(y)-Xm.shape[1]); se=np.sqrt(np.diag(s2*np.linalg.inv(Xm.T@Xm))); return b[1:],(b/se)[1:]
z=lambda s:(s-s.mean())/s.std()
base=['hh_income_median','pct_immigrants','pct_hh_renter','median_age','pct_bachelor_plus_25_64']
for lab,sub in [('all',X),('excl PCN',X.drop('PCN'))]:
    rd=pd.get_dummies(sub.region,drop_first=True).astype(float).values
    b,t=ols(sub.swing.values,np.column_stack([z(sub[c]).values for c in base]+[rd])); print(lab,'income b',round(b[0],2),'t',round(t[0],2))
    for extra in ['pct_vm_south_asian','pct_vm_total','pct_vm_chinese','pct_men_plus']:
        b,t=ols(sub.swing.values,np.column_stack([z(sub[c]).values for c in base+[extra]]+[rd])); print('  +',extra,'t',round(t[-1-rd.shape[1]+0],2) if False else round(t[len(base)],2),'income t',round(t[0],2))
# same field 56
same=pd.read_csv(OUT+'ridings_with_census.csv',index_col=0)
import itertools
d=pd.read_csv(B+'results24/out/districts_2024.csv')
# federal grouping alternatives
X['fedLC']=np.where(f.LPC_share_pct>f.CPC_share_pct,'LPC>CPC','CPC>=LPC')
for g,x in X.groupby('fedLC'):
    print(g,len(x),'dNDP',round(x.dNDP.mean(),1),'dCON',round(x.dCON.mean(),1),'swing',round(x.swing.mean(),1),'CON lead',(x.lead26=='CON').sum(),'NDP lead',(x.lead26=='NDP').sum(),'flips',(x.win24!=x.lead26).sum())
print(X[f.fed_winner.isin(['NDP','GPC'])][['name','lead26']].assign(fw=f.fed_winner).to_string())
# same-field (56) full-model checks
d24=pd.read_csv(B+'results24/out/districts_2024.csv')
c=pd.read_csv(B+'live/raw/snapshots/20261025T115814Z/GE-2026-10-24_Candidate.csv',encoding='utf-8-sig'); c.columns=['ed','n','name','aff','v','pc','b','d','t','a','f','s']
c=c[c.name.str.strip()!='Rejected Ballots']; c['aff']=c.aff.fillna('').str.strip()
pm={'Conservative Party':'CON','BC NDP':'NDP','BC Green Party':'GRN'}
f24=d24.groupby('ed_code').party.apply(lambda s:frozenset(x for x in s if x in('CON','NDP','GRN')))
f26=c.groupby('ed').aff.apply(lambda s:frozenset(pm[a] for a in s if a in pm))
same=(f24==f26.reindex(f24.index))&(X.ind24<5)
S=X[same.reindex(X.index)]
print('same-field n',len(S),'PCN in?', 'PCN' in S.index)
rd=pd.get_dummies(S.region,drop_first=True).astype(float).values
b,t=ols(S.swing.values,np.column_stack([z(S[c]).values for c in base+['pct_vm_south_asian']]+[rd])); print('same-field full+SA: SA t',round(t[len(base)],2),'income t',round(t[0],2))
b,t=ols(S.swing.values,np.column_stack([z(S[c]).values for c in base]+[rd])); print('same-field full: income b',round(b[0],2),'t',round(t[0],2))
