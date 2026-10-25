# 2025 federal election (BC) on 2023 BC provincial districts

How the April 28, 2025 federal vote in British Columbia splits across the 93 provincial electoral districts used on October 24, 2026. The official totals for this layer are Elections Canada's. The district figures are estimates.

## Scorecard

| Party | BC votes (official) | Share | Provincial districts led |
|---|---|---|---|
| Liberal (LPC) | 1,105,033 | 41.79% | 42 |
| Conservative (CPC) | 1,088,655 | 41.17% | 44 |
| NDP | 343,670 | 13.00% | 6 |
| Green (GPC) | 79,255 | 3.00% | 1 |
| Others (OTH) | 27,456 | 1.04% | 0 |
| Valid total | 2,644,069 | | 93 |

Rejected ballots: 15,430. Electors: 3,844,085. Turnout: 69.2% (Elections Canada Table 3).

Close districts (lead under 0.5 points): Kelowna-Mission (LPC by 0.01), Penticton-Summerland (CPC 0.14), Bulkley Valley-Stikine (NDP 0.27), Coquitlam-Maillardville (CPC 0.34), Juan de Fuca-Malahat (CPC 0.49). At these margins the method cannot reliably say who led.

## Sources (details in manifest.json)
- Elections Canada, 45th General Election official voting results: poll results file for BC (`pollresults_resultatsbureau59.zip`, 43 ridings, 2023 representation order), plus Tables 3, 8 and 12 for the checks.
- Elections Canada polling division boundaries, 2025 (`PollingDivisionBoundaries_2025_SHP.zip`).
- Statistics Canada 2021 dissemination block populations (Geographic Attribute File 92-151-X, BC extract) and 2021 dissemination block polygons. Both come from the BC Data Catalogue and BC Geographic Warehouse copies, because www12.statcan.gc.ca returned HTTP 403 (a Cloudflare challenge) to this environment.
- BC provincial electoral districts, 2023 boundaries: `analysis/geo/raw/bcgw/ed2023.geojson` (BC Geographic Warehouse, EBC_ELECTORAL_DISTS_BS11). This is the unclipped version. Population weighting makes clipping irrelevant here, except for the 4 area-fallback polls listed below.

## Method
1. **Poll types** (from the poll number). Ordinary polling divisions are 1-399 (8,825 rows, including suffixes such as 95-3 and split letters such as 10A/10B). Single-building special polling divisions are the 400s (69). Mobile polls are the 500s (664). Advance polls are the 600s (1,160). Special voting rules groups are S/R 1 and S/R 2 (86).
2. **Combined polls.** 1,088 poll rows report "combined with" another poll. These rows carry zero votes, and the receiving poll carries them. Each receiving poll's footprint is the union of its own polygon and every polygon combined into it, with chains followed to the end.
3. **Geographic polls** (ordinary, 400s, mobile). Each poll footprint is intersected with the 2023 provincial districts. Each piece then gets 2021 population from dissemination blocks, intersected with area weighting inside each block (most blocks fall wholly in one piece). The poll's votes, per party, are split by population share. 8,714 reporting units used population. 4 used **area share** because their footprint had zero 2021 population: 59004-95-3, 59021-4-1, 59021-73-1 and 59031-2-2. These are all rural or remote, and the 4 together hold very few votes.
4. **Advance and special-ballot votes** (600s and S/R, together 51.5% of all BC votes). These polls are not tied to polling divisions. Within each federal riding, each party's advance + SVR votes are spread over the provincial districts in proportion to that party's own ordinary-geographic votes in that riding. Rejected ballots are treated the same way. This assumes that, within a riding, early and special-ballot voters split by district the way election-day voters did. Polls that served 2 or more districts are smoothed by this assumption. It is the largest source of uncertainty here.
5. **Mobile polls without a polygon.** 59019-502 and 59040-500 have no polygon in the boundary file. Both had 0 votes, so they are handled with step 4.
6. **Electors.** Each poll row's elector count is split by its own polygon's population share. The electors listed on S/R Group 1 rows (19,943 in BC) are spread within the riding in proportion to the riding's mapped electors.
7. **Turnout estimate** = (valid + rejected) / estimated electors, which matches the Elections Canada definition (ballots cast / electors). Elector lists change over the campaign, so treat this as approximate.
8. **No polls dropped.** Every one of the 10,804 BC poll rows is included. Void and no-poll rows carry 0 votes.

## Checks
| Check | Result |
|---|---|
| Poll file BC totals per party vs Table 8 (BC column) | exact match, all 4 named parties; others = valid (Table 3) minus the 4 |
| Poll file rejected ballots and electors vs Table 3 | 15,430 and 3,844,085, exact |
| Per-riding valid votes vs Table 12 | 0 of 43 ridings differ |
| Re-allocated per-party totals (unrounded) vs official | exact (LPC 1,105,033; CPC 1,088,655; NDP 343,670; GPC 79,255; OTH 27,456) |
| Re-allocated rejected and electors | 15,430 and 3,844,085, exact |
| Rounded CSV column sums | within 5 votes of official (LPC -2, CPC +1, NDP -5, GPC +2, OTH 0), from per-district rounding |
| 2021 population captured in poll x district pieces | 5,000,555 of 5,000,879 (99.99%) |
| Dissemination blocks matched to population file | 52,423 of 52,423 (103 have blank population in the GAF, treated as 0) |
| Federal ridings per provincial district | 1 to 4 contributing 1% or more of votes. Counting boundary slivers too, up to 10. |

All counts are in `scripts/allocation_log.json`.

## Data dictionary: fed2025_on_ed2023.csv (93 rows)
| Column | Meaning |
|---|---|
| ed_code | Elections BC district abbreviation (ED_ABBREVIATION, 2023 boundaries) |
| ed_name | District name |
| LPC_votes, CPC_votes, NDP_votes, GPC_votes | Estimated 2025 federal valid votes, Liberal / Conservative / NDP / Green, rounded |
| OTH_votes | All other candidates (PPC, independents, minor parties) |
| total_valid_votes | Sum of the five vote columns (before rounding, then rounded) |
| rejected_ballots | Estimated rejected ballots |
| *_share_pct | Party share of valid votes, % |
| electors_est | Estimated electors on the lists |
| turnout_est_pct | (valid + rejected) / electors_est, % |
| fed_winner | Party with the most estimated federal votes in the district (plurality) |
| margin_pts | Lead of first over second, percentage points |
| federal_ridings_overlapping | 2023-order federal ridings contributing 1% or more of the district's votes, with share |

## Comparison with 2024 provincial winners (results24/out/districts_2024_summary.csv)
| 2024 provincial winner | Fed LPC led | Fed CPC led | Fed NDP led | Fed GPC led |
|---|---|---|---|---|
| BC Conservative (44) | 10 | 33 | 1 | 0 |
| BC NDP (47) | 31 | 11 | 5 | 0 |
| BC Green (2) | 1 | 0 | 0 | 1 |

## Scripts
- `scripts/01_download_db.py`: downloads the dissemination block polygons (WFS, paged).
- `scripts/02_allocate.py`: builds the CSV and the log. Run with `python3 -I`.
- `scripts/03_manifest.py`: writes manifest.json with hashes.
