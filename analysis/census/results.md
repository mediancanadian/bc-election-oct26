# BC 2026 election: 2021 Census demographic layer, 93 districts (2023 boundaries)

Built 2026-10-24. All paths under `analysis/census/`.

## Method

1. **BC Stats publishes this directly.** "Census Profiles for BC Provincial Electoral Districts" (BC Data Catalogue, BC Stats) has a 2021 Census profile on the 93 districts of the 2023 Redistribution. It is a Statistics Canada tabulation on the district geography, so medians, rates and LIM-AT are true district values, not roll-ups. This is the primary source for every variable except two.
2. **The two variables BC Stats does not publish are built from DAs and blocks.**
   - Land area: 2021 dissemination-block land area (StatCan GAF) × block-to-district fraction (geo thread `db_to_ed2023.csv`).
   - 2016 population: StatCan does not publish 2016 population for 2021 DAs (flag "not applicable"). It is published for 2021 aggregate DAs (ADAs). Each ADA's 2016 count is shared to its DAs by 2021 population, then DA to district by `da_to_ed2023.csv` pop_share. Growth = (2021 DA roll-up ÷ 2016 estimate) − 1, so both years use the same allocation. **Approximate** where an ADA straddles a district line. One ADA (59170041, Esquimalt, 2021 pop 120) has no 2016 value (flag 1); it adds nothing to ESC's 2016 figure.
3. District codes and names come from the Elections BC 2026 candidate list. All 93 match the BCGW 2023 layer and the BC Stats column headers exactly.
4. Medians are not summed or averaged anywhere: BC Stats gives the true district median. No population-weighted DA median was needed.
5. Suppression: `x` (suppressed) affects 19 of 960,774 BC Stats cells; `...` (not applicable) affects 48,275. **None of the cells used for the profile is suppressed or not applicable** (columns `n_cells_suppressed_x`, `n_cells_not_applicable`). Every flagged cell is listed in `out/suppression_log.csv`. No DA was dropped: all 7,848 DAs are in the crosswalk; 28 DAs have population "not available" (flag 1, 0 or unpublished pop) and are counted.

Access log: www12.statcan.gc.ca returns a bot-check 403 to the shell (profile CSVs and boundary zips). The StatCan Census Profile SDMX API (`api.statcan.gc.ca/census-recensement/profile/sdmx`, dataflows DF_DA and DF_ADA) works and was used. ftp.geobc.gov.bc.ca (BC Boundary Terrestrial) resets the connection through the proxy and was not used.

## Coverage checks (`out/checks.json`)

| Check | Result |
|---|---|
| Districts | 93; codes/names identical in Elections BC 2026 list, BCGW 2023, BC Stats |
| Sum of district pop 2021 (BC Stats) | 5,000,870 vs official 5,000,879 (diff -9, StatCan random rounding; BC column in file = 5,000,880) |
| Sum of DA roll-up pop 2021 | 5,000,879 |
| BC Stats vs block-level allocation, per district | max 550 persons (0.914%, SRF) |
| Land area sum | 920,686.58 km² vs GAF BC 920,686.55 |
| Pop 2016 sum | 4,648,053 vs ADA BC sum 4,648,055 (213 ADA values flagged "revised") |
| DAs | 7,848 in, 7,848 in crosswalk, 0 dropped |

## Files

| Path | Content |
|---|---|
| `out/ed2023_profile.csv` | One row per district (+ BC row), `ed_code` = Elections BC code, 205 variables |
| `out/ed2023_profile_long.csv` | Same, long format, with unit, universe and source per variable |
| `out/bcstats_ped93_tidy.csv.gz` | Every BC Stats cell (2,601+806 characteristics × 3 genders × 94 geographies), long, with flag |
| `out/suppression_log.csv` | Every suppressed / not-applicable cell |
| `out/checks.json` | Coverage checks |
| `maps/` | District geometry and verification (below) |
| `manifest.json` | URLs, access times, sha256, licences, output hashes |
| `scripts/01_download.py` … `20_build_profile.py` | Run with `python3 -I` |

## Map verification record

Requested for this thread by the coordinator. The geo thread (`analysis/geo/out`) has its own web/slide layers; the files here are an independent build to this spec.

**Master:** Elections BC 2023 boundaries, BCGW `WHSE_ADMIN_BOUNDARIES.EBC_ELECTORAL_DISTS_BS11_SVW`, full resolution, EPSG:3005 (814,379 vertices). Source check: 93 valid polygons, 0 m² pairwise overlap, no interior gaps.

**Land clip:** GeoBC Freshwater Atlas Watershed Groups (1:20,000; coastal groups are bounded by the FWA coastline, one polygon per island). The union is BC land, including lakes and rivers, excluding ocean. It is used because the 1:20,000 "BC Boundary Terrestrial" file sits on an FTP host that is unreachable here. Clipped land total: 948,034 km² of 1,039,594 km² unclipped. Clipped result: all 93 valid, 0 overlap, 28,179 polygon parts (NOH 17,504; NOI 6,966). Note: FWA land includes inland water, so this differs from StatCan land area (920,687 km²), which excludes lakes; the census `land_area_km2` uses StatCan.

**Simplification:** mapshaper 0.6.102, Douglas-Peucker on shared arcs (topology-preserving; each shared edge simplified once), planar metres in EPSG:3005, `keep-shapes`, then `-clean` with gap-fill and sliver-control off (this repairs three lake holes crossing their shell at 25 m). **Chosen tolerance: 10 m.**

| Check (clipped) | 10 m (chosen) | 25 m |
|---|---|---|
| is_valid, all 93 | 93/93 | 93/93 |
| Max abs area diff vs full-res clipped | 0.138% (VNR) | 0.354% (NMC) |
| Districts outside ±1% | none | none |
| Pairwise overlap | 0.0 km² | 0.0 km² |
| Polygon parts kept | 27,029 of 28,179 | 15,270 of 28,179 |
| Parts lost | 1,363 islets, 0.43 km² total; only 1 ≥ 0.5 ha (1.34 ha); the only part ≥ 1 ha lost is that 1.34 ha islet | 13,285 islets, 11.1 km²; 5 of 4,846 ≥ 1 ha lost, 0 ≥ 5 ha |
| Vertices | 672,063 | 344,278 |
| Unclipped: valid / max area diff / overlap | 93/93, 0.138%, 0 | 93/93, 0.354%, 0 |

The union-level difference from full resolution (60 km² removed, 44 km² added at 10 m) sits along coastline edges, where DP moves lines up to 10 m. Shared district edges stay coincident (0 overlap). Per-district areas are in `maps/check_area_*_s10m.csv`.

Small urban districts at 10 m (clipped): code, full-res km², area diff %, valid, parts full / simplified.

| District | km² | diff % | valid | parts |
|---|---|---|---|---|
| NVL | 15.9317 | +0.0068 | True | 1 / 1 |
| RCC | 6.6265 | -0.0335 | True | 1 / 1 |
| SRC | 16.8743 | +0.0431 | True | 1 / 1 |
| VNS | 5.7134 | +0.1116 | True | 1 / 1 |
| VNT | 8.7695 | +0.0739 | True | 1 / 1 |
| VNW | 6.5993 | -0.0597 | True | 1 / 1 |
| VNY | 2.9573 | -0.0068 | True | 1 / 1 |
| VTB | 10.2439 | +0.0329 | True | 3 / 2 |
| VTS | 17.5300 | -0.0589 | True | 1 / 1 |

None disappears or self-intersects.

**Label anchors:** `maps/ed2023_label_points.csv` / `.gpkg` hold the pole of inaccessibility (shapely polylabel, 10 m precision) on the largest land part of the full-resolution clipped polygon. All 93 points lie inside both the full-res and the 10 m polygon; the minimum distance to an edge is 674 m.

**Visual checks** (`maps/checks/`): province, Metro Vancouver, Capital Region and Kelowna at 720 px and 1440 px. Full-res clipped outline is blue (thick) and the 10 m outline is orange (thin) on top, in EPSG:3005. At 720 and 1440 px the orange line sits on the blue line everywhere inspected.

| Map file | Content |
|---|---|
| `maps/ed2023_full_unclipped_3005.gpkg` | Full resolution, as published (over water) |
| `maps/ed2023_full_clipped_3005.gpkg` | Full resolution, land-clipped (with `area_land_km2`, `n_parts`) |
| `maps/ed2023_{clipped,unclipped}_s10m_3005.gpkg/.geojson` | 10 m simplified (master for slides/web) |
| `maps/ed2023_{clipped,unclipped}_s25m_3005.gpkg` | 25 m alternative, lighter |
| `maps/bc_land_fwa_3005.gpkg` | Land mask used |
| `maps/check_simplify_*.json`, `check_area_*.csv` | Verification numbers |

## Data dictionary

Sources: **BCS-100** = BC Stats PED93 2021 profile, 100% data (part 1); **BCS-25** = 25% sample data (part 2). All values are StatCan randomly rounded. Shares (`pct_*`) = count ÷ the universe total in the same table, ×100; `%` rates without a computed denominator are as published. Income is 2020 income in CAD. Labour and commute data refer to May 2021 (pandemic period). `top_industry_n` and `top_home_language_non_english_n` give the label and share of the n-th largest category (industries: NAICS sectors; languages: single-response non-official languages, most often spoken at home). Language variables `pct_lang_home_*` and `pct_lang_mt_*` cover the ten largest non-official languages province-wide. Last column = BC value.

| Variable | Unit | Universe / denominator | Source | BC |
|---|---|---|---|---|
| `pop_2021` | persons | Total population | BCS-100 | 5,000,880 |
| `pop_men_plus` | persons | Total population | BCS-100 | 2,457,515 |
| `pop_women_plus` | persons | Total population | BCS-100 | 2,543,365 |
| `pct_men_plus` | % | Men+ / (Men+ + Women+) | BCS-100 | 49.14 |
| `pct_women_plus` | % | Women+ / (Men+ + Women+) | BCS-100 | 50.86 |
| `age_0_14` | persons | Total population | BCS-100 | 716,900 |
| `age_15_19` | persons | Total population | BCS-100 | 253,690 |
| `age_20_34` | persons | Total population | BCS-100 | 990,325 |
| `age_35_64` | persons | Total population | BCS-100 | 2,023,600 |
| `age_65_plus` | persons | Total population | BCS-100 | 1,016,365 |
| `pct_age_0_14` | % | Total population (100% data) | BCS-100 | 14.34 |
| `pct_age_15_19` | % | Total population (100% data) | BCS-100 | 5.07 |
| `pct_age_20_34` | % | Total population (100% data) | BCS-100 | 19.8 |
| `pct_age_35_64` | % | Total population (100% data) | BCS-100 | 40.46 |
| `pct_age_65_plus` | % | Total population (100% data) | BCS-100 | 20.32 |
| `median_age` | years | Total population | BCS-100 | 42.8 |
| `average_age` | years | Total population | BCS-100 | 43.1 |
| `age_0_17_privhh` | persons | Population in private households (25% sample) | BCS-25 | 867,740 |
| `age_18_64_privhh` | persons | Population in private households (25% sample) | BCS-25 | 3,083,550 |
| `age_65_plus_privhh` | persons | Population in private households (25% sample) | BCS-25 | 964,645 |
| `pct_age_0_17_privhh` | % | Population in private households (25% sample) | BCS-25 | 17.65 |
| `pct_age_18_64_privhh` | % | Population in private households (25% sample) | BCS-25 | 62.73 |
| `pct_age_65_plus_privhh` | % | Population in private households (25% sample) | BCS-25 | 19.62 |
| `hh_income_median` | CAD 2020 | Private households | BCS-25 | 85,000 |
| `hh_income_median_after_tax` | CAD 2020 | Private households | BCS-25 | 76,000 |
| `hh_income_average` | CAD 2020 | Private households | BCS-25 | 108,600 |
| `hh_income_average_after_tax` | CAD 2020 | Private households | BCS-25 | 91,100 |
| `ind_income_median` | CAD 2020 | Income recipients 15+ in private households | BCS-25 | 40,800 |
| `ind_income_average` | CAD 2020 | Income recipients 15+ in private households | BCS-25 | 54,450 |
| `pct_low_income_lim_at` | % | Population in private households (published rate) | BCS-25 | 10.8 |
| `low_income_lim_at` | persons | Population in private households | BCS-25 | 528,850 |
| `hh_inc_under_50k` | households | Private households | BCS-25 | 538,005 |
| `pct_hh_inc_under_50k` | % | Private households (household total income 2020) | BCS-25 | 26.35 |
| `hh_inc_50k_100k` | households | Private households | BCS-25 | 650,970 |
| `pct_hh_inc_50k_100k` | % | Private households (household total income 2020) | BCS-25 | 31.88 |
| `hh_inc_100k_150k` | households | Private households | BCS-25 | 414,390 |
| `pct_hh_inc_100k_150k` | % | Private households (household total income 2020) | BCS-25 | 20.3 |
| `hh_inc_150k_200k` | households | Private households | BCS-25 | 222,145 |
| `pct_hh_inc_150k_200k` | % | Private households (household total income 2020) | BCS-25 | 10.88 |
| `hh_inc_200k_plus` | households | Private households | BCS-25 | 216,315 |
| `pct_hh_inc_200k_plus` | % | Private households (household total income 2020) | BCS-25 | 10.59 |
| `vm_total` | persons | Population in private households | BCS-25 | 1,689,490 |
| `pct_vm_total` | % | Population in private households | BCS-25 | 34.37 |
| `vm_south_asian` | persons | Population in private households | BCS-25 | 473,970 |
| `pct_vm_south_asian` | % | Population in private households | BCS-25 | 9.64 |
| `vm_chinese` | persons | Population in private households | BCS-25 | 550,590 |
| `pct_vm_chinese` | % | Population in private households | BCS-25 | 11.2 |
| `vm_black` | persons | Population in private households | BCS-25 | 61,755 |
| `pct_vm_black` | % | Population in private households | BCS-25 | 1.26 |
| `vm_filipino` | persons | Population in private households | BCS-25 | 174,275 |
| `pct_vm_filipino` | % | Population in private households | BCS-25 | 3.55 |
| `vm_arab` | persons | Population in private households | BCS-25 | 28,010 |
| `pct_vm_arab` | % | Population in private households | BCS-25 | 0.57 |
| `vm_latin_american` | persons | Population in private households | BCS-25 | 65,970 |
| `pct_vm_latin_american` | % | Population in private households | BCS-25 | 1.34 |
| `vm_southeast_asian` | persons | Population in private households | BCS-25 | 71,785 |
| `pct_vm_southeast_asian` | % | Population in private households | BCS-25 | 1.46 |
| `vm_west_asian` | persons | Population in private households | BCS-25 | 69,270 |
| `pct_vm_west_asian` | % | Population in private households | BCS-25 | 1.41 |
| `vm_korean` | persons | Population in private households | BCS-25 | 72,815 |
| `pct_vm_korean` | % | Population in private households | BCS-25 | 1.48 |
| `vm_japanese` | persons | Population in private households | BCS-25 | 44,125 |
| `pct_vm_japanese` | % | Population in private households | BCS-25 | 0.9 |
| `vm_nie` | persons | Population in private households | BCS-25 | 18,080 |
| `pct_vm_nie` | % | Population in private households | BCS-25 | 0.37 |
| `vm_multiple` | persons | Population in private households | BCS-25 | 58,840 |
| `pct_vm_multiple` | % | Population in private households | BCS-25 | 1.2 |
| `not_vm` | persons | Population in private households | BCS-25 | 3,226,450 |
| `pct_not_vm` | % | Population in private households | BCS-25 | 65.63 |
| `indigenous` | persons | Population in private households | BCS-25 | 290,210 |
| `pct_indigenous` | % | Population in private households | BCS-25 | 5.9 |
| `indigenous_first_nations` | persons | Population in private households | BCS-25 | 180,085 |
| `pct_indigenous_first_nations` | % | Population in private households | BCS-25 | 3.66 |
| `indigenous_metis` | persons | Population in private households | BCS-25 | 97,865 |
| `pct_indigenous_metis` | % | Population in private households | BCS-25 | 1.99 |
| `indigenous_inuk` | persons | Population in private households | BCS-25 | 1,720 |
| `pct_indigenous_inuk` | % | Population in private households | BCS-25 | 0.03 |
| `immigrants` | persons | Population in private households | BCS-25 | 1,425,715 |
| `pct_immigrants` | % | Population in private households | BCS-25 | 29 |
| `recent_immigrants_2016_2021` | persons | Population in private households | BCS-25 | 197,420 |
| `pct_recent_immigrants_2016_2021` | % | Population in private households | BCS-25 | 4.02 |
| `non_permanent_residents` | persons | Population in private households | BCS-25 | 171,000 |
| `pct_non_permanent_residents` | % | Population in private households | BCS-25 | 3.48 |
| `non_immigrants` | persons | Population in private households | BCS-25 | 3,319,230 |
| `pct_non_immigrants` | % | Population in private households | BCS-25 | 67.52 |
| `rel_buddhist` | persons | Population in private households | BCS-25 | 83,860 |
| `pct_rel_buddhist` | % | Population in private households | BCS-25 | 1.71 |
| `rel_christian` | persons | Population in private households | BCS-25 | 1,684,870 |
| `pct_rel_christian` | % | Population in private households | BCS-25 | 34.27 |
| `rel_catholic` | persons | Population in private households | BCS-25 | 588,140 |
| `pct_rel_catholic` | % | Population in private households | BCS-25 | 11.96 |
| `rel_hindu` | persons | Population in private households | BCS-25 | 81,315 |
| `pct_rel_hindu` | % | Population in private households | BCS-25 | 1.65 |
| `rel_jewish` | persons | Population in private households | BCS-25 | 26,850 |
| `pct_rel_jewish` | % | Population in private households | BCS-25 | 0.55 |
| `rel_muslim` | persons | Population in private households | BCS-25 | 125,915 |
| `pct_rel_muslim` | % | Population in private households | BCS-25 | 2.56 |
| `rel_sikh` | persons | Population in private households | BCS-25 | 290,865 |
| `pct_rel_sikh` | % | Population in private households | BCS-25 | 5.92 |
| `rel_indigenous_spirituality` | persons | Population in private households | BCS-25 | 11,570 |
| `pct_rel_indigenous_spirituality` | % | Population in private households | BCS-25 | 0.24 |
| `rel_other` | persons | Population in private households | BCS-25 | 51,440 |
| `pct_rel_other` | % | Population in private households | BCS-25 | 1.05 |
| `rel_none_secular` | persons | Population in private households | BCS-25 | 2,559,255 |
| `pct_rel_none_secular` | % | Population in private households | BCS-25 | 52.06 |
| `hh_owner` | households | Private households | BCS-25 | 1,363,185 |
| `pct_hh_owner` | % | Private households | BCS-25 | 66.76 |
| `hh_renter` | households | Private households | BCS-25 | 669,455 |
| `pct_hh_renter` | % | Private households | BCS-25 | 32.79 |
| `hh_band_housing` | households | Private households | BCS-25 | 9,190 |
| `pct_hh_band_housing` | % | Private households | BCS-25 | 0.45 |
| `hh_shelter_30plus` | households | Owner+tenant hh, income>0, non-farm non-reserve | BCS-25 | 506,845 |
| `pct_hh_shelter_30plus` | % | Owner+tenant hh, income>0, non-farm non-reserve | BCS-25 | 25.49 |
| `hh_core_need` | households | Owner+tenant hh, income>0, STIR<100%, non-farm non-reserve | BCS-25 | 257,090 |
| `pct_hh_core_need` | % | Owner+tenant hh, income>0, STIR<100%, non-farm non-reserve | BCS-25 | 13.42 |
| `pct_tenant_shelter_30plus` | % | Tenant households (published rate) | BCS-25 | 37.8 |
| `median_dwelling_value` | CAD | Owner households, non-farm non-reserve | BCS-25 | 785,000 |
| `median_rent` | CAD/month | Tenant households, non-farm non-reserve | BCS-25 | 1,370 |
| `dw_condo` | dwellings | Occupied private dwellings | BCS-25 | 482,760 |
| `pct_dw_condo` | % | Occupied private dwellings | BCS-25 | 23.64 |
| `dw_single_detached` | dwellings | Occupied private dwellings | BCS-100 | 866,340 |
| `dw_apartment` | dwellings | Occupied private dwellings | BCS-100 | 889,160 |
| `dw_apartment_5plus_storeys` | dwellings | Occupied private dwellings | BCS-100 | 221,845 |
| `pct_dw_single_detached` | % | Occupied private dwellings (100% data) | BCS-100 | 42.43 |
| `pct_dw_apartment` | % | Occupied private dwellings (100% data) | BCS-100 | 43.55 |
| `pct_dw_apartment_5plus_storeys` | % | Occupied private dwellings (100% data) | BCS-100 | 10.87 |
| `bachelor_plus_25_64` | persons | Population 25-64 in private households | BCS-25 | 941,735 |
| `pct_bachelor_plus_25_64` | % | Population 25-64 in private households | BCS-25 | 34.98 |
| `no_certificate_25_64` | persons | Population 25-64 in private households | BCS-25 | 216,660 |
| `pct_no_certificate_25_64` | % | Population 25-64 in private households | BCS-25 | 8.05 |
| `bachelor_plus_15plus` | persons | Population 15+ in private households | BCS-25 | 1,199,710 |
| `pct_bachelor_plus_15plus` | % | Population 15+ in private households | BCS-25 | 28.56 |
| `participation_rate` | % | Population 15+ (published rate) | BCS-25 | 63.3 |
| `employment_rate` | % | Population 15+ (published rate) | BCS-25 | 57.9 |
| `unemployment_rate` | % | Labour force 15+ (published rate; May 2021 reference week) | BCS-25 | 8.4 |
| `pct_ind_11_agriculture_forestry_fishing_and_hunting` | % | Labour force 15+ with an industry | BCS-25 | 2.32 |
| `pct_ind_21_mining_quarrying_and_oil_and_gas_extraction` | % | Labour force 15+ with an industry | BCS-25 | 0.96 |
| `pct_ind_22_utilities` | % | Labour force 15+ with an industry | BCS-25 | 0.57 |
| `pct_ind_23_construction` | % | Labour force 15+ with an industry | BCS-25 | 9 |
| `pct_ind_31_33_manufacturing` | % | Labour force 15+ with an industry | BCS-25 | 5.87 |
| `pct_ind_41_wholesale_trade` | % | Labour force 15+ with an industry | BCS-25 | 3.08 |
| `pct_ind_44_45_retail_trade` | % | Labour force 15+ with an industry | BCS-25 | 11.57 |
| `pct_ind_48_49_transportation_and_warehousing` | % | Labour force 15+ with an industry | BCS-25 | 5.46 |
| `pct_ind_51_information_and_cultural_industries` | % | Labour force 15+ with an industry | BCS-25 | 2.74 |
| `pct_ind_52_finance_and_insurance` | % | Labour force 15+ with an industry | BCS-25 | 3.67 |
| `pct_ind_53_real_estate_and_rental_and_leasing` | % | Labour force 15+ with an industry | BCS-25 | 2.27 |
| `pct_ind_54_professional_scientific_and_technical_services` | % | Labour force 15+ with an industry | BCS-25 | 9.17 |
| `pct_ind_55_management_of_companies_and_enterprises` | % | Labour force 15+ with an industry | BCS-25 | 0.22 |
| `pct_ind_56_administrative_and_support_waste_management_and_remediation_services` | % | Labour force 15+ with an industry | BCS-25 | 4.23 |
| `pct_ind_61_educational_services` | % | Labour force 15+ with an industry | BCS-25 | 7.41 |
| `pct_ind_62_health_care_and_social_assistance` | % | Labour force 15+ with an industry | BCS-25 | 12.27 |
| `pct_ind_71_arts_entertainment_and_recreation` | % | Labour force 15+ with an industry | BCS-25 | 2.33 |
| `pct_ind_72_accommodation_and_food_services` | % | Labour force 15+ with an industry | BCS-25 | 7 |
| `pct_ind_81_other_services_except_public_administration` | % | Labour force 15+ with an industry | BCS-25 | 4.37 |
| `pct_ind_91_public_administration` | % | Labour force 15+ with an industry | BCS-25 | 5.48 |
| `commute_car` | persons | Employed 15+ commuters (usual place / no fixed address) | BCS-25 | 1,497,770 |
| `pct_commute_car` | % | Employed 15+ commuters | BCS-25 | 79.94 |
| `commute_transit` | persons | Employed 15+ commuters (usual place / no fixed address) | BCS-25 | 174,040 |
| `pct_commute_transit` | % | Employed 15+ commuters | BCS-25 | 9.29 |
| `commute_walk` | persons | Employed 15+ commuters (usual place / no fixed address) | BCS-25 | 121,555 |
| `pct_commute_walk` | % | Employed 15+ commuters | BCS-25 | 6.49 |
| `commute_bike` | persons | Employed 15+ commuters (usual place / no fixed address) | BCS-25 | 36,790 |
| `pct_commute_bike` | % | Employed 15+ commuters | BCS-25 | 1.96 |
| `commute_other` | persons | Employed 15+ commuters (usual place / no fixed address) | BCS-25 | 43,535 |
| `pct_commute_other` | % | Employed 15+ commuters | BCS-25 | 2.32 |
| `commute_walk_bike` | persons | Employed 15+ commuters | BCS-25 | 158,345 |
| `pct_commute_walk_bike` | % | Employed 15+ commuters | BCS-25 | 8.45 |
| `worked_at_home` | persons | Employed labour force 15+ | BCS-25 | 549,850 |
| `pct_worked_at_home` | % | Employed labour force 15+ (May 2021, pandemic period) | BCS-25 | 22.59 |
| `pct_lang_home_english` | % | Total pop. excl. institutional residents (single responses) | BCS-25 | 78.49 |
| `pct_lang_home_punjabi_panjabi` | % | Total pop. excl. institutional residents | BCS-25 | 3.77 |
| `pct_lang_home_mandarin` | % | Total pop. excl. institutional residents | BCS-25 | 3.31 |
| `pct_lang_home_yue_cantonese` | % | Total pop. excl. institutional residents | BCS-25 | 2.78 |
| `pct_lang_home_korean` | % | Total pop. excl. institutional residents | BCS-25 | 0.92 |
| `pct_lang_home_tagalog_pilipino_filipino` | % | Total pop. excl. institutional residents | BCS-25 | 0.9 |
| `pct_lang_home_iranian_persian` | % | Total pop. excl. institutional residents | BCS-25 | 0.66 |
| `pct_lang_home_spanish` | % | Total pop. excl. institutional residents | BCS-25 | 0.62 |
| `pct_lang_home_vietnamese` | % | Total pop. excl. institutional residents | BCS-25 | 0.41 |
| `pct_lang_home_hindi` | % | Total pop. excl. institutional residents | BCS-25 | 0.35 |
| `pct_lang_home_russian` | % | Total pop. excl. institutional residents | BCS-25 | 0.33 |
| `pct_lang_mt_english` | % | Total pop. excl. institutional residents (single responses) | BCS-100 | 67.15 |
| `pct_lang_mt_punjabi_panjabi` | % | Total pop. excl. institutional residents | BCS-100 | 4.86 |
| `pct_lang_mt_mandarin` | % | Total pop. excl. institutional residents | BCS-100 | 4.14 |
| `pct_lang_mt_yue_cantonese` | % | Total pop. excl. institutional residents | BCS-100 | 3.88 |
| `pct_lang_mt_tagalog_pilipino_filipino` | % | Total pop. excl. institutional residents | BCS-100 | 1.67 |
| `pct_lang_mt_spanish` | % | Total pop. excl. institutional residents | BCS-100 | 1.22 |
| `pct_lang_mt_korean` | % | Total pop. excl. institutional residents | BCS-100 | 1.21 |
| `pct_lang_mt_german` | % | Total pop. excl. institutional residents | BCS-100 | 1.02 |
| `pct_lang_mt_iranian_persian` | % | Total pop. excl. institutional residents | BCS-100 | 0.94 |
| `pct_lang_mt_vietnamese` | % | Total pop. excl. institutional residents | BCS-100 | 0.66 |
| `pct_lang_mt_hindi` | % | Total pop. excl. institutional residents | BCS-100 | 0.65 |
| `land_area_km2` | km2 | Land area of 2021 dissemination blocks allocated to district | StatCan GAF 2021 DB land area x geo/out/db_to_ed2023.csv | 920,686.55 |
| `density_per_km2` | persons/km2 | pop_2021 / land_area_km2 | derived | 5.4 |
| `pop_2016_approx` | persons | 2016 population on 2021 ADA geography, allocated to 2021 DAs by 2021 pop then to districts | StatCan SDMX DF_ADA (Population, 2016) + DF_DA (Population, 2021) + geo/out/da_to_ed2023.csv | 4,648,055 |
| `pop_2021_from_da` | persons | Total population (DA rollup cross-check) | StatCan SDMX DF_DA + geo/out/da_to_ed2023.csv | 5,000,879 |
| `pop_growth_2016_2021_pct_approx` | % | pop_2021_from_da / pop_2016_approx - 1 (same allocation for both years) | derived | 7.59 |
| `top_industry_1` | text | nan | BCS-25 | Health care and social assistance (12.3%) |
| `top_home_language_non_english_1` | text | nan | BCS-25 | Punjabi (Panjabi) (3.8%) |
| `top_industry_2` | text | nan | BCS-25 | Retail trade (11.6%) |
| `top_home_language_non_english_2` | text | nan | BCS-25 | Mandarin (3.3%) |
| `top_industry_3` | text | nan | BCS-25 | Professional, scientific and technical services (9.2%) |
| `top_home_language_non_english_3` | text | nan | BCS-25 | Yue (Cantonese) (2.8%) |
| `n_cells_used` | count | nan | derived (QA) | 662 |
| `n_cells_suppressed_x` | count | nan | derived (QA) | 0 |
| `n_cells_not_applicable` | count | nan | derived (QA) | 0 |
| `ed_name` | text | Elections BC name | Elections BC 2026 | |
| `n_cells_used` / `n_cells_suppressed_x` / `n_cells_not_applicable` | count | BC Stats cells read for this district | BCS | |
