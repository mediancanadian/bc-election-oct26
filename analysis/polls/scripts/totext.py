import sys,os,subprocess,re,html as H
for root,_,fs in os.walk('raw'):
    if root.startswith('raw/wikipedia'): continue
    for f in fs:
        p=os.path.join(root,f)
        if f.endswith('.txt'): continue
        out=p+'.txt'
        head=open(p,'rb').read(5)
        if head.startswith(b'%PDF'):
            subprocess.run(['pdftotext','-layout',p,out])
        else:
            h=open(p,encoding='utf8',errors='replace').read()
            h=re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>','',h,flags=re.S|re.I)
            h=re.sub(r'<(br|p|tr|li|h\d|div)[^>]*>','\n',h,flags=re.I)
            h=re.sub(r'<t[dh][^>]*>',' | ',h,flags=re.I)
            t=H.unescape(re.sub('<[^>]+>','',h))
            t='\n'.join(' '.join(l.split()) for l in t.splitlines())
            t=re.sub(r'\n{3,}','\n\n',t)
            open(out,'w').write(t)
        print(os.path.getsize(out),out)
