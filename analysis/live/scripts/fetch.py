#!/usr/bin/env python3
"""Election-night snapshot of Elections BC preliminary (initial count) results, 2026 Provincial General Election.

Run with:  python3 -I analysis/live/scripts/fetch.py            (fetch + parse)
           python3 -I analysis/live/scripts/fetch.py --reparse <snapshot_dir>   (parse an existing snapshot)

Official sources only:
  * https://results.elections.bc.ca/  (entry point named in Elections BC's Oct 2026 news release; before results
    it 301-redirects to the static elections.bc.ca results page)
  * https://electionsbcenr.blob.core.windows.net/electionsbcenr/  (Elections BC ENR container; public listing via
    ?restype=container&comp=list. 2024 pages were Results_<n>_GE-2024-10-19_{Party,Candidate}.html; the 2026 pages are
    expected as Results_<n>_GE-2026-10-24_*.html, with a #tblReport table and a CSV download link.)
Generic user agent, no cookies, no personal data. Each URL is fetched at most once per 120 s (state in logs/).

Exit codes: 0 = results parsed, or no results posted yet (clear message); 2 = files found but nothing parseable; 1 = network error.
"""
import csv, datetime as dt, html, io, json, os, re, ssl, sys, time, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser

BASE = 'analysis/live'
RAW = os.path.join(BASE, 'raw', 'snapshots')
LOGS = os.path.join(BASE, 'logs')
UA = 'Mozilla/5.0 (compatible; research-bot)'
ENTRY = 'https://results.elections.bc.ca/'
CONTAINER = 'https://electionsbcenr.blob.core.windows.net/electionsbcenr/'
EVENT_TAGS = ('GE-2026-10-24', '2026-10-24', 'GE2026', 'PGE-2026', 'PGE2026')
OFFICIAL_HOSTS = ('elections.bc.ca', 'results.elections.bc.ca', 'www.elections.bc.ca', 'electionsbcenr.blob.core.windows.net')
MIN_INTERVAL = 120
STATE = os.path.join(LOGS, 'fetch_state.json')
DATA_EXT = ('.html', '.htm', '.aspx', '.csv', '.json', '.xml', '.txt')
STATIC_PAGE = 'elections.bc.ca/resources/results/provincial-election-results'


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def ssl_ctx():
    for p in (os.environ.get('SSL_CERT_FILE'), os.environ.get('REQUESTS_CA_BUNDLE'), '/root/.ccr/ca-bundle.crt'):
        if p and os.path.exists(p):
            return ssl.create_default_context(cafile=p)
    return ssl.create_default_context()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}


def save_state(st):
    os.makedirs(LOGS, exist_ok=True)
    json.dump(st, open(STATE, 'w'), indent=1)


def get(url, state, follow=True, timeout=45):
    """Polite GET. Returns (status, headers dict, bytes, final_url). Enforces MIN_INTERVAL per URL."""
    host = urllib.parse.urlparse(url).hostname or ''
    if not any(host == h or host.endswith('.' + h) for h in OFFICIAL_HOSTS):
        raise ValueError('refusing non-official host: ' + host)
    last = state.get(url, 0)
    wait = MIN_INTERVAL - (time.time() - last)
    if wait > 0:
        return None, {}, b'', url  # skipped: fetched too recently
    handlers = [urllib.request.HTTPSHandler(context=ssl_ctx())]
    if not follow:
        handlers.append(NoRedirect())
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*', 'Cache-Control': 'no-cache'})
    state[url] = time.time()
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read(), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read() if hasattr(e, 'read') else b'', url
    finally:
        time.sleep(1.5)


def list_container(state):
    names, marker = [], ''
    while True:
        url = CONTAINER + '?restype=container&comp=list' + (('&marker=' + urllib.parse.quote(marker)) if marker else '')
        st, h, body, _ = get(url, state)
        if st != 200:
            return None, body
        t = body.decode('utf-8', 'replace')
        for b in re.findall(r'<Blob>(.*?)</Blob>', t, re.S):
            n = re.search(r'<Name>(.*?)</Name>', b).group(1)
            lm = re.search(r'<Last-Modified>(.*?)</Last-Modified>', b)
            names.append((html.unescape(n), lm.group(1) if lm else ''))
        m = re.search(r'<NextMarker>([^<]+)</NextMarker>', t)
        if not m:
            return names, body
        marker = m.group(1)


def is_result_blob(name):
    low = name.lower()
    if not low.endswith(DATA_EXT):
        return False
    if any(t.lower() in low for t in EVENT_TAGS):
        return True
    return bool(re.match(r'(.*/)?results_\d+_', low)) and '2024' not in low and '2020' not in low


# ---------------------------------------------------------------- parsing
class Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.stack, self.title, self.heads, self._in, self._buf, self.links = [], [], '', [], None, '', []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'table':
            self.stack.append({'id': a.get('id', ''), 'rows': [], 'context': ' '.join(self.heads[-3:])})
        elif tag == 'tr' and self.stack:
            self.stack[-1]['rows'].append([])
        elif tag in ('td', 'th') and self.stack and self.stack[-1]['rows']:
            self._in, self._buf = tag, ''
        elif tag in ('title', 'h1', 'h2', 'h3', 'h4', 'caption'):
            self._in, self._buf = tag, ''

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self._in in ('td', 'th') and self.stack and self.stack[-1]['rows']:
            self.stack[-1]['rows'][-1].append(re.sub(r'\s+', ' ', self._buf).strip())
            self._in = None
        elif tag in ('title', 'h1', 'h2', 'h3', 'h4', 'caption') and self._in == tag:
            txt = re.sub(r'\s+', ' ', self._buf).strip()
            if tag == 'title':
                self.title = txt
            elif txt:
                self.heads.append(txt)
            self._in = None
        elif tag == 'table' and self.stack:
            self.tables.append(self.stack.pop())

    def handle_data(self, d):
        if self._in:
            self._buf += d


def num(s):
    if s is None:
        return None
    s = str(s).strip().replace(',', '').replace('%', '')
    try:
        return float(s) if '.' in s else int(s)
    except ValueError:
        return None


COLS = {
    'district': r'electoral district|^district|^ed name|^riding|edname',
    'ed_code': r'^ed code|^ed abbr|^code$',
    'candidate': r'candidate',
    'party': r'affiliation|^party',
    'votes': r'^votes|valid votes|^total votes|vote count|^count$',
    'share': r'% of|percent|^%$|popular vote|pop.? vote',
    'reported': r'reported|ballot box|voting places|polls',
    'elected': r'elected|status|result',
    'leading': r'lead',
    'turnout': r'who voted|turnout',
    'registered': r'registered',
}


def map_header(h):
    m = {}
    for i, c in enumerate(h):
        lc = c.lower().strip()
        for k, pat in COLS.items():
            if k not in m and re.search(pat, lc):
                if k == 'votes' and ('%' in lc or 'percent' in lc):
                    continue
                if k == 'party' and 'candidate' in lc:
                    continue
                m[k] = i
                break
    return m


def reported_pair(s):
    if not s:
        return None, None
    m = re.search(r'(\d[\d,]*)\s*(?:of|/|out of)\s*(\d[\d,]*)', s)
    if m:
        return num(m.group(1)), num(m.group(2))
    return num(s), None


def rows_from_table(rows, context):
    """Return list of candidate dicts if table looks like candidate results."""
    hdr_i = next((i for i, r in enumerate(rows[:5]) if r and any(re.search(COLS['candidate'], c.lower()) for c in r)), None)
    if hdr_i is None:
        return []
    m = map_header(rows[hdr_i])
    if 'candidate' not in m or 'votes' not in m:
        return []
    out, cur_d, cur_rep = [], None, (None, None)
    ctx_d = None
    mm = re.search(r'([A-Z][A-Za-z.\' ]+(?:-[A-Z][A-Za-z.\' ]+)*)', context or '')
    if mm:
        ctx_d = mm.group(1).strip()
    for r in rows[hdr_i + 1:]:
        if not r or len(r) <= max(m['candidate'], m['votes']):
            continue
        g = lambda k: r[m[k]] if k in m and m[k] < len(r) else ''
        d = g('district') or cur_d
        if g('district'):
            cur_d = g('district')
        if g('reported'):
            cur_rep = reported_pair(g('reported'))
        cand = g('candidate')
        if not cand or re.match(r'^(total|totals|sub-?total)', cand.lower()) or (d or '').lower().startswith('total'):
            continue
        v = num(g('votes'))
        if v is None:
            continue
        out.append({'ed_code': g('ed_code'), 'district': d or ctx_d or '', 'candidate': cand, 'party': g('party'),
                    'votes': v, 'share_src': num(g('share')), 'places_reported': cur_rep[0], 'places_total': cur_rep[1],
                    'elected_src': g('elected')})
    return out


def parse_csv_bytes(b):
    t = b.decode('utf-8-sig', 'replace') if b[:3] == b'\xef\xbb\xbf' else b.decode('cp1252', 'replace')
    rows = list(csv.reader(io.StringIO(t)))
    return rows_from_table(rows, '')


def parse_snapshot(snapdir):
    cand, meta = [], {'turnout': None, 'party_table': [], 'files_parsed': []}
    files = sorted(os.listdir(snapdir))
    csvs = [f for f in files if f.lower().endswith('.csv')]
    htmls = [f for f in files if f.lower().endswith(('.html', '.htm', '.aspx'))]
    for f in csvs:
        rows = parse_csv_bytes(open(os.path.join(snapdir, f), 'rb').read())
        if rows:
            cand.extend(rows); meta['files_parsed'].append(f)
    for f in htmls:
        p = Tables()
        p.feed(open(os.path.join(snapdir, f), 'rb').read().decode('utf-8', 'replace'))
        for tb in p.tables:
            rows = tb['rows']
            if not csvs:
                got = rows_from_table(rows, tb['context'] or p.title)
                if got:
                    cand.extend(got); meta['files_parsed'].append(f)
            # province/party summary table
            hi = next((i for i, r in enumerate(rows[:4]) if r and any(re.search(r'party|affiliation', c.lower()) for c in r)), None)
            if hi is not None and not any('candidate' in c.lower() for c in rows[hi]):
                meta['party_table'] = [rows[hi]] + rows[hi + 1:]
            for r in rows:
                for i, c in enumerate(r):
                    if re.search(r'who voted|turnout', c.lower()) and i + 1 < len(r):
                        meta['turnout'] = r[i + 1]
    # dedupe (same candidate in same district from several files): keep the row with most places reported
    best = {}
    for r in cand:
        k = (r['district'].lower(), r['candidate'].lower())
        if k not in best or (r['places_reported'] or 0) >= (best[k]['places_reported'] or 0):
            best[k] = r
    return list(best.values()), meta


def ed_codes():
    try:
        return {r['district'].lower(): r['ed_code'] for r in csv.DictReader(open(os.path.join(BASE, 'candidates_2026.csv'), encoding='utf-8'))}
    except Exception:
        return {}


def write_outputs(cands, meta, snap_time, snapdir):
    codes = ed_codes()
    for r in cands:
        if not r['ed_code']:
            r['ed_code'] = codes.get(r['district'].lower(), '')
    by_d = {}
    for r in cands:
        by_d.setdefault(r['district'], []).append(r)
    rows = []
    for d, rs in sorted(by_d.items()):
        tot = sum(r['votes'] for r in rs)
        mx = max(r['votes'] for r in rs)
        for r in sorted(rs, key=lambda x: -x['votes']):
            share = r['share_src'] if r['share_src'] is not None else (round(100 * r['votes'] / tot, 2) if tot else None)
            rows.append([r['ed_code'], d, r['candidate'], r['party'], r['votes'], share, r['places_reported'], r['places_total'],
                         'Y' if tot > 0 and r['votes'] == mx else 'N', 'Y' if re.search(r'elected', r['elected_src'] or '', re.I) else '', snap_time])
    hdr = ['district_code', 'district_name', 'candidate', 'party', 'votes', 'share_pct', 'places_reported', 'places_total', 'leading', 'elected_flag_src', 'snapshot_utc']
    for path in (os.path.join(BASE, 'latest.csv'), os.path.join(snapdir, 'parsed_latest.csv')):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
    party = {}
    grand = sum(r[4] for r in rows)
    for r in rows:
        p = party.setdefault(r[3] or '(none)', {'candidates': 0, 'leading': 0, 'elected': 0, 'votes': 0})
        p['candidates'] += 1; p['votes'] += r[4]
        p['leading'] += r[8] == 'Y'; p['elected'] += r[9] == 'Y'
    districts_reporting = sum(1 for d, rs in by_d.items() if sum(x['votes'] for x in rs) > 0)
    rep = [(rs[0]['places_reported'], rs[0]['places_total']) for rs in by_d.values()]
    pr = sum(a or 0 for a, b in rep); pt = sum(b or 0 for a, b in rep)
    with open(os.path.join(BASE, 'latest_summary.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['party', 'candidates', 'seats_leading', 'seats_elected_flagged', 'votes', 'province_share_pct', 'snapshot_utc'])
        for k, v in sorted(party.items(), key=lambda kv: -kv[1]['votes']):
            w.writerow([k, v['candidates'], v['leading'], v['elected'], v['votes'], round(100 * v['votes'] / grand, 2) if grand else '', snap_time])
        w.writerow([])
        w.writerow(['metric', 'value'])
        w.writerow(['districts_with_votes', districts_reporting])
        w.writerow(['districts_total_seen', len(by_d)])
        w.writerow(['voting_places_reported', pr if pt else ''])
        w.writerow(['voting_places_total', pt if pt else ''])
        w.writerow(['total_valid_votes_counted', grand])
        w.writerow(['turnout_reported_by_ebc', meta.get('turnout') or ''])
        w.writerow(['note', 'Initial count only; preliminary. "leading" = most votes in the district at this snapshot.'])
    if meta.get('party_table'):
        with open(os.path.join(snapdir, 'party_table_src.csv'), 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(meta['party_table'])
    return len(rows), districts_reporting


def log(msg):
    os.makedirs(LOGS, exist_ok=True)
    line = f"{now_utc().strftime('%Y-%m-%dT%H:%M:%SZ')} {msg}"
    print(line)
    with open(os.path.join(LOGS, 'fetch.log'), 'a') as f:
        f.write(line + '\n')


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--reparse':
        snapdir = sys.argv[2]
        cands, meta = parse_snapshot(snapdir)
        if not cands:
            log(f'REPARSE {snapdir}: no candidate rows found'); return 2
        n, d = write_outputs(cands, meta, os.path.basename(snapdir.rstrip('/')), snapdir)
        log(f'REPARSE {snapdir}: {n} candidate rows, {d} districts with votes'); return 0

    state = load_state()
    ts = now_utc().strftime('%Y%m%dT%H%M%SZ')
    status = {'snapshot_utc': ts, 'entry': ENTRY}
    try:
        if any(time.time() - state.get(u, 0) < MIN_INTERVAL for u in (ENTRY, CONTAINER + '?restype=container&comp=list')):
            log(f'SKIPPED: last fetch was under {MIN_INTERVAL}s ago (polite-interval rule); nothing downloaded'); return 0
        st, h, body, final = get(ENTRY, state, follow=False)
        loc = h.get('Location') or h.get('location') or ''
        status.update(entry_status=st, entry_location=loc)
        entry_live = st == 200 or (st in (301, 302, 303, 307, 308) and STATIC_PAGE not in loc)
        blobs, _ = list_container(state)
    except (urllib.error.URLError, OSError, ssl.SSLError) as e:
        save_state(state); log(f'NETWORK ERROR: {e}'); return 1
    save_state(state)
    if blobs is None:
        log('ERROR: could not list the Elections BC ENR container'); return 1
    targets = [CONTAINER + urllib.parse.quote(n) for n, lm in blobs if is_result_blob(n)]
    status['candidate_blobs'] = [n for n, lm in blobs if is_result_blob(n)]

    entry_links = []
    if entry_live:
        if st in (301, 302, 303, 307, 308) and loc:
            st2, h2, body, final = get(urllib.parse.urljoin(ENTRY, loc), state)
        p = Tables(); p.feed(body.decode('utf-8', 'replace'))
        for href in p.links:
            u = urllib.parse.urljoin(final or ENTRY, href)
            host = urllib.parse.urlparse(u).hostname or ''
            if any(host == x or host.endswith('.' + x) for x in OFFICIAL_HOSTS) and urllib.parse.urlparse(u).path.lower().endswith(DATA_EXT) \
                    and STATIC_PAGE not in u and ('result' in u.lower() or 'GE-2026' in u):
                entry_links.append(u)
        targets = sorted(set(targets + entry_links))
        status['entry_links'] = entry_links

    if not targets:
        msg = (f'NO RESULTS POSTED YET: {ENTRY} -> {status.get("entry_status")} {status.get("entry_location") or ""}; '
               f'no 2026 result files in ENR container ({len(blobs)} blobs listed). Polls close 8 p.m. PDT (03:00 UTC Oct 25).')
        log(msg)
        with open(os.path.join(LOGS, 'last_status.json'), 'w') as f:
            json.dump(dict(status, result='no_results'), f, indent=1)
        save_state(state)
        return 0

    snapdir = os.path.join(RAW, ts)
    os.makedirs(snapdir, exist_ok=True)
    manifest = []
    for u in targets:
        st, h, b, fin = get(u, state)
        if st is None:
            continue
        fn = re.sub(r'[^A-Za-z0-9._-]', '_', urllib.parse.unquote(urllib.parse.urlparse(u).path.split('/')[-1]) or 'index.html')
        open(os.path.join(snapdir, fn), 'wb').write(b)
        manifest.append({'url': u, 'status': st, 'bytes': len(b), 'last_modified': h.get('Last-Modified', ''), 'file': fn,
                         'fetched_utc': now_utc().isoformat(timespec='seconds')})
        # follow CSV / data links found inside result pages (e.g. #reportdownloadcsv)
        if fn.lower().endswith(('.html', '.htm', '.aspx')) and st == 200:
            p = Tables(); p.feed(b.decode('utf-8', 'replace'))
            for href in p.links:
                cu = urllib.parse.urljoin(u, href)
                hst = urllib.parse.urlparse(cu).hostname or ''
                if cu.lower().split('?')[0].endswith(('.csv', '.json', '.xml')) and any(hst == x or hst.endswith('.' + x) for x in OFFICIAL_HOSTS) \
                        and cu not in targets:
                    targets.append(cu)
    save_state(state)
    json.dump(dict(status, files=manifest), open(os.path.join(snapdir, 'snapshot_manifest.json'), 'w'), indent=1)
    cands, meta = parse_snapshot(snapdir)
    if not cands:
        log(f'FILES FOUND BUT NOT PARSEABLE: {len(manifest)} files saved in {snapdir}; inspect and adjust COLS in fetch.py')
        return 2
    n, d = write_outputs(cands, meta, ts, snapdir)
    log(f'OK {ts}: {len(manifest)} files, {n} candidate rows, {d} districts with votes -> latest.csv, latest_summary.csv')
    return 0


if __name__ == '__main__':
    sys.exit(main())
