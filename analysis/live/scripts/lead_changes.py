import pandas as pd, glob, sys
snaps=sorted(glob.glob('analysis/live/raw/snapshots/*/GE-*_Candidate.csv'))[-2:]
def leads(p):
    d=pd.read_csv(p); d=d[d["Candidate's Ballot Name"]!='Rejected Ballots']
    g=d.sort_values('Total Valid Votes').groupby('Electoral District Name')
    top=g.tail(1).set_index('Electoral District Name'); sec=g.nth(-2).set_index('Electoral District Name') if False else None
    return top.Affiliation.to_dict()
a,b=leads(snaps[0]),leads(snaps[1])
print({k:(a[k],b[k]) for k in b if a.get(k)!=b[k]})
