"""Step 3 of map build: label anchors (pole of inaccessibility on largest land part, shapely.polylabel, tolerance 10 m)
and visual check PNGs: simplified outline (orange) over full-resolution clipped outline (blue), EPSG:3005,
province + Metro Vancouver + Capital Region + Kelowna, at 720 px and 1440 px wide.
Usage: python3 -I 12_maps_render_labels.py <tag e.g. s10m>
"""
import sys, os, json
import geopandas as gpd, shapely, numpy as np
from shapely.ops import polylabel
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

tag = sys.argv[1]
ROOT = "analysis/census"; M = os.path.join(ROOT, "maps"); C = os.path.join(M, "checks"); os.makedirs(C, exist_ok=True)
full = gpd.read_file(os.path.join(M, "ed2023_full_clipped_3005.gpkg")).sort_values("ed_code").reset_index(drop=True)
simp = gpd.read_file(os.path.join(M, "ed2023_clipped_%s_3005.gpkg" % tag)).sort_values("ed_code").reset_index(drop=True)

# label anchors from full-resolution clipped geometry
rows = []
for code, name, g in zip(full.ed_code, full.ed_name, full.geometry):
    parts = list(shapely.get_parts(g)); big = max(parts, key=lambda p: p.area)
    p = polylabel(big, tolerance=10)
    inside_s = simp.loc[simp.ed_code == code, "geometry"].iloc[0].contains(p)
    d = big.exterior.distance(p)
    for r in big.interiors:
        d = min(d, r.distance(p))
    rows.append(dict(ed_code=code, ed_name=name, x_3005=round(p.x, 1), y_3005=round(p.y, 1), inside_full=bool(g.contains(p)),
                     inside_simplified=bool(inside_s), dist_to_edge_m=round(d, 1), geometry=p))
lab = gpd.GeoDataFrame(rows, crs=3005)
ll = lab.to_crs(4326); lab["lon"] = ll.geometry.x.round(6); lab["lat"] = ll.geometry.y.round(6)
lab.to_file(os.path.join(M, "ed2023_label_points_3005.gpkg"), driver="GPKG")
lab.drop(columns="geometry").to_csv(os.path.join(M, "ed2023_label_points.csv"), index=False)
print("labels inside full:", lab.inside_full.all(), "inside simplified:", lab.inside_simplified.all(),
      "min dist to edge m:", lab.dist_to_edge_m.min())

# extents in EPSG:3005 derived from official district geometry (no hand-drawn boxes)
def ext(codes, pad=0.06):
    b = full[full.ed_code.isin(codes)].total_bounds; w, h = b[2] - b[0], b[3] - b[1]
    return (b[0] - w * pad, b[1] - h * pad, b[2] + w * pad, b[3] + h * pad)

METRO = ["VNW", "VNY", "VNS", "VNT", "VNP", "VNQ", "VLA", "VFV", "VHA", "VKE", "VLM", "VNR", "BNC", "BNE", "BNN", "BNO", "BNS",
         "RCB", "RCC", "RCQ", "RCS", "NVL", "NVS", "WVC", "NMC", "CQM", "POM", "POC", "DLN", "SRC", "SRG", "SUN", "SRF", "SRN"]
CRD = ["VTB", "VTS", "OBG", "SAS", "ESC", "LFH"]
KEL = ["KEC", "KLM", "KLC", "WKP"]
views = {"province": tuple(full.total_bounds), "metro_vancouver": ext(METRO), "capital_region": ext(CRD), "kelowna": ext(KEL)}
out = {}
for vname, (x0, y0, x1, y1) in views.items():
    for px in (720, 1440):
        aspect = (y1 - y0) / (x1 - x0); dpi = 144
        fig = plt.figure(figsize=(px / dpi, px * aspect / dpi), dpi=dpi); ax = fig.add_axes([0, 0, 1, 1])
        box = shapely.box(x0, y0, x1, y1)
        f = full[full.intersects(box)]; s = simp[simp.intersects(box)]
        lw = 0.6 if px == 720 else 0.8
        f.boundary.plot(ax=ax, color="#1f5fbf", linewidth=lw * 1.8)
        s.boundary.plot(ax=ax, color="#ff7a00", linewidth=lw * 0.7)
        if vname != "province":
            lab[lab.intersects(box)].plot(ax=ax, color="black", markersize=4)
            for _, r in lab[lab.intersects(box)].iterrows():
                ax.annotate(r.ed_code, (r.x_3005, r.y_3005), fontsize=5 if px == 720 else 7, ha="center", va="bottom")
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")
        fn = os.path.join(C, "check_%s_%s_%dpx.png" % (vname, tag, px))
        fig.savefig(fn, dpi=dpi, facecolor="white"); plt.close(fig); out[fn] = px
print(json.dumps(list(out), indent=0))
