import re,sys,html
from html.parser import HTMLParser
src=sys.argv[1]
h=open(src,encoding='utf8').read()
i=h.find('id="Opinion_polling"'); j=h.find('id="Notes"')
seg=h[i:j]
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.tables=[]; s.row=None; s.cell=None; s.depth=0; s.links=[]
    def handle_starttag(s,t,a):
        a=dict(a)
        if t=='table': s.tables.append([])
        elif t=='tr' and s.tables: s.row=[]
        elif t in('td','th') and s.row is not None: s.cell=[]; s.clinks=[]
        elif t=='a' and s.cell is not None and a.get('href','').startswith('http'): s.clinks.append(a['href'])
        elif t=='br' and s.cell is not None: s.cell.append(' ')
        elif t in('sup','style') : s.depth+=1
    def handle_endtag(s,t):
        if t in('sup','style'): s.depth-=1
        elif t in('td','th') and s.cell is not None:
            s.row.append((' '.join(''.join(s.cell).split()), s.clinks)); s.cell=None
        elif t=='tr' and s.row is not None:
            s.tables[-1].append(s.row); s.row=None
    def handle_data(s,d):
        if s.cell is not None and s.depth==0: s.cell.append(d)
p=P(); p.feed(seg)
for ti,t in enumerate(p.tables):
    print('=== TABLE',ti,len(t))
    for r in t:
        print(' | '.join(c[0] for c in r), ' || ', ' '.join(l for c in r for l in c[1]))
