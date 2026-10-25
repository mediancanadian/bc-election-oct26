"""Topology-preserving simplification with separate tolerances for outer arcs (coast / provincial border,
used by one polygon) and inner arcs (shared by two districts). Arcs are built by the topojson package
(no quantization), each arc is simplified with Douglas-Peucker keeping its end nodes, so neighbouring
districts still share identical edges (no gaps, no overlaps)."""
import copy, json
import shapely
import numpy as np
import geopandas as gpd
import topojson as tp
from shapely.geometry import LineString, shape
from shapely.validation import make_valid


def _walk(geom, out):
    t = geom["type"]
    if t == "Polygon":
        for ring in geom["arcs"]:
            out.extend(ring)
    elif t == "MultiPolygon":
        for poly in geom["arcs"]:
            for ring in poly:
                out.extend(ring)
    elif t == "GeometryCollection":
        for g in geom["geometries"]:
            _walk(g, out)


CHUNK = 60
_MEMO = {}


def build(gdf_3005):
    T = tp.Topology(gdf_3005, prequantize=False, topology=True)
    return T


def simplify(gdf_3005, tol_outer, tol_inner, min_ring_area=0.0, k=None, tmin=0.0, tmax=None, mult=None, T=None, arc_mult=None, arc_cap=None):
    """Fixed tolerances (tol_outer for unshared arcs, tol_inner for shared arcs), or, when k is given,
    tolerance per arc = clip(k * sqrt(area of smallest district using the arc), tmin, tmax)."""
    if T is None:
        T = build(gdf_3005)
    simplify.last_T = T
    out = T.output
    use = np.zeros(len(out["arcs"]), int)
    minA = np.full(len(out["arcs"]), np.inf)
    minM = np.ones(len(out["arcs"]))
    areas = gdf_3005.area.values
    obj = list(out["objects"].values())[0]
    for fi, geom in enumerate(obj["geometries"]):
        refs = []
        _walk(geom, refs)
        for a in set(x if x >= 0 else ~x for x in refs):
            use[a] += 1
            minA[a] = min(minA[a], areas[fi])
            if mult is not None:
                minM[a] = min(minM[a], mult[fi])
    T2 = copy.deepcopy(T)
    new_arcs = []
    simplify.chunk_index = []  # (arc, chunk, x0, y0, x1, y1) for repair targeting
    for i, arc in enumerate(out["arcs"]):
        if k is not None:
            base = float(np.clip(k * np.sqrt(minA[i]), tmin, tmax if tmax else np.inf)) * minM[i]
            if arc_cap is not None and arc_cap.get(i) is not None:
                base = min(base, arc_cap[i])
        else:
            base = tol_outer if use[i] <= 1 else tol_inner
        a = np.asarray(arc, float)
        closed = len(a) > 3 and tuple(a[0]) == tuple(a[-1])
        cs = (arc_mult or {}).get(("cs", i), len(a))
        nch = max(1, int(np.ceil((len(a) - 1) / cs)))
        res = []
        for c in range(nch):
            seg = a[c * cs: min(len(a), (c + 1) * cs + 1)]
            tol = base * ((arc_mult or {}).get((i, c), 1.0) if nch > 1 else (arc_mult or {}).get((i, -1), 1.0))
            simplify.chunk_index.append((i, c if nch > 1 else -1, seg[:, 0].min(), seg[:, 1].min(), seg[:, 0].max(), seg[:, 1].max(), nch))
            key = (i, c, cs, round(tol, 3))
            if key in _MEMO:
                sc = _MEMO[key]
            else:
                sc = np.asarray(LineString(seg).simplify(tol, preserve_topology=True).coords) if (len(seg) > 2 and tol > 0) else seg
                _MEMO[key] = sc
            res.append(sc if c == 0 else sc[1:])
        c2 = np.vstack(res)
        if closed and len(c2) < 4:
            idx = np.linspace(0, len(a) - 1, 4).astype(int)
            c2 = a[idx]
        new_arcs.append(c2.tolist())
    T2.output["arcs"] = new_arcs
    simplify.last_output = T2.output
    g = T2.to_gdf()
    g = g.set_crs(gdf_3005.crs, allow_override=True)
    g["geometry"] = [make_valid(x) for x in g.geometry]
    if min_ring_area > 0:
        g["geometry"] = g.geometry.apply(lambda x: drop_small_parts(x, min_ring_area))
    return g, use


def drop_small_parts(geom, min_area):
    from shapely.geometry import MultiPolygon, Polygon
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon"]
    if not polys:
        return geom
    big = max(polys, key=lambda p: p.area)
    keep = [p for p in polys if p.area >= min_area or p is big]
    return MultiPolygon(keep) if len(keep) > 1 else keep[0]


def polygons_only(geom):
    from shapely.geometry import MultiPolygon
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    polys = []
    for p in getattr(geom, "geoms", []):
        if p.geom_type == "Polygon":
            polys.append(p)
        elif p.geom_type == "MultiPolygon":
            polys.extend(p.geoms)
    return MultiPolygon(polys) if len(polys) > 1 else polys[0]


def write_topojson(output, src_crs, fn, quant=1e5, object_name="districts", keep=None):
    """Write a TopoJSON (EPSG:4326, quantized, delta-encoded) from a topojson output dict whose arcs are
    in src_crs. Arcs are reprojected vertex by vertex, so no vertices are dropped (keeps curved parallels)."""
    from pyproj import Transformer
    tr = Transformer.from_crs(src_crs, 4326, always_xy=True)
    arcs = []
    for arc in output["arcs"]:
        a = np.asarray(arc, float)
        x, y = tr.transform(a[:, 0], a[:, 1])
        arcs.append(np.column_stack([x, y]))
    allp = np.vstack(arcs)
    x0, y0 = allp.min(0)
    x1, y1 = allp.max(0)
    sx, sy = (x1 - x0) / (quant - 1), (y1 - y0) / (quant - 1)
    qarcs = []
    for a in arcs:
        q = np.round((a - [x0, y0]) / [sx, sy]).astype(np.int64)
        keepm = np.ones(len(q), bool)
        keepm[1:] = np.any(q[1:] != q[:-1], axis=1)
        q = q[keepm]
        if len(q) < 2:
            q = np.vstack([q, q])
        d = np.vstack([q[:1], np.diff(q, axis=0)])
        qarcs.append(d.tolist())
    obj = copy.deepcopy(list(output["objects"].values())[0])
    if keep is not None:
        for g in obj["geometries"]:
            g["properties"] = {k: v for k, v in g.get("properties", {}).items() if k in keep}
    for g in obj["geometries"]:
        g.pop("id", None)
    topo = {"type": "Topology", "transform": {"scale": [sx, sy], "translate": [x0, y0]},
            "bbox": [x0, y0, x1, y1], "objects": {object_name: obj}, "arcs": qarcs}
    with open(fn, "w") as f:
        json.dump(topo, f, separators=(",", ":"))


def write_geojson_compact(gdf4326, fn, dp, props):
    """RFC 7946 GeoJSON, compact separators, coordinates rounded to dp decimals; consecutive duplicate points removed."""
    from shapely.geometry.polygon import orient
    def ring(r):
        c = np.round(np.asarray(r.coords), dp)
        keep = np.ones(len(c), bool); keep[1:] = np.any(c[1:] != c[:-1], axis=1)
        c = c[keep]
        return [[float(x) if dp else int(x) for x in pt] for pt in c.tolist()]
    feats = []
    for _, r in gdf4326.iterrows():
        polys = [orient(p, 1.0) for p in shapely.get_parts(polygons_only(r.geometry))]
        coords = [[ring(p.exterior)] + [ring(h) for h in p.interiors] for p in polys]
        geom = {"type": "MultiPolygon", "coordinates": coords} if len(coords) > 1 else {"type": "Polygon", "coordinates": coords[0]}
        pr = {k: (v.item() if hasattr(v, "item") else v) for k, v in r[props].items()}
        feats.append({"type": "Feature", "properties": pr, "geometry": geom})
    with open(fn, "w") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f, separators=(",", ":"), ensure_ascii=False)


def grid_arcs(output, src_crs, step, dst_crs=4326, coarse=1, fine=frozenset()):
    """Reproject every arc vertex to dst_crs (None = keep) and snap to a grid; returns integer arcs in units of `step`.
    Interior vertices of arcs not in `fine` snap to the coarser lattice step*coarse (a subset of the fine lattice);
    arc end nodes always snap to `step`, so arcs meeting at a node agree exactly. Shared arcs are snapped once,
    so neighbouring districts stay identical."""
    from pyproj import Transformer
    tr = Transformer.from_crs(src_crs, dst_crs, always_xy=True) if dst_crs is not None else None
    arcs = []
    for i, arc in enumerate(output["arcs"]):
        a = np.asarray(arc, float)
        x, y = tr.transform(a[:, 0], a[:, 1]) if tr else (a[:, 0], a[:, 1])
        xy = np.column_stack([x, y])
        if coarse > 1 and i not in fine:
            q = np.round(xy / (step * coarse)).astype(np.int64) * coarse
            q[0] = np.round(xy[0] / step)
            q[-1] = np.round(xy[-1] / step)
        else:
            q = np.round(xy / step).astype(np.int64)
        keep = np.ones(len(q), bool)
        keep[1:] = np.any(q[1:] != q[:-1], axis=1)
        q = q[keep]
        if len(q) < 2:
            q = np.vstack([q, q])
        arcs.append(q)
    return arcs


def _ring_coords(refs, arcs):
    pts = []
    for a in refs:
        c = arcs[a] if a >= 0 else arcs[~a][::-1]
        pts.extend(c.tolist() if not pts else c[1:].tolist())
    return pts


def decode(output, arcs, step):
    """Build shapely geometries (EPSG:4326) from integer arcs. Returns list of (properties, geometry)."""
    from shapely.geometry import Polygon, MultiPolygon
    obj = list(output["objects"].values())[0]
    res = []
    for g in obj["geometries"]:
        polys = []
        plist = [g["arcs"]] if g["type"] == "Polygon" else (g["arcs"] if g["type"] == "MultiPolygon" else [])
        for poly in plist:
            rings = [np.asarray(_ring_coords(r, arcs), float) * step for r in poly]
            rings = [r for r in rings if len(r) >= 4]
            if rings:
                polys.append(Polygon(rings[0], rings[1:]))
        geom = MultiPolygon(polys) if len(polys) != 1 else polys[0]
        res.append((g.get("properties", {}), geom))
    return res


def write_grid_topojson(output, arcs, step, fn, object_name="districts", keep=None):
    allp = np.vstack(arcs)
    x0, y0 = allp.min(0)
    qarcs = []
    for a in arcs:
        q = a - [x0, y0]
        qarcs.append(np.vstack([q[:1], np.diff(q, axis=0)]).tolist())
    obj = copy.deepcopy(list(output["objects"].values())[0])
    for g in obj["geometries"]:
        g.pop("id", None)
        if keep is not None:
            g["properties"] = {k: v for k, v in g.get("properties", {}).items() if k in keep}
    x1, y1 = allp.max(0)
    dp = max(0, int(round(-np.log10(step))))
    topo = {"type": "Topology", "transform": {"scale": [step, step], "translate": [round(float(x0 * step), dp), round(float(y0 * step), dp)]},
            "bbox": [round(float(x0 * step), dp), round(float(y0 * step), dp), round(float(x1 * step), dp), round(float(y1 * step), dp)],
            "objects": {object_name: obj}, "arcs": qarcs}
    with open(fn, "w") as f:
        json.dump(topo, f, separators=(",", ":"))


def write_grid_geojson(decoded, step, fn, keep):
    from shapely.geometry.polygon import orient
    dp = max(0, int(round(-np.log10(step))))
    def ring(r):
        c = np.round(np.asarray(r.coords), dp)
        return [[round(float(x), dp), round(float(y), dp)] for x, y in c.tolist()]
    feats = []
    for pr, geom in decoded:
        polys = [orient(p, 1.0) for p in shapely.get_parts(geom)]
        coords = [[ring(p.exterior)] + [ring(h) for h in p.interiors] for p in polys]
        gj = {"type": "MultiPolygon", "coordinates": coords} if len(coords) > 1 else {"type": "Polygon", "coordinates": coords[0]}
        feats.append({"type": "Feature", "properties": {k: pr.get(k) for k in keep}, "geometry": gj})
    with open(fn, "w") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f, separators=(",", ":"), ensure_ascii=False)


SPLIT = 150
MAXCH = 20


def valid_pipeline(gdf_3005, k, tmin, tmax, mult, grids, max_iter=40, log=print, R_=1500, init_am=None, cap_fn=None):
    """simplify -> snap to each output grid -> decode -> validate. grids = [(dst_crs or None, step), ...].
    Invalidities are repaired locally: a long arc near the problem is split into SPLIT-vertex chunks, and chunks near
    the problem get their tolerance cut (x0.4, then 0 = full detail) until every geometry in every grid is valid.
    Returns (output, {grid: (arcs, decoded)}, repair_state)."""
    from shapely.validation import explain_validity
    from pyproj import Transformer
    import re
    T = build(gdf_3005)
    am = {} if init_am is None else dict(init_am)
    fine = set(am.pop("fine", set())) if isinstance(am.get("fine"), set) else set()
    caps = {i: cap_fn(arc) for i, arc in enumerate(T.output["arcs"])} if cap_fn else None
    valid_pipeline.caps = caps
    for it in range(max_iter):
        simplify(gdf_3005, 0, 0, k=k, tmin=tmin, tmax=tmax, mult=mult, T=T, arc_mult=am, arc_cap=caps)
        out = simplify.last_output
        res, pts = {}, []
        for gr in grids:
            dst, step = gr[0], gr[1]
            coarse = gr[2] if len(gr) > 2 else 1
            arcs = grid_arcs(out, "EPSG:3005", step, dst, coarse, fine)
            dec = decode(out, arcs, step)
            res[(dst, step)] = (arcs, dec)
            back = Transformer.from_crs(dst, 3005, always_xy=True) if dst is not None else None
            for (x, y) in arc_crossings(arcs, step):
                pts.append(back.transform(x, y) if back else (x, y))
            for pr, g in dec:
                if not g.is_valid:
                    mm = re.search(r"\[([-0-9.e]+) ([-0-9.e]+)\]", explain_validity(g))
                    if mm:
                        x, y = float(mm.group(1)), float(mm.group(2))
                        pts.append(back.transform(x, y) if back else (x, y))
        if not pts:
            log("valid after %d repair rounds; arcs split %d, chunks reduced %d, fine-grid arcs %d" % (it, sum(1 for q in am if q[0] == "cs"), sum(1 for q in am if q[0] != "cs"), len(fine)))
            am["fine"] = set(fine)
            return out, res, am
        hit = 0
        arcs_orig = T.output["arcs"]
        for (i, c, x0, y0, x1, y1, nch) in simplify.chunk_index:
            for (x, y) in pts:
                if x0 - R_ <= x <= x1 + R_ and y0 - R_ <= y <= y1 + R_:
                    if i not in fine and any(len(gr) > 2 and gr[2] > 1 for gr in grids):
                        fine.add(i)
                    elif c == -1 and len(arcs_orig[i]) > 2 * SPLIT:
                        am[("cs", i)] = max(SPLIT, len(arcs_orig[i]) // MAXCH)
                    else:
                        v = am.get((i, c), 1.0)
                        am[(i, c)] = v * 0.4 if v > 0.02 else 0.0
                    hit += 1
                    break
        log("round %d: %d invalid points; adjusted %d" % (it, len(pts), hit))
    raise RuntimeError("could not make valid")


def arc_crossings(arcs, step):
    """Points where two different snapped arcs (or one arc with itself) touch or cross anywhere other than at
    shared arc end nodes. Such contacts create overlaps or gaps between districts even when every polygon is valid."""
    lines = [shapely.LineString(np.asarray(a, float) * step) if len(a) >= 2 else None for a in arcs]
    ends = {}
    for i, a in enumerate(arcs):
        for e in (tuple(a[0]), tuple(a[-1])):
            ends.setdefault(e, set()).add(i)
    idx = [i for i, l in enumerate(lines) if l is not None and l.length > 0]
    geoms = np.array([lines[i] for i in idx], dtype=object)
    tree = shapely.STRtree(geoms)
    A, B = tree.query(geoms, predicate="intersects")
    pts = []
    for ia, ib in zip(A, B):
        if ia >= ib:
            continue
        i, j = idx[ia], idx[ib]
        inter = shapely.intersection(lines[i], lines[j])
        for g in shapely.get_parts(inter):
            for c in (g.coords if g.geom_type == "Point" else list(g.coords)):
                key = (int(round(c[0] / step)), int(round(c[1] / step)))
                if key in ends and i in ends[key] and j in ends[key]:
                    continue
                pts.append((c[0], c[1]))
    # self-crossing of an arc (non-simple line)
    for i in idx:
        if not lines[i].is_simple:
            closed = tuple(arcs[i][0]) == tuple(arcs[i][-1])
            if closed and shapely.Polygon(lines[i].coords).is_valid:
                continue
            co = np.asarray(lines[i].coords)
            segs = [shapely.LineString(co[k:k + 2]) for k in range(len(co) - 1)]
            st = shapely.STRtree(segs)
            sa, sb = st.query(segs, predicate="intersects")
            for u, v in zip(sa, sb):
                if v > u + 1 and not (closed and u == 0 and v == len(segs) - 1):
                    q = shapely.intersection(segs[u], segs[v]).representative_point()
                    pts.append((q.x, q.y))
    return pts
