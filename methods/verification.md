# Verification record

Every claim in the post was checked by a separate checker who had not done the analysis, working from the saved raw files and the official pages, and recomputing each number with their own code. The reports are kept in full in `analysis/check/` and `analysis/core/verification.md`, with the scripts the checker of the analysis used (`analysis/core/verify/`).

## 1. The analysis (October 25, 2026): `analysis/core/verification.md`

118 claims in the analysis were recomputed from the raw files: 102 confirmed, 3 wrong, 3 unsupported and 10 needing new wording. The fixes that touch a published number:

- The Conservatives' 1928 share is 53.30%, the party's own vote (Electoral History of British Columbia 1871 to 1986, page 159); 53.60% adds Independent Conservatives.
- Ridings are grouped by the party with the most 2025 federal votes, in four groups (Liberal 42, Conservative 44, NDP 6, Green 1), replacing a two-way Liberal or Conservative split.
- The link between turnout and swing is described as weak, with the measure named.

## 2. The first slides and page: `analysis/check/slides-site-check.md`

The slides and the page were checked against the data, with the page rendered at 390 px and 1280 px in light and dark mode and every control clicked. Fixes included the wording on census links ("once income, age, renting and Metro Vancouver are held equal"), the Green seats in two regional tables, and final count dates taken from Elections BC's own page.

## 3. The slides: `analysis/check/final-check-slides.md`

- Car commuting is described as "go to work by car", which counts drivers and passengers, as the census measure does.
- The pledge not to raise taxes is attributed to the party's plan page, where it appears, rather than to the platform.
- The Metro Vancouver map was redrawn so that every label sits on its own city and exactly the ridings that changed party are coloured.

## 4. The slides, page and methodology: `analysis/check/final-check-2.md`

- "Every riding the BC Liberals would have held in 2020" refers to 2020 results moved onto the 2023 ridings (29 of 29); West Vancouver-Sea to Sky elected a Green.
- The tax promise uses the platform's words: "$1,000 a year in income-tax relief per person".
- The 100-day review is described as the platform does: a review of reforms from other public systems.
- The slides and the page say the final count, planned for November 6 to 10, 2026, can change the closest ridings.

## 5. The slides, page, methodology and post text: `analysis/check/final-check-3.md`

Every slide number was recomputed from the raw files and found correct. Fixes made before publishing:

- Slide 3's line says the Conservatives took the BC Liberals' place as the NDP's main rival, which describes who finished second; riding totals cannot show how individual voters moved.
- The page rounds each share once, from unrounded values (visible minorities in the ridings that stayed Conservative: 28%; several riding values that were off by 0.1).
- Place types test density first for whole ridings, so three rural ridings are no longer called active cores; West Vancouver-Sea to Sky and Powell River-Sunshine Coast are in "Rest of Vancouver Island and Coast".
- In the ridings where the main race was between the NDP and the Greens, each riding's description gives the race as it was.
- The federal grouping is marked as an estimate where the federal margin is 0.5 point or less (five ridings).
- Smaller fixes: the 2024 comparison of ballots left to the final count names the ballot types; the poll release is "a weighted sample of 1,000"; independents are named as such; platform pages 7, 61 and 64; "will seek to amend the party's rules"; dates in full; the 2001 Conservative share (0.15%) is plotted from Elections BC's 2001 results by district.
