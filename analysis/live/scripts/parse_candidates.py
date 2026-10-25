"""Parse Elections BC 2026 candidate list HTML -> rows (district, ballot name, affiliation)."""
import re, html, sys, csv, json
src = sys.argv[1]
t = open(src, encoding='utf-8', errors='replace').read()
tb = t[t.find('<table id="candidates_table"'):]
tb = tb[:tb.find('</table>')]
rows = []
for tr in re.findall(r'<tr class="district_section_\d">(.*?)</tr>', tb, re.S):
    tds = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
    rows.append({'district': tds[0], 'ballot_order_key': tds[1], 'candidate': tds[3], 'affiliation': tds[4]})
json.dump(rows, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
from collections import Counter
print(len(rows), 'candidates;', len({r['district'] for r in rows}), 'districts')
for k, v in Counter(r['affiliation'] for r in rows).most_common(): print(v, k)
