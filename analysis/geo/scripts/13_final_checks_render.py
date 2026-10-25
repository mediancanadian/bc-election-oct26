"""Check renders (EPSG:3005) into geo/checks/:
 - check_{view}_{720,1440}px.png: full-resolution master outline (blue, thick) under the simplified outline (orange, thin);
   province and slide views use the slide720 file at 720 px and the web file at 1440 px; insets use the web file.
 - check_filled_lakes_{720,1440}px.png: districts filled (muted categorical), lakes >= 50 km2 in light blue, plus insets.
 - check_labels_1440px.png: label anchors on the web file.
 - check_pcn_artifact.png: zoom on the removed 0.003 m2 gap in Peace River North (census check image dot)."""
import os
import geopandas as gpd, matplotlib, numpy as np, pandas as pd, shapely
matplotlib.use("Agg")
import matplotlib.pyplot as plt

F = "analysis/geo/out/final/"
C = "analysis/geo/checks/"
os.makedirs(C, exist_ok=True)
master = gpd.read_file(F + "FINAL_ed2023_land_lakes_3005.gpkg")
web = gpd.read_file(F + "FINAL_ed2023_land_lakes_web_3005.geojson").set_crs(3005, allow_override=True)
slide = gpd.read_file(F + "FINAL_ed2023_land_lakes_slide720_3005.geojson").set_crs(3005, allow_override=True)
lakes = gpd.read_file(F + "FINAL_lakes_ge50km2_3005.gpkg")
labels = pd.read_csv(F + "FINAL_ed2023_label_points.csv")
reg = dict(zip(web.ed_code, web.rd_abbr))
INS = {"metro_vancouver": "MVRD", "capital_region": "CAPRD", "kelowna": "RDCO"}


def ext(codes, pad=0.06):
    b = master[master.ed_code.isin(codes)].total_bounds
    w, h = b[2] - b[0], b[3] - b[1]
    return (b[0] - w * pad, b[1] - h * pad, b[2] + w * pad, b[3] + h * pad)


VIEWS = {"province": tuple(master.total_bounds)}
for k, abbr in INS.items():
    VIEWS[k] = ext([c for c, r in reg.items() if r == abbr])


def fig_for(view, px):
    x0, y0, x1, y1 = VIEWS[view]
    dpi = 144
    fig = plt.figure(figsize=(px / dpi, px * (y1 - y0) / (x1 - x0) / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax, dpi


def clip_view(g, view):
    x0, y0, x1, y1 = VIEWS[view]
    return g.cx[x0:x1, y0:y1]


out = []
for view in VIEWS:
    for px in (720, 1440):
        simp = slide if (view == "province" and px == 720) else web
        sname = "slide720" if simp is slide else "web"
        fig, ax, dpi = fig_for(view, px)
        clip_view(master, view).boundary.plot(ax=ax, color="#2f6fd6", lw=1.6 if px == 1440 else 1.2)
        clip_view(simp, view).boundary.plot(ax=ax, color="#f07a1a", lw=0.5)
        ax.text(0.01, 0.01, f"blue = full-resolution master, orange = {sname} file; {view}, {px}px", transform=ax.transAxes, fontsize=6)
        fn = C + f"check_{view}_{px}px.png"
        fig.savefig(fn, dpi=dpi, facecolor="white"); plt.close(fig); out.append(fn)

PAL = ["#c9d7c1", "#e6d5b8", "#d6c7de", "#f0e1a8", "#bfd3dd", "#e3c4c0", "#d2dcb0", "#cfc6b6"]
# greedy colouring so neighbours differ
nb = {c: set() for c in web.ed_code}
g = web.geometry.values
a, b = shapely.STRtree(g).query(g, predicate="intersects")
for i, j in zip(a, b):
    if i != j:
        nb[web.ed_code.iloc[i]].add(web.ed_code.iloc[j])
col = {}
for c in sorted(nb, key=lambda c: -len(nb[c])):
    used = {col.get(n) for n in nb[c]}
    col[c] = next(p for p in PAL if p not in used)
for px in (720, 1440):
    simp = slide if px == 720 else web
    x0, y0, x1, y1 = VIEWS["province"]
    dpi = 144
    W = px
    H = int(px * 0.62)
    fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 0.58, 1])
    simp.plot(ax=ax, color=[col[c] for c in simp.ed_code], edgecolor="#555", lw=0.25)
    lakes.plot(ax=ax, color="#a9d3f0", edgecolor="#7fb6de", lw=0.1)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")
    for k, pos in zip(INS, [[0.59, 0.36, 0.40, 0.63], [0.59, 0.0, 0.20, 0.35], [0.795, 0.0, 0.20, 0.35]]):
        a2 = fig.add_axes(pos)
        v = clip_view(web, k)
        v.plot(ax=a2, color=[col[c] for c in v.ed_code], edgecolor="#555", lw=0.3)
        clip_view(lakes, k).plot(ax=a2, color="#a9d3f0", edgecolor="#7fb6de", lw=0.1)
        X0, Y0, X1, Y1 = VIEWS[k]
        a2.set_xlim(X0, X1); a2.set_ylim(Y0, Y1); a2.set_aspect("equal"); a2.set_xticks([]); a2.set_yticks([]); a2.set_xlabel(""); a2.set_ylabel("")
        for s in a2.spines.values():
            s.set_color("#999"); s.set_linewidth(0.5)
        ax.add_patch(plt.Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fill=False, ec="#c33", lw=0.6))
    fn = C + f"check_filled_lakes_{px}px.png"
    fig.savefig(fn, dpi=dpi, facecolor="white"); plt.close(fig); out.append(fn)

# labels
fig, ax, dpi = fig_for("province", 1440)
web.boundary.plot(ax=ax, color="#666", lw=0.3)
lakes.plot(ax=ax, color="#a9d3f0", lw=0)
ax.scatter(labels.label_x_3005, labels.label_y_3005, s=4, c="#c00", zorder=5)
for _, r in labels.iterrows():
    ax.text(r.label_x_3005, r.label_y_3005, r.ed_code, fontsize=3.5, ha="left", va="bottom")
fig.savefig(C + "check_labels_1440px.png", dpi=dpi, facecolor="white"); plt.close(fig); out.append(C + "check_labels_1440px.png")
for k in INS:
    fig, ax, dpi = fig_for(k, 1440)
    clip_view(web, k).boundary.plot(ax=ax, color="#666", lw=0.4)
    clip_view(lakes, k).plot(ax=ax, color="#a9d3f0", lw=0)
    lb = labels[labels.ed_code.isin(clip_view(web, k).ed_code)]
    ax.scatter(lb.label_x_3005, lb.label_y_3005, s=6, c="#c00", zorder=5)
    for _, r in lb.iterrows():
        ax.text(r.label_x_3005, r.label_y_3005, r.ed_code, fontsize=6, ha="left", va="bottom")
    fn = C + f"check_labels_{k}_1440px.png"
    fig.savefig(fn, dpi=dpi, facecolor="white"); plt.close(fig); out.append(fn)

# PCN artifact zoom (census master before fix vs final)
cm = gpd.read_file("analysis/census/maps/ed2023_full_clipped_3005.gpkg")
x, y = 1220541, 1604659
fig, axs = plt.subplots(1, 2, figsize=(8, 4), dpi=110)
for a_, g_, t in [(axs[0], cm, "census master: hole 0.003 m2"), (axs[1], master, "FINAL master: removed")]:
    g_.cx[x - 60:x + 60, y - 60:y + 60].boundary.plot(ax=a_, color="k", lw=0.8)
    a_.set_xlim(x - 30, x + 30); a_.set_ylim(y - 30, y + 30); a_.set_title(t, fontsize=8); a_.set_aspect("equal")
fig.savefig(C + "check_pcn_artifact.png"); plt.close(fig); out.append(C + "check_pcn_artifact.png")
print("\n".join(out))
