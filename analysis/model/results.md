# BC 2026: pre-results seat estimate (polls vs the count)

**Frozen 2026-10-24T10:41:31+00:00 UTC (2026-10-24T03:41:31-07:00 (PDT)), 978 minutes before polls closed (8 p.m. Pacific, 03:00 UTC Oct 25).** Hashes of inputs, outputs and scripts are in `model_frozen.json`.

## Method in plain words

1. **Poll average.** For each pollster, take its last poll with fieldwork ending on or after Sept 22, 2026 (election call). Average them with equal weight. No adjustments for sample size, mode or house effects.
2. **Regions.** Each of the 93 districts goes to Metro Vancouver, the Capital Region or the rest of BC, by where most of its 2021 census population lives (census divisions 5915 and 5917). Metro Vancouver uses the regional poll average where at least 2 pollsters publish that region. No pollster publishes the Capital Region alone, so it gets the change pollsters show for Vancouver Island. The rest of BC is whatever keeps the province total equal to the poll average.
3. **Swing.** Uniform: each party's 2024 district share plus the change in its regional share. Proportional: the 2024 district share multiplied by the ratio of new to old regional share. Parties are then scaled so each region's total matches its target and each district adds to 100.
4. **New parties and gaps.** CentreBC and OneBC ran nowhere in 2024. Their poll share is spread evenly over only the districts where they have a 2026 candidate, scaled so the regional total still matches the poll. A party with no 2026 candidate in a district gets 0 and its share is spread over the other parties there by rescaling (NDP has no candidate in Peace River North). A party running where it did not run in 2024 starts from its 2024 regional average.
5. **Tiers** (lead over second place): toss-up under 3 points, lean under 8, likely under 15, safe 15 or more.

## Poll average

| Party | Average | Pollsters |
|---|---|---|
| NDP | 38.9 | 10 |
| Conservative | 43.8 | 10 |
| Green | 12.0 | 10 |
| CentreBC | 1.7 | 7 |
| OneBC | 2.4 | 7 |
| Other | 1.2 | remainder |

Polls used: Liaison Strategies (2026-10-08); Angus Reid (2026-10-19); Innovative Research (2026-10-19); Pollara (2026-10-21); Leger (2026-10-22); Ipsos (2026-10-22); Pallas Data (2026-10-22); Mainstreet Research (2026-10-23); Research Co. (2026-10-23); Forum Research (2026-10-23).

Regional targets (% of valid votes) vs 2024:

| Region | NDP | Conservative | Green | Basis |
|---|---|---|---|---|
| Metro Vancouver | 40.4 (-10.2) | 44.0 (+1.7) | 11.5 (+6.7) | poll avg (n=7) |
| Capital Region | 42.9 (-3.8) | 30.1 (+1.0) | 24.1 (+0.3) | 2024 + Vancouver Island poll change (n=7) |
| Rest of BC | 36.1 (-1.9) | 47.1 (-0.8) | 9.5 (+1.5) | residual to match province |

## Projected seats (47 for a majority)

| Party | Uniform swing | Proportional swing | 2024 result |
|---|---|---|---|
| NDP | 33 | 31 | 47 |
| Conservative | 58 | 60 | 44 |
| Green | 2 | 2 | 2 |

- **Uniform** tiers: CON-lean 9, CON-likely 11, CON-safe 30, CON-toss-up 8, GRN-lean 2, NDP-lean 4, NDP-likely 10, NDP-safe 14, NDP-toss-up 5
- **Proportional** tiers: CON-lean 10, CON-likely 12, CON-safe 29, CON-toss-up 9, GRN-lean 1, GRN-likely 1, NDP-lean 4, NDP-likely 11, NDP-safe 12, NDP-toss-up 4

## Toss-ups (lead under 3 points)

| District | Region | Uniform | Proportional |
|---|---|---|---|
| Burnaby Centre | Metro Vancouver | NDP +2.3 (toss-up) | NDP +0.9 (toss-up) |
| Burnaby East | Metro Vancouver | CON +0.7 (toss-up) | CON +1.0 (toss-up) |
| Burnaby North | Metro Vancouver | CON +1.6 (toss-up) | CON +2.3 (toss-up) |
| Coquitlam-Maillardville | Metro Vancouver | NDP +0.2 (toss-up) | CON +0.1 (toss-up) |
| Courtenay-Comox | Rest of BC | CON +1.0 (toss-up) | CON +1.1 (toss-up) |
| Cowichan Valley | Rest of BC | NDP +2.1 (toss-up) | NDP +1.9 (toss-up) |
| Delta North | Metro Vancouver | NDP +0.6 (toss-up) | CON +0.1 (toss-up) |
| Kelowna Centre | Rest of BC | CON +1.1 (toss-up) | CON +1.3 (toss-up) |
| Maple Ridge-Pitt Meadows | Metro Vancouver | CON +2.2 (toss-up) | CON +3.4 (lean) |
| North Island | Rest of BC | CON +2.7 (toss-up) | CON +2.9 (toss-up) |
| Penticton-Summerland | Rest of BC | CON +2.1 (toss-up) | CON +2.3 (toss-up) |
| Port Coquitlam | Metro Vancouver | NDP +3.1 (lean) | NDP +2.4 (toss-up) |
| Port Moody-Burquitlam | Metro Vancouver | CON +0.5 (toss-up) | CON +0.9 (toss-up) |
| Vernon-Lumby | Rest of BC | NDP +0.9 (toss-up) | NDP +0.7 (toss-up) |

Variants disagree on: Coquitlam-Maillardville (uniform NDP, proportional CON), Delta North (uniform NDP, proportional CON).

## Limits

- Swing models carry 2024 patterns forward. They ignore candidate effects: Conservatives who sat as independents or joined CentreBC and are now running again as Conservatives, Elenore Sturko (CentreBC leader, Surrey South), Dallas Brodie (OneBC, Vancouver-Quilchena), Jordan Kealy (independent incumbent, Peace River North), and open seats.
- CentreBC and OneBC get a flat share where they run; real support will be lumpy. Their poll shares come from only 7 of 10 pollsters (Pallas, Forum and Innovative do not report them separately).
- The Capital Region uses Vancouver Island poll numbers as a proxy. Regional subsamples are small (often 150 to 300 people) and pollsters define regions differently; only exactly matching labels are used.
- Rest of BC is a residual, so any error in the Metro or Island figures lands there.
- Simple average: no weighting by recency, sample size or pollster track record. One poll per pollster.
- No uncertainty interval. The toss-up list is where a normal polling miss (2 to 3 points) flips the seat.
- 2024 shares are on the same 2023 boundaries, so no transposition is needed.

## Files

- `out/poll_average.json`, `out/polls_used.csv`: poll average and the polls in it
- `out/regions.csv`: district to region
- `out/districts_projection.csv`: every district, 2024 shares, both variants, winner, margin, tier
- `out/projection_summary.json`: seats, targets, tiers, toss-ups
- `model_frozen.json`: freeze time and SHA-256 hashes
- `scripts/run_all.sh` rebuilds; `scripts/compare.py [results.csv]` runs polls vs the count (default `analysis/live/latest.csv`, columns district code, party, votes) into `out/compare/`.
