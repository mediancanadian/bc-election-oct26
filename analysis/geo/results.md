# BC 2026 geography layer: results

Thread: geography. All paths are relative to `analysis/geo/`. Scripts are in `scripts/` and are run with `python3 -I`. Sources, URLs, access times, licences and sha256 hashes are in `manifest.json`.

## STATUS for the census thread
`out/da_to_ed2023.csv` is **FINAL** (built 2026-10-24 about 06:20 UTC, unchanged since). The columns are `dguid, ed_code, pop_share, method`. Details are below.

## FINAL map files (use these)
The master is in EPSG:3005. Every derived file comes from one simplified topology per variant, so the province map, the insets, the GeoJSON and the TopoJSON line up exactly.

| File | Content |
|---|---|
| `out/final/FINAL_ed2023_land_lakes_3005.gpkg` | **Master.** Full resolution, land-clipped, lakes of 50 km² or more removed, EPSG:3005 |
| `out/final/FINAL_ed2023_land_3005.gpkg` | Same master without the lake cut-outs |
| `out/final/FINAL_lakes_ge50km2_3005.gpkg` | The 55 lakes removed (for drawing in light blue) |
| `out/final/FINAL_ed2023_land_lakes_web_4326.{geojson,topojson}` | Web files, EPSG:4326, each under 400 KB |
| `out/final/FINAL_ed2023_land_lakes_web_3005.geojson` | The same web geometry in EPSG:3005 |
| `out/final/FINAL_ed2023_land_lakes_slide720_{3005,4326}.{geojson,topojson}` | 720 px slide version |
| `out/final/FINAL_ed2023_land_{web,slide720}_*` | The same two products without lake cut-outs |
| `out/final/FINAL_inset_{metro_vancouver,capital_region,kelowna}_{3005,4326}.geojson` | Member districts, taken from the web geometry |
| `out/final/FINAL_inset_*_frame_{3005,4326}.geojson` | All districts clipped to each inset box (for context) |
| `out/final/FINAL_ed2023_label_points.{csv,geojson}`, `_3005.geojson` | Label anchors |
| `out/final/FINAL_verification.json`, `FINAL_verification_per_district.csv` | Verification record (below) |
| `checks/*.png` | Check renders |

Properties on every district file: `ed_code`, `ed_name` and `ebc_ed_id` (as Elections BC publishes them), `area_master_km2`, `statcan_land_km2`, `pop2021`, `rd_abbr`, `inset`.

## Map verification record
**Codes and names:** the census thread's master (`analysis/census/maps/ed2023_full_clipped_3005.gpkg`) has the same 93 `ed_code`, `ed_name` and `ebc_ed_id` values as `out/ed2023.geojson` (Elections BC, BCGW `EBC_ELECTORAL_DISTS_BS11_SVW`). There are 0 differences. That master was itself built from this thread's raw download.

**Stray fragment (census check image, about x 853, y 118):**
- It is an artifact, not an island. It is a 0.003 m² triangular hole in Peace River North (PCN) at 59.3712 N, 122.1246 W.
- It comes from a sliver in the FWA watershed-group union, where four groups meet: Middle Fort Nelson (MFRT), Sahtaneh (SAHT), Lower Fort Nelson (LFRT) and Tsea River (TSEA).
- No FWA lake lies there, and the Elections BC polygon has no hole.
- It looked like a dot because a hole ring is outlined at a fixed line width.
- It was removed: interior rings under 1 m² were dropped, and this was the only one in all 93 districts. See `out/final/final_artifacts_removed.csv` and `checks/check_pcn_artifact.png`.

**Lakes:**
- FWA Lakes (1:20,000, BCGW `WHSE_BASEMAPPING.FWA_LAKES_POLY`). Pieces were dissolved by `WATERBODY_KEY`, and the 55 lakes of 50 km² or more were cut out, removing 9,958 km² in total.
- The list includes Williston, Okanagan, Kootenay, Upper and Lower Arrow, Kinbasket, Shuswap, Babine, Stuart, Quesnel, Harrison and François.
- Nechako Reservoir is covered through its named reaches: Ootsa, Intata Reach, Natalkuz, Whitesail, Eutsuk, Knewstubb and Tahtsa Reach.
- No man-made waterbody reaches 50 km².
- Islands inside lakes are holes in the FWA lake polygons, so they stay with their district.
- Lake area removed by district is in `out/final/final_lakes_by_district.csv` (largest: NEC 2,933 km², PCN 1,323 km², BLS 1,129 km²).

**Simplification method:** `scripts/simplify_lib.py`, `scripts/11_final_derive.py`.
- Shared arcs are built once from the master (topojson, no quantization, EPSG:3005 metres). Each arc is simplified once with Douglas-Peucker.
- Tolerance is k·√(area of the smallest district on the arc), clamped, times a per-district multiplier. The multiplier is tuned so that every district stays within 1% of its master area.
- Lake-shore arcs are capped at 350 m (web) and 400 m (slide) so the lakes keep their shape.
- Islets are dropped smallest first, only while each is under 5.0 km² and the total stays at or below 0.5% of the district's area.
- Snapping: arcs are snapped once to the output grid. Web uses 1e-5° at arc nodes and in repaired areas, and 1e-4° (about 11 m) elsewhere. EPSG:3005 output uses 1 m.
- Repair: every geometry and every arc-to-arc contact is checked, and any self-intersection or arc crossing is repaired locally by splitting the arc and lowering the tolerance there.
- Final web settings: k = 0.0300, repair {'arcs_split': 50, 'chunks_reduced': 81}.
- Districts that needed a lower multiplier: ABW 0.707, CHC 0.236, CQB 0.752, CRC 0.75, LAO 0.6, LWI 0.93, MPR 0.464, NAI 0.7, NOH 0.19, NOI 0.196, POC 0.865, POR 0.419, SKE 0.5, SRG 0.819, SWR 0.636, VHA 0.865, VNP 0.426, VTB 0.5, WVS 0.7.

**Verification** (`scripts/14_final_verify.py`, independent re-read of every file, measured in EPSG:3005 against the full-resolution master):

| File | Bytes | Valid | Overlap m² | Spurious gaps | Lake holes kept | Max area diff % | >1% | Parts ≥5 km² missing | Labels inside |
|---|---|---|---|---|---|---|---|---|---|
| `FINAL_ed2023_land_lakes_slide720_3005.geojson` | 490,184 | 93/93 | 0.0 | 0 | 44/44 | 0.966 (VLA) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_lakes_slide720_3005.topojson` | 260,300 | 93/93 | 0.0 | 0 | 44/44 | 0.966 (VLA) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_lakes_slide720_4326.geojson` | 495,444 | 93/93 | 0.0 | 0 | 44/44 | 0.959 (NOI) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_lakes_slide720_4326.topojson` | 262,815 | 93/93 | 0.0 | 0 | 44/44 | 0.959 (NOI) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_lakes_web_3005.geojson` | 377,167 | 93/93 | 0.0 | 0 | 44/44 | 0.966 (VLA) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_lakes_web_4326.geojson` | 373,667 | 93/93 | 0.0 | 0 | 44/44 | 0.931 (NOH) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_lakes_web_4326.topojson` | 210,096 | 93/93 | 0.0 | 0 | 44/44 | 0.931 (NOH) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_slide720_3005.geojson` | 391,618 | 93/93 | 0.0 | 0 | 0/0 | 0.969 (NOI) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_slide720_3005.topojson` | 205,188 | 93/93 | 0.0 | 0 | 0/0 | 0.969 (NOI) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_slide720_4326.geojson` | 398,394 | 93/93 | 0.0 | 0 | 0/0 | 0.969 (NOI) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_slide720_4326.topojson` | 206,896 | 93/93 | 0.0 | 0 | 0/0 | 0.969 (NOI) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_web_3005.geojson` | 356,972 | 93/93 | 0.0 | 0 | 0/0 | 0.964 (NOH) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_web_4326.geojson` | 365,794 | 93/93 | 0.0 | 0 | 0/0 | 0.963 (NOH) | 0 | 0 | 93/93 |
| `FINAL_ed2023_land_web_4326.topojson` | 197,103 | 93/93 | 0.0 | 0 | 0/0 | 0.963 (NOH) | 0 | 0 | 93/93 |

- **Valid:** `is_valid` is true for all 93 geometries in every file, in both the file's own CRS and in EPSG:3005.
- **Overlap:** pairwise intersection area.
- **Spurious gaps:** holes in the simplified union that do not correspond to a master hole (lake). There are none.
- **Lake holes kept:** all 44 holes in the master union (lakes not touching the coast or a district boundary) survive in every land_lakes file.
- **Within 1%:** no district in any file falls outside ±1%.
- **Islands:** every master part of 5 km² or more is still present. Islets dropped (smallest first) total 585.624 km² in the web file.
- **Labels:** all 93 label points lie inside every land_lakes file.

Small urban districts in the web file (all present as one part, all valid):

| District | Master km² | Diff % | Parts master/web | Valid |
|---|---|---|---|---|
| BNC | 18.434 | -0.005 | 1/1 | True |
| BNN | 8.808 | -0.360 | 1/1 | True |
| BNO | 14.630 | -0.667 | 1/1 | True |
| NMC | 12.723 | +0.437 | 1/1 | True |
| NVL | 15.932 | -0.180 | 1/1 | True |
| RCC | 6.627 | -0.154 | 1/1 | True |
| SRC | 16.874 | +0.524 | 1/1 | True |
| SRF | 14.632 | -0.545 | 1/1 | True |
| SRN | 14.071 | +0.470 | 1/1 | True |
| SUP | 12.847 | -0.274 | 1/1 | True |
| VFV | 11.606 | -0.006 | 1/1 | True |
| VHA | 12.257 | +0.931 | 1/1 | True |
| VKE | 8.684 | +0.408 | 1/1 | True |
| VLA | 12.493 | +0.849 | 1/1 | True |
| VLM | 9.667 | +0.175 | 1/1 | True |
| VNR | 8.020 | -0.811 | 1/1 | True |
| VNS | 5.713 | -0.552 | 1/1 | True |
| VNT | 8.770 | -0.487 | 1/1 | True |
| VNW | 6.599 | +0.321 | 1/1 | True |
| VNY | 2.957 | -0.374 | 1/1 | True |
| VTB | 10.244 | +0.424 | 3/1 | True |
| VTS | 17.530 | -0.204 | 1/1 | True |

**Label anchors:** `out/final/FINAL_ed2023_label_points.csv` and `.geojson`. Each is the pole of inaccessibility (shapely `polylabel`, 10 m tolerance) on the largest land part of the land_lakes master, so no label falls in a lake. All 93 are inside the master and every simplified land_lakes file. The minimum distance to an edge is 674 m (VNY).

**Check renders** (`checks/`, EPSG:3005):
- `check_{province,metro_vancouver,capital_region,kelowna}_{720,1440}px.png`: full-resolution master outline in blue (thick) under the simplified outline in orange (thin). Province at 720 px uses the slide720 file; everything else uses the web file.
- `check_filled_lakes_{720,1440}px.png`: filled districts with lakes in light blue, plus the three insets.
- `check_labels_*.png`: label anchors.
- `check_pcn_artifact.png`: the removed artifact.
- At 720 px the orange line sits on the blue line. At 1440 px, rural fjord coastlines (NOH, NOI, POR, MPR) and long rural edges are visibly generalised, which is the cost of the 400 KB limit. Urban edges and the insets coincide. For full coastline detail at large sizes, use the census thread's 10 m file (`analysis/census/maps/ed2023_clipped_s10m_3005.gpkg`, same master except for the lakes and the PCN artifact).


## Earlier outputs (superseded for display)
These were built from the published (unclipped, over-water) boundaries before the coordinator asked for land clipping. They are still valid as boundary files but are not land-clipped:
- `out/ed2023.geojson`: full resolution, unclipped, EPSG:4326.
- `out/ed2023_web.{geojson,topojson}`: under 400 KB.
- `out/ed2023_slide720.*`.
- `out/inset_*`.

Use `out/final/` for anything displayed.

## Regions (inset membership)
`out/ed2023_regions.csv`. Rule: a district belongs to the regional district (BCGW `WHSE_LEGAL_ADMIN_BOUNDARIES.ABMS_REGIONAL_DISTRICTS_SP`) that contains its representative point (`shapely` `representative_point`, which always falls inside the district). The file also records `area_share_in_rd` and `pop_share_in_rd`, the latter from 2021 dissemination block populations.

- Metro Vancouver (MVRD), 44 districts: BNC BNE BNN BNO BNS CQB CQM DLN DLS LLA LWG LWI NMC NVL NVS POC POM RCB RCC RCQ RCS SRC SRD SRF SRG SRN SUN SUP SUR SUS SWR VFV VHA VKE VLA VLM VNP VNQ VNR VNS VNT VNW VNY WVC.
- Capital Region (CAPRD), 8 districts: ESC JFM LFH OBG SAN SAS VTB VTS.
- Central Okanagan (RDCO, Kelowna), 4 districts: KEC KLC KLM WKP.
- Borderline cases:
  - LLA (Langley-Abbotsford) is in Metro Vancouver with 88% of its population in MVRD.
  - JFM is in the Capital Region with 57% of its population in CAPRD.
  - KLC is in RDCO with 81% of its population in RDCO.
  - MAE and MAP (Maple Ridge) have their representative points in the Fraser Valley RD, but almost all of their population is in Metro Vancouver (pop_share_in_rd for FVRD is 0.106 and 0.001). They are not in the Metro inset by the rule, though they appear in its frame file. Override by hand if the post should treat Maple Ridge as Metro Vancouver.
  - WVS (West Vancouver-Sea to Sky) is in Squamish-Lillooet, with 74% of its population there.

## Voting areas
- **2024:** `out/va2024.geojson` (5,778 polygons, 93 districts; BCGW `EBC_VOTING_AREAS_BS11_POLY_SVW`, gazetted 2024-09-19). `edva_code` matches Elections BC results (e.g. ABM049). There are also 640 site-based voting areas as points in `out/sva2024_points.geojson` (codes ending in S; these have no polygon). The web version is `out/va2024_web.topojson` (1.7 MB).
- **2020:** `out/va2020.geojson`. The 2020 election used the voting areas gazetted 2017-02-23 (BCGW `EBC_VOTING_AREAS_BS10_POLY_SVW`): 5,658 polygons in 87 districts, plus 690 site-based points in `out/sva2020_points.geojson`.
- **Transposition:** `out/va2020_to_ed2023.csv` gives, for each 2020 voting area, its share of 2021 population in each 2023 district, based on dissemination blocks (same 98% rule as below). 233 voting areas are split; all 5,658 are covered. `out/sva2020_to_ed2023.csv` assigns site-based voting areas by point.
- **Official cross-reference:** Elections BC's own conversion tables (`raw/bcdc/edva_conversiontable2017to2024.xlsx` and `...2024to2017.xlsx`) list which 2024 voting areas each 2017 voting area intersects. They give no weights.
- **Voting places:** voting-area-to-voting-place assignment for 2024 is in `raw/bcgw/vavp2024.geojson`.

## 2020 districts (87)
`out/ed2015.geojson`, with `_web.geojson` and `_web.topojson` (2015 redistribution, used in 2017 and 2020; all valid; 0 overlap). These are unclipped and extend about 30,500 km² further offshore on the west coast than the 2023 file.

## Dissemination areas, dissemination blocks and the DA-to-district lookup
- **Boundaries:**
  - `out/db2021_digital_bc.geojson`: 52,423 dissemination blocks, from the digital boundary file, with GAF population, dwellings and main district.
  - `out/da2021_digital_bc.geojson`: the StatCan digital DA layer.
  - `out/da2021_cartographic_bc.geojson`: the cartographic DA layer, shoreline-clipped.
  - All 7,848 BC DAs are present in each.
  - Source is StatCan's official ArcGIS service, geo.statcan.gc.ca (2021 Digital and Cartographic boundary files). The www12 zip downloads are behind a Cloudflare browser check (HTTP 403) and could not be used.
- **Block populations:** StatCan 2021 Geographic Attribute File (92-151-X) BC extract, as republished on the BC Data Catalogue. The province total is 5,000,879.
- **Lookup:** `out/da_to_ed2023.csv` has 8,393 rows; `pop_share` sums to 1 for each DA. `out/da_to_ed2023_detail.csv` adds DAUID and DA population. `out/db_to_ed2023.csv` is the block-level lookup.
  - Each digital block goes to the 2023 district that holds at least 98% of its area. Otherwise its population is split by area among districts holding at least 2%. Only about 8,000 people (0.16%) are split this way.
  - `method` values:
    - `whole`: 7,340 DAs lie entirely in one district.
    - `db_pop`: the DA is split, but every block in it is whole.
    - `db_pop_area`: the DA is split and at least one populated block is split by area.
    - `area`: a zero-population DA, split by land area.
- **Cross-check:** district populations from blocks match the BC Stats 2021 PED93 profile with a median absolute difference of 0.10% and a maximum of 0.91% (SRF). See `out/ed2023_pop_check_vs_bcstats.csv`.

## District area and population
`out/ed2023_area_pop.csv`: `area_km2` (published Elections BC polygon, which includes ocean), `land_km2` (StatCan block land area), `pop2021` and density. `out/final/final_lakes_by_district.csv` gives FWA land area with and without the 55 lakes.

| | District | Value |
|---|---|---|
| Largest area | BLS Bulkley Valley-Stikine | 196,484 km² published; 195,348 km² land excluding lakes of 50 km² or more; 191,302 km² StatCan land |
| Smallest area | VNY Vancouver-Yaletown | 3.5 km² published; 3.0 km² land |
| Largest population (2021) | SHU Salmon Arm-Shuswap | 62,631 from blocks. BC Stats gives 62,550 and ranks WVC West Vancouver-Capilano first at 62,585 (block total 62,566). The top two are within rounding. |
| Smallest population (2021) | BLS Bulkley Valley-Stikine | 20,549 (BC Stats 20,555) |

## Test render
`out/test_map.png` is the first check of the unclipped files. The final checks are in `checks/`.
