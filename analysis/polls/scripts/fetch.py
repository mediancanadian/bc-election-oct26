# usage: python3 -I scripts/fetch.py <pollster_dir> <url> [outname]
import sys,subprocess,os,json,datetime,re
d,u=sys.argv[1],sys.argv[2]
os.makedirs(f'raw/{d}',exist_ok=True)
name=sys.argv[3] if len(sys.argv)>3 else re.sub(r'[^A-Za-z0-9._-]+','_',u.split('?')[0].rstrip('/').split('/')[-1])[-90:]
fn=f'raw/{d}/{name}'
r=subprocess.run(['curl','-sS','-L','--max-time','90','-A','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36','-o',fn,'-w','%{http_code}',u],capture_output=True,text=True)
m=json.load(open('manifest.json'))
m['downloads'].append({'pollster':d,'url':u,'file':fn,'http':r.stdout,'bytes':os.path.getsize(fn) if os.path.exists(fn) else 0,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'err':r.stderr.strip()[:200]})
json.dump(m,open('manifest.json','w'),indent=1)
print(r.stdout,fn,r.stderr.strip()[:150])
