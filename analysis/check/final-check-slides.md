# Final check: B.C. election carousel (8 slides) and post text

Independent check, October 25, 2026, 13:40 to 14:10 UTC. Every number was recomputed from the official raw files (Elections BC 2026 initial-count CSVs, the 2024 and 2005 to 2020 Elections BC result files, the 2001 Elections BC workbook, the BC Stats 2021 Census riding profile, the pollster PDFs, the platform PDF). story.json was used only to compare against.

The build changed six times while I worked (09:36 to 10:05 EDT). This report judges these files:

| File | Time (EDT) | md5 |
|---|---|---|
| slides 1, 2, 4, 6, 7, 8 (.jpg) | 10:05 | ab5514, fee490, d2accb, 987582, b62a06, 16daae |
| slide 3 (.jpg) | 10:05:45 | ae9f54 |
| slide 5 (.jpg) | 10:05 | 8dcf19 |
| slides.html | 10:05:43 | 642910 (text same as 10:02 except label order) |
| data/story.json | 09:44:06 | b15ea3 |
| post/post-text.md | 09:05:26 | 032454 |

If anything is rebuilt after 10:05:45, slide 3 (map) is the part to re-verify.

## Summary

- Totals are right: the leads (64, 27, 2), the vote shares, the 47-seat majority, the 22 changed ridings, the poll figures, the seat chart and the platform quotes all reproduce from the raw sources.
- 3 errors remain: slide 4 "drive to work" figures, the slide 2 source line, and the slide 8 tax pledge attributed to the platform. A 4th sits in METHODOLOGY.md.
- Slide 3's line "made most of the change" is true only within Metro Vancouver, and it leaves out the City of Vancouver. A replacement line is suggested in B1.
- The slide 3 map is now correct. The current render puts every label on its own city and colours exactly the 16 changed ridings. The earlier renders had 5 labels on the wrong city and 2 missing.

## (a) Errors

**A1. Slide 4: "8 in 10 / 7 in 10 workers drive to work" counts passengers and leaves out people who worked from home.**
- The figures shown (78.8% and 68.7%) are "car, truck or van" in total. That total includes passengers.
- Drivers alone are 72.0% (switched) and 63.1% (stayed NDP), which is "7 in 10" and "6 in 10".
- The base is commuters only: people with a usual place of work or no fixed address. In May 2021, 24.0% and 27.7% of employed people in these ridings worked at home and are outside it.
- Fix, keeping the numbers: "commuters go to work by car" (8 in 10 and 7 in 10).
- Fix, keeping the word "drive": "commuters drive to work" (7 in 10 and 6 in 10).
- The headline "Most own their home and drive to work" holds either way: drivers are 72% of commuters and 54% of all workers in the 21 ridings.
- Evidence: census/raw/bcstats/census_profile_2021_ped93_part2.csv, rows 7687 to 7688 and 7717 to 7724; analysis/story.py, pooled(), lines 87 to 88.

**A2. Slide 2 source line does not cover the chart.**
- It says "Elections BC, 2017 to 2024 results", but the chart plots 2001, 2005, 2009 and 2013 as well.
- Fix: "Elections BC, 2001 to 2024 results; Elections BC initial count, 2026".
- Slide 1's footer also says "Elections BC 2017 to 2024 · Charts CC BY 4.0", although slide 1 has no chart. Use the same corrected range, or drop "Charts CC BY 4.0" there.

**A3. Slide 8: "No new taxes for the whole term" is not in the platform.**
- The slide calls the list "The Conservative platform's answer…" and the footer cites "Conservative Party of BC platform, 2026".
- The pledge is not in the 71-page platform PDF (no "raise taxes" or "new tax" pledge anywhere in it).
- It comes from the party's "No New Taxes" plan page, dated October 5, 2026: "A Conservative Party of BC Government will never raise taxes on British Columbians. Not once, for the entirety of our government."
- The slide's wording is also narrower than the pledge: "no new taxes" against "never raise taxes", and "whole term" against "entirety of our government".
- Fix: "Never raise taxes while in government", with the footer "Conservative Party of BC platform and plan pages, 2026".
- Evidence: next/raw/cbc_plan_conservative-party-of-bc-pledges-no-new-taxes-on-british-columbians.html and cbc_plan.html (fetched 12:28 UTC); a full-text search of next/raw/cbc_platform2026.pdf.

**A4. METHODOLOGY.md, row N8, is wrong (not on the slides).**
- N8 gives visible minorities as "46% vs 34%". story.json has 48.5% vs 33.5%.
- The correct figures are 49.2% vs 34.1%. story.py divides by total population (100% data); the visible-minority universe is the population in private households (25% sample, rows 4957 to 4958).
- The slide's "Nearly half" stays true.
- Also in N1: it lists "Cover" as showing the lead counts, but the cover no longer shows numbers.

## (b) Wording that overstates or could be challenged

**B1. Slide 3 line: "Surrey, Burnaby, Coquitlam, Richmond and Delta made most of the change."** Judged against the whole slide:
- **Metro Vancouver only:** 10 of its 16 changes are in these five places (Surrey 4, Burnaby 2, Coquitlam 2, Richmond 1, Delta 1). On that reading the line is literally true.
- **Whole province:** the footnote on the same slide adds six changes outside Metro Vancouver. Across all of them, the five places hold 10 of 21 Conservative gains (48%), which is not "most".
- **The City of Vancouver is left out:** it has 3 changes (Fraserview, Langara and downtown Yaletown), more than Richmond or Delta. Those 3 are blue on the map, under the "Vancouver" label.
- **Arbitrary picks:** Richmond and Delta are named with one change each, but Maple Ridge, North Vancouver and Port Moody, also one each, are not.
- **Burnaby still leans NDP:** 3 of its 5 ridings are NDP-led, the NDP has slightly more votes across them (34,626 to 34,345), and its average swing (7.1 points) is the lowest of the five places.
- Suggested replacement (verified): "All 10 Surrey ridings have a Conservative lead."
- Another verified option: "Conservatives lead in 28 of 34 suburban ridings, up from 15 in 2024." Suburban ridings here means the Metro Vancouver ridings outside the City of Vancouver.

**B2. Slide 3 footnote: "Downtown and rural ridings moved about half as much as the suburbs."**
- The ratio holds:
  - By place type: average swing 4.4 points against 8.8 points (0.50).
  - Five ridings that sit badly in their class moved: 0.49.
  - Against Metro Vancouver's suburbs only (9.5 points): 0.47.
- "Downtown" is the wrong word for the class. "Active core" includes Columbia River-Revelstoke, Kootenay Central, North Coast-Haida Gwaii, Oak Bay-Gordon Head and Esquimalt-Colwood.
- "Rural" includes Coquitlam-Burke Mountain and Maple Ridge-Pitt Meadows. Their wilderness areas pull their density under 150 people per km².
- "The suburbs" here means 45 ridings across B.C., not the headline's Vancouver suburbs.
- Fix: "City-centre and rural ridings moved about half as much as suburban ones."
- The method itself matches the Canadian Suburbs project as stated (canadiansuburbs.ca/methods).

**B3. Slide 5.**
- **Headline "B.C.'s middle ground moved the most": supported.**
  - Average two-party swing: 8.9 points in Liberal-plurality ridings, 4.9 in Conservative ones, 3.0 in the NDP or Green group.
  - Ridings that changed: 15 of 42, against 7 of 44 and 0 of 7.
  - "Middle ground" is a label, not a measurement. "Ridings that voted Liberal federally moved the most" says the same thing without it.
- **Line "Ridings that voted Liberal federally swung from the NDP to the Conservatives":** true for the group, but it reads as if all of them changed. Only 15 of 42 changed; 16 stayed NDP.
  - Suggest: "…swung furthest: 15 of 42 moved from the NDP to the Conservatives."
- **"Voted Liberal federally" is an estimate:** the 2025 poll results were allocated to provincial ridings. Five ridings are within 0.5 points: Kelowna-Mission (Liberal by 0.01), Penticton-Summerland, Bulkley Valley-Stikine, Coquitlam-Maillardville and Juan de Fuca-Malahat.
  - Two of the five changed hands, so the group counts could move by 1 or 2. The headline survives that.
  - Consider "estimated" in the chart note.
- The earlier headline, "decided the election", would have been unsupported: without the 15 Liberal-area switches the Conservatives would still lead in 49 ridings (47 needed).

**B4. Slide 6.**
- **Margin of error.** "About even: the gap is within the margin of error." Innovative Research Group's own release says a margin of error "cannot be calculated" for this online panel. Its own reading of the same numbers is "tie on health and housing".
  - Suggest: "About even: two points or less apart."
- **"58% of voters named it."** Angus Reid's base is 793 B.C. adults, all respondents. Suggest "58% named it".
- **Housing as third worry.** Housing is third at 28%, but only 3 points above economy/jobs (25%) and 4 above crime (24%). The slide applies the margin-of-error test to the party chips but not to this ranking.
- Evidence: polls/raw/innovative_research/irg_34_2026_bc_election_blog_post_release.pdf.txt, lines 817 to 831 and 947 to 950; polls/raw/angus_reid/2026.10.19_BC_Poll_3_tables.pdf.txt, lines 20 to 60.

**B5. Slide 8.**
- **The tax cut has a condition.** The slide's "$1,000 income tax cut per person, $2,000 per couple" matches the platform's page 5. The costing on page 59 qualifies it: "$1,000 or a little more for people who owe at least that much" and "$2,000 or more for a two-earner couple".
  - Suggest: "$1,000 a year income tax cut for anyone who owes that much ($2,000 for a two-earner couple)".
- **The headline predicts behaviour.** "Voters will hold them to these promises" says what voters will do. "Promises voters can track" keeps the intent.

**B6. Slide 2: "Its voters moved over."** This is a claim about individual voters drawn from riding totals. Suggest "The Conservatives took its place."

**B7. Slide 4: "$92k / $81k median household income".** These are the median of the riding medians, so the typical riding's figure, not the median household of the group (METHODOLOGY.md N9 says so). They are also 2020 incomes. Suggest "typical riding's median household income".

## (c) Visual defects

**C1. Slide 3, current render (10:05:45).**
- Correct:
  - Exactly the 16 Metro Vancouver ridings with a new leader are blue.
  - Each coloured shape matches the official Elections BC 2023 boundary of the same code.
  - All 9 labels sit on their own municipality, checked against Statistics Canada boundaries and city-hall coordinates.
  - Nothing is clipped.
- Minor:
  - There is no key saying blue means a new Conservative lead.
  - Labels cover about 40% of the small Surrey City Centre, Surrey-Fleetwood, Burnaby Centre and Delta North shapes.
  - "Vancouver" and "Burnaby" are about 5 px apart.

**C2. Slide 5: some ridings have no label.**
- The Green riding in the Liberal group, and the Conservative and Green ridings in the NDP or Green group, are drawn as unlabelled hairlines.
- So the labelled numbers add to 41 of 42 and 5 of 7.
- In the Conservative group, the 6 ridings that went from the NDP to the Conservatives and the 1 that went the other way show only as faint bands with no count.

**C3. Hard to read.**
- Slide 1's photo credit is white text on a near-white sky.
- Slide 8's credit runs partly over pale sky.
- The ends of the source lines on slides 4 and 8 sit over light patches: a porch and a white boat.

**C4. Layout passes.** Every text element on all 8 slides sits inside x 180 to 900, nothing is clipped, and no chart labels overlap. I measured this by loading slides.html read-only in a headless browser.

## (d) Style rules

- **Pass:**
  - No em or en dashes.
  - No "now", "today" or "currently".
  - No "won", "lost", "carried" or "beat".
  - No "X, not Y" framing and no "our analysis".
  - No contractions in the post text. The apostrophes are possessives.
- **Numbers:** no statistic repeats across slides. Some numerals coincide but measure different things: 27 seats and NDP 27%, 44 ridings and 44%, 26 ridings and NDP 26%.
- **Dates:**
  - Slide 8: "November 6 to 10" should be "November 6 to 10, 2026".
  - Slide 5: "April 2025 federal election" should be "April 28, 2025 federal election" if every date must be written in full.
- **Photo credits:** the account's recorded rule is "©" plus the credit line. The slides use "Photo: Name, licence". Please confirm which you want.
- **Slide 4 caveat:** "say nothing about how any one person voted" is a negation. It is the required caveat, so keep it, or use "These figures describe the places as a whole."
- **WhatsApp text:** "here is my quick analysis" is fine. It is not the banned "our analysis".

## (e) Verified correct

- **Leads and majority:**
  - Leads: Conservative 64, NDP 27, Green 2 of 93.
  - Majority: 47.
  - Party and candidate CSVs agree in all 93 ridings.
- **2026 shares:** Conservative 48.05%, NDP 37.38%, Green 10.97%, others 3.60% (valid votes, 1,792,235).
- **2024 base:** NDP 47, Conservative 44, Green 2; NDP 44.87%, Conservative 43.28%.
- **BC United ran no candidates in 2024:** no candidate carries that affiliation, and the CEO report (pages 49 to 50) records the August 28, 2024 suspension.
- **Ridings with a new leader:** 22 in all.
  - 21 moved from the NDP to the Conservatives.
  - Courtenay-Comox moved to the NDP (lead of 696).
- **Where they are:** 16 in Metro Vancouver. The "five more" are Cowichan Valley, Juan de Fuca-Malahat, Ladysmith-Oceanside, Saanich South and Vernon-Lumby.
- **2020 BC Liberal ridings:** all 29 have a Conservative lead. This holds even for near-tie notional ridings on either side.
- **"Conservatives 2% in 2020":** 1.91%.
- **Chart shares, 2005 to 2020:** match the raw Elections BC file exactly.
- **2001:** BC Liberal 57.62%, NDP 21.56% (raw workbook within 0.3 points). The Conservative 2,417 votes (0.15%) are drawn as zero, which is not visible.
- **Slide 2 chart:** drawn values match the data within 0.7 points (rendering).
- **Suburbs:** 28 of 34 Metro suburban ridings Conservative, up from 15. All 10 Surrey ridings are Conservative.
- **Census (21 vs 26 ridings):** owners 67.8% vs 56.0% ("7 in 10" and "6 in 10"); typical-riding income $92k vs $81k; visible minorities 49.2% ("nearly half").
- **Federal groups:**
  - Group sizes: 44 / 42 / 7.
  - Conservative group: 32 stayed Conservative, 6 NDP to Conservative, 5 stayed NDP, 1 Conservative to NDP.
  - Liberal group: 10 stayed Conservative, 15 NDP to Conservative, 16 stayed NDP, 1 stayed Green.
  - NDP or Green group: 5 stayed NDP, 1 stayed Conservative, 1 stayed Green.
  - Allocated votes match Elections Canada's B.C. totals within 5 votes.
- **Angus Reid (October 15 to 19, 2026):** cost of living 58%, health care 44%, housing affordability 28% are the top three.
- **Innovative Research Group (October 15 to 19, 2026, weighted n 1,000, all respondents):**
  - Cost of living: Conservative 33%, NDP 26%.
  - Health care: NDP 30%, Conservative 28%.
  - Housing: Conservative 28%, NDP 27%.
- **"Trusted":** the party-best question is framed as trust in the release.
- **Seat chart:** 27 orange, 2 green and 64 blue dots. The vote arc reads 37.1 / 11.1 / 3.7 / 48.1.
- **Seat chart text:** "Just under half the vote" (48%) and "big majority" (69% of seats) are fair.
- **Platform (Draft-18 PDF, the cited URL):**
  - Page 5: $1,000 a year per person, $2,000 for a couple.
  - Page 6: "Approve homes in months, not years".
  - Page 32: Universal Health-Care Guarantee and the $50-million Rural Health Emergency Fund.
  - No housing target for homes built, rents or prices on any of the 71 pages.
- **Final count:** "November 6-10, 2026 (planned)"; Return Day November 18, 2026 (Elections BC 2026 election page).
- **Photo credits:** all 8 match the Commons records saved by the photo thread.
- **Labels and links:**
  - "Week 3 · October 25, 2026" follows the account's labelling rule.
  - mediancanadian.ca is the account's domain.

## Resolved during the check (in earlier renders, now fixed)

- Slide 4 said "22 ridings that switched to the Conservatives" (now 21) and showed $91k for that group (now $92k).
- Slide 5's headline "decided the election" was not supported (see B3). It is now replaced.
- Slide 3's interim line "turned mostly Conservative" was wrong: Burnaby has 2 of 5 Conservative leads, and Surrey and Richmond were already mostly Conservative in 2024.
- Slide 3's map in the 09:36 to 10:02 renders put "Burnaby" on North Vancouver, "Port Moody" on Coquitlam-Burke Mountain, "Coquitlam" on Maple Ridge-Pitt Meadows, "Surrey" on Langley and "Richmond" on Delta. The 10:02 render also cut off "Richmond" and dropped "North Vancouver" and "Maple Ridge". All of this is fixed in the 10:05:45 render.

## Could not check

- **Later 2026 results.** The snapshot is from 01:49 PDT, October 25: 7,237 of 7,268 boxes, with 31 out in 6 ridings. The live results page is not on this session's allowlist, so I could not see later updates.
  - In each of those ridings the leader's margin is larger than any votes the missing boxes could hold.
  - If those boxes vote like the rest of their ridings, the rounded shares do not move.
- **The 2025 federal allocation** was not re-run from the poll level. I checked its totals, the plurality assignment, the flows and the near-tie sensitivity.
- **One 2001 district sheet** (PRN_2001) did not parse cleanly. The 2001 shares rest on the history thread's match to the official summaries plus my 78-sheet parse.
- **Photo credits** were checked against the saved Commons API records, not the live Commons pages. The photo thread lists the slide 4 photo's location as unverified.
- **Week numbering against the hub:** the project documents are not available to me here.
