# BC general election, October 24, 2026: findings (Elections BC results as of October 25, 2026, 1:49 a.m. Pacific)

Source snapshot: Elections BC results files, 2026-10-25 11:58 UTC, 7,237 of 7,268 ballot boxes (all 588 advance boxes). The 31 boxes left are in 6 ridings where the leader is ahead by 5.3 points or more. Final count (mail, absentee, out-of-district): planned for November 6 to 10, 2026 (Elections BC 2026 election page, key dates). In 2024 these late ballots leaned NDP: Conservatives 42.7% of the two-party vote vs 49.5% in the other ballots, so the narrow Conservative leads (89, 132, 150, 387, 395 votes) are most at risk. All numbers below are the initial count and will move a little.

Scripts: `analysis/full.py` (all tables in `analysis/out/`), log in `analysis/out/full_log.txt`.

## 1. Result
| Party | Votes | Share 2026 | Share 2024 | Change | Ridings leading | Seats 2024 |
|---|---|---|---|---|---|---|
| Conservative | 861,258 | 48.05% | 43.28% | +4.77 | 64 | 44 |
| NDP | 669,901 | 37.38% | 44.87% | -7.49 | 27 | 47 |
| Green | 196,593 | 10.97% | 8.24% | +2.73 | 2 | 2 |
| CentreBC | 28,998 | 1.62% | new | | 0 | |
| OneBC | 26,991 | 1.51% | new | | 0 | |
| Other | 8,494 | 0.47% | 3.62% | | 0 | 0 |

- Majority line is 47. Conservatives lead in 64.
- Votes per riding led: Conservative 13,457, NDP 24,811, Green 98,296.
- Conservative-NDP two-party share: 49.1% in 2024, 56.2% in 2026.

## 2. History (Elections BC series 1928 to 2024)
- 48.05% is the highest share for any party since the BC Liberals' 57.62% in 2001 (BC Liberals 2005 to 2013: 44.13% to 45.82%).
- 64 seats is the most for any party since 2001 (BC Liberals 77 of 79). BC Liberals won 46, 49, 49, 43 from 2005 to 2017.
- Best Conservative Party share since its last win in 1928 (53.30%, 35 of 48 seats; Electoral History of BC 1871-1986, p.159).
- NDP 37.38%: lowest since 2001 (21.56%).

## 3. Seats that changed hands: 22
- NDP to Conservative: 21. Metro Vancouver 16 (Surrey 4: City Centre, Fleetwood, Guildford, Newton; Burnaby 2: Centre, North; Coquitlam 2; Port Moody-Burquitlam; Delta North; Richmond-Steveston; North Vancouver-Seymour; Maple Ridge-Pitt Meadows; Vancouver 3: Fraserview, Langara, Yaletown), Capital Region 2 (Saanich South, Juan de Fuca-Malahat), Vancouver Island 2 (Cowichan Valley, Ladysmith-Oceanside), Okanagan 1 (Vernon-Lumby).
- Conservative to NDP: 1, Courtenay-Comox.
- 21 sitting MLAs running are trailing: 17 NDP, plus Brennan Day (CON, Courtenay-Comox), Jordan Kealy (Ind, Peace River North), Elenore Sturko (CentreBC, Surrey South), Dallas Brodie (OneBC leader, Vancouver-Quilchena).

## 4. Where: Metro Vancouver decided it
| Region | Ridings | CON 24 → 26 | NDP 24 → 26 | GRN 24 → 26 | CON seats 24 → 26 | NDP seats 24 → 26 |
|---|---|---|---|---|---|---|
| Metro Vancouver | 46 | 42.3 → 48.4 | 50.6 → 39.2 | 4.9 → 8.8 | 16 → 32 | 30 → 14 |
| Capital Region | 8 | 29.2 → 30.9 | 46.7 → 37.2 | 23.8 → 29.0 | 0 → 2 | 7 → 5 |
| Rest of Vancouver Island | 8 | 38.5 → 42.2 | 45.7 → 45.6 | 12.8 → 11.6 | 2 → 3 | 6 → 5 |
| Fraser Valley | 5 | 56.7 → 60.2 | 40.3 → 33.9 | | 5 → 5 | 0 → 0 |
| Okanagan | 6 | 46.9 → 52.2 | 36.9 → 36.2 | | 5 → 6 | 1 → 0 |
| Interior and North | 20 | 51.8 → 56.0 | 33.0 → 29.0 | 9.2 → 10.3 | 16 → 16 | 3 → 3 |
Regions: regional district of each riding (BC Data Catalogue), Maple Ridge counted in Metro Vancouver. Average two-party swing: Metro Vancouver 9.0 points, every one of its 46 ridings moved toward the Conservatives (1.0 to 15.2).

## 5. Who moved (2021 Census by riding)
Method: Conservative share of the two-party vote, 2024 vs 2026, which reduces (does not remove) distortion from 2024 independents and Green entry or exit; Peace River North (no NDP candidate in 2026) is excluded from swing statements. Ridings split into quarters. These are links between ridings, not how individuals voted.

| Riding trait (low vs high quarter) | Two-party swing, low | High | r |
|---|---|---|---|
| Median household income ($72k vs $104k) | 3.9 | 11.0 | 0.57 |
| Median home value ($424k vs $1.29M) | 3.2 | 11.1 | 0.55 |
| Indigenous (1.6% vs 14.4%) | 9.4 | 2.7 | -0.48 |
| Immigrants (10% vs 52%) | 3.0 | 8.6 | 0.43 |
| University degree (18% vs 50%) | 3.2 | 8.1 | 0.41 |
| Visible minority (5% vs 75%) | 3.9 | 8.6 | 0.39 |
| South Asian (1% vs 16%) | 3.2 | 8.7 | 0.31 |
| Chinese (1% vs 32%) | 2.8 | 8.3 | 0.24 |
| Renters (19% vs 46%) | 6.1 | 6.0 | -0.05 |
| Median age (39 vs 50) | 7.1 | 6.2 | -0.08 |

- Income is the strongest and most robust link: r 0.57 overall, 0.62 in the 56 ridings with the same field of parties both times, 0.70 inside Metro Vancouver. It holds when immigrants, renters, age, education and a Metro Vancouver marker are held constant (about 3.3 points of swing per standard deviation of income, t 4.9).
- Immigrant, visible minority, Chinese and education links mostly fade once income, age, renters and Metro Vancouver are held constant. Median age becomes significant with income held constant (older ridings moved more, t 3.2). South Asian share keeps a small link (t 2.3, 1.7 in same-field ridings).
- Renters: no link to the swing, but a strong link to the level of the vote (r -0.54 with two-party Conservative share): renter-heavy ridings stayed NDP.
- Where the NDP vote went: in high-education, high-value ridings the Green vote rose most (Green change r 0.40 with university share); in high-income ridings the Conservatives gained most.
- Not available by riding: ethnic origin (ancestry), candidate gender. Gender of residents (men+ share) shows no robust link.

## 6. Two ballots: 2025 federal vote on the same ridings
| Federal 2025 plurality (re-allocated votes) | Ridings | NDP change | CON change | Two-party swing | CON lead 2026 | NDP lead 2026 | Flips |
|---|---|---|---|---|---|---|---|
| Liberal | 42 | -10.5 | +5.5 | 8.9 | 25 | 16 | 15 |
| Conservative | 44 | -4.6 | +4.8 | 4.9 | 38 | 6 | 7 |
| NDP | 6 | -5.5 | -1.2 | 0.7 | 1 | 5 | 0 |
| Green | 1 | -14.7 | +1.9 | | 0 | 0 | 0 |
- Federal Liberal share and NDP drop: r -0.59. 15 of 22 flips were in ridings where Liberals had the most votes in April 2025.

## 7. Polls vs the count
- Final poll average (frozen 03:41 PT Oct 24): CON 43.84, NDP 38.87, GRN 12.00. Count: CON +4.21, NDP -1.49, GRN -1.03.
- Metro Vancouver: CON 44.0 polled vs 48.4 counted. Vancouver Island: polls within 2 points for every party.
- Frozen seat estimate: CON 58, NDP 33, GRN 2. Right leader in 81 of 93 ridings (proportional variant 83). The 13 toss-ups (uniform variant, under 3 points) went CON 11, NDP 2.

## 8. Turnout (election-night ballots only; final turnout comes with the final count)
- Initial count 2026: 1,796,615 ballots including rejected (48.06% of 3,738,182 registered, Oct 14 list).
- No like-for-like 2024 figure exists: the 2026 initial count includes all advance, district office and in-district special ballots. Comparable 2024 estimates give 51.07% (advance in district plus voting day) to 55.05% (adding district office and special). Turnout is down by somewhere between 3 and 7 points; the real figure comes with the final count. Not for slides.

## 9. New parties and leaders
- CentreBC: 35 ridings, 4.24% where it ran; best Oak Bay-Gordon Head 10.4%, Surrey South 10.1%. Leader Elenore Sturko third in Surrey South (10.1%).
- OneBC: 33 ridings, 4.13% where it ran; best Kelowna-Lake Country-Coldstream 11.4%. OneBC leader Dallas Brodie 4.0% in Vancouver-Quilchena.
- Ridings where a new party's vote was larger than the winning margin: CentreBC 4 (Surrey City Centre, Courtenay-Comox, Oak Bay-Gordon Head, Vancouver-Point Grey); OneBC 6 (Kelowna Centre, Penticton-Summerland, Surrey City Centre, Burnaby East, Burnaby South-Metrotown, Kootenay Central). This shows where they could have mattered, not where they did.
- David Eby holds Vancouver-Point Grey: 42.97% vs 40.01%, 538 votes. Lorne Doerkson 77.1% in Cariboo-Chilcotin. Emily Lowan (Green) wins Saanich North and the Islands with 48.5%. Jordan Kealy (Ind) 14.3% in Peace River North.

## 10. Close races (recount watch for the final count)
| Riding | Leading | Margin |
|---|---|---|
| Burnaby South-Metrotown | NDP | 66 |
| Ladysmith-Oceanside | CON | 89 |
| Kelowna Centre | CON | 132 |
| Cowichan Valley | CON | 150 |
| Burnaby East | NDP | 241 |
| Port Coquitlam | NDP | 386 |
| Vancouver-Fraserview | CON | 387 |
| Surrey City Centre | CON | 395 |
- 4 ridings under 1 point; 18 under 5 points (22 in 2024).

## Cautions
- Initial count only; say "leads", not "won". Final count adds mail and out-of-district ballots, which leaned NDP in 2024.
- Riding-level links are ecological. Wording: "ridings with higher incomes moved more", never "higher-income voters".
- Big raw swings in West Vancouver-Capilano, Kootenay-Rockies, Prince George-North Cariboo, West Kelowna-Peachland and Peace River North come mainly from 2024 independents not running again. Do not present them as voter swings.
