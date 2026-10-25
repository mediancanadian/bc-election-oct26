import re,sys,json,html as H
h=open(sys.argv[1],encoding='utf8').read()
i=h.find('id="Opinion_polling"'); j=h.find('id="Notes"')
seg=h[i:j]
# references list
notes={}
for m in re.finditer(r'<li id="(cite_note-[^"]+)".*?</li>',h,re.S):
    urls=re.findall(r'class="external text" href="([^"]+)"',m.group(0))
    txt=re.sub('<[^>]+>','',m.group(0))
    notes[m.group(1)]=(urls,H.unescape(' '.join(txt.split()))[:250])
out=[]
for tr in re.findall(r'<tr.*?</tr>',seg,re.S):
    cells=re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',tr,re.S)
    if len(cells)<8: continue
    txt=[H.unescape(' '.join(re.sub(r'<sup.*?</sup>','',c,flags=re.S).replace('<br','\n<br').split())) for c in cells]
    txt=[re.sub('<[^>]+>','',t).strip() for t in txt]
    refs=re.findall(r'href="#(cite_note-[^"]+)"',tr)
    out.append({'cells':txt,'refs':[{'id':r,'urls':notes.get(r,([],''))[0],'text':notes.get(r,([],''))[1]} for r in refs]})
json.dump(out,open(sys.argv[2],'w'),indent=1,ensure_ascii=False)
for o in out:
    print(o['cells'][0],'|',o['cells'][2] if len(o['cells'])>2 else '','|',[ (u for u in r['urls']) and r['urls'] for r in o['refs']])
