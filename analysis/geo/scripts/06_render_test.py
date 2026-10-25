"""Test render: province (web file) with Metro Vancouver, Capital Region and Kelowna insets; outlines only.
Drawn in BC Albers (EPSG:3005). Output out/test_map.png"""
import geopandas as gpd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

O = "analysis/geo/out/"
web = gpd.read_file(O + "ed2023_web.geojson").to_crs(3005)
slide = gpd.read_file(O + "ed2023_slide720.geojson").to_crs(3005)
fig = plt.figure(figsize=(14, 9), dpi=110)
ax = fig.add_axes([0.0, 0.0, 0.55, 1.0])
slide.boundary.plot(ax=ax, color="#222", lw=0.4)
ax.set_title("2023 districts (93), slide720 file", fontsize=10)
ax.set_axis_off()
ax.set_aspect("equal")
for i, (name, title) in enumerate([("metro_vancouver", "Metro Vancouver"), ("capital_region", "Capital Region"), ("kelowna", "Central Okanagan")]):
    fr = gpd.read_file(O + f"inset_{name}_frame_web.geojson").to_crs(3005)
    mem = gpd.read_file(O + f"inset_{name}_web.geojson").to_crs(3005)
    pos = [[0.56, 0.36, 0.43, 0.62], [0.56, 0.0, 0.21, 0.34], [0.78, 0.0, 0.21, 0.34]][i]
    a = fig.add_axes(pos)
    fr.boundary.plot(ax=a, color="#999", lw=0.4)
    mem.boundary.plot(ax=a, color="#111", lw=0.6)
    for _, r in mem.iterrows():
        p = r.geometry.representative_point()
        a.text(p.x, p.y, r.ed_code, fontsize=5 if name == "metro_vancouver" else 6, ha="center", va="center")
    a.set_title(f"{title} inset ({len(mem)} districts, web file)", fontsize=9)
    a.set_axis_off()
    a.set_aspect("equal")
    b = mem.total_bounds
    ax.add_patch(plt.Rectangle((b[0], b[1]), b[2] - b[0], b[3] - b[1], fill=False, ec="red", lw=0.8))
fig.savefig(O + "test_map.png")
print("ok")
