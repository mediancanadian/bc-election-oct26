# Download each pollster release listed in the Wikipedia index; record manifest.
import json,subprocess,re,os,datetime,hashlib,sys
rows=json.load(open('raw/wikipedia/wiki_rows.json'))
man=json.load(open('manifest.json')) if os.path.exists('manifest.json') else {'downloads':[]}
done={d['url'] for d in man['downloads'] if d.get('http')=='200'}
def slug(s): return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
for r in rows:
    c=r['cells']
    if len(c)<10 or c[0] in('Polling firm',) or 'election' in c[0]: continue
    p=slug(c[0])
    for ref in r['refs']:
        for u in ref['urls'][:1]:
            if u in done: continue
            os.makedirs(f'raw/{p}',exist_ok=True)
            base=slug(u.split('?')[0].rstrip('/').split('/')[-1])[-80:] or 'index'
            ext='.pdf' if '.pdf' in u.lower() else '.html'
            if base.endswith('_pdf'): base=base[:-4]
            fn=f'raw/{p}/{base}{ext}'
            res=subprocess.run(['curl','-sS','-L','--max-time','60','-A','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36','-o',fn,'-w','%{http_code}',u],capture_output=True,text=True)
            code=res.stdout.strip()
            sz=os.path.getsize(fn) if os.path.exists(fn) else 0
            man['downloads'].append({'pollster':c[0],'dates':c[2],'url':u,'file':fn,'http':code,'bytes':sz,'accessed_utc':datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),'err':res.stderr.strip()[:200]})
            print(code,sz,fn,res.stderr.strip()[:100])
            done.add(u)
json.dump(man,open('manifest.json','w'),indent=1)
