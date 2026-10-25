"""Part 4: re-run the published regression specs (metro dummy) with my own data build."""
import pandas as pd, numpy as np
B='analysis/'; OUT=B+'core/verify/'
X=pd.read_csv(OUT+'ridings_with_census.csv',index_col=0)
X['metro']=(X.region=='Metro Vancouver').astype(float)
d24=pd.read_csv(B+'results24/out/districts_2024.csv')
c=pd.read_csv(B+'live/raw/snapshots/20261025T115814Z/GE-2026-10-24_Candidate.csv',encoding='utf-8-sig'); c.columns=['ed','n','name','aff','v','pc','b','d','t','a','f','s']
c=c[c.name.str.strip()!='Rejected Ballots']; c['aff']=c.aff.fillna('').str.strip()
pm={'Conservative Party':'CON','BC NDP':'NDP','BC Green Party':'GRN'}
f24=d24.groupby('ed_code').party.apply(lambda s:frozenset(x for x in s if x in('CON','NDP','GRN')))
f26=c.groupby('ed').aff.apply(lambda s:frozenset(pm[a] for a in s if a in pm))
same=((f24==f26.reindex(f24.index))&(X.ind24<5)).reindex(X.index)
def ols(df,cols):
    Z=(df[cols]-df[cols].mean())/df[cols].std(); M=np.column_stack([np.ones(len(df)),Z.values]); y=df.swing.values
    b,*_=np.linalg.lstsq(M,y,rcond=None); e=y-M@b; s2=e@e/(len(y)-M.shape[1]); se=np.sqrt(np.diag(s2*np.linalg.inv(M.T@M)))
    return pd.DataFrame({'b':b[1:],'t':b[1:]/se[1:]},index=cols).round(2)
s1=['hh_income_median','pct_immigrants','pct_hh_renter','median_age','pct_bachelor_plus_25_64','metro']
s2=['hh_income_median','pct_vm_south_asian','pct_vm_chinese','pct_hh_renter','median_age','metro']
for lab,df in [('all',X),('all excl PCN',X.drop('PCN')),('same-field',X[same])]:
    print(lab,len(df)); print(ols(df,s1).T.to_string()); print(ols(df,s2).T.to_string())
