#!/usr/bin/env python3
"""Detailed riding maps for the zoomed views: slide 3 (Metro Vancouver) and the page's Metro Vancouver,
Victoria area and Okanagan views.

The province-wide map files are simplified for a map of all of B.C.; zoomed into a city, that simplification
shows as angular edges, and water drawn as background reads as black gaps. For each zoomed view this script:
- cuts the full-resolution riding master (Elections BC 2023 boundaries, clipped to land, lakes of 50 km2 or more
  removed) to the view and simplifies the riding coverage lightly, so neighbouring ridings keep one shared edge;
- adds water to draw over the land: lakes of 1 km2 or more and rivers of 50 ha or more (BC Freshwater Atlas);
- adds the B.C. mask: Elections BC's published boundaries before land clipping, which run out to the
  international boundary, so B.C. water can be drawn as water and the United States left blank;
- keeps riding borders only where two ridings meet, never along a shore or the edge of the view.

python3 build_map_detail.py
-> ../data/geo/DETAIL_metro_vancouver_{4326,water_4326,frame_4326}.geojson (slide 3; frame south edge on the border)
-> ../data/geo/site_map_detail.json (page zooms metro, vic, okan: one TopoJSON topology each)
"""
import os, json
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from shapely.geometry import Polygon, box, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "geo")
GEO = os.path.join(HERE, "geo")             # analysis/geo: the geography thread (raw downloads in geo/raw, see REPRODUCE.md)
MASTER = f"{GEO}/out/final/FINAL_ed2023_land_lakes_3005.gpkg"           # land-clipped riding master
PUBLISHED = f"{GEO}/raw/bcgw/ed2023.geojson"                             # Elections BC boundaries as published (over water)
LAKES = f"{GEO}/raw/fwa/fwa_lakes_ge100ha.geojson"                       # Freshwater Atlas lakes of 1 km2 or more
RIVERS = {"slide": f"{GEO}/raw/fwa_rivers/fwa_rivers_metro.geojson", "metro": f"{GEO}/raw/fwa_rivers/fwa_rivers_metro_site.geojson",
          "vic": f"{GEO}/raw/fwa_rivers/fwa_rivers_vic.geojson", "okan": f"{GEO}/raw/fwa_rivers/fwa_rivers_okan.geojson"}
UTM = 26910                                  # NAD83 / UTM zone 10N (metres), used for all cutting and simplifying
# views: west, south, east, north (degrees). The page views cover what the page map shows for each zoom, plus a margin.
VIEWS = {"slide": (-123.285, 49.0, -122.25, 49.40), "metro": (-123.36, 48.90, -122.36, 49.50),
         "vic": (-123.96, 48.25, -123.03, 48.80), "okan": (-120.70, 49.25, -118.36, 50.60)}
TOL = {"slide": 12, "metro": 15, "vic": 15, "okan": 35}   # metres, about 0.15 px at each view's scale

to_utm = Transformer.from_crs(4326, UTM, always_xy=True)
master = gpd.read_file(MASTER).to_crs(UTM)
published = gpd.read_file(PUBLISHED).to_crs(UTM)
lakes_all = gpd.read_file(LAKES).to_crs(UTM)


def frame_of(w, s, e, n):
    """Lon-lat rectangle traced along its meridians and parallels every 0.01 degree."""
    lons = np.arange(w, e + 1e-9, 0.01); lats = np.arange(s, n + 1e-9, 0.01)
    ring = [(x, s) for x in lons] + [(e, y) for y in lats] + [(x, n) for x in lons[::-1]] + [(w, y) for y in lats[::-1]]
    return Polygon([to_utm.transform(x, y) for x, y in ring])


def polys_only(g):
    """Polygonal part of a geometry (a cut along the view edge can leave stray lines or points)."""
    parts = [p for p in shapely.get_parts(g) if p.geom_type in ("Polygon", "MultiPolygon")]
    return unary_union(parts) if parts else shapely.geometry.Polygon()


def view(key):
    fr = frame_of(*VIEWS[key]); tol = TOL[key]
    d = master[master.intersects(fr)].copy()
    d["geometry"] = [polys_only(g) for g in d.geometry.intersection(fr)]
    d = d[~d.geometry.is_empty]
    d["geometry"] = shapely.coverage_simplify(d.geometry.values, tol, simplify_boundary=True)
    d["geometry"] = d.geometry.make_valid()
    lk = lakes_all[lakes_all.intersects(fr)].copy()
    lk["geometry"] = [polys_only(g).simplify(tol) for g in lk.geometry.intersection(fr)]
    rv = gpd.read_file(RIVERS[key]).to_crs(UTM)
    rv = rv[(rv.AREA_HA >= 50) & rv.intersects(fr)].copy()
    rv["geometry"] = [polys_only(g).simplify(tol) for g in rv.geometry.intersection(fr)]
    cols = {"GNIS_NAME_1": "name", "AREA_HA": "area_ha"}
    water = gpd.GeoDataFrame(pd.concat([lk[["GNIS_NAME_1", "AREA_HA", "geometry"]].rename(columns=cols).assign(kind="lake"),
                                        rv[["GNIS_NAME_1", "AREA_HA", "geometry"]].rename(columns=cols).assign(kind="river")],
                                       ignore_index=True), crs=UTM)
    water = water[~water.geometry.is_empty]
    land = unary_union(d.geometry.values)
    borders = unary_union([g.boundary for g in d.geometry]).difference(land.boundary.buffer(1.0))
    mask = polys_only(unary_union(published[published.intersects(fr)].geometry.values).intersection(fr)).simplify(tol)
    return fr, d, water, borders, mask


def to4326(geom):
    return gpd.GeoSeries([geom], crs=UTM).to_crs(4326).iloc[0]


def d3_geom(geom, nd=5):
    """GeoJSON geometry for d3-geo: exterior rings clockwise (d3's spherical convention), coordinates rounded."""
    def fix(p):
        return orient(p, sign=-1.0)
    if geom.geom_type == "Polygon":
        geom = fix(geom)
    elif geom.geom_type == "MultiPolygon":
        geom = shapely.geometry.MultiPolygon([fix(p) for p in geom.geoms])
    elif geom.geom_type == "GeometryCollection":
        polys = [p for g in geom.geoms for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon"]
        geom = shapely.geometry.MultiPolygon([fix(p) for p in polys])
    m = mapping(geom)
    def rnd(c):
        return [round(c[0], nd), round(c[1], nd)] if isinstance(c[0], float) else [rnd(x) for x in c]
    m["coordinates"] = rnd(m["coordinates"])
    return m


os.makedirs(OUT, exist_ok=True)
# slide 3: Metro Vancouver, south edge on the 49th parallel
fr, d, water, borders, mask = view("slide")
gpd.GeoDataFrame(d[["ed_code", "ed_name"]], geometry=d.geometry, crs=UTM).to_crs(4326).to_file(
    os.path.join(OUT, "DETAIL_metro_vancouver_4326.geojson"), driver="GeoJSON", COORDINATE_PRECISION=6)
water.to_crs(4326).to_file(os.path.join(OUT, "DETAIL_metro_vancouver_water_4326.geojson"), driver="GeoJSON", COORDINATE_PRECISION=6)
gpd.GeoDataFrame({"name": ["Metro Vancouver frame"]}, geometry=[fr], crs=UTM).to_crs(4326).to_file(
    os.path.join(OUT, "DETAIL_metro_vancouver_frame_4326.geojson"), driver="GeoJSON", COORDINATE_PRECISION=6)
print("slide: ridings", len(d), "water", len(water), "vertices", int(sum(shapely.get_num_coordinates(g) for g in d.geometry)))

# page zooms: one TopoJSON topology per view, objects districts, water and mask; borders are drawn on the page
# with topojson.mesh between different ridings only
import topojson as tp
site = {}
for key in ("metro", "vic", "okan"):
    fr, d, water, borders, mask = view(key)
    dist = gpd.GeoDataFrame({"ed_code": d.ed_code.values}, geometry=[shapely.geometry.shape(d3_geom(to4326(g))) for g in d.geometry], crs=4326)
    wat = gpd.GeoDataFrame({"name": water["name"].fillna("").values, "kind": water.kind.values},
                           geometry=[shapely.geometry.shape(d3_geom(to4326(g))) for g in water.geometry], crs=4326)
    msk = gpd.GeoDataFrame({"name": ["B.C."]}, geometry=[shapely.geometry.shape(d3_geom(to4326(mask)))], crs=4326)
    topo = tp.Topology([dist, wat, msk], object_name=["districts", "water", "mask"], prequantize=200000, topology=True, shared_coords=False)
    site[key] = json.loads(topo.to_json())
    print(key, "ridings", len(d), "water", len(water), "vertices", int(sum(shapely.get_num_coordinates(g) for g in d.geometry)))
p = os.path.join(OUT, "site_map_detail.json")
json.dump(site, open(p, "w"), separators=(",", ":"))
print("site_map_detail.json", os.path.getsize(p) // 1024, "KB")
