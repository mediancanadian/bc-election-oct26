# Final check 3: B.C. election carousel, website and post text

Checked October 25, 2026, against Elections BC's results files as posted October 25, 2026, 1:49 a.m. Pacific (snapshot `analysis/live/raw/snapshots/20261025T150040Z/`), the 2024 open data and Statement of Votes, the 2001 to 2020 Elections BC files, the BC Stats 2021 census profile by riding, the federal 2025 allocation, the pollster PDFs and the Conservative platform PDF (Draft 18). Every slide number was recomputed from the raw files, not from `story.json`. The website was run in Playwright at 390 px and 1280 px, light and dark, with every "More about this" block open, 16 ridings chosen, the finder, map, chips, both sliders, worries and promise cards exercised.

## Scorecard

| Area | Errors | Overstatements | Visual or interaction | Style |
|---|---|---|---|---|
| Slides | 1 (minor) | 3 | 0 | 3 |
| Website | 11 | 9 | 4 | 4 |
| METHODOLOGY.md | 5 | 1 | n/a | 1 |
| Post text | 0 | 1 | n/a | 2 |

Every headline number on the 8 slides is correct. Nothing on the slides sits outside x 180 to 900, nothing is clipped, and each source line fits. The website has no console errors and no horizontal overflow in any of the four modes. The fixes that matter most before publishing: A1 to A6 on the website, A13 to A17 in METHODOLOGY.md (including pushing the repository the page links to), and B2 and B3 on slides 5 and 6.

## (a) Errors

**A1. Website, "Compare your riding" cards, Stayed Conservative column: "29% visible minorities".**
Should be 28%. The pooled share is 28.48% (43 ridings, "Total visible minority population" over "Total - Visible minority for the population in private households", BC Stats `census_profile_2021_ped93_part2.csv`). `story.json` stores 28.5 (`who_pooled.stayed_con.vismin`) and `site.js` line 35 (`pct0`) rounds it again. The More about this text (28.5%) is correct. Fix: round whole percentages from unrounded values.

**A2. Website, middle ground riding chips ("Con. +X") and one Green-race sentence: 18 values off by 0.1.**
`site.js` line 527 subtracts shares already rounded to one decimal. Saanich South shows "Con. +6.9" (shown in the default list); the correct value is +6.8 (39.280 minus 32.450). The others:

| Riding | Shown | Correct |
|---|---|---|
| Port Coquitlam | +4.7 | +4.8 |
| Vancouver-Langara | +4.6 | +4.5 |
| Vancouver-South Granville | +4.5 | +4.6 |
| Victoria-Beacon Hill | −5.2 | −5.1 |
| Surrey-Guildford | +3.9 | +3.8 |
| Abbotsford West | +3.5 | +3.6 |
| Chilliwack-Cultus Lake | +5.5 | +5.6 |
| Kamloops-North Thompson | +5.3 | +5.2 |
| Langley-Abbotsford | +5.8 | +5.7 |
| Langley-Walnut Grove | +7.2 | +7.3 |
| Mid Island-Pacific Rim | +1.0 | +1.1 |
| Nechako Lakes | −3.5 | −3.6 |
| North Coast-Haida Gwaii | −6.3 | −6.2 |
| North Island | +0.9 | +1.0 |
| Peace River North | +11.3 | +11.4 |
| Peace River South | +7.9 | +7.8 |
| Richmond Centre | +5.6 | +5.7 |

Also Victoria-Swan Lake's where sentence says "Green up 12.0"; the correct value is 12.1. Fix: carry shares at two or more decimals into `site.json`.

**A3. Website, swing for 5 ridings off by 0.1.**
These are stored at two decimals and then rounded half up (panel, tooltips and personal sentences). Burnaby Centre shows +10.7 (true 10.645, so +10.6). Burnaby-New Westminster shows +7.7 (7.648, so +7.6). Juan de Fuca-Malahat shows +2.6 (2.548, so +2.5). Kamloops Centre shows +9.2 (9.146, so +9.1). Surrey North shows +9.9 (9.846, so +9.8). The fix is the same as A2.

**A4. Website, What comes next, More about this: "In the 2024 B.C. election, ballots counted at the final count gave the Conservatives 42.7% of the Conservative and NDP vote, against 49.5% in all other ballots."**
The 42.7% comes from all vote-by-mail, all assisted telephone and all Final Voting Day out-of-district ballots (`site/build_data.py` lines 103 to 108; 5.7% of the two-party vote). In 2024 only 3% of ballots were counted at the final count. Mail returned by October 15 and every ballot cast at a full-tech voting place, out-of-district ballots included, were counted at the initial count (Report of the CEO 2024, pages 54 and 57: "initial count included 97% of all ballots cast"). The 2024 open data has totals by voting opportunity, not by count. Suggested wording, same space: "In the 2024 B.C. election, the kinds of ballots left to the 2026 final count (vote-by-mail, assisted telephone and absentee ballots on Final Voting Day) gave the Conservatives 42.7%...". The `#watchnote` line ("those ballots leaned NDP") is already worded as ballot types and is fine.

**A5. Website, region labels.**
West Vancouver-Sea to Sky is labelled "Interior and North": the riding card shows "Interior and North · Exurban and rural", and the By region table counts its Green seat there ("Green 1 → 1" for Interior and North). Powell River-Sunshine Coast is labelled "Rest of Vancouver Island", but it is on the mainland coast. Evidence: `data/ridings.csv` region column. `analysis/core/full.py` lines 29 to 42 map qathet to "Rest of Vancouver Island", and Squamish-Lillooet falls through to "Interior and North". `geo/out/ed2023_regions.csv` puts 74% of West Vancouver-Sea to Sky's people in the Squamish-Lillooet Regional District. No slide claim changes, because none of the 22 switched ridings is affected. Fix: put West Vancouver-Sea to Sky in Metro Vancouver or a "Sea to Sky and Coast" group, and rename "Rest of Vancouver Island" to "Rest of Vancouver Island and Coast".

**A6. Website, place types: three very rural ridings are called "Active core".**
Columbia River-Revelstoke (1.1 people per km²), Kootenay Central (2.9) and North Coast-Haida Gwaii (0.4) are classed as active cores. The where sentence reads "North Coast-Haida Gwaii, an active core, swung...", and the say-where line calls the group "walkable centres". This happens because the walk-or-cycle test runs before the density test (`analysis/core/meta/meta.py`, `typ()`). The Canadian Suburbs project uses the same order, but only for census tracts inside metropolitan areas (canadiansuburbs.ca/methods). Fix: for whole ridings, apply the density test first. That gives Active core 13 ridings at +5.7 and Exurban and rural 34 at +3.9. "Suburbs swung about twice as much" stays true (8.8 against 4.4).

**A7. Website, where sentence for Victoria-Beacon Hill: "swung 5.3 points toward the NDP, one of six ridings that moved that way".**
The Greens are second there (NDP 45.7, Green 40.3), and the NDP share fell 1.7 points (47.4 to 45.7). By the page's own rule (`site.js` line 366), the sentence should say the Conservative and NDP swing "is not comparable here". The `tp < 0` branch on line 363 runs first. Fix: test the Green race before the negative swing. Excluding it, five ridings moved toward the NDP, not six.

**A8. Website, Who lives there, More about this: "Courtenay-Comox, which moved to the NDP, is left out."**
The two ridings that elected Greens both years are also left out (21 + 26 + 43 = 90 of 93). Fix: "Courtenay-Comox, which moved to the NDP, and the two ridings that elected Greens both years are left out."

**A9. Website, worry details: "Innovative Research Group, October 15 to 19, 2026, 1,000 people".**
The release surveyed 1,153 people, weighted to 1,000 (IRG release, page 27: "n=1153 ... weighted to n=1000"). Fix: "a weighted sample of 1,000".

**A10. Website, riding card lists independents as "(Other)".**
For example, "Jordan Kealy (Other)" in Peace River North, where Elections BC's file says Independent. The same happens for Ed Ewald in Bulkley Valley-Stikine and Helen Scott in Peace River South. Fix: keep IND or UNAF in `c26`; the `PN` map already has both names.

**A11. Website, promise card "Up to $150 million a year for family benefits and child care": "Platform page 7, 61".**
The phasing quoted ("$15 million in 2027/28 to the full amount from 2030/31") is in Table B1 on page 64. Fix: "Platform pages 7, 61, 64".

**A12. Slide 3 chart and the website's 2001 to 2026 chart: 2001 Conservative plotted at 0.0%.**
Elections BC's 2001 results by district give the BC Conservative Party (CP) 2,417 votes, which is 0.15% (`history/raw/ge2001_xls/2001ResultsxED.xls`; `history/results.md`: "2001: the BC Conservative (CP) vote ... sits inside 'Other'"). The difference cannot be seen at chart scale, and METHODOLOGY N7 rounds it to 0% anyway. Fix `story.json` (line 33) so the data file is right.

**A13. METHODOLOGY.md N12 (line 40), Where column: "Slide 4 ("about twice as much"), site".**
Slide 4 has no such statement; it appears only on the website. Fix: "Site".

**A14. METHODOLOGY.md N19 (line 47): "NDP or Green federally 2.9".**
The website shows "+0.7 points in the 6 ridings that voted NDP federally" and gives Saanich North and the Islands (+16.4) separately, so 2.9 appears nowhere on the site. Fix: "NDP federally (6 ridings) 0.7; Saanich North and the Islands, Green federally, 16.4".

**A15. METHODOLOGY.md line 18: "The Angus Reid Institute surveyed B.C. adults, so the slides say British Columbians."**
No slide says "British Columbians"; only the website does. Fix: "so the website says British Columbians."

**A16. METHODOLOGY.md line 16 says owners are counted over "private households".**
The computation (`story.py`, `pooled()`) and N13 use owner plus renter households, with band housing left out. Shown values do not change (67.9 against 67.8). Fix the wording in line 16.

**A17. METHODOLOGY.md source paths and the repository.**
The Source file column (lines 29 to 47) cites `analysis/history/province_series.csv`, `analysis/results24/out/...`, `analysis/federal25/...` and `analysis/meta/place_types.csv`. None exists in the project folder, whose `analysis/` holds only `story.py` and `build_map_detail.py`, and `story.py` reads absolute `analysis/` paths. The local repository has only the Initial commit (LICENSE); every other file is untracked. The page says "The full methodology, every script and a table of every published number are in the project's repository", and source [11] says "each release linked in the repository". Before publishing: copy the inputs to the cited paths, then commit and push.

## (b) Overstatements, with fixes that fit the same space

**B1. Slide 3 lead: "The vote that went BC Liberal for 20 years moved to them."**
This states a flow of voters that riding totals cannot show; the data show replacement (the BC Liberals last ran in 2020, the riding-level correlation is 0.82, and all 29 notional BC Liberal ridings elected Conservatives). "20 years" also fits neither 1991 to 2020 nor the 2001 to 2017 government. Suggested (51 characters, fewer than now): "They replaced the BC Liberals, who last ran in 2020." The post text's "where the BC Liberal vote went" (short description) has the same issue: "how they replaced the BC Liberals".

**B2. Slide 5 headline and lead have no comparison group.**
Switched ridings have more homeowners and car commuters than ridings that stayed NDP. Against B.C. as a whole they are at the average for owners (67.9% against 67.1%) and slightly below it for car commuting (78.8% against 79.9%). Ridings that stayed Conservative have more of both (73.8%, 87.1%). Across all ridings, ownership (r = 0.10) and car commuting (r = −0.04) do not track the swing; income does (r = 0.57). Suggested lead: "Against ridings that stayed NDP, they also have more visible minorities, car commuters and higher incomes." This adds one lead line, and the card has 94 px to spare above the logo (content ends at y 1134, logo at 1228).

**B3. Slide 6 note and website: the federal winner of each provincial riding is an estimate stated as fact.**
Kelowna-Mission is Liberal by 0.01 point. Coquitlam-Maillardville (Conservative by 0.34) and Juan de Fuca-Malahat (Conservative by 0.49) both switched, so "15 of their 20 extra provincial seats" would be 16 or 17 if either were Liberal (`federal25/results.md`: "At these margins the method cannot reliably say who led"). Without Kelowna-Mission, the 41-riding figures are NDP 50.4 to 39.6 and Conservative 38.8 to 44.3, so the picture holds. Suggested note, which fits on its second line: "...in the April 28, 2025 federal election (estimated)". On the website, the personal sentences ("Kelowna-Mission gave the Liberals the most votes ... (48.2%)") should say "about even (estimated)" when the margin is under 0.5 point: Kelowna-Mission, Penticton-Summerland, Bulkley Valley-Stikine, Coquitlam-Maillardville and Juan de Fuca-Malahat.

**B4. Website, swing in Green races.**
For West Vancouver-Sea to Sky, Saanich North and the Islands, Vancouver-Strathcona, Victoria-Swan Lake and Victoria-Beacon Hill, the where sentence says the swing "is not comparable here". The riding card ("+21.3 to Con."), the who sentence ("Swing: 21.3 points toward the Conservatives, bigger than in 9 in 10 ridings"), the dot chart, the scatter, the quartile table and the place-type averages all use it anyway. Leaving the five out moves Active core from +5.2 to +6.2 and Exurban and rural from +4.0 to +3.0; "about twice as much" still holds (8.8 against 4.0). Fix: leave them out of the swing measures, or drop the "not comparable" sentence.

**B5. Website, Who lives there note: "links to immigration, visible minority share and education mostly fade once income, age, renting and Metro Vancouver are held equal."**
With those controls (92 ridings, effect per standard deviation), immigration goes from 2.2 to 1.6 points (t 2.2), visible minorities from 2.0 to 1.3 (t 1.9) and degrees from 2.1 to 1.0 (t 1.5). The project's own model keeps South Asian share at t 2.3 (`analysis/out/full_log.txt`, lines 343 to 350). Suggested: "links to immigration and visible minority share weaken by about a third, and to education by half, once income, age, renting and Metro Vancouver are held equal."

**B6. Website: "The party's board says he will remain leader and that the party's rules will be amended."**
The board said it "will pursue the appropriate means under the Party's Constitution" (X post, September 23, 2026). An amendment needs a two-thirds vote of members at a general meeting (constitution 10.03). Suggested: "...and that it will seek to amend the party's rules."

**B7. Website, What comes next: heading "The three promises we will track" sits above eight "Promised" cards.**
Fix: tag the three cards shown on slide 8 ("Tracked"), or add a line such as "Slide 8's three are marked; the other five are on the record."

**B8. Website, Who lives there: "Ridings that stayed Conservative have the most homeowners and car commuters of all: 74% and 87%."**
The two Green-held ridings have 76.7% owners, and Courtenay-Comox has 76.6%. Fix: "...of the three groups: 74% and 87%."

**B9. Website meta description and METHODOLOGY.md line 7: "the promises voters will hold the new government to".**
This is a claim about voters that no data supports. Fix: "the promises we will track".

**B10. Website (low): "top worry" and "top three worries".**
Angus Reid's question (QBC1) is "the most important to you when it comes to deciding which party and candidate to support". "Top issues" would match it; the current paraphrase is acceptable.

**B11. Website (low), middle ground subtitle: "Share of all votes cast in the 42 ridings".**
The shares are of valid votes, which the More about this text already says. Fix: "Share of all valid votes in the 42 ridings".

## (c) Visual or interaction defects

1. **Closest margins:** your riding is listed twice when its margin equals the slider value. Cowichan Valley at 150 appears in the list and again under "Your riding" ("3 ridings are closer"). `site.js` line 892 uses `>=`; it should be `>`.
2. **At 390 px:** the swingometer's end labels "← Toward the Conservatives" and "Toward the NDP →" run together on one line with no gap (screenshot checked at slider 5.6).
3. **Same riding, two rank phrasings.** Vancouver-Yaletown's where chapter says "a smaller swing than in 5 in 10 ridings", and its who chapter says "close to the middle of all ridings". Kelowna-Mission has the same split. Use one rule (`rankIn`) in both.
4. **Region naming differs:** the region chips say "Victoria area (Capital Region)", while the riding card says "Capital Region (Victoria)".

Checked and working: finder by riding name, code ("srg"), city ("Surrey" lists 10 ridings by share; Kelowna 3; Victoria 4), a nonsense string (shows the no-match message) and Enter. Also working: map tap (sets the riding and the URL hash), the four zoom views, the five layer chips and More measures, all three group chips, the bands, the worries, all 8 promise cards and the filter, both poll ranges, and the 28 year buttons. Both sliders work across their full range. No console errors or warnings in any mode, and no horizontal overflow at 390 or 1280 px, light or dark, with details open and with a riding chosen. Dark mode applies.

## (d) Style breaks

1. **Number repeated across slides:** 44 (slide 2, "44" Conservative seats; slide 7, "Named by 44%") and 20 (slide 3, "20 years"; slide 6, "20 extra provincial seats"). B1's fix removes the second.
2. **Federal without provincial.** The slide 6 headline "Federal Liberal ridings shifted Conservative" is paired only in the lead; possible fix: "The provincial Conservatives gained 15 of their 20 extra seats in these ridings." The post text's short description ("the suburbs and federal Liberal ridings that switched") has no "provincial"; fix: "...that switched provincially".
3. **Dates not in full** on the website year cards. The 2017 card says "BC Liberal to 18 Jul 2017, then NDP; premier Christy Clark to 18 Jul 2017; John Horgan from 18 Jul 2017", and the 1941 card says "Pattullo to 9 Dec 1941; John Hart from 9 Dec 1941" (`site.json` history; `site.js` line 174). Also minor: the campaign-view poll ticks ("September 22", "October 8", "October 24") have no year.
4. **Stray punctuation ",:"** in the where sentences for West Vancouver-Sea to Sky, Saanich North and the Islands, Vancouver-Strathcona and Victoria-Swan Lake: "an exurban and rural riding,: Conservative up 2.8". `site.js` line 361 ends the opening with a comma, and line 367 appends a colon.
5. **"X, not Y"** appears only inside a platform quotation ("Approve homes in months, not years", two promise details). Acceptable as a quote; flagged for the editor.
6. **WhatsApp message:** "here is my quick analysis" is close to the banned "our analysis". Suggested: "here it is in numbers:".
7. **Source lines (minor):** slide 4 cites "2021 Census" but uses no census data, slide 8 cites "Elections BC" but uses none, and slide 1 says "Charts CC BY 4.0" with no chart on it.
8. **METHODOLOGY.md** titles chapter 6 "Why it changed"; the slide and the site use "Before the vote", which avoids the causal claim.

Clean: no em dashes, and no "now", "today", "currently", "won", "lost", "carried", "beat", "lead(s)", "leading", "ahead by", "initial count", "in Ottawa" or "in Victoria" in the slides, the visible website text (including every personal sentence for the 16 ridings tested, tooltips, promise and worry details), the post text or METHODOLOGY.md. The post text has no contractions.

## (e) Claims verified as correct

Slides:
- 2026 seats: Conservative 64, NDP 27, Green 2, from the candidate with the most votes in each of the 93 districts in Elections BC's candidate file; this matches the party file's Electoral Districts Leading.
- 2026 shares: Conservative 48.05% (861,258), NDP 37.38% (669,901), Green 10.97% (196,593) of 1,792,235 valid votes; the margin is 10.67, shown as 10.7.
- 2024 seats: NDP 47, Conservative 44, Green 2; shares 44.87% and 43.28% (SOV 2024 summary; raw voting-place file). Gap: 1.59 points (shown 1.6) and 3 seats.
- Slide 2 hemicycles: dot counts are 47/2/44 (2024) and 27/2/64 (2026); the dotted line sits on seat 47 of 93.
- Ballot boxes: 7,237 of 7,268; time 25/10/2026 01:49:02 AM, shown as "1:49 a.m. Pacific".
- Nine years: Horgan became premier on July 18, 2017 (Hansard index, `province_series.csv`).
- Final count November 6 to 10, 2026 (planned) and Return Day November 18, 2026 (Elections BC 2026 election page).
- Conservatives 1.91% in 2020 (SOV 2020), shown as 2%.
- Slide 3 line chart: BC Liberal, Conservative and NDP points for 2005 to 2026 match the Elections BC files to 0.01 (2001 Conservative is A12).
- All 10 Surrey ridings Conservative in 2026; 6 in 2024 (Surrey-Cloverdale, Surrey North, Surrey-Panorama, Surrey-Serpentine River, Surrey South, Surrey-White Rock).
- Slide 4 map: all 51 polygons checked. The 16 bright ridings are exactly the 16 Metro ridings that changed from NDP to Conservative, the muted fills match "both years", the key matches the fills, and the city labels sit on their cities.
- "Outside Metro Vancouver, five more ... and Courtenay-Comox to the NDP": Cowichan Valley, Juan de Fuca-Malahat, Ladysmith-Oceanside, Saanich South and Vernon-Lumby.
- Slide 5, recomputed from the raw BC Stats file: owners 67.9 against 56.2 (68%, 56%); visible minorities 49.2 against 34.1 (49%, 34%); car 78.8 against 68.7 (79%, 69%); median of riding medians $92,000 against $81,000. An approximate household-pooled median from income bands gives $91k against $81k.
- Slide 6: 42 ridings; NDP 49.90 to 39.26; Conservative 39.12 to 44.72; Green 8.73 to 12.53; Conservative seats 10 to 25 (+15) of a net +20 (21 gained, Courtenay-Comox lost).
- Slide 7, Angus Reid (QBC1, October 15 to 19, 2026, 793 B.C. adults): 58%, 44%, 28%. Up to three answers is supported by the October 5 release note on the same question and by answers summing to 291%.
- Slide 7, Innovative Research (October 15 to 19, 2026, weighted 1,000): Conservative 33 against NDP 26, NDP 30 against Conservative 28, Conservative 28 against NDP 27. The calls are right: a gap of 7 against a 4.7 margin of error; gaps of 2 and 1 against 4.7 and 4.6. IRG itself calls health and housing a tie.
- Slide 8: "$1,000 a year in income-tax relief per person" (page 5), the Universal Health-Care Guarantee (page 32), "Approve homes in months, not years" (page 6).
- Slide 5 footnote and slide 2 note are accurate. All slide elements stay within x 180 to 900, no element is clipped, and the source lines fit.

Website:
- Swingometer: the majority ends at a 5.58-point shift (shown 5.6) and an NDP majority starts at 6.48 (6.5). Readouts at 1, 5.5, 5.6, 6.4, 6.5, 10, −5 and −10 are consistent, and "One point on the slider is one point of swing" is true.
- Tipping point: 18 seats, 7,509 voters, 0.42% of votes, Coquitlam-Maillardville at 1,569 votes; 17 could change hands with the majority kept.
- Share of each party's votes cast where it did not finish first: NDP 62.5%, Conservative 23.6%, Green 87.3%.
- "Rose 4.8, fell 7.5, 20 seats moved, net": correct.
- Gallagher index 17.1 (2026) and 7.0 (2024); volatility 10.6; effective number of parties 2.6 (votes) and 1.8 (seats).
- Notional 2020 results: 29 of 29 BC Liberal and 35 of 62 NDP ridings elected Conservatives; correlation 0.82; transposed totals equal the 2020 official totals.
- Best since 1928 (53.30%, Conservative Party line in the 1871 to 1986 volume); coalition 1941 to 1952.
- Place types: averages +5.2, +8.7, +9.0 and +4.0; suburbs 8.8 against 4.4; 14 of 22 changed ridings are suburbs.
- Metro Vancouver outside the City of Vancouver: Conservatives in 28 of 34 ridings, up from 15. Metro areas list: Surrey (4), Vancouver (3) and the rest correct.
- Six regional share and seat tables match the raw files (labels aside, A5).
- Income and swing: r = 0.57 across 92 ridings; quartile table $72k +3.7, $82k +5.7, $92k +5.9, $104k +11.0; income and education cells +5.9, +10.4, +3.3, +6.3 with counts; renters r = −0.05, and 16 of the 23 most-renter ridings elected NDP MLAs; income measures are the top correlates.
- Federal groups: swings +8.9, +4.9 and +0.7 (6 NDP ridings); Conservative group shares 49.0 to 53.6, 39.0 to 34.8, 6.7 to 7.7; NDP or Green group shares 51.9 to 43.1, 31.0 to 31.3, 16.1 to 23.7; seat sentences correct.
- Goodman estimates recomputed: federal Liberal voters' NDP share 80 to 55, Conservative 13 to 18, Green 8 to 13; the other rows match. Federal Liberal share against NDP change: r = −0.60.
- Final polls: the last campaign poll from each of the 10 pollsters with campaign polls; averages 43.8 and 38.9 match `polls.csv`; the "understated share and margin" sentence is correct.
- Ipsos, October 20 to 22, 2026: 53% time for a change, 31% deserves re-election.
- Platform: $1.425 billion (pages 60 and 63); $11.1 billion of tax relief and a $10.8 billion deficit in 2029/30 (page 68); posted October 19, 2026 (WordPress media date); $2.9 billion and $13,216 to $32,000 from the 2027 tax year (pages 59 to 60); $50 million Rural Health Emergency Fund and the 100-day review (page 32); no housing number anywhere in the text.
- No-tax pledge on the plan page; release dated September 27, 2026 (WordPress JSON). Board statement posted on X on September 23, 2026.
- Closest margins: 66, 89, 132, 150, 241, 386, 387, 395; 4 ridings within 150; 26 within 1,500; 2 within 100.
- Citation numbering matches the source list. Source URLs match the thread manifests. The Gallagher and effective-number pages resolve. Kitschelt and Rehm (2023) is Politics and Society 51(4): 520 to 566 (IDEAS listing). The Canadian Suburbs methods page matches the stated thresholds.

## What I could not check, and why

- **Federal 2025 allocation:** the poll-by-poll allocation to provincial ridings was not re-run, because it is a long geospatial job. I checked that party totals equal Elections Canada's and recomputed every group statistic from the allocation file.
- **2020 transposition:** the move onto the 2023 ridings by voting-area overlay was not re-run. I checked that totals are preserved and recomputed the 29/29, 35/62 and 0.82 figures from it.
- **Place index:** the 446-place finder index was spot-checked for 18 places (all plausible), not rebuilt from dissemination blocks.
- **Photo credits and licences:** commons.wikimedia.org is not reachable from this session; credits match the project's own photo metadata only.
- **Repository and DOI:** github.com and doi.org are not reachable. Locally the repository has only LICENSE committed (A17).
- **Final-poll timing:** "Fixed before polls closed" for the final-poll set has no timestamp to check against.
