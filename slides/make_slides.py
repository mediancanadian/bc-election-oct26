#!/usr/bin/env python3
"""Week 3 carousel: B.C. election, October 24, 2026 (The Median Canadian), draft 2: the story version.

python3 ../analysis/story.py && python3 make_slides.py
-> slides.html, out/the-median-canadian-bc-election-n-of-8.png and .jpg, out/contact-sheet.jpg,
   out/slide3-options.jpg (two map treatments side by side) and a fit report.
Every number on a slide is read from ../data/story.json. All text, labels, logo and slide numbers sit in the
reel-safe column (x 180 to 900) so the same image works as a carousel slide and as a reel.
"""
import html, json, os, re, sys
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import geopandas as gpd
from shapely.geometry import box

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "..", "data", "story.json")))
PH = json.load(open(os.path.join(HERE, "photos_used.json")))
if os.path.exists(os.path.join(HERE, "photos_new.json")):
    PH.update(json.load(open(os.path.join(HERE, "photos_new.json"))))
GEO = os.path.join(HERE, "..", "data", "geo")
N = 8
OUTDIR = os.path.join(HERE, "out"); os.makedirs(OUTDIR, exist_ok=True)
MAP_OPTION = os.environ.get("MAP_OPTION", "A")     # A: highlighted Metro Vancouver map, B: equal-size riding tiles

COL = {"CON": "#5b9dff", "NDP": "#ff9a3c", "GRN": "#5cc879", "BCLIB": "#c39bff", "OTH": "#b8bec8"}
TEXT, MUTED, GRID, PALE = "#ffffff", "#c9d0d9", "rgba(255,255,255,0.18)", "rgba(255,255,255,0.13)"
FONT = 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
CW = 684

# photo per slide and focus point; replaced when the new free photos arrive
PHOTO = {1: ("legislature3", "46% 0%", "auto 100%"), 2: ("d1", "50% 60%"), 3: ("nanaimo", "50% 100%", "auto 118%"), 4: ("richmond", "50% 40%"),
         5: ("rowhouses", "50% 50%"), 6: ("vancouver2", "55% 50%"), 7: ("metrotown", "50% 40%"), 8: ("legislature2", "50% 50%")}
for k, v in json.loads(os.environ.get("PHOTO_OVERRIDE", "{}")).items():
    PHOTO[int(k)] = tuple(v)


WORDS = {n: w for n, w in enumerate("Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty".split())}


def esc(s): return html.escape(str(s), quote=True)
def r0(v): return str(Decimal(str(v)).quantize(Decimal("1"), ROUND_HALF_UP))
def r1(v): return str(Decimal(str(v)).quantize(Decimal("0.1"), ROUND_HALF_UP))


def halo(x, y, txt, size=22, fill=TEXT, anchor="start", weight=700):
    s = f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" font-family=\'{FONT}\''
    return (f'<text x="{x:.1f}" y="{y:.1f}" {s} fill="none" stroke="rgba(8,11,16,0.92)" stroke-width="6" stroke-linejoin="round">{esc(txt)}</text>'
            f'<text x="{x:.1f}" y="{y:.1f}" {s} fill="{fill}">{esc(txt)}</text>')


def svg(W, H, g): return f'<svg width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}">{g}</svg>'


# ------------------------------------------------------------------ 2. the right's vote by election: one band that changes colour
def v_rise():
    """Share of the vote by party at each election, 2001 to 2026, as lines: BC Liberal (to 2020), Conservative, NDP."""
    D = S["rise_long"]
    W, H, L, R, T, B = CW, 340, 64, CW - 170, 26, 290
    X = lambda yr: L + (R - L) * (yr - 2001) / (2026 - 2001)
    Y = lambda v: B - (B - T) * v / 62
    g = ""
    for v in (20, 40, 60):
        g += f'<line x1="{L}" x2="{R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1.5"/>'
        g += halo(L - 10, Y(v) + 7, f"{v}%", 19, fill=MUTED, anchor="end", weight=600)
    def line(key, col, pts, w=6):
        out = f'<polyline points="{" ".join(f"{X(yr):.1f},{Y(v):.1f}" for yr, v in pts)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>'
        return out + "".join(f'<circle cx="{X(yr):.1f}" cy="{Y(v):.1f}" r="6.5" fill="{col}"/>' for yr, v in pts)
    lib = [(d["year"], d["BCLIB"]) for d in D if d["BCLIB"] > 0]
    con = [(d["year"], d["CON"]) for d in D]
    ndp = [(d["year"], d["NDP"]) for d in D]
    g += line("BCLIB", COL["BCLIB"], lib) + line("NDP", COL["NDP"], ndp) + line("CON", COL["CON"], con, 8)
    g += halo(X(2006), Y(lib[1][1]) - 18, "BC Liberal", 23, fill=COL["BCLIB"], anchor="middle", weight=800)
    g += halo(X(2026) + 16, Y(con[-1][1]) + 8, "Conservative", 23, fill=COL["CON"], weight=800)
    g += halo(X(2026) + 16, Y(ndp[-1][1]) + 8, "NDP", 23, fill=COL["NDP"], weight=800)
    for yr in (2001, 2009, 2020, 2026):
        g += halo(X(yr), B + 38, str(yr), 20, fill=MUTED, anchor="middle", weight=700)
    return svg(W, H, g)


def rise_legend():
    return ""


# ------------------------------------------------------------------ 3. where: option A, Metro Vancouver highlight map
def paths(gdf, bounds, W, H, pad=2):
    minx, miny, maxx, maxy = bounds
    sc = min((W - 2 * pad) / (maxx - minx), (H - 2 * pad) / (maxy - miny))
    def ring(coords):
        return "M" + "L".join(f"{(x - minx) * sc + pad:.1f},{(maxy - y) * sc + pad:.1f}" for x, y in coords) + "Z"
    out = []
    for _, r in gdf.iterrows():
        geoms = getattr(r.geometry, "geoms", [r.geometry])
        d = "".join(ring(p.exterior.coords) + "".join(ring(i.coords) for i in p.interiors) for p in geoms if not p.is_empty)
        out.append((r.ed_code, d))
    T = lambda x, y: ((x - minx) * sc + pad, (maxy - y) * sc + pad)
    return out, (maxx - minx) * sc + 2 * pad, (maxy - miny) * sc + 2 * pad, T


SW = {d["code"]: d for d in S["switched"]}
WATER, LAND = "#141c26", "#4a5466"
# city labels: lon, lat (degrees) and text anchor, each placed on its own city; the fit report fails labels that touch
LABELS_LL = {"North Vancouver": (-123.0, 49.375, "middle"), "Port Moody": (-122.87, 49.33, "middle"),
             "Coquitlam": (-122.79, 49.29, "middle"), "Maple Ridge": (-122.53, 49.27, "middle"), "Burnaby": (-122.975, 49.255, "middle"),
             "Vancouver": (-123.16, 49.245, "middle"), "Richmond": (-123.12, 49.165, "middle"), "Delta": (-122.935, 49.155, "middle"),
             "Surrey": (-122.79, 49.175, "middle")}


def v_where_map():
    """Metro Vancouver from the full-resolution riding master (see build_metro_detail.py), in UTM zone 10N.
    Water (sea, lakes of 1 km2 or more, the Fraser and other large rivers) is drawn as water; riding borders are
    drawn only between ridings, never along the shore; the frame's south edge is the Canada-United States border."""
    from pyproj import Transformer
    from shapely.ops import unary_union
    det = gpd.read_file(os.path.join(GEO, "DETAIL_metro_vancouver_4326.geojson")).to_crs(26910)
    water = gpd.read_file(os.path.join(GEO, "DETAIL_metro_vancouver_water_4326.geojson")).to_crs(26910)
    frame = gpd.read_file(os.path.join(GEO, "DETAIL_metro_vancouver_frame_4326.geojson")).to_crs(26910).geometry.iloc[0]
    minx, miny, maxx, maxy = frame.bounds
    sc = CW / (maxx - minx); H = (maxy - miny) * sc
    T = lambda x, y: ((x - minx) * sc, (maxy - y) * sc)
    pts = lambda cs: "L".join(f"{x:.1f},{y:.1f}" for x, y in (T(*c[:2]) for c in cs))

    def d_poly(geom):
        out = ""
        for p in getattr(geom, "geoms", [geom]):
            if p.geom_type == "Polygon" and not p.is_empty:
                out += "".join("M" + pts(r.coords) + "Z" for r in [p.exterior, *p.interiors])
        return out

    def d_line(geom):
        out = ""
        for l in getattr(geom, "geoms", [geom]):
            if l.geom_type == "LineString" and not l.is_empty:
                out += "M" + pts(l.coords)
        return out
    edge = unary_union(det.geometry.values).boundary.buffer(1.0)       # shore, lake shores and frame cut: no border line
    inner = {r.ed_code: r.geometry.boundary.difference(edge) for _, r in det.iterrows()}
    fd = d_poly(frame)
    g = f'<defs><clipPath id="mvclip"><path d="{fd}"/></clipPath></defs><path d="{fd}" fill="{WATER}"/><g clip-path="url(#mvclip)">'
    import pandas as pd
    party26 = pd.read_csv(os.path.join(HERE, "..", "data", "ridings.csv"), index_col="district_code").lead26.to_dict()
    PALE26 = {"CON": "#5d7290", "NDP": "#c08452", "GRN": "#4f7d5c"}   # same party as 2024: a muted, greyer shade of the party colour
    g += "".join(f'<path d="{d_poly(r.geometry)}" fill="{COL[SW[r.ed_code]["to"]] if r.ed_code in SW else PALE26.get(party26.get(r.ed_code), LAND)}" fill-rule="evenodd"/>'
                 for _, r in det.iterrows())
    g += "".join(f'<path d="{d_line(inner[c])}" fill="none" stroke="rgba(255,255,255,0.30)" stroke-width="0.8" stroke-linejoin="round"/>'
                 for c in inner if c not in SW)
    g += "".join(f'<path d="{d_line(inner[c])}" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>'
                 for c in inner if c in SW)
    g += "".join(f'<path d="{d_poly(r.geometry)}" fill="{WATER}" fill-rule="evenodd"/>' for _, r in water.iterrows())
    g += f'</g><path d="{fd}" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="1.2"/>'
    ll = Transformer.from_crs(4326, 26910, always_xy=True)
    for name, (lon, lat, anc) in LABELS_LL.items():
        px, py = T(*ll.transform(lon, lat))
        g += halo(px, py + 8, name, 23, anchor=anc, weight=800)
    return svg(CW, H, g)


def elsewhere():
    others = [d for d in S["switched"] if d["region"] != "Metro Vancouver"]
    to_con = [d["name"] for d in others if d["to"] == "CON"]; to_ndp = [d["name"] for d in others if d["to"] == "NDP"]
    n = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}.get(len(to_con), str(len(to_con)))
    return (f'<p class="foot">Outside Metro Vancouver, {n} more ridings switched to the Conservatives, and '
            f'{" and ".join(to_ndp)} to the NDP.</p>')


# ------------------------------------------------------------------ 3. where: option B, equal-size riding tiles
def v_where_tiles():
    from scipy.optimize import linear_sum_assignment
    import pandas as pd
    lp = pd.read_csv(os.path.join(GEO, "FINAL_ed2023_label_points.csv")).set_index("ed_code")
    u = lp.label_x_3005.rank(pct=True).values; v = lp.label_y_3005.rank(pct=True).values
    cols, rows = 13, 9
    cells = np.array([((c + (0.5 if r % 2 else 0)) / cols, r / (rows - 1)) for r in range(rows) for c in range(cols)])
    cost = (u[:, None] - cells[None, :, 0]) ** 2 + (v[:, None] - cells[None, :, 1]) ** 2
    ri, ci = linear_sum_assignment(cost)
    rr = 27
    W = CW; H = (rows - 1) * rr * 1.55 + 2 * rr + 8
    g = ""
    for i, j in zip(ri, ci):
        code = lp.index[i]; cx, cy = cells[j]
        X = rr + 4 + cx * (W - 2 * rr - 30); Yp = H - rr - 4 - cy * (H - 2 * rr - 8)
        pts = " ".join(f"{X + rr * np.cos(np.pi / 6 + k * np.pi / 3):.1f},{Yp + rr * np.sin(np.pi / 6 + k * np.pi / 3):.1f}" for k in range(6))
        fill = COL[SW[code]["to"]] if code in SW else PALE
        g += f'<polygon points="{pts}" fill="{fill}" stroke="rgba(8,11,16,0.9)" stroke-width="2"/>'
    return svg(W, H, g)


# ------------------------------------------------------------------ 4. who lives there: two profile cards
def in10(v):
    return "Nearly half" if 45 <= v < 50 else f"{r0(v / 10)} in 10"


def v_who():
    A, B = S["who_pooled"]["switched"], S["who_pooled"]["stayed_ndp"]
    def card(title, d, col):
        return (f'<div class="pc" style="border-top:6px solid {col}"><div class="pct" style="color:{col}">{esc(title)}</div>'
                f'<div class="pcr"><b>{r0(d["own"])}%</b><span>own their home</span></div>'
                f'<div class="pcr"><b>{r0(d["vismin"])}%</b><span>visible minorities</span></div>'
                f'<div class="pcr"><b>{r0(d["drive"])}%</b><span>go to work by car</span></div>'
                f'<div class="pcr"><b>${r0(d["income"] / 1000)}k</b><span>median household income</span></div></div>')
    return ('<div class="pcs">' + card('Switched to Conservative', A, COL["CON"])
            + card('Stayed NDP', B, COL["NDP"]) + '</div>')


assert (S['middle_pooled']['LPC']['seats26']['CON'] - S['middle_pooled']['LPC']['seats24']['CON']) * 4 == (S['seats']['CON'] - S['seats24']['CON']) * 3, 'slide 6 ratio no longer three in four'


def v_income():
    """Swing toward the Conservatives, 2024 to 2026, by riding income: four groups of 23 ridings, lowest income on the left.
    As on the website: each group's average as a bar, and every riding as a dot. Values under the bars."""
    G = S["income_groups"]
    W, top, bot, y0, y1 = CW, 22, -10, 16, 300
    sc = (y1 - y0) / (top - bot)
    Y = lambda v: y0 + (top - v) * sc
    L, cw, gap = 50, 120, 52
    g = ""
    for v in (20, 10, -10):
        g += f'<line x1="{L - 6}" x2="{W}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="rgba(255,255,255,0.14)" stroke-width="1.5"/>'
        g += halo(L - 12, Y(v) + 7, f'{"+" if v > 0 else "−"}{abs(v)}', 18, fill=MUTED, anchor="end", weight=600)
    g += f'<line x1="{L - 6}" x2="{W}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="rgba(255,255,255,0.55)" stroke-width="2"/>'
    g += halo(L - 12, Y(0) + 7, "0", 18, fill=MUTED, anchor="end", weight=600)
    for i, d in enumerate(G):
        x = L + i * (cw + gap); cx = x + cw / 2
        g += f'<rect x="{x}" y="{Y(d["swing"]):.1f}" width="{cw}" height="{Y(0) - Y(d["swing"]):.1f}" fill="{COL["CON"]}" fill-opacity="0.30"/>'
        g += f'<line x1="{x}" x2="{x + cw}" y1="{Y(d["swing"]):.1f}" y2="{Y(d["swing"]):.1f}" stroke="{COL["CON"]}" stroke-width="5"/>'
        placed, r = [], 5.2
        for v in d["swings"]:
            yy = Y(v)
            for k in range(0, 30):
                off = (k + 1) // 2 * (2 * r + 1.2) * (1 if k % 2 else -1)
                if all((off - px) ** 2 + (yy - py) ** 2 >= (2 * r + 0.8) ** 2 for px, py in placed):
                    break
            placed.append((off, yy))
            g += f'<circle cx="{cx + off:.1f}" cy="{yy:.1f}" r="{r}" fill="#e9edf3" stroke="rgba(8,11,16,0.85)" stroke-width="1.2"/>'
        g += halo(cx, 334, f'+{r1(d["swing"])}', 30, fill=COL["CON"], anchor="middle", weight=800)
        g += halo(cx, 373, f'${r0(d["income"] / 1000)}k', 24, anchor="middle", weight=800)
    g += halo(L + (4 * cw + 3 * gap) / 2, 408, f"Typical riding's median household income; {G[0]['n']} ridings per group", 20, fill=MUTED, anchor="middle", weight=600)
    return svg(W, 420, g)


def who_legend():
    return ""


# ------------------------------------------------------------------ 5. the middle ground: riding flows, 2024 to 2026, by federal vote
def v_middle():
    F = S["middle_flows"]
    left = {}
    for g in ("NDP", "GPC"):
        for k, v in F[g].items():
            left[k] = left.get(k, 0) + v
    groups = [("Conservative federally", F["CPC"], False), ("Liberal federally", F["LPC"], True),
              ("NDP or Green federally", left, False)]
    order = ["NDP", "CON", "GRN"]   # Green last, so its one-riding lines run along the bottom instead of crossing the switch
    k = 3.55; X1, X2, NW = 128, 556, 16; gap_node = 4
    # a switched band starts in its 2024 party colour and ends in its 2026 party colour, so its origin reads at a glance
    defs = "".join(f'<linearGradient id="sw{a}{b}" gradientUnits="userSpaceOnUse" x1="{X1 + NW}" x2="{X2}" y1="0" y2="0">'
                   f'<stop offset="0.12" stop-color="{COL[a]}"/><stop offset="0.88" stop-color="{COL[b]}"/></linearGradient>'
                   for a in order for b in order if a != b)
    g = f"<defs>{defs}</defs>" + halo(X1 + NW / 2, 22, "Provincial 2024", 21, fill=MUTED, anchor="middle", weight=800) + halo(X2 + NW / 2, 22, "Provincial 2026", 21, fill=MUTED, anchor="middle", weight=800)
    y = 40
    for title, fl, hi in groups:
        n = sum(fl.values())
        g += halo(0, y + 22, f"{title}: {n} ridings" if hi else title, 22, weight=800, fill=TEXT if hi else MUTED)
        y += 34
        lt = {p: sum(v for kk, v in fl.items() if kk.split(">")[0] == p) for p in order}
        rt = {p: sum(v for kk, v in fl.items() if kk.split(">")[1] == p) for p in order}
        ly, ry, yl, yr_ = {}, {}, y, y
        for p in order:
            if lt[p]:
                ly[p] = yl; h = lt[p] * k
                g += f'<rect x="{X1}" y="{yl:.1f}" width="{NW}" height="{h:.1f}" fill="{COL[p]}"/>'
                if lt[p] >= 4 and hi:   # numbers only on the group the slide is about; the others stay as context
                    g += halo(X1 - 10, yl + h / 2 + 8, f'{"NDP" if p == "NDP" else "Green" if p == "GRN" else "Con."} {lt[p]}', 20, anchor="end", weight=800, fill=COL[p])
                yl += h + gap_node
            if rt[p]:
                ry[p] = yr_; h = rt[p] * k
                g += f'<rect x="{X2}" y="{yr_:.1f}" width="{NW}" height="{h:.1f}" fill="{COL[p]}"/>'
                if rt[p] >= 4 and hi:
                    g += halo(X2 + NW + 10, yr_ + h / 2 + 8, f'{"NDP" if p == "NDP" else "Green" if p == "GRN" else "Con."} {rt[p]}', 20, weight=800, fill=COL[p])
                yr_ += h + gap_node
        lo = dict(ly); ro = dict(ry)
        for a in order:
            for b in order:
                c = fl.get(f"{a}>{b}", 0)
                if not c:
                    continue
                h = c * k; y0 = lo[a]; y1 = ro[b]; lo[a] += h; ro[b] += h
                xa, xb = X1 + NW, X2; xm = (xa + xb) / 2
                path = (f"M{xa},{y0:.1f} C{xm},{y0:.1f} {xm},{y1:.1f} {xb},{y1:.1f} L{xb},{y1 + h:.1f} C{xm},{y1 + h:.1f} {xm},{y0 + h:.1f} {xa},{y0 + h:.1f} Z")
                switched = a != b
                op = (0.95 if switched else 0.5) if hi else (0.6 if switched else 0.22)
                g += f'<path d="{path}" fill="{f"url(#sw{a}{b})" if switched else COL[b]}" opacity="{op}"/>'
                if switched and hi:
                    g += halo(xm, (y0 + y1) / 2 + h / 2 + 8, "Switched", 22, anchor="middle", weight=800)
        y = max(yl, yr_) + 18
    return svg(CW, y, g)


def v_middle_cross():
    """Provincial vote in the ridings that voted Liberal in the 2025 federal election: NDP and Conservative, 2024 to 2026.
    Each line is the party it measures, in that party's colour."""
    D = S["middle_pooled"]["LPC"]
    W, H, T, B = CW, 330, 40, 300
    X1, X2 = 120, 380
    lo, hi = 34, 54
    Y = lambda v: B - (B - T) * (v - lo) / (hi - lo)
    g = halo(X1, 24, "2024", 24, fill=MUTED, anchor="middle", weight=800) + halo(X2, 24, "2026", 24, fill=MUTED, anchor="middle", weight=800)
    for p, name in (("NDP", "NDP"), ("CON", "Conservative")):
        a, b = D["y2024"][p], D["y2026"][p]
        g += f'<line x1="{X1}" y1="{Y(a):.1f}" x2="{X2}" y2="{Y(b):.1f}" stroke="{COL[p]}" stroke-width="9" stroke-linecap="round"/>'
        g += f'<circle cx="{X1}" cy="{Y(a):.1f}" r="10" fill="{COL[p]}"/><circle cx="{X2}" cy="{Y(b):.1f}" r="10" fill="{COL[p]}"/>'
        g += halo(X1 - 20, Y(a) + 9, f"{r1(a)}%", 26, fill=COL[p], anchor="end", weight=800)
        g += halo(X2 + 20, Y(b) + 9, f"{r1(b)}%", 26, fill=COL[p], weight=800)
        g += halo(X2 + 116, Y(b) + 9, name, 24, fill=COL[p], weight=800)
    return svg(W, H, g)


def middle_legend():
    return ""


# ------------------------------------------------------------------ 6. why: voters' to-do list, with the party rated best on each
def v_why():
    NAME = {"CON": "Con.", "NDP": "NDP"}; FULL = {"CON": "Conservatives", "NDP": "NDP"}
    out = '<div class="todo">'
    for i, it in enumerate(S["why"]["issues"], 1):
        (p1, v1), (p2, v2) = sorted(it["best"].items(), key=lambda kv: -kv[1])
        head, col = ("About even", "#ffffff") if it["lead"] == "even" else (f"Rated best: {FULL[p1]}", COL[p1])
        nums = "" if it["lead"] == "even" else f'<span>{NAME[p1]} {v1}%, {NAME[p2]} {v2}%</span>'
        out += (f'<div class="td"><div class="tdn">{i}</div><div class="tdb"><div class="tdi">{esc(it["issue"])}</div>'
                f'<div class="tds">Named by {it["pct"]}%</div></div>'
                f'<div class="chip" style="border-color:{col};color:{col}">{esc(head)}{nums}</div></div>')
    return out + "</div>"


# ------------------------------------------------------------------ 7. votes and seats: 93-seat hemicycle under a ring of vote shares
def v_majority():
    import math
    seats = S["seats"]; share = S["share"]
    order = [("NDP", seats["NDP"]), ("GRN", seats["GRN"]), ("CON", seats["CON"])]
    fills = [COL[p] for p, n in order for _ in range(n)]
    n = len(fills); rows = 6; R0, R1 = 120, 250; cx, cy = CW / 2, 342
    radii = [R0 + (R1 - R0) * i / (rows - 1) for i in range(rows)]
    per = [round(n * r / sum(radii)) for r in radii]; per[-1] += n - sum(per)
    pos = []
    for i, r in enumerate(radii):
        for j in range(per[i]):
            a = math.pi - j * math.pi / (per[i] - 1)
            pos.append((a, cx + r * math.cos(a), cy - r * math.sin(a)))
    pos.sort(key=lambda p: -p[0])
    rad = 11.5
    g = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{f}"/>' for (a, x, y), f in zip(pos, fills))
    # outer ring: share of the vote, same order
    RR = 290; a0 = math.pi
    vs = [("NDP", share["NDP"]), ("GRN", share["GRN"]), ("OTH", share["CENTRE"] + share["ONEBC"] + share["OTH"]), ("CON", share["CON"])]
    tot = sum(v for _, v in vs)
    for p, v in vs:
        a1 = a0 - math.pi * v / tot
        x0, y0 = cx + RR * math.cos(a0), cy - RR * math.sin(a0); x1, y1 = cx + RR * math.cos(a1), cy - RR * math.sin(a1)
        g += f'<path d="M{x0:.1f},{y0:.1f} A{RR},{RR} 0 0 1 {x1:.1f},{y1:.1f}" fill="none" stroke="{COL.get(p, COL["OTH"])}" stroke-width="16"/>'
        a0 = a1
    g += f'<line x1="{cx}" x2="{cx}" y1="{cy - RR - 18}" y2="{cy - R0 + 30}" stroke="#fff" stroke-width="3" stroke-dasharray="6 5"/>'
    g += halo(cx, cy - RR - 24, f'{S["majority"]} seats for a majority', 20, anchor="middle", weight=800)
    g += halo(cx, cy - 40, "Seats", 22, fill=MUTED, anchor="middle", weight=800)
    va = math.radians(142)
    g += halo(cx + (RR + 16) * math.cos(va) - 4, cy - (RR + 16) * math.sin(va) - 4, "Votes", 22, fill=MUTED, anchor="end", weight=800)
    y = cy + 46
    cols = [("NDP", "NDP", -1), ("CON", "Conservative", 1)]
    g += halo(cx - 170, y, f'NDP: {r0(share["NDP"])}% of votes', 21, fill=COL["NDP"], anchor="middle", weight=800)
    g += halo(cx - 170, y + 28, f'{seats["NDP"]} seats', 21, fill=COL["NDP"], anchor="middle", weight=700)
    g += halo(cx + 170, y, f'Conservative: {r0(share["CON"])}% of votes', 21, fill=COL["CON"], anchor="middle", weight=800)
    g += halo(cx + 170, y + 28, f'{seats["CON"]} seats', 21, fill=COL["CON"], anchor="middle", weight=700)
    g += halo(cx, y + 62, f'Green: {r0(share["GRN"])}% of votes, {seats["GRN"]} seats', 20, fill=COL["GRN"], anchor="middle", weight=700)
    return svg(CW, y + 74, g)


# ------------------------------------------------------------------ 2. 2024 against 2026: the same 93 seats, two results
def v_two_houses():
    import math
    sh24 = next(y for y in S["rise"]["years"] if y["year"] == 2024)
    years = [("2024", S["seats24"], {"NDP": sh24["NDP"], "CON": sh24["CON"]}), ("2026", S["seats"], {"NDP": S["share"]["NDP"], "CON": S["share"]["CON"]})]
    W2 = CW / 2; R0, R1, rows, rad = 92, 154, 5, 6.2; cy = 186
    g = ""
    for k, (yr, seats, sh) in enumerate(years):
        cx = W2 * k + W2 / 2
        # 2026: ring the seats that changed party since 2024 (as on the website), next to the majority line
        gain = {p: sum(1 for d in S["switched"] if d["to"] == p) for p in ("CON", "NDP")} if yr == "2026" else {"CON": 0, "NDP": 0}
        seq = ([("NDP", i >= seats["NDP"] - gain["NDP"]) for i in range(seats["NDP"])] + [("GRN", False)] * seats["GRN"]
               + [("CON", i < gain["CON"]) for i in range(seats["CON"])])
        fills = [COL[p] for p, _ in seq]; rings = [rg for _, rg in seq]
        radii = [R0 + (R1 - R0) * i / (rows - 1) for i in range(rows)]
        per = [round(len(fills) * r / sum(radii)) for r in radii]; per[-1] += len(fills) - sum(per)
        pos = sorted(((math.pi - j * math.pi / (per[i] - 1), r) for i, r in enumerate(radii) for j in range(per[i])), key=lambda t: -t[0])
        g += "".join(f'<circle cx="{cx + r * math.cos(a):.1f}" cy="{cy - r * math.sin(a):.1f}" r="{rad - 0.5 if rg else rad}" fill="{f}"'
                     + (' stroke="#ffffff" stroke-width="1.7"/>' if rg else '/>') for (a, r), f, rg in zip(pos, fills, rings))
        g += f'<line x1="{cx}" x2="{cx}" y1="{cy - R1 - 12}" y2="{cy - R0 + 6}" stroke="#fff" stroke-width="2.5" stroke-dasharray="5 4"/>'
        g += halo(cx, cy - 10, yr, 40, anchor="middle", weight=800)
        g += halo(cx, cy + 34, f'NDP {seats["NDP"]} seats', 22, fill=COL["NDP"], anchor="middle", weight=800)
        g += halo(cx - 8, cy + 72, f'NDP {r1(sh["NDP"])}%', 24, fill=COL["NDP"], anchor="end", weight=800)
        g += halo(cx + 8, cy + 72, f'Con. {r1(sh["CON"])}%', 24, fill=COL["CON"], anchor="start", weight=800)
        g += halo(cx, cy + 104, "of the vote", 22, fill=MUTED, anchor="middle", weight=600)
    return svg(CW, cy + 116, g)


# ------------------------------------------------------------------ 8. promises
def v_promises():
    rank = {it["issue"]: lab for it, lab in zip(S["why"]["issues"], ("Top worry", "Second worry", "Third worry"))}
    out = '<div class="prom">'
    for blk in S["promises"]:
        items = blk["items"]
        pick = [items[0]]
        out += (f'<div class="pr"><div class="pw">{esc(blk["worry"])}</div><ul>'
                + "".join(f'<li class="{"gap" if i["short"].startswith("No target") else ""}">{esc(i["short"])}</li>' for i in pick) + "</ul></div>")
    return out + "</div>"


# ------------------------------------------------------------------ slides
def build(option):
    s = S["seats"]
    # 2026 results are dated by the time Elections BC posted them
    d_, t_ = S["meta"]["source_time"].split(" ", 1)
    dd, mm, yy = (int(v) for v in d_.split("/")); hh, mi = int(t_[:2]), t_[3:5]; ap = "a.m." if t_.endswith("AM") else "p.m."
    MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    asof = f"as of {MONTHS[mm - 1]} {dd}, {yy}, {hh % 12 or 12}:{mi} {ap} Pacific"
    src = f"Elections BC results {asof}"
    SL = []
    sh24 = next(y for y in S["rise"]["years"] if y["year"] == 2024)
    m26 = r1(S["share"]["CON"] - S["share"]["NDP"]); m24 = r1(sh24["NDP"] - sh24["CON"])
    SL.append(dict(kicker="The Median Canadian · Week 3 · October 25, 2026", head="B.C. elects Conservatives", cover=True, key="result",
                   body='<p class="lead">The party\'s first majority since 1928, after nine years of NDP government.</p>'
                        '<p class="body">Here is how it happened.</p>',
                   source=f"Elections BC, 1928 to 2026 ({asof}) · Charts CC BY 4.0"))
    SL.append(dict(kicker="The result", head=f'Conservatives rose from {S["seats24"]["CON"]} seats to {S["seats"]["CON"]}', key="majority",
                   body=f'<p class="lead">Their margin over the NDP was {m26} points, against {m24} points the other way in 2024.</p>'
                        f'<div class="card"><div class="note">The 93 seats and share of the vote after each election. Ringed seats changed party.</div>{v_two_houses()}'
                        f'<p class="foot">Majority: {S["majority"]} seats, with {S["seats"]["CON"] - S["majority"]} to spare. The final count, planned for November 6 to 10, 2026, can change the closest ridings.</p></div>',
                   source=f"Elections BC, 2024; 2026 {asof} · Charts CC BY 4.0"))
    SL.append(dict(kicker="How they got here", head="Conservatives had 2% of the vote in 2020", key="how",
                   body="<p class=\"lead\">In 2024, they took the BC Liberals' place as the NDP's main rival.</p>"
                        f'<div class="card"><div class="note">Share of the vote by party, 2001 to 2026</div>{v_rise()}</div>',
                   source=f"Elections BC, 2001 to 2026 ({asof}) · Charts CC BY 4.0"))
    SL.append(dict(kicker="Where it changed", head="Vancouver's suburbs went Conservative", key="where",
                   body=f'<p class="lead">Conservatives were elected in {S["vancouver_suburbs"]["con26"]} of {S["vancouver_suburbs"]["n"]} suburban ridings, up from {S["vancouver_suburbs"]["con24"]} in 2024.</p>'
                        '<div class="card"><div class="note">Metro Vancouver ridings, 2026. Suburbs: those outside the City of Vancouver.</div>'
                        '<div class="lg"><span><i style="background:#5b9dff"></i>Switched to Conservative</span><span><i style="background:#5d7290"></i>Conservative both years</span><span><i style="background:#c08452"></i>NDP both years</span><span><i style="background:#4f7d5c"></i>Green both years</span></div>'
                        + v_where_map()
                        + f'<p class="foot">All {S["surrey"]["n"]} Surrey ridings elected Conservatives, up from {S["surrey"]["con24"]} in 2024. Outside Metro Vancouver, five more ridings switched to the Conservatives, and Courtenay-Comox to the NDP.</p></div>',
                   source=f"Elections BC, 2024 and 2026 ({asof.split(', 1:')[0]}) · Charts CC BY 4.0"))
    SL.append(dict(kicker="By household income", head="Higher-income ridings moved the most", key="who",
                   body='<p class="lead">On average, ridings at every income level moved toward the Conservatives.</p>'
                        f'<div class="card"><div class="note">Swing to the Conservatives, 2024 to 2026, in points. Each dot is a riding; bars show each group\'s average.</div>{v_income()}'
                        '<p class="foot">Swing: change in the Conservative share of the Conservative and NDP vote. These describe the places, and say nothing about how any one person voted.</p></div>',
                   source="2021 Census (StatCan, BC Stats); Elections BC 2024 and 2026 · Charts CC BY 4.0"))
    SL.append(dict(kicker="The middle ground", head="Federal Liberal areas swung Conservative", key="middle",
                   body='<p class="lead">Three of every four seats the Conservatives added were in these ridings.</p>'
                        f'<div class="card"><div class="note">Provincial vote in the {S["middle_pooled"]["LPC"]["n"]} ridings where the Liberals came first in the April 28, 2025 federal election</div>'
                        f'{v_middle_cross()}<p class="foot">The Greens rose from {r1(S["middle_pooled"]["LPC"]["y2024"]["GRN"])}% to {r1(S["middle_pooled"]["LPC"]["y2026"]["GRN"])}% in these ridings. Federal votes were allocated to provincial ridings by population.</p></div>',
                   source="Elections Canada 2025; Elections BC 2024 and 2026 · Charts CC BY 4.0"))
    SL.append(dict(kicker="Before the vote", head="Conservatives rated best on cost of living", key="why",
                   body='<p class="lead">It was the top worry, and ratings were about even on the other two.</p>'
                        f'<div class="card"><div class="note">Top worries and the party rated best on each</div>{v_why()}'
                        '<p class="foot">Both polls taken October 15 to 19, 2026; people could name up to three worries.</p></div>',
                   source="Angus Reid Institute; Innovative Research Group · October 2026 · Charts CC BY 4.0"))
    SL.append(dict(kicker="What comes next", head="What Conservatives promised", key="promises",
                   body='<p class="lead">The Conservative platform\'s answer to each top worry.</p>'
                        f'<div class="card">{v_promises()}'
                        '</div>'
                        '<div class="explore"><div class="ex1">Find your riding and see how it changed</div>'
                        '<div class="ex2">Link in bio · mediancanadian.ca</div></div>',
                   source="Conservative Party of BC platform, 2026 · Sources on the website"))
    return SL


CSS = f"""
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#0c1016; font-family:{FONT}; color:{TEXT}; }}
.slide {{ position:relative; width:1080px; height:1350px; overflow:hidden; background:#0c1016; }}
.photo {{ position:absolute; inset:0; background-size:cover; background-repeat:no-repeat; filter:brightness(1.08) saturate(1.1); }}
.shade {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(8,11,16,0.42) 0%, rgba(8,11,16,0.32) 32%, rgba(8,11,16,0.08) 48%, rgba(8,11,16,0.08) 76%, rgba(8,11,16,0.72) 100%); }}
.cover .shade {{ background:linear-gradient(180deg, rgba(8,11,16,0.10) 0%, rgba(8,11,16,0) 30%, rgba(8,11,16,0.38) 44%, rgba(8,11,16,0.50) 66%, rgba(8,11,16,0.30) 82%, rgba(8,11,16,0.62) 100%); }}
.content {{ position:absolute; top:200px; left:180px; width:720px; }}
.kicker {{ font-size:27px; font-weight:700; text-transform:uppercase; letter-spacing:0.09em; color:#ffd2c7; text-shadow:0 2px 10px rgba(0,0,0,0.8); }}
h1 {{ font-size:64px; font-weight:800; line-height:1.07; letter-spacing:-0.022em; margin-top:16px; text-shadow:0 3px 18px rgba(0,0,0,0.85), 0 1px 3px rgba(0,0,0,0.9); }}
.cover .content {{ top:520px; }}
.cover .kicker {{ font-size:21px; letter-spacing:0.06em; }}
.cover h1 {{ font-size:96px; margin-top:20px; }}
.lead {{ font-size:32px; font-weight:600; line-height:1.3; margin-top:18px; text-shadow:0 2px 12px rgba(0,0,0,0.9); }}
.cover .lead {{ font-size:38px; line-height:1.27; margin-top:28px; }}
.body {{ font-size:32px; line-height:1.4; margin-top:20px; color:#f2f4f7; text-shadow:0 2px 12px rgba(0,0,0,0.9); }}
.card {{ margin-top:22px; padding:18px; background:rgba(10,13,19,0.94); border-radius:22px; }}
.note {{ font-size:26px; color:{MUTED}; line-height:1.3; margin-bottom:10px; }}
.foot {{ font-size:23px; color:{MUTED}; margin-top:12px; line-height:1.35; }}
.lg {{ display:flex; flex-wrap:wrap; gap:8px 22px; font-size:24px; color:{MUTED}; margin-top:10px; }}
.lg span {{ display:flex; align-items:center; gap:8px; }}
.lg i {{ display:inline-block; width:22px; height:16px; border-radius:3px; }}
.pcs {{ display:flex; gap:16px; }}
.pc {{ flex:1; background:rgba(255,255,255,0.05); border-radius:16px; padding:14px 18px 8px; }}
.pct {{ font-size:24px; font-weight:800; line-height:1.25; margin-bottom:8px; min-height:56px; }}
.pcr {{ padding:10px 0; border-top:1.5px solid rgba(255,255,255,0.18); }}
.pcr b {{ display:block; font-size:44px; font-weight:800; line-height:1.05; letter-spacing:-0.02em; }}
.pcr span {{ font-size:25px; color:{MUTED}; }}
.todo {{ display:flex; flex-direction:column; gap:12px; }}
.td {{ display:flex; align-items:center; gap:16px; padding:10px 0; border-top:1.5px solid rgba(255,255,255,0.18); }}
.td:first-child {{ border-top:none; }}
.tdn {{ flex:0 0 52px; height:52px; border-radius:26px; border:3px solid #fff; text-align:center; font-size:28px; font-weight:800; line-height:46px; }}
.tdb {{ flex:1; }}
.tdi {{ font-size:32px; font-weight:800; line-height:1.1; }}
.tds {{ font-size:24px; color:{MUTED}; margin-top:4px; }}
.chip {{ flex:0 0 auto; border:3px solid; border-radius:14px; padding:8px 12px; font-size:24px; font-weight:800; text-align:center; line-height:1.25; }}
.chip span {{ display:block; font-size:23px; font-weight:600; color:{MUTED}; }}
.prom {{ display:flex; flex-direction:column; gap:14px; }}
.pr {{ border-left:6px solid {COL["CON"]}; padding:4px 0 4px 16px; }}
.pw {{ font-size:27px; font-weight:800; }}
.pw span {{ font-size:22px; font-weight:600; color:{MUTED}; margin-left:12px; }}
.pr ul {{ margin:6px 0 0 0; list-style:none; font-size:28px; line-height:1.3; }}
.pr li.gap {{ color:{MUTED}; }}
.explore {{ margin-top:18px; border:3px solid #5b9dff; border-radius:20px; padding:16px 22px; background:rgba(10,13,19,0.95); }}
.ex1 {{ font-size:33px; font-weight:800; }}
.ex2 {{ font-size:26px; color:{MUTED}; margin-top:6px; }}
.footer-logo {{ position:absolute; left:180px; bottom:56px; height:66px; filter:drop-shadow(0 2px 8px rgba(0,0,0,0.7)); }}
.pagenum {{ position:absolute; right:180px; bottom:56px; height:66px; line-height:66px; font-size:25px; font-weight:700; text-shadow:0 2px 8px rgba(0,0,0,0.8); }}
.source {{ position:absolute; left:180px; width:720px; bottom:22px; font-size:17px; color:#d5dae1; white-space:nowrap; overflow:hidden; text-shadow:0 1px 6px rgba(0,0,0,0.9); }}
.credit {{ position:absolute; top:146px; right:180px; font-size:15px; color:rgba(255,255,255,0.92); background:rgba(8,11,16,0.45); padding:2px 8px; border-radius:6px; }}
"""


def credit(k):
    d = PH.get(k, {})
    return d.get("credit") or f"Photo: {d.get('author', '')}, {d.get('licence', '')}"


def section(i, s, sid=None):
    k, pos, *size = PHOTO[i]
    cls = "slide cover" if s.get("cover") else "slide"
    return (f'<section class="{cls}" id="{sid or "s%d" % i}"><div class="photo" style="background-image:url(\'photos/{k}.jpg\');background-position:{pos}{";background-size:" + size[0] if size else ""}"></div>'
            f'<div class="shade"></div><div class="content"><div class="kicker">{esc(s["kicker"])}</div><h1>{esc(s["head"])}</h1>{s["body"]}</div>'
            f'<img class="footer-logo" src="logo-dark.png" alt="The Median Canadian">'
            f'<div class="pagenum">{"Swipe to learn more →" if i == 1 else f"{i}/{N}"}</div>'
            f'<div class="source">{esc(s["source"])}</div><div class="credit">{esc(credit(k))}</div></section>')


MEASURE = """(id) => { const s=document.getElementById(id), T=s.getBoundingClientRect().top, Lx=s.getBoundingClientRect().left;
 let bottom=0,left=1e9,right=0; for (const e of s.querySelector('.content').querySelectorAll('*')) { const r=e.getBoundingClientRect();
 if(!r.width&&!r.height) continue; bottom=Math.max(bottom,r.bottom-T); right=Math.max(right,r.right-Lx); left=Math.min(left,r.left-Lx);}
 const ex=[...s.querySelectorAll('.footer-logo,.pagenum,.source,.credit')].map(e=>{const r=e.getBoundingClientRect();return [r.left-Lx,r.right-Lx]});
 const logo=s.querySelector('.footer-logo'), src=s.querySelector('.source'), h=s.querySelector('h1');
 return {bottom,left,right,ex,logoTop:logo.getBoundingClientRect().top-T, logoOk:logo.complete&&logo.naturalWidth>0,
  srcOne:src.scrollWidth<=src.clientWidth+1, lines:Math.round(h.getBoundingClientRect().height/parseFloat(getComputedStyle(h).lineHeight)),
  clash:(()=>{const ts=[...s.querySelectorAll('svg text')].filter(t=>t.getAttribute('fill')!=='none');
    const bx=ts.map(t=>({r:t.getBoundingClientRect(), s:t.textContent})); const out=[];
    for(let i=0;i<bx.length;i++) for(let j=i+1;j<bx.length;j++){ const A=bx[i].r, B=bx[j].r, m=3;
      if(A.left<B.right+m && B.left<A.right+m && A.top<B.bottom+m && B.top<A.bottom+m) out.push(bx[i].s+' | '+bx[j].s); }
    return out;})(),
  leadLines:(()=>{const l=s.querySelector('.lead'); return l?Math.round(l.getBoundingClientRect().height/parseFloat(getComputedStyle(l).lineHeight)):0})()}; }"""

BANNED = [r"\blead(s|ing)?\b", r"\bnow\b", r"\btoday\b", r"\bcurrently\b", "—", r"\bwon\b", r"\blost\b", r"\bbeat\b", r"\bcarried\b", r"\bour (analysis|estimate|count)\b", r", not ", r"\bnot \w+, but\b",
          r"\btrack", r"\bwe will\b", r"\bvoters will\b", r"\binitial count\b", r"\bin (Ottawa|Victoria)\b"]


def main():
    SL = build(MAP_OPTION)
    # the page uses the slides' own headlines and lines, so the two never differ
    lead = lambda b: html.unescape(re.sub(r"<[^>]+>", "", (re.search(r'<p class="lead">(.*?)</p>', b) or [None, ""])[1])).strip()
    json.dump({"order": [x["key"] for x in SL], "kickers": {x["key"]: x["kicker"] for x in SL},
               "headlines": {x["key"]: x["head"] for x in SL}, "lines": {x["key"]: lead(x["body"]) for x in SL}},
              open(os.path.join(HERE, "..", "data", "slide_text.json"), "w"), indent=1, ensure_ascii=False)
    other = "B" if MAP_OPTION == "A" else "A"
    sections = "".join(section(i, s) for i, s in enumerate(SL, 1))
    text = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>B.C. election 2026</title><style>{CSS}</style></head><body>{sections}</body></html>"
    open(os.path.join(HERE, "slides.html"), "w").write(text)
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", text, flags=re.S)
    warn = [f"banned {p}: ...{vis[max(0, m.start() - 40):m.end() + 40]}..." for p in BANNED for m in re.finditer(p, vis, re.I)]
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    from playwright.sync_api import sync_playwright
    from PIL import Image
    ok = True
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto("file://" + os.path.join(HERE, "slides.html")); pg.wait_for_load_state("networkidle")
        for sid in [f"s{i}" for i in range(1, N + 1)]:
            m = pg.evaluate(MEASURE, sid)
            gap = m["logoTop"] - m["bottom"]; iss = []
            if gap < 18: iss.append(f"gap {gap:.0f}px to footer")
            if m["right"] > 901 or m["left"] < 179: iss.append(f"content outside reel-safe column ({m['left']:.0f} to {m['right']:.0f})")
            if any(a < 179 or b_ > 901 for a, b_ in m["ex"]): iss.append(f"footer outside column {m['ex']}")
            if not m["srcOne"]: iss.append("source line wraps")
            if not m["logoOk"]: iss.append("logo missing")
            if m["lines"] > 2: iss.append(f"headline runs {m['lines']} lines")
            if m["leadLines"] > 2: iss.append(f"line under the headline runs {m['leadLines']} lines")
            if m["clash"]: iss.append("labels touch: " + "; ".join(m["clash"][:4]))
            ok &= not iss
            print(f"{sid}: bottom {m['bottom']:.0f}, footer {m['logoTop']:.0f}, gap {gap:.0f}, heading {m['lines']} lines, line {m['leadLines']}", "!! " + "; ".join(iss) if iss else "ok")
            name = f"the-median-canadian-bc-election-{sid[1:]}-of-{N}"
            f = os.path.join(OUTDIR, name + ".png")
            pg.locator(f"#{sid}").screenshot(path=f)
            Image.open(f).convert("RGB").save(f[:-4] + ".jpg", quality=92)
        b.close()
    ims = [Image.open(os.path.join(OUTDIR, f"the-median-canadian-bc-election-{i}-of-{N}.jpg")) for i in range(1, N + 1)]
    tw, th = 360, 450
    sheet = Image.new("RGB", (tw * 4 + 50, th * 2 + 30), "white")
    for k, im in enumerate(ims):
        sheet.paste(im.resize((tw, th)), (10 + (k % 4) * (tw + 10), 10 + (k // 4) * (th + 10)))
    sheet.save(os.path.join(OUTDIR, "contact-sheet.jpg"), quality=90)
    for w in warn: print("WARNING", w)
    sys.exit(0 if ok and not warn else 1)


if __name__ == "__main__":
    main()
