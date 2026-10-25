# Final check 4: B.C. election carousel, website, methodology and post text

Checked October 25, 2026, 15:20 to 15:50 EDT, against Elections BC's results files as posted October 25, 2026, 1:49 a.m. Pacific (`analysis/live/raw/snapshots/20261025T150040Z/GE-2026-10-24_Candidate.csv` and `_Party.csv`), the 2024 voting-place open data, the 2005 to 2020 voting-area file, the 2001 district file, the Electoral History of BC 1871 to 1986 (1928 summary page), the BC Stats 2021 profiles by riding, StatCan 2021 block areas and census-division names, the federal 2025 allocation file and Elections Canada Table 8, the pollster PDFs and the platform PDF (Draft 18). Every slide number and every number in the personal sentences of all 93 ridings was recomputed from those files, not from `story.json`.

The site was run in Playwright at 390 px and 1280 px, light and dark, with every "More about this" open, all 93 ridings chosen in turn (Victoria-Beacon Hill, Saanich North and the Islands, West Vancouver-Sea to Sky, Kelowna-Mission, Peace River North, Cowichan Valley and Surrey-Guildford read in full), the finder with "Surrey-Guild", "Kelowna" and a nonsense string, both sliders, every chip, year, worry, promise, region and income-education button, and taps on dots in the income, place-type, scatter and seat charts.

Files checked: `slides/slides.html` and the 8 JPGs built 15:08 (md5 d9423c60...), `index.html` built 15:22:51 (md5 a2ead94a...), `METHODOLOGY.md` 15:18 (md5 d5b00fc6..., identical to a fresh build from `methods/`), `post/post-text.md` 14:50. Builders were being edited for A17 during the check (paths only; `story.json` and `site.json` content did not change). Anything rebuilt after 15:48 EDT was not checked.

## Scorecard

| Area | Errors | Overstatements | Visual or interaction | Style |
|---|---|---|---|---|
| Slides | 0 | 1 (low) | 1 | 3 |
| Website | 5 | 4 | 4 | 1 |
| METHODOLOGY.md | 3 | 3 | n/a | 2 |
| Post text | 0 | 0 | n/a | 1 |

Every number on the 8 slides is correct. Nothing on the slides sits outside x 180 to 900 and every source line fits. The site has no console errors and no horizontal overflow at 390 or 1280 px, light or dark. Nothing anywhere says the account will track or follow up on promises, or forecasts what voters will do. Fix first: E1 (two riding regions), E2 to E4 (METHODOLOGY), C1 and C2 (labels printing over each other in "Which ridings changed party").

## Status of the final-check-3 items

| Item | Status | Evidence |
|---|---|---|
| A1 | Fixed | Stayed Conservative card shows 28% (28.48% recomputed from BC Stats counts). |
| A2 | Fixed | Every riding chip and Green-race sentence matches the raw files; Victoria-Swan Lake now "rose 12.1". One new double-rounding case: E5. |
| A3 | Fixed | All 92 swing values in the where, who and card text match. |
| A4 | Fixed | Now worded as "the kinds of ballots left to the 2026 final count". See O4. |
| A5 | Fixed for West Vancouver-Sea to Sky and Powell River-Sunshine Coast | Both in "Rest of Vancouver Island and Coast", as METHODOLOGY says. Two other ridings are mislabelled: E1. |
| A6 | Fixed | Density first: active core 13 (+5.7), transit suburb 25 (+8.7), car suburb 20 (+9.0), exurban and rural 34 (+3.9); 8.8 against 4.4; 14 of 22. |
| A7 | Fixed | Victoria-Beacon Hill gets the Green-race sentence; the others say "one of five ridings". |
| A8 | Fixed | |
| A9 | Fixed | "a weighted sample of 1,000". |
| A10 | Fixed | Jordan Kealy (Independent), Helen Scott (Unaffiliated), Ed Ewald (Christian Heritage, as Elections BC's file has it). No card shows "(Other)". |
| A11 | Fixed | "Platform pages 7, 61, 64". |
| A12 | Fixed | 2001 Conservative 0.15% (2,417 votes) in both data files. |
| A13 to A16 | Fixed | N18 Where "Site"; N27 holds the federal-group swings; "the website says British Columbians"; owner and renter households, band housing left out. |
| A17 | Push time | The cited inputs are now copied under `analysis/` and every Source file path in the table exists; the repository still has only the Initial commit. |
| B1 | Fixed | Slide 3 lead and the post text. |
| B2 | No longer applies | Slide 5 now shows income groups. |
| B3 | Partly fixed | Site: "(federal results estimated on provincial ridings)" and "about even ... estimated" for all five ridings within 0.5 point. Slide 6 adds "Federal votes were allocated to provincial ridings by population." but its subtitle still states the grouping as fact (O5), and the riding card ("2025 federal vote: Liberal 48.2%") and the map tooltip ("most votes for the Liberals") do the same for Kelowna-Mission. |
| B4 | Fixed | "Not comparable" sentence dropped; Green races have their own sentence and card line; swing stays in the averages and is documented. METHODOLOGY describes the five wrongly: E2. |
| B5 to B9, B11 | Fixed | |
| B10 | Unchanged | Acceptable, as before. |
| (c)1 to (c)4 | Fixed | Cowichan Valley at 150 is listed once; "← Conservatives" and "NDP →" at 390 px; the who sentence no longer ranks; "Victoria area (Capital Region)" everywhere. |
| (d)1 | Partly fixed | "20" is gone; "44" still repeats, and new repeats appear (D1). |
| (d)2 | Partly fixed | Post text fixed; slide 6 still pairs only in the chart note (D2). |
| (d)3 | Fixed | "Pattullo to December 9, 1941", "July 18, 2017"; campaign-view ticks carry the year. |
| (d)4 | Fixed | No ",:" in any riding's text. |
| (d)5 | Unchanged | Inside a quotation; acceptable. |
| (d)6 | Not fixed | WhatsApp: "here is my quick analysis". |
| (d)7 | Partly fixed | Slides 4 and 8 fixed; slide 1 still says "Charts CC BY 4.0" with no chart. |
| (d)8 | Fixed | Chapter 6 is "Before the vote". |

## (a) Errors still present

**E1. Website, riding card and By region tables: Boundary-Similkameen and Fraser-Nicola are labelled "Interior and North".**
By where their people live (2021 dissemination blocks, `geo/out/db_to_ed2023.csv` joined to StatCan's census-division names), 72.3% of Boundary-Similkameen's people are in the Okanagan-Similkameen Regional District (Osoyoos, Oliver, Princeton) and 54.8% of Fraser-Nicola's are in the Fraser Valley Regional District (Hope, Kent, Harrison Hot Springs). The labels come from the regional district holding each riding's representative point (`analysis/geo/scripts/04_build_districts.py` line 64), although `analysis/core/full.py` line 29 calls the rule "by population share" and METHODOLOGY says "Regions follow regional districts". Correct: Okanagan and Fraser Valley. The By region tables then read: Fraser Valley 6 ridings, Conservative 56.4% → 60.0%, NDP 39.7% → 33.1%, Green 2.3% → 1.9%, Conservative 6 seats both years; Interior and North 17 ridings, Conservative 53.4% → 57.5%, NDP 32.6% → 29.7%, Green 6.9% → 7.9%, 14 Conservative and 3 NDP both years; Okanagan 7 ridings, Conservative 47.1% → 52.2%, NDP 37.7% → 36.8%, Green 3.5% → 6.0%, Conservative 6 → 7, NDP 1 → 0. No slide claim changes.

**E2. METHODOLOGY.md line 15: "In the five ridings where the main race was between the NDP and the Greens".**
In Saanich North and the Islands (Green 48.5%, Conservative 31.7%, NDP 17.5%) and West Vancouver-Sea to Sky (Green 47.6%, Conservative 38.4%, NDP 10.3%) the top two were the Greens and the Conservatives. The site's rule (`site.js` line 47) is "the Greens finished in the top two in 2026 or held the seat in 2024". Fix: "In the five ridings where the Greens finished in the top two or held the seat".

**E3. METHODOLOGY.md N23 (line 51): "Kelowna-Mission, Liberal by 0.02".**
The allocation gives 17,125 Liberal against 17,120 Conservative votes, 48.195% against 48.181%: 0.01 point (`federal25/fed2025_on_ed2023.csv`, margin_pts 0.01; 0.02 comes from subtracting the rounded shares). Fix: "Liberal by 0.01".

**E4. METHODOLOGY.md N31 (line 59): "CON 48% of votes, 69% of seats; NDP 37% of votes, 29% of seats; GRN 11% of votes, 2% of seats", Where "Site".**
The site shows 48.1% of the vote and 64 of 93 seats (68.8%) for the Conservatives and gives no seat share for the NDP or the Greens. Fix: "Conservative 48.1% of votes, 64 of 93 seats (68.8%)".

**E5. Website, Langley-Abbotsford: "the Conservative share there went from 55.7% in 2024" (middle-ground sentence) and "Conservative 55.7%" (2024 riding note).**
Correct: 55.6% (14,341 of 25,770 valid votes = 55.6499%; the riding's own 2024 candidate row shows 55.6). Cause: `site/build_data.py` line 73 stores shares at four decimals (55.65), then `f1` rounds half up a second time. No other stored 2024 or 2026 share has this problem.

**E6. Website, How they got here, 2020 riding note ("the 2020 votes moved onto this riding"): 9 values in 7 ridings are 0.1 off.**
Shares are rounded three times (two decimals in `transposed_2020_on_2023_eds.csv`, one decimal in `build_data.py` line 79, then `f1`). Shown → correct, from the vote counts in the same file: Abbotsford West BC Liberal 45.0 → 44.9; Burnaby North BC Liberal 31.4 → 31.5; Chilliwack-Cultus Lake BC Liberal 29.6 → 29.5; North Island BC Liberal 24.1 → 24.0, Conservative 6.0 → 5.9, NDP 50.8 → 50.7; Oak Bay-Gordon Head BC Liberal 22.9 → 22.8; Penticton-Summerland BC Liberal 47.4 → 47.3; Vancouver-Kensington BC Liberal 27.8 → 27.7. Fix: compute from votes and round once.

**E7. Website, The result, personal sentence "changes hands at a shift of X points": no single rounding rule.**
The value is the first step of a 0.02-point scan (`site.js` line 807), then rounded. For 12 ridings it reads 0.1 above the exact threshold rounded: Cowichan Valley 0.4 (0.34), Burnaby North 2.5 (2.45), Maple Ridge-Pitt Meadows 2.1 (2.04), Nanaimo-Lantzville 2.0 (1.94), Kootenay-Monashee 6.3 (6.25), Vernon-Lumby 7.4 (7.35), Skeena 7.9 (7.84), Langley-Willowbrook 9.4 (9.35), Kamloops Centre 13.6 (13.55), Surrey-Serpentine River 14.1 (14.04), Abbotsford South 18.0 (17.94), Kamloops-North Thompson 19.4 (19.35). For 28 others it rounds down to a slider stop where the seat has not yet changed (for example Kelowna Centre 0.3 for 0.31, Abbotsford West 18.2 for 18.22). Fix: solve the threshold exactly and use one rule (rounded, or the first 0.1 slider stop past it, worded "just past"). The majority marks are right: 5.6 (exact 5.575) and 6.5 (6.477).

**E8. Website, Every election since 1928, 1928 card: "Conservative 53.3% · Liberal 40.3% · Other 6.1%" adds to 99.7%.**
Setting the Conservative share to the party's own 53.30% (`build_data.py` line 102) drops the Independent Conservatives' 0.29% (1,064 votes) instead of moving it to Other. Correct Other: 6.4% (6.08 + 0.29; Electoral History 1871 to 1986, 1928 summary). The stacked band for 1928 is 0.3 point short for the same reason.

## (b) Overstatements, with fixes that fit the same space

**O1. Website, The result, Victoria-Beacon Hill and Victoria-Swan Lake: "changes hands at a shift of 9.0 points toward the Conservatives" (13.0 for Swan Lake).**
At that shift the seat goes to the Greens: the slider moves NDP votes to the Conservatives, and the Greens pass the NDP. Fix: "goes Green at a shift of 9.0 points toward the Conservatives".

**O2. Website methods (`site.js` line 971): "a table of every published number"; METHODOLOGY's heading "Every published number".**
The table covers every slide number but not about 15 website figures: swingometer 5.6 and 6.5, 17 closest ridings, Gallagher 17.1 and 7.0, effective parties 2.6 and 1.8, volatility 10.6, 62.5% / 23.6% / 87.3%, 35 of 62, correlation 0.82, the four place-type averages, 16 of 23 renter ridings and r = −0.05, the income and education cells, the Goodman estimates, final-poll averages 43.8% and 38.9%, Ipsos 53% and 31%, 42.7% against 49.5%, and $1.425 billion, $11.1 billion and $10.8 billion. Fix: add the rows, or "a table of every slide's numbers".

**O3. Website methods (`site.js` line 966) and METHODOLOGY line 17: "Totals match Elections Canada's B.C. totals."**
The allocated totals differ by 1 to 5 votes a party: Liberal 1,105,031 against 1,105,033, Conservative 1,088,656 against 1,088,655, NDP 343,665 against 343,670, Green 79,257 against 79,255 (Elections Canada Table 8). Fix: "Totals match Elections Canada's within 5 votes."

**O4. Website, What comes next, More about this, and METHODOLOGY line 9: "the kinds of ballots left to the 2026 final count (vote-by-mail, assisted telephone and absentee ballots on Final Voting Day)".**
Elections BC's list also has absentee ballots cast at special voting opportunities, which the 2024 data cannot separate. Fix: "three of the four kinds of ballots left to the 2026 final count".

**O5. Slide 6 subtitle (low; B3 residual): "the 42 ridings where the Liberals came first in the April 28, 2025 federal election".**
Kelowna-Mission is in the group by 5 allocated votes, and if Coquitlam-Maillardville (0.34 point) or Juan de Fuca-Malahat (0.49) were Liberal the lead would be 16 or 17 of 20. Fix, if it fits the two lines: "...where the Liberals came first (estimated) in the April 28, 2025 federal election".

## (c) Visual or interaction defects

1. **Which ridings changed party:** in the "Conservative federally" block, the "6 switched" and "Courtenay-Comox" band labels print on top of each other at 390 and 1280 px whenever that group is selected (its chip, or any of its ridings chosen, such as Cowichan Valley). A chosen riding from that group also puts its name on both. Bounding-box test: about 40 of the group's 44 ridings at either width.
2. **Same chart:** the chosen riding's name lands on its group's subtitle line for ridings near the top of a band: "Provincial swing +8.9 points" at 390 px (16 ridings, including Victoria-Beacon Hill, Victoria-Swan Lake, Vancouver-West End, Burnaby East), "Provincial swing +4.9 points" (Kootenay Central, Kootenay-Monashee, Langford-Highlands, the two Nanaimo ridings) and the NDP-group line at both widths (Mid Island-Pacific Rim, North Coast-Haida Gwaii, Vancouver-Hastings, Vancouver-Renfrew, Vancouver-Strathcona). Cause: `site.js` line 669 places the name above the dot without testing the subtitle.
3. **How they got here, 2001 to 2026 view, 390 px:** the chosen riding's name runs into the "BC Liberal" label for 33 of 93 ridings (plainly for Cowichan Valley). Cause: `site.js` line 245 anchors the name at 2020 and runs it left. Not seen at 1280 px.
4. **Slide 4 map:** the note says "Metro Vancouver ridings, 2026", but five ridings outside Metro Vancouver are filled in party colours: Abbotsford-Mission, Abbotsford South, Abbotsford West and Fraser-Nicola ("Conservative both years") and West Vancouver-Sea to Sky, the only "Green both years" area on the map, which the project files under "Rest of Vancouver Island and Coast". Fix: fill non-Metro ridings with the plain land colour and drop "Green both years" from the key, or say "Metro Vancouver and nearby ridings".
5. **Every riding by type of place (low):** at 390 px the dashed zero line runs through the row captions ("1 changed", "12 changed").

Checked and working: finder by riding name, city (Kelowna lists 3 ridings at 41.0%, 40.8%, 18.2%, matching the block populations; Surrey, Victoria, Nanaimo and Saanich also match), nonsense string and Enter; taps on dots in the income, place-type, scatter and seat charts set the riding and the URL hash; both sliders across their range (5.6 gives Conservative 46, NDP 45; −10 gives Conservative 83, NDP 7, Green 3; closest margins at 100, 150, 400 and 1,500 list 2, 4, 8 and 26 ridings with no duplicate); all layer chips, zooms, years, worries, promises, region and income-education buttons; dark mode.

## (d) Style breaks

1. **Numbers repeated across slides:** 44 (slide 2 "44 seats", slide 7 "Named by 44%"), 28 (slide 4 "28 of 34", slide 7 "Named by 28%"), and 47 twice on slide 2 ("NDP 47 seats" in the 2024 chart and "Majority: 47 seats").
2. **Federal without provincial, slide 6 and the site's chapter head:** "Federal Liberal areas swung Conservative" and "Three of every four seats the Conservatives added were in these ridings."; "provincial" appears only in the chart note. Fix: "Three of every four provincial seats the Conservatives added were in these ridings."
3. **Date not in full:** METHODOLOGY line 7, "a snap election called on September 22". Fix: "September 22, 2026".
4. **Close to "won":** METHODOLOGY calls the 2026 leader the "2026 winner" (N14 to N17) and "2026 winners" (N24). Fix: "the party elected in 2026".
5. **WhatsApp message:** "here is my quick analysis" (unchanged from final check 3). Fix: "here it is in numbers:".
6. **Source line:** slide 1 says "Charts CC BY 4.0" with no chart (slide 7 shows a list, not a chart).

Outside the brief's list, for the editor: the slide credits read "Photo: name, licence", while the account's pre-send checklist asks for "© " plus the credit line (the CC0 photo on slide 7 cannot take ©); the site's licence note spells "licenced" and "licensed" in one sentence; METHODOLOGY N30 says "summarised" where the site says "summarize".

Clean everywhere checked (slides, all site text including the 93 riding sentences, tooltips, promise and worry details, post text, METHODOLOGY): no em dashes; no "now", "today", "currently"; no "won", "lost", "carried", "beat"; no "lead", "leads", "leading" or "ahead by" for results ("led by David Gordon" and "ahead of health care" are not results); no "initial count"; "X, not Y" only inside the platform quotation; no "in Ottawa" or "in Victoria" (only the riding names); no contractions in the post text; nothing on the slides outside x 180 to 900. No tracking or follow-up wording and no forecast of what voters will do; the only forward-looking lines are "the closest Conservative margins are the most likely to change" (ballots already cast) and "Lorne Doerkson ... is expected to become premier" (supported by Eby's post congratulating him "on becoming B.C.'s next premier").

## (e) Verified as correct

Slides:
- 2026: Conservative 64, NDP 27, Green 2 seats; 48.05%, 37.38%, 10.97% of 1,792,235 valid votes (rejected-ballot rows excluded); margin 10.7. 2024: NDP 47, Conservative 44, Green 2; 44.87% and 43.28%; gap 1.6. 7,237 of 7,268 ballot boxes.
- Slide 2: 2024 hemicycle 47/2/44; 2026 hemicycle 27/2/64 with 21 ringed Conservative seats and 1 ringed NDP seat; 22 ridings changed, matching the raw files exactly; majority 47, 17 to spare.
- Slide 1: first majority since 1928 (Conservative Party 35 of 48 seats, 192,867 votes, 53.30%; no Conservative majority in the 26 elections from 1933 to 2024; the 1945 and 1949 majorities were the Coalition's); nine years from July 18, 2017.
- Slide 3: 2% in 2020 (1.91%); every point 2001 to 2026 matches the raw files to 0.01, including 2001 Conservative 0.15%.
- Slide 4: 28 of 34 suburban ridings (15 in 2024); Surrey 10 of 10 (6); 16 changed in Metro Vancouver; Cowichan Valley, Juan de Fuca-Malahat, Ladysmith-Oceanside, Saanich South and Vernon-Lumby to the Conservatives elsewhere, Courtenay-Comox to the NDP.
- Slide 5: groups of 23 (Peace River North out), +3.7, +5.7, +5.9, +11.0; $72k, $82k, $92k, $104k; all 92 dots sit at each riding's swing within 0.01; r = 0.57.
- Slide 6: 42 ridings (exact margins: Kelowna-Mission 0.014, Penticton-Summerland 0.136, Bulkley Valley-Stikine 0.271, Coquitlam-Maillardville 0.337, Juan de Fuca-Malahat 0.494, next 1.10); NDP 49.9 → 39.3, Conservative 39.1 → 44.7, Green 8.7 → 12.5; seats 10 → 25, 15 of the net 20.
- Slide 7: Angus Reid QBC1 58%, 44%, 28%; IRG cost of living Conservative 33, NDP 26; health care NDP 30, Conservative 28; housing Conservative 28, NDP 27; n = 1,000 weighted (1,153 unweighted); margins of error 4.7, 4.7, 4.6.
- Slide 8: platform pages 5 and 59 ($1,000, $13,216 to $32,000, 2027 tax year), 32 (Universal Health-Care Guarantee), 6 ("Approve homes in months, not years").

Website:
- All 93 ridings' personal sentences, cards and notes match the raw files (margins, 2024 margins, swings, rank phrases, place types, income groups, the five "about even" federal sentences, 2024 and 2026 shares, Green-race changes, closer counts, candidates and parties, ballot boxes), apart from E5 to E7.
- Swingometer 5.6 and 6.5; tipping point 18 seats, 7,509 voters, 0.42%, Coquitlam-Maillardville; 62.5%, 23.6%, 87.3%; Gallagher 17.1 and 7.0, effective parties 2.6 and 1.8, volatility 10.6.
- 29 of 29 and 35 of 62 notional ridings; r = 0.82; West Vancouver-Sea to Sky 2020 (37.54% against 37.30% on the old map, Green 38.17% against 36.13% on the new).
- Place types and averages; region tables (with the project's labels); profile cards 67.9/78.8/49.2, 56.2/68.7/34.1, 73.8/87.1/28.5, $92k/$81k/$91k; 16 of 23 renter ridings; income and education cells +5.9 (22), +10.4 (26), +3.3 (24), +6.3 (20); the two strongest census links are income measures ($200k+ r = 0.62, median income 0.57).
- Federal groups: 42/44/7; swings 8.9, 4.9, 0.7 (6), Saanich North 16.4; seat flows; "rose 5.6 ... fell 10.6 ... rose 4.6 ... fell 4.2"; Goodman 80 → 55, 13 → 18, 8 → 13; r = −0.60.
- Final polls: last campaign poll of 10 pollsters, all with the Conservatives first, averaging 43.8% and 38.9%; Ipsos 53% and 31%; late-ballot 42.7% against 49.5%.
- Platform $1.425 billion, $11.1 billion, $10.8 billion; Draft 18 posted October 19, 2026; no-tax release September 27, 2026; board statement September 23, 2026; final count November 6 to 10, 2026; Return Day November 18, 2026; election called September 22, 2026.
- Year cards for all 28 elections; closest margins 66, 89, 132, 150, 241, 386, 387, 395.
- METHODOLOGY slide numbers, chapter titles, place-type order and region names match the slides and site, apart from E2 to E4.

## What I could not check

- **Federal allocation and 2020 transposition:** not re-run (long geospatial jobs). I checked totals against Elections Canada Table 8 and the 2020 file, and recomputed every group statistic from the allocation and transposition outputs.
- **Census measures other than income, tenure, commuting, visible minorities and density:** taken from the project's profile file (`census/out/ed2023_profile.csv`) for the correlation checks, not re-derived from the BC Stats raw files.
- **Photo licences:** matched to the project's photo metadata only; Wikimedia Commons was not checked online.
- **Canadian Suburbs methods page:** no local copy, so the stated thresholds were not re-read.
- **Repository and push (A17), and the hub site:** outside this check.
- **"Fixed before polls closed"** for the final-poll set: no timestamp to check against.
- **Files rebuilt after 15:48 EDT.**
