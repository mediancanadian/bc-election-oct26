#!/usr/bin/env python3
"""Build index.html: template + site.js + data, all inlined in one file."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
site = json.load(open(os.path.join(ROOT, 'data', 'site.json')))
story = json.load(open(os.path.join(ROOT, 'data', 'story.json')))
story.update(json.load(open(os.path.join(ROOT, 'data', 'slide_text.json'))))   # headlines and lines exactly as on the slides
P = sorted(site['polls'], key=lambda p: p['end'])
MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
d0, d1 = P[0]['end'], P[-1]['end']
names = sorted({p['pollster'] for p in P})
W = story['why']
def dr(s):
    a, z = [list(map(int, x.split('-'))) for x in s.split(' to ')]
    return f'{MON[a[1]-1]} {a[2]} to {z[2]}, {z[0]}' if a[1] == z[1] else f'{MON[a[1]-1]} {a[2]} to {MON[z[1]-1]} {z[2]}, {z[0]}'
REFS = [
    dict(id='ebc26', title='Elections BC, 2026 Provincial General Election results files, as posted October 25, 2026, 1:49 a.m. Pacific', url='https://results.elections.bc.ca/'),
    dict(id='ebcdates', title='Elections BC, 2026 Provincial Election: key dates (final count, Return Day)', url='https://elections.bc.ca/2026-provincial-election/'),
    dict(id='ebcnight', title='Elections BC, "Final Voting Day is Saturday, October 24" (ballots counted at the final count)', url='https://elections.bc.ca/news/final-voting-day-is-saturday-october-24/'),
    dict(id='ebc24', title='Elections BC, Statement of Votes, 2024 Provincial General Election', url='https://elections.bc.ca/docs/rpt/statement-of-votes-2024-provincial-election.pdf'),
    dict(id='ebc20', title='Elections BC, provincial voting results by voting area and voting area boundaries, 2020 and 2024 (BC Data Catalogue)', url='https://catalogue.data.gov.bc.ca/dataset/44914a35-de9a-4830-ac48-870001ef8935'),
    dict(id='ebchist', title='Elections BC, Electoral History of British Columbia, 1871 to 1986, 1987 to 2001 and 2002 to 2013, and Statements of Votes 2017 to 2024', url='https://elections.bc.ca/docs/rpt/1871-1986_ElectoralHistoryofBC.pdf'),
    dict(id='bcstats', title='BC Stats, 2021 Census Profile by Provincial Electoral District (2023 boundaries)', url='https://catalogue.data.gov.bc.ca/dataset/da0326f2-2191-4345-84d3-d14cd6ee76eb'),
    dict(id='statcan', title='Statistics Canada, Census of Population 2021, Census Profile', url='https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm'),
    dict(id='ecan25', title='Elections Canada, 45th General Election (April 28, 2025), official poll-by-poll results and polling division boundaries', url='https://www.elections.ca/res/rep/off/ovrGE45/62/data_donnees/pollresults_resultatsbureau59.zip'),
    dict(id='bcdc', title='BC Data Catalogue, provincial electoral districts (2023), Freshwater Atlas and census dissemination blocks', url='https://catalogue.data.gov.bc.ca/'),
    dict(id='polls', title=f'Pollster releases, {MON[int(d0[5:7]) - 1]} {d0[:4]} to {MON[int(d1[5:7]) - 1]} {d1[:4]}: ' + ', '.join(names) + ' (each release linked in the repository)',
         url='https://github.com/mediancanadian/bc-election-oct26'),
    dict(id='ar', title=f'Angus Reid Institute, B.C. election poll tables, field work {dr(W["issues_source"]["field"])}', url=W['issues_source']['url']),
    dict(id='irg', title=f'Innovative Research Group, 2026 B.C. election release, field work {dr(W["best_source"]["field"])}', url=W['best_source']['url']),
    dict(id='ipsos', title=f'Ipsos, B.C. election poll release, field work {dr(W["time_for_change"]["field"])}', url=W['time_for_change']['url']),
    dict(id='platform', title=f'Conservative Party of BC, "{story["platform"]["title"]}" (platform and costing, posted October 19, 2026)', url=story['platform']['url']),
    dict(id='cpcboard', title='Conservative Party of BC, Board of Directors statement on the party leadership (party X account)', url='https://x.com/Conservative_BC/status/2102856519058669613'),
    dict(id='cpcconst', title='Conservative Party of BC, Constitution, March 1, 2025', url='https://conservativebc.ca/wp-content/uploads/2025/07/CPBC_1_March_2025_Constitution.pdf'),
    dict(id='suburbs', title='Canadian Suburbs project (David Gordon, Queen\'s University), methods: active core, transit suburb, auto suburb and exurban', url='https://www.canadiansuburbs.ca/methods/'),
    dict(id='kr', title='Kitschelt, H. and P. Rehm (2023), "Polarity Reversal: The Socioeconomic Reconfiguration of Partisan Support in Knowledge Societies", Politics and Society 51(4): 520 to 566', url='https://doi.org/10.1177/00323292221100220'),
    dict(id='goodman', title='Goodman, L. A. (1953), "Ecological Regressions and Behavior of Individuals", American Sociological Review 18(6)', url=None),
    dict(id='gallagher', title='Gallagher, M., Election indices (least squares index of disproportionality), Trinity College Dublin', url='https://www.tcd.ie/Political_Science/about/people/Michael.Gallagher/ElSystems/Docts/ElectionIndices.pdf'),
    dict(id='laakso', title='Laakso, M. and R. Taagepera (1979), "Effective" Number of Parties, Comparative Political Studies 12(1); calculation notes by M. Gallagher', url='https://www.tcd.ie/Political_Science/about/people/michael_gallagher/ElSystems/Docts/effno.php'),
    dict(id='pedersen', title='Pedersen, M. N. (1979), "The Dynamics of European Party Systems: Changing Patterns of Electoral Volatility", European Journal of Political Research 7(1)', url=None),
]
t = open(os.path.join(HERE, 'template.html')).read()
topo = open(os.path.join(ROOT, 'data', 'geo', 'FINAL_ed2023_land_lakes_web_4326.topojson')).read()
detail = open(os.path.join(ROOT, 'data', 'geo', 'site_map_detail.json')).read()
js = open(os.path.join(HERE, 'site.js')).read()
def build(vpmeta):
    return (t.replace('__VPMETA__', vpmeta).replace('__SITE__', json.dumps(site, separators=(',', ':'))).replace('__STORY__', json.dumps(story, separators=(',', ':')))
            .replace('__TOPO__', topo).replace('__DETAIL__', detail).replace('__REFS__', json.dumps(REFS)).replace('__JS__', js))
out = build('')
open(os.path.join(ROOT, 'index.html'), 'w').write(out)
print('index.html', os.path.getsize(os.path.join(ROOT, 'index.html')) // 1024, 'KB')
