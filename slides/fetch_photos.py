"""Download the slide photos (Wikimedia Commons, free licences) into slides/photos/.

The photos, their authors, licences and source pages are listed in photos_used.json and photos_new.json and in NOTICE.
Files already present are kept.
"""
import json, os, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))
UA = 'TheMedianCanadianSlides/1.0 (https://mediancanadian.ca/)'
P = json.load(open(os.path.join(HERE, 'photos_used.json'), encoding='utf-8'))
P.update(json.load(open(os.path.join(HERE, 'photos_new.json'), encoding='utf-8')))
os.makedirs(os.path.join(HERE, 'photos'), exist_ok=True)
for name, p in P.items():
    f = os.path.join(HERE, 'photos', f'{name}.jpg')
    if os.path.exists(f) and os.path.getsize(f) > 100000:
        continue
    url = p.get('url') or p.get('thumbnail_url')
    r = subprocess.run(['curl', '-sSfL', '-A', UA, '-o', f, url], capture_output=True, text=True)
    print(name, 'ok' if r.returncode == 0 else r.stderr[:80], flush=True)
    time.sleep(5)
