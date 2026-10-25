#!/usr/bin/env python3
"""Write METHODOLOGY.md: the method by chapter and a table of every published number, filled from data/story.json,
the same file the slides and the page read."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
S = json.load(open(os.path.join(ROOT, 'data', 'story.json')))
r0 = lambda v: str(Decimal(str(v)).quantize(Decimal('1'), ROUND_HALF_UP))
r1 = lambda v: str(Decimal(str(v)).quantize(Decimal('0.1'), ROUND_HALF_UP))
M, W, P = S['middle'], S['who_pooled'], S['promises']
MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def span(f):
    """'2026-10-15 to 2026-10-19' -> 'October 15 to 19, 2026'"""
    (y1, m1, d1), (y2, m2, d2) = [tuple(int(v) for v in x.split('-')) for x in f.split(' to ')]
    if (y1, m1) == (y2, m2):
        return f"{MON[m1 - 1]} {d1} to {d2}, {y1}"
    return f"{MON[m1 - 1]} {d1}, {y1} to {MON[m2 - 1]} {d2}, {y2}" if y1 != y2 else f"{MON[m1 - 1]} {d1} to {MON[m2 - 1]} {d2}, {y1}"
from rows import build_rows
rows = build_rows(S, r0, r1, span)
head = open(os.path.join(ROOT, 'methods', 'methodology_head.md')).read()
tbl = '| ID | Number | As published | Where | Source file | How it is computed |\n|---|---|---|---|---|---|\n'
tbl += ''.join(f"| N{i} | {a} | {b} | {c} | `{d}` | {e} |\n" if d and not d.startswith('http') else f"| N{i} | {a} | {b} | {c} | {d} | {e} |\n" for i, (a, b, c, d, e) in enumerate(rows, 1))
open(os.path.join(ROOT, 'METHODOLOGY.md'), 'w').write(head + '\n## Every published number\n\nFilled by `methods/build_methodology.py` from `data/story.json`, the file the slides and the page read.\n\n' + tbl)
print('METHODOLOGY.md', len(rows), 'numbers')
