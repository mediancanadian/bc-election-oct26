"""Build manifest.json from dl_log.txt plus file hashes. Usage: python3 -I build_manifest.py <history_dir>"""
import sys, os, json, hashlib, re
h = sys.argv[1]
EBC = 'Elections BC Open Data Licence (https://elections.bc.ca/docs/EBC-Open-Data-Licence.pdf); attribution: "Contains information licenced under the Elections BC Open Data Licence"'
LEG = 'Legislative Assembly of British Columbia website content; copyright Legislative Assembly; no open licence stated on the page (not verified)'
GOV = 'Province of British Columbia news release; Crown copyright (BC Government terms of use; not verified)'
USE = {
 'hist_1871_1986': 'Province series 1928-1986: party summaries, General Election Summary (turnout), premiers, multi-member districts',
 'hist_1871_1986_errata': 'Errata to 1871-1986 volume (checked; none affect the summaries used)',
 'hist_1987_2001': 'Province series 1991-2001 party summaries; premiers 1986-2001; 2001 district names cross-check',
 'hist_2002_2013': 'Province series 2005-2013 party summaries; premiers 2001-2011',
 'ge2001_xls': 'districts_2001_2017.csv (2001)', 'ge2005_xls': 'districts_2001_2017.csv (2005)', 'ge2009_xls': 'districts_2001_2017.csv (2009)',
 'ge2013_xls': 'districts_2001_2017.csv (2013); Table 2 comparison 1928-2013 (turnout, eligible voters)',
 'ge2017_xlsx': 'districts_2001_2017.csv (2017)', 'ge2005_errata': '2005 party totals corrections',
 'ge2001_sov': '2001 registration/turnout cross-check', 'ge2005_sov': 'eligible voter estimate cross-check',
 'ge2009_sov': 'eligible voter estimate cross-check', 'ge2013_sov': 'Table 2: 1928-2013 comparison (parsed to derived/sov2013_table2_comparison.csv)',
 'ge2017_sov': '2017 Statement of Votes (cross-check)', 'ge2020_sov': '2020 party summary (Table 19) and turnout (Table 21)',
 'ge2024_sov': '2024 party summary and turnout', 'ceo2017': '2017 party summary, eligible voters, minority note',
 'ceo2020': '2020 turnout cross-check', 'ceo2024': '2024 turnout cross-check; BC United withdrawal',
 'licence': 'Licence text', 'turnout_page': 'Turnout 1996-2024 cross-check',
 'leg_premiers': 'NOT USED (page did not contain a premiers list)', 'leg_exec_council': 'NOT USED (current cabinet page; premier not found in static HTML)',
 'govbc_news_2024PREM0061': 'Premier David Eby after 2024 election',
}
entries = []
for line in open(os.path.join(h, 'dl_log.txt')):
    m = re.match(r'(\S+)\s+(\d{3})?\s*(\d+)?\s*(https?://\S+) -> (\S+)', line.strip())
    if not m: continue
    ts, code, size, url, rel = m.groups()
    path = os.path.join(h, 'raw', rel)
    if not os.path.exists(path): continue
    folder = rel.split('/')[0]
    lic = EBC if 'elections.bc.ca' in url else (LEG if 'leg.bc.ca' in url else GOV)
    if folder.startswith('lims_index_'): use = 'Premier in office (Executive Council list, Hansard index) for ' + folder.replace('lims_index_', '') + ' session'
    else: use = USE.get(folder, '')
    entries.append(dict(url=url, file=f'raw/{rel}', accessed_utc=ts, http_status=code, bytes=os.path.getsize(path),
                        sha256=hashlib.sha256(open(path, 'rb').read()).hexdigest(), licence=lic, used_for=use))
# keep last entry per file
seen = {}
for e in entries: seen[e['file']] = e
out = dict(project='BC election history 1928-2024 (official sources)', user_agent='Mozilla/5.0 (research)', files=list(seen.values()),
           outputs=['province_series.csv', 'province_party_detail.csv', 'right_vs_left.csv', 'turnout_trend.csv', 'districts_2001_2017.csv',
                    'derived/sov2013_table2_comparison.csv'])
json.dump(out, open(os.path.join(h, 'manifest.json'), 'w'), indent=1)
print(len(seen), 'files')
