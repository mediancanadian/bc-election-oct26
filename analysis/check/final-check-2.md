# Final check 2: slides, site and post text

**Build judged:** slides 12:50 (slides.html and the eight images, 12:50:04 to 12:50:08), index.html 12:50:08, METHODOLOGY.md 12:21:57, data/story.json 12:20:49, data/site.json 12:05:06, post/post-text.md 09:05:26. The files changed six times while I worked (12:14, 12:18, 12:20 to 12:22, 12:25, 12:32, 12:50). Every finding below was re-tested on the 12:50 files. Checksums are at the end.

**In short:** 2 errors on the slides (slide 3 footnote, slide 8 tax cut), 5 errors on the site, and METHODOLOGY.md rows that no longer match the slides. Since 12:50 the set says "elected" with no caveat that the closest ridings can still change. Everything else I recomputed reproduces from the raw files.

---

## 1. Errors

**E1. Slide 3 footnote: "Every area that voted BC Liberal in 2020 elected a Conservative in 2026."** This is false as written.
- **At the riding level:** the BC Liberals won West Vancouver-Sea to Sky in 2020 (by 0.2 points). 95% of its 2020 electorate is in the 2023 riding of the same name, which elected a Green in 2026.
- **At the voting-area level:** 124 of the 1,988 voting areas with a BC Liberal plurality in 2020 sit in ridings that elected an NDP (112) or Green (12) member in 2026.
- The "29 of 29" figure is true only for 2020 results recomputed on the 2023 ridings, and areas do not elect anyone.
- The site says it correctly: "All 29 ridings the BC Liberals would have held in 2020 elected Conservatives in 2026".
- **Fix:** "Every riding the BC Liberals would have held in 2020 elected a Conservative in 2026." (measured: 2 lines, as now).

**E2. Slide 8, site card and METHODOLOGY N17: "Up to $1,000 a year off each person's income tax."**
- The platform says "$1,000 a year in income-tax relief per person" (page 5) and "by $1,000 or a little more for people who owe at least that much" (page 59).
- "Up to" makes $1,000 a ceiling, but the platform says the cut is $1,000 or a little more. The site card's own detail adds that people who owe less save less, which is right.
- **Fix:** "$1,000 a year off each person's income tax" (1 line, 714 px), with the caveat left in the site detail.

**E3. Site card and METHODOLOGY N17: "A review of wait times in the first 100 days."**
- Platform page 32: "Launch the 100-day Patients First review to identify reforms from other universal public systems that cut waits, expand capacity, keep ERs open, and strengthen rural services, without user fees."
- It is a review of reforms that lasts 100 days, not a review of wait times within the first 100 days.
- **Fix:** "A 100-day review of reforms from other public systems to cut waits".

**E4. Site: candidate shares rounded twice.** The map riding card and the "why" sentence read `c26`, Elections BC's two-decimal percentages rounded again with round-half-to-even. The year card reads `s26`, computed from votes, which is correct. 13 candidate shares are off by 0.1, and 7 ridings show two different figures for the same share:

| Riding | Share | Computed from votes | `s26` (year card) | `c26` (card, sentence) |
|---|---|---|---|---|
| Kelowna Centre | NDP | 47.749 | 47.7 | 47.8 |
| Peace River North | Conservative | 85.746 | 85.7 | 85.8 |
| Burnaby North | Conservative | 46.447 | 46.4 | 46.5 |
| Esquimalt-Colwood | NDP | 43.253 | 43.3 | 43.2 |
| Fraser-Nicola | Conservative | 58.747 | 58.7 | 58.8 |
| Kamloops Centre | Conservative | 53.347 | 53.3 | 53.4 |
| West Vancouver-Capilano | NDP | 20.547 | 20.5 | 20.6 |

- **Fix:** compute `c26` percentages from votes over valid votes.

**E5. Site: "Ladysmith-Oceanside elected a Conservative MLA by 89 votes. 1 of the other 92 ridings are closer."** The verb is plural for one riding. The other cases are fine ("No riding is closer", "2 of the other 92 ridings are closer").

**E6. Site year card for Peace River North: "Conservative 85.7%, NDP 0.0%".**
- No NDP candidate ran, so "NDP 0.0%" reads as a result.
- The independent's 14.3% (Jordan Kealy) is not shown at all.
- **Fix:** list the candidates who ran, or say "no NDP candidate".

**E7. METHODOLOGY.md (12:21:57) is out of step with the 12:50 slides.**
- **N1 "Cover, slide 2":** the cover shows no seat numbers. Slide 2 prints only the Conservative counts (44 and 64).
- **N3 (47 for a majority), "Slide 2":** the slide no longer prints 47 as the majority; it labels the line "majority".
- **N16 (69% of seats and so on), "Slide 2":** slide 2 shows no seat percentages. This row is site only.
- **N12:** lists Conservative-group numbers (33 to 38) that slide 6 stopped printing at 12:20.
- **N14 "Slides 7 and 8":** slide 8 shows the worry ranks, not the percentages.
- **Missing rows:**
  - the 2024 shares as printed on slide 2 (NDP 44.9%, Con. 43.3%; N5 gives 45% and 43%);
  - "nine years of NDP government" (source: Legislative Library index, "Hon. John Horgan (from July 18, 2017)");
  - "15 of the 21" (slide 6).
- **N5:** labelled "2017 to 2024" but lists 2026.
- **N6:** its label "Areas that voted BC Liberal in 2020 ..." repeats the E1 wording.
- **N10:** says owners are counted "over private households", but `story.py` divides by owner plus renter households. That gives 67.9, 56.2 and 73.8; over all private households (including band housing) the figures are 67.8, 56.0 and 73.3. The rounded cards are unaffected. Either change the denominator or the description.
- **N17:** repeats E2 and E3.

## 2. Overstatements

**O1. "Elected" before the final count, and no remaining caveat.** "Elected" is the editor's choice; these are the facts it now asserts.
- Elections BC: "Results reported at initial count are preliminary" and "At the end of final count, a candidate is officially declared elected".
- At 12:50 slide 8's line "can still change the closest ridings" was removed. Slide 2 now only says when late ballots are counted.
- The exposed claims are below. "2024 net NDP" is what the 2024 final-count ballots (mail, assisted telephone, final-day out-of-district) netted the NDP in that riding.

| Riding | 2026 margin | 2024 net NDP | Slide claims it feeds |
|---|---|---|---|
| Ladysmith-Oceanside | 89 | +390 | slide 4 "five more" switches; slide 5's 21 |
| Kelowna Centre | 132 | +68 | slide 3's 29 |
| Cowichan Valley | 150 | +135 | slide 4 "five more" switches; slide 5's 21 |
| Vancouver-Fraserview | 387 | +408 | slide 4 map; slide 5's 21; slide 6's 15 |
| Surrey City Centre | 395 | +124 | slide 4 "All 10 Surrey" |

- Ladysmith-Oceanside and Vancouver-Fraserview have margins below what the 2024 final count netted the NDP there; Cowichan Valley is about level.
- Any flip changes 64, 22, 16, "five", 21 or 15.
- **Fix that keeps "elected":** slide 2 footnote "Each riding elects the candidate who finishes first. The final count, planned for November 6 to 10, 2026, can still change the closest ridings." (measured: 2 lines, same as now). This also removes "late ballots" (see S2).

**O2. Slide 8 and site: "$150 million a year for family benefits and child care."**
- Table B1 phases it in: $15 million (2027/28), $68 million (2028/29), $113 million (2029/30), full cost from 2030/31.
- The site detail now names the renovation credit, but not the phasing.
- **Fix:** "Up to $150 million a year for family benefits and child care" (1 line, 875 px), or "$150 million a year by 2030 for family benefits, child care" (1 line).

**O3. Site, cost of living worry card: "That gap is larger than a poll this size could produce by chance."**
- This contradicts the site's own note: "The pollster notes that a margin of error cannot be calculated for its online panel."
- **Fix:** "The gap is larger than the margin of error a random sample of this size would have."

**O4. Site swing sentences for the two Green ridings.**
- West Vancouver-Sea to Sky "swung 21.3 points toward the Conservatives, a bigger swing than in 9 in 10 ridings". The Conservative share rose only 2.8 points (35.6% to 38.4%); the NDP fell from 26.3% to 10.3% while the Greens rose from 38.1% to 47.6%.
- Saanich North and the Islands shows +16.4 with a Conservative rise of 1.9 points.
- West Vancouver-Sea to Sky's 21.3 also sits inside two averages. Without it, the "exurban and rural" average falls from 4.0 to 3.4 and the federal-Liberal group from 8.9 to 8.6. Both conclusions still hold.
- **Fix:** for ridings where the Greens finish first or second, say the swing is not comparable, or give the raw changes.

**O5. Site promise card: "No target for homes built, rents or prices", with the detail "The platform sets no number or timeline for housing".**
- The platform does set a timeline for approvals: "Approve homes in months, not years" (page 6).
- **Fix:** "The platform sets no number of homes and no target for rents or prices."

**O6. Final-count description (site watch note and methods).**
- The site says the final count "adds vote-by-mail, assisted telephone and out-of-district ballots".
- Elections BC's counting-processes document lists a fourth group: in-district voters who voted on Final Voting Day away from their assigned voting place.
- METHODOLOGY's "and other ballots" is right; use the same on the site.

**O7 (low). Site: the platform "was posted on the party's website on October 19, 2026".**
- The cited Draft-18 was uploaded October 19, but a Draft-17 was uploaded October 18 (WordPress media records).
- I could not confirm which version went public first. "The version cited was posted October 19, 2026" is safe.

## 3. Visual or interaction defects

**V1. Slide 2, 2024 arc (new at 12:50).** The big number is now "44 / Conservative seats", directly under the "majority" label, so it can read as "a 44-seat majority". The site's version of the same chart still shows "47 NDP seats" for 2024, so slide and site differ. Move "majority" to the top of the dashed line, or go back to "47 NDP seats" for 2024.

**V2. Slide 3 source line contrast.** It sits over bright lawn at about 4.5 to 1, the lowest in the set (the others are 5.6 to 12.3). Darken the bottom shade.

**V3. Slide 1 (minor, unchanged).** The source line says "Charts CC BY 4.0" on a slide with no chart.

**V4. Site watch slider.** At 150 it says "Show margins under 150 votes: 3 ridings", while the block below says "Four ridings have margins of 150 votes or fewer" (Cowichan Valley is exactly 150). Make the slider inclusive or word both the same way.

**Clean:**
- **Slides:** no text outside x 180 to 900 on any of the 8 slides, no clipping, no chart-label overlaps.
- **Slide 2 arcs:** 93 dots each, 47/2/44 and 27/2/64.
- **Slide 4 map (recoloured at 12:50):** correct for every riding I checked.
  - Bright blue for the 16 changes.
  - Muted NDP for Vancouver, Burnaby South-Metrotown, Burnaby East, Port Coquitlam and North Vancouver-Lonsdale; muted Green for West Vancouver-Sea to Sky; muted Conservative for the rest.
- **Slide 6 Sankey:** drawn to scale (3.55 px per riding).
- **Site layout:** no horizontal overflow at 390 or 1280 px, no console errors, no outside requests.
- **Site slider:** the 2026 arc redraws at both widths. At 5.6 points it shows 46 to 45; at 6.5, 47 NDP; at 3.0 toward the Conservatives, 71. The shares match uniform-shift arithmetic with Peace River North held Conservative.
- **Site interactions:** tapping a seat selects its riding. The place finder works (Surrey 10 ridings; Langley district 41.2/37.2/21.5; Lantzville; no-match message).

## 4. Style

**S1.** "Nearly half residents are visible minorities" (slide 5 card since 12:50, and the site's who card) is missing "of". "of residents are visible minorities" fits (2 lines, as now).

**S2.** Slide 2: "Mail-in and other late ballots are counted November 6 to 10, 2026."
- These ballots are not late; they wait for integrity checks.
- Elections BC calls the dates "planned".
- The O1 fix replaces this line.

**S3.** Slide 6 headline "Federal Liberal ridings switched most".
- It has "federal" without "provincial" (the house rule), and can read as federal ridings held by Liberal MPs.
- The line under it pairs the two words correctly, so this is optional. "Ridings that voted Liberal federally switched most" runs to 3 lines.
- The chart note can become "Provincial ridings grouped by the party with the most votes in the April 28, 2025 federal election" (2 lines, as now).

**S4. Source lines.** Slide 3's "Elections BC, 2001 to October 25, 2026, 1:49 a.m. Pacific" and slide 4's "Elections BC to October 25, 2026, 1:49 a.m. Pacific; 2021 Census" read oddly. Measured options:

| Slide | Option | Ends at |
|---|---|---|
| 3 | "Elections BC, 2001 to 2026 (as of October 25, 2026, 1:49 a.m. Pacific) · Charts CC BY 4.0" | 896 px |
| 4 | "Elections BC, 2024 and 2026 (as of October 25, 2026); 2021 Census · Charts CC BY 4.0" | 886 px |
| 2 (optional) | "Elections BC, 2024 and 2026 (as of October 25, 2026, 1:49 a.m.) · Charts CC BY 4.0" | 854 px |

Slide 2's current line ("2024; 2026 as of October 25, 2026") is readable as is.

**S5. Site dates without the year.**
- The Gallagher note: "2026 (as of October 25, 1:49 a.m. Pacific): 17.1".
- The year-card header: "2026, as of October 25, 1:49 a.m. Pacific".

**S6. METHODOLOGY.md wording.**
- "Lead" wording remains: N6, N7 and N8 ("2026 leader"), N15 ("A lead is shown"), N16 ("Seats are ridings leading over 93").
- Three "X, not Y" sentences remain: "These describe places, not how any person voted"; "estimates from riding totals, not measurements of individual voters"; "so the slides say British Columbians, not voters".

**S7.** Site methods: reference [19] (Kitschelt and Rehm) is attached to "They describe places as a whole and do not show how any one person voted", which it does not support.

**S8. No-repeat rule.**
- "21" (ridings that switched to the Conservatives) appears on slides 5 and 6.
- "44" appears on slides 2, 6 and 7 with three different meanings: 2024 Conservative seats, ridings that voted Conservative federally, and health care named by 44%.
- Low priority.

**S9 (nit).** The slide 4 map note has no final period.

## 5. Requested fixes from my earlier report

| Item | Status |
|---|---|
| "Commuters go to work by car" (slide 5, was 4) | Fixed: 8 in 10 and 7 in 10; 78.8% and 68.7% include passengers |
| Visible-minority denominator in `story.py` `pooled()` | Fixed: 49.2, 34.1 and 28.5 reproduce from the raw profile |
| Source years on slides 1 and 3 (were 1 and 2) | Fixed (2001 to 2026); wording awkward (S4) |
| Slide 8 tax cut "up to" | **Not fixed** (E2) |
| Plan-page "no tax increases" pledge off slide 8 | Fixed; on the site only, cited to the plan page and the September 27, 2026 release |
| Slide 7 (was 6) wording | Fixed: "British Columbians", "About even: a gap too small to call in a poll this size", "Named by 58%". New headline "Conservatives were rated best on costs" is more exact |
| Slide 6 (was 5) line | Rewritten at 12:50: "15 of the 21 ridings that went Conservative provincially voted Liberal federally", which is correct (15 in the Liberal group, 6 in the Conservative group) |
| Slide 4 (was 3) Surrey line and map | Numbers correct (10 of 10, 6 in 2024). Full-resolution boundaries, water and labels correct; recolouring correct |
| Slide 4 footnote "about twice as much" | Supported: 8.8 vs 4.4; 2.2 times rural, 1.7 times active cores |
| Dates in full | Slides yes; site has two exceptions (S5) |
| Slide 1 credit legibility | Fixed (dark pill) |
| "Decided the election" | Gone |
| "Its voters moved over" and the 12:20 "its voters went Conservative" | Replaced at 12:25 by "The vote that went BC Liberal for 20 years moved to the Conservatives". This is an aggregate claim and is supported: the 2024 Conservative share is at least the 2020 BC Liberal plus Conservative share in 73 of 93 ridings, correlation 0.82; 2001 to 2020 is 19.4 years |
| "Voters will hold them to these promises" | Replaced at 12:50 by "The Conservative promises we will track" |

## 6. The "as of" swap

- **Visible text:** no "initial" on any slide, on the site (with every block opened), in METHODOLOGY.md or in the post text. It survives only as internal data keys (`d.initial`, `"initial": true`).
- **Sentences the swap made awkward:** S4 (slides 3 and 4 source lines) and S5 (site dates without the year).
- **Since 12:50:** the slides no longer say the result can still change (O1).

## 7. Post text versus the final set

- **Consistent:** no dashes, no contractions, no "lead", "federal" or "initial", no banned words. "My quick analysis" is fine.
- **One mismatch:** the caption "and the promises voters will hold them to" and the short description "the promises they will be held to" no longer match slide 8's new headline "The Conservative promises we will track". Suggest "and the promises we will track" in both.
- **Optional:** "why voters moved" talks about individuals; "why the vote moved" matches the set's place-level framing.

## 8. Verified (new or changed since my last report), one line each

- **Nine years of NDP government:** from July 18, 2017 (Legislative Library index) to October 24, 2026 is 9 years 3 months.
- **10.7:** 48.055 minus 37.378 is 10.677 points (1,792,235 valid votes).
- **1.6:** 44.866 minus 43.278 is 1.588 points (2,105,341 valid votes in 2024).
- **3 seats:** 47 minus 44.
- **Seat arcs:** 47 NDP, 2 Green, 44 Conservative (2024) and 27, 2, 64 (2026), 93 dots each.
- **Slide 2 shares:** 48.1 (exact 48.055 rounds up), 37.4, 44.9, 43.3.
- **Slide 6 Sankey:**
  - Conservative group: NDP 11 to 6 and Conservative 33 to 38, with 6 switches to the Conservatives and 1 the other way (Courtenay-Comox).
  - Liberal group: 16 stayed NDP, 15 switched, 10 stayed Conservative, 1 Green.
  - NDP or Green group: unchanged.
- **Slide 5 "more diverse":** visible minorities 49.2% vs 34.1%; immigrants 38.3% vs 30.1% (story.json).
- **Site majority chapter:** +4.8 and minus 7.5 points; 20 seats net; 68.8% of seats; 7,509 voters in 18 ridings (0.42% of votes counted); wasted votes 62.5%, 23.6%, 87.3%.
- **Site how chapter:** 29 of 29, and 35 of the 62 notional NDP ridings (notional 2020: 62 NDP, 29 BC Liberal, 2 Green); correlation 0.82; best Conservative share since 1928.
- **Site where chapter:**
  - The 16 Metro changes by city, and the five changes outside Metro by name.
  - Place types 16/25/20/31 ridings, with 22 changes of which 14 are suburbs; 8.8 vs 4.4.
  - Metro region: Conservative 42.3% to 48.4% and seats 16 to 32; NDP 50.6% to 39.2% and seats 30 to 14.
- **Site who chapter:**
  - Owners 67.9, 56.2, 73.8; car 78.8, 68.7, 87.1; visible minorities 49.2, 34.1, 28.5; incomes $92k, $81k, $91k; groups 21, 26, 43.
  - Quadrants 22/26/24/20 with +5.9, +10.4, +3.3, +6.3 (split at or above the median).
  - Income quarters $72k, $82k, $92k, $104k with +3.7, +5.7, +5.9, +11.0.
- **Site middle chapter:** 8.9, 4.9 and 0.7 points; Saanich North and the Islands +16.4; the list of 15.
- **Site why chapter:** 10-poll average 43.8 and 38.9; Ipsos 53% and 31%.
- **Final count and Return Day:** Elections BC's key-dates page says "Final count: November 6-10, 2026 (planned)" and "Return Day: November 18, 2026".
- **Health-care promise:** "Publicly paid surgery elsewhere when waits pass set limits" matches page 32 ("publicly funded treatment through another qualified provider when medically recommended surgical wait benchmarks are exceeded"). The $50 million fund is correct.
- **Swingometer:** thresholds 5.6 and 6.5.
  - Shift needed to flip (points): Kelowna Centre 0.3, Ladysmith-Oceanside 0.2, Surrey City Centre 1.8, Burnaby South-Metrotown 0.3, Burnaby East 0.8, Vancouver-Fraserview 1.4.
  - Toward the Conservatives: Courtenay-Comox 1.3, West Vancouver-Sea to Sky 18.8.
- **"Closer" counts:** 1, 2, 4, 6, 7, 11, 36, 73, 84, and "No riding is closer" for Burnaby South-Metrotown.
- **Watch lists:** under 400 votes, 8 ridings; under 150, 3; under 1,500, 26.
- **References:** 23, all cited.

## 9. Could not check

- Elections BC results after 1:49 a.m. Pacific (the results site is not reachable from here), so I do not know how the final count turns out.
- The slide 2 photo credit "Hayden Soloviev, CC BY 4.0" on Wikimedia Commons (blocked); it matches the local photo record.
- "Week 3": the project also holds a "week-03-turkiye-story-draft" document, so confirm the week number.
- Which platform version went public first (Draft-17 uploaded October 18, Draft-18 October 19).
- The cited Elections BC news release [3]. My final-count comparison uses Elections BC's counting-processes document instead.
- I did not re-run the federal poll-by-poll allocation (it was accepted in the earlier check).

## Files judged (md5, first 6 characters)

| File | md5 |
|---|---|
| slides/slides.html | 107e34 |
| Slides 1 to 8 | 321faa, 1200b3, 6793f2, 6274b0, b86076, a73225, af5173, 2d4166 |
| index.html | 5d6ee2 |
| METHODOLOGY.md | a362c7 |
| data/story.json | 2cf589 |
| data/site.json | f32691 |
| post/post-text.md | 032454 |
