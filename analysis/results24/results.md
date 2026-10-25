# BC general elections 2024 and 2020: official results base

Built 2026-10-24 from Elections BC open data (BC Data Catalogue), Elections BC Statements of Votes and CEO reports, and the Legislative Assembly of BC. Every number in `out/` comes from the files listed in `manifest.json`. No rows were dropped.

## Scorecard

| Item | 2024 (93 EDs) | 2020 (87 EDs) |
|---|---|---|
| Seats | NDP 47, CON 44, GRN 2 | NDP 57, LIB 28, GRN 2 |
| Vote share | NDP 44.87, CON 43.28, GRN 8.24, IND 2.24, Unaffiliated 1.21 | NDP 47.69, LIB 33.77, GRN 15.09, CON 1.91 |
| Valid votes / rejected | 2,105,341 / 4,317 | 1,883,632 / 14,921 |
| Registered voters | 3,609,288 | 3,524,812 |
| Turnout (ballots considered / registered at close of voting) | 58.45% | 53.86% |
| Advance voting share of ballots | 47.49% (45.17 in-district + 2.32 out-of-district) | 35.35% |
| Vote by mail share | 3.73% | 31.41% |
| Races under 5 points | 22 | n/a |
| Judicial recounts | Kelowna Centre, Surrey-Guildford, Prince George-Mackenzie (partial) | West Vancouver-Sea to Sky |

Turnout denominator: Elections BC divides "registered voters who voted" (valid + rejected ballots considered) by total registered voters at close of voting (SOV 2024 p.1, district summary pp.13-15). Our sums match the SOV exactly for every district (validated by script, 0 differences), both years.

## Five notable facts

1. Majority by one seat: NDP 47 of 93 (exactly the 47 needed), on 44.87% vs Conservatives 43.28% (33,426 votes apart province-wide).
2. Surrey-Guildford was decided by 22 votes (0.12 pts) after a judicial recount cut the margin from 27; Kelowna Centre went Conservative by 40 (recount widened it from 38). Five seats were decided by under 1 point; four of the five closest were under 100 votes.
3. On notional 2020 results (transposed to the new map), the NDP would have held 62 of 93 seats; it lost 17 notional NDP seats to the Conservatives and took 2 from notional BC Liberal seats (Vancouver-Langara, Vancouver-Yaletown).
4. Advance voting was the largest single channel in 2024 (47.5% of ballots), while mail collapsed from 31.4% (pandemic 2020) to 3.7%.
5. Turnout ranged from 44.82% (Surrey City Centre) to 69.80% (Oak Bay-Gordon Head). 22 of 58 sitting MLAs on the ballot lost (15 NDP).

## Files (`out/`)

| File | Grain |
|---|---|
| districts_2024.csv | district x candidate, 2024 |
| districts_2024_summary.csv | district, 2024 |
| voting_places_2024_long.csv | reporting unit x candidate (official rows) |
| voting_places_2024_wide.csv | reporting unit (voting place x opportunity), party columns |
| va_to_voting_place_2024.csv | 2024 voting area -> assigned final voting place (join key to results) |
| province_2024.csv, province_2024_by_opportunity.csv | province |
| districts_2020.csv, districts_2020_summary.csv | 2020 on 87 old districts |
| voting_areas_2020.csv | 2020 election-day results per voting area (EDVA code joins 2017 VA polygons) |
| advance_places_2020.csv | 2020 advance results per voting place |
| province_2020.csv, province_2020_by_opportunity.csv | province |
| transposed_2020_on_2023_eds.csv | 2020 results on the 93 new districts (our transposition) |
| transposed_2020_flows_ed20_to_ed23.csv | votes moving from each old district to each new district |
| va2020_to_ed2023_weights.csv | weight of each 2020 VA in each new district |
| close_races_2024.csv | 2024 margin < 5 pts |
| seat_changes_2020n_2024.csv (+ _all) | notional 2020 winner vs 2024 winner |

Scripts (`scripts/`, run in order with `python3 -I <script> analysis/results24`): parse_sov.py (takes txt, year, out dir), build_2024.py, build_2020.py, transpose_2020.py, compare.py, add_pre2026_holder.py, make_manifest.py. `work/` holds the parsed SOV tables used for cross-checks.

## What exists and what does not

- 2024 voting-area results: **not published, by design.** Elections BC (SOV 2024 p.2 and data dictionary, April 17 2025) says 2024 used "first-come, first-served" voting, so results exist only by voting place, not by voting area. Finest 2024 level = voting place x voting opportunity. To map them: `va_to_voting_place_2024.csv` lists, for every 2024 areal VA, its assigned final voting place (`vp_key` = Elections BC ID prefix). All 1,241 final voting places match. Advance and other opportunities are not area-based (in-district voters could use any advance place; mail, special, DEO and telephone are district-wide).
- Initial vs final count: the open data gives only certified final totals per opportunity. "Final voting - out-of-district" and the other ED-wide lines hold most final-count ballots (CEO report: 63,764 ballots considered at final count). A separate initial-count snapshot is not published as data.
- 2020 transposed to 2023 districts: **neither Elections BC nor the 2021-2023 Electoral Boundaries Commission published one** (searched the Commission's final report, Elections BC results and maps pages, and the BC Data Catalogue). Elections BC did publish a 2017-to-2024 VA conversion table (`raw/ebc_edva_conv`), which lists intersecting VAs but no weights, so I built the transposition myself.
- Dissemination-block population (StatCan): download refused (HTTP 403 bot-check). I used official 2024 registered voters per 2024 VA as the weight instead (finer than area, and from the same agency).

## Transposition method (2020 -> 93 districts)

1. Overlay 2020 VA polygons (2017 gazette, 5,658 areal) with 2024 VA polygons (5,778). Weight of each piece = 2024 registered voters of the 2024 VA x share of that VA's area in the piece. The piece belongs to the 2023 district of its 2024 VA. Slivers under 1 m² ignored. 2020 site-based VAs (619 care-home points) go wholly to the district containing the point (all fell inside one).
2. Election-day votes per 2020 VA are split by those weights (fractional, not winner-take-all; a largest-share flag is also kept).
3. Advance, mail, absentee, special and DEO votes (reported only per old district, 71% of 2020 ballots) are split per party in proportion to that party's transposed election-day votes from the same old district.
4. Checks: totals preserved exactly (1,883,632); transposed 2020 registrations vs actual 2024 registrations per new district: median ratio 1.02, range 0.93 to 1.17 (fastest growth Langley-Walnut Grove, Langford-Highlands).
- Limits: within-district differences between election-day and advance or mail voters are lost in step 3. Notional winners with margins under about 3 pts are sensitive to this (Kamloops Centre LIB +0.90, Surrey-White Rock LIB +0.82, Vancouver-Langara LIB +2.43).

## Recounts 2024 (Report of the CEO, pp.58-63)

| District | What happened | Certified margin |
|---|---|---|
| Surrey-Guildford | Judicial recount Nov 7-8 (Justice Loo); earlier recount request declined | 22 (from 27) |
| Kelowna Centre | DEO partial recount, then judicial recount Nov 7-8 (Justice Beames) | 40 (from 38) |
| Prince George-Mackenzie | Partial judicial recount Nov 8 of an uncounted advance box (861 ballots) | 6,068 (from 5,705) |
| Juan de Fuca-Malahat | Automatic DEO full recount (initial margin ≤100); 2 quarantined boxes counted first under CEO Order | 141 |
| Surrey City Centre | Automatic DEO full recount; outcome confirmed | 232 |
| Courtenay-Comox, Maple Ridge East, Oak Bay-Gordon Head | Recount requests declined | as certified |

A CEO Order (EA-ORD040-2024) added unreported out-of-district votes found on 11 tabulator tapes (CQB 76, SRC 214, SWR 441, WVS 22, BDS 28 votes, spread over 69 districts). The open data matches the SOV, so it includes these corrections. 2020: West Vancouver-Sea to Sky judicial recount, margin 41 -> 60.

## Closest 2024 races (margin < 5 pts)

Surrey-Guildford NDP 22 (0.12); Kelowna Centre CON 40 (0.16); Courtenay-Comox CON 93 (0.27); Maple Ridge East CON 97 (0.38); Juan de Fuca-Malahat NDP 141 (0.59); Penticton-Summerland CON 317 (1.13); Surrey-Panorama CON 263 (1.49); Surrey City Centre NDP 232 (1.62); Coquitlam-Burke Mountain NDP 368 (1.70); Vernon-Lumby NDP 476 (1.72); Richmond-Steveston NDP 484 (2.07); North Island CON 639 (2.14); Surrey-Serpentine River CON 435 (2.21); Vancouver-Langara NDP 419 (2.38); West Vancouver-Sea to Sky GRN 676 (2.47); Surrey-Cloverdale CON 586 (2.75); Cowichan Valley NDP 849 (2.92); Columbia River-Revelstoke CON 670 (3.66); Surrey-Fleetwood NDP 753 (3.69); Langley-Willowbrook CON 867 (3.81); Saanich North and the Islands GRN 1,350 (3.96); Langley-Walnut Grove CON 1,172 (4.79).

## Seats changing hands, notional 2020 -> 2024 (46)

- NDP -> CON (17): Abbotsford-Mission; Boundary-Similkameen; Bulkley Valley-Stikine; Chilliwack-Cultus Lake; Chilliwack North; Courtenay-Comox; Fraser-Nicola; Langley-Walnut Grove; Langley-Willowbrook; Maple Ridge East; North Island; Richmond Centre; Richmond-Queensborough; Surrey-Cloverdale; Surrey North; Surrey-Panorama; Surrey-Serpentine River.
- LIB -> NDP (2): Vancouver-Langara; Vancouver-Yaletown.
- LIB -> CON (27, label change: BC Liberals became BC United, which suspended its 2024 campaign): Abbotsford South; Abbotsford West; Cariboo-Chilcotin; Columbia River-Revelstoke; Delta South; Kamloops Centre; Kamloops-North Thompson; Kelowna Centre; Kelowna-Lake Country-Coldstream; Kelowna-Mission; Kootenay-Rockies; Langley-Abbotsford; Nechako Lakes; Peace River North; Peace River South; Penticton-Summerland; Prince George-Mackenzie; Prince George-North Cariboo; Prince George-Valemount; Richmond-Bridgeport; Salmon Arm-Shuswap; Skeena; Surrey South; Surrey-White Rock; Vancouver-Quilchena; West Kelowna-Peachland; West Vancouver-Capilano.
- No notional NDP seat went Green; the 2 Green seats stay Green.

## Incumbency

- Before the 2024 vote: `member_of_previous_parliament` and `sitting_mla_candidates` come from the SOV asterisk ("Member of the 42nd Parliament"). Elections BC does not state an incumbent party for the new districts (boundaries changed), so none is assigned.
- Before the 2026 vote: the Legislative Assembly "Current Party Standings" page (accessed 2026-10-24) gives NDP 47, Conservative 39, Green 2, Independent 5 = 93 at dissolution (Sept 22 2026). Per-district holders come from the Assembly's LIMS API (`lims_43rd_*` columns). **Anomaly:** the API's per-seat party labels sum to NDP 47, CP 29, Independent 13, Green 2, vacant 2, which does not match the standings page. Values are kept verbatim. Use the standings page for totals and check the per-seat labels before publishing.

## Anomalies and data notes

- The 2020 VA results CSV has a UTF-8 BOM but its body is Latin-1 (é, ç, ö). It was decoded as Latin-1; the voting-place CSV is valid UTF-8.
- COMBINED_INDICATOR = Y rows (2020: 3,921; 2024: 286): to protect ballot secrecy, small units are reported under another unit (`reported_under`). Their own rows show 0 and the receiving unit holds the votes. They are kept; totals are unaffected.
- "Unaffiliated" (2024, 25,464 votes) = blank AFFILIATION in the open data (mostly former BC United candidates). Labelled UNAF, as in the SOV.
- Party codes: NDP, CON (2024 Conservative Party; 2020 "Conservative"), LIB (BC Liberal Party 2020), GRN, IND, UNAF, LBN, FPBC, COMM, CHP, BCV, WEXIT, RURAL, OTH (transposition only).

## Data dictionary

districts_2024.csv / districts_2020.csv: `ed_code` (Elections BC 3-letter code), `ed_name`, `candidate` (open data "Last, First"), `ballot_name` (SOV), `affiliation` (official), `party` (code), `votes` (certified final), `vote_share_pct` (of district valid votes), `rank`, `elected` (Elections BC flag; equals rank 1 in all districts), `member_of_previous_parliament`, `votes_<opportunity>` (2024: adv, adv_ood, final, final_ood, special, deo, mail, atv; 2020: general, adv, mail, absentee_in_ed, absentee_out_ed, absentee_adv, special, deo), `registered_voters`, `total_valid_votes`, `rejected_ballots`, `ballots_considered` (valid + rejected), `turnout_pct` (ballots_considered / registered), `margin_votes` and `margin_pts` (first minus second, votes and rounded share points), `margin_pts_exact` (2024).
districts_2024_summary.csv: winner and second (party, name, votes, share), margin, totals, turnout, `sitting_mla_candidates`, `sitting_mla_won`, `recount_note`, `judicial_recount`, `deo_recount`, `ceo_order_unreported_ood_votes_added`, `n_candidates`, `lims_43rd_members`, `lims_43rd_party_latest_active`.
voting_places_2024_wide.csv: `vp_key` (Elections BC ID minus candidate digits), `ed_code`, `voting_opportunity`, `voting_location`, `address_standard_id`, `combined`, `reported_under`, party columns, `REJECTED`, `total_valid`.
va_to_voting_place_2024.csv: `edva_code` (joins 2024 VA polygons, layer WHSE_ADMIN_BOUNDARIES.EBC_VOTING_AREAS_BS11_POLY_SVW), `address_standard_id`, `building_name`, `registered_voters_2024`, `va_type`, `vp_key`.
voting_areas_2020.csv: `edva_code` (joins 2017 VA polygons, `raw/ebc_va_shp_2017`), party columns, `REJECTED`, `combined`, `reported_under`, `va_type`, `registered_voters`, `total_valid`.
transposed_2020_on_2023_eds.csv: party votes (fractional), `REJECTED`, `total_valid`, `registered_2020`, `<party>_pct`, `turnout_pct`, `notional_winner_2020`, `notional_second_2020`, `notional_margin_pts_2020`, `election_day_share_of_votes` (share of the district's transposed votes that came from geographic VA results).
va2020_to_ed2023_weights.csv: `va20`, `ed20`, `ed23`, `w_reg`, `area` (m²), `share`, `basis`, `is_largest`.
province_*_by_opportunity.csv: valid, rejected and ballots per voting opportunity and share of ballots.
