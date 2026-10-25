# Print PDF links found in pollster HTML release pages (pollster-owned domains only)
import re,os,html,sys
own=('researchco.ca','leger360.com','angusreid.org','abacusdata.ca','pallas-data.ca','liaisonstrategies.ca','ipsos.com','mainstreetresearch.ca','website-files.com','innovativeresearch.ca','pollara.com','constantcontact.com','hubspotusercontent','604polling.ca','cardinalresearch.ca')
seen=set()
for root,_,fs in os.walk('raw'):
    if 'wikipedia' in root: continue
    for f in fs:
        if not f.endswith('.html'): continue
        h=open(os.path.join(root,f),encoding='utf8',errors='replace').read()
        for u in re.findall(r'href="([^"]+?\.pdf[^"]*)"',h,re.I):
            u=html.unescape(u)
            if any(o in u for o in own) and u not in seen:
                seen.add(u); print(root.split('/')[1]+'\t'+u)
