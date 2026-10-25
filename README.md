# B.C.'s 2026 provincial election, in numbers

Week 3 of The Median Canadian: an explorable page on the British Columbia provincial election of October 24, 2026, built from official data. The Conservative Party of BC formed its first majority since 1928, after nine years of NDP government.

- Page: https://mediancanadian.ca/bc-election-oct26/
- All posts: https://mediancanadian.ca/ (the link in the Instagram bio)

The 2026 numbers are Elections BC's results as of October 25, 2026, 1:49 a.m. Pacific (7,237 of 7,268 ballot boxes). The final count, planned for November 6 to 10, 2026, can change the closest ridings.

Everything behind the page and the Instagram slides is here: every analysis script, every output table, the independent checks and the steps to rebuild it from the official sources. Nothing is hidden, so anyone can reproduce or challenge any number.

- **[METHODOLOGY.md](METHODOLOGY.md):** what was measured and how, and a table of the published numbers (N1 to N33) with the file it comes from and how it is computed.
- **[REPRODUCE.md](REPRODUCE.md):** environment, downloads and run order.
- **[data/SOURCES.md](data/SOURCES.md):** every source with its link and licence.
- **[methods/verification.md](methods/verification.md):** the independent checks of every claim and what they changed.

## What the page shows

- **Find your riding:** by riding name or by any city, town or community in B.C.; every chapter then shows where your riding fits.
- **The result:** the 93 seats in 2024 and 2026, with the seats that changed party; a swingometer that redraws the seats as votes move between the Conservatives and the NDP; votes against seats; the tipping point.
- **How they got here:** each party's share of the vote, 2001 to 2026 and every election since 1928.
- **Where it changed:** a map of every riding (all of B.C., Metro Vancouver, Victoria and the Okanagan) by change of party, party elected, swing, type of place, 2025 federal vote and census measures; regions and types of place.
- **By household income:** swing by riding income, with every riding as a dot; who lives in the ridings that switched or stayed.
- **The middle ground:** the provincial vote and seats in the ridings grouped by the party that came first in the April 28, 2025 federal election.
- **Before the vote:** the top worries and the party rated best on each, the final campaign polls against the result.
- **What comes next:** what the Conservatives promised on each top worry, with platform pages; the final count and the closest margins.

## Files

| Path | What it is |
|---|---|
| `index.html` | The page (one file: HTML, CSS, JavaScript and data), built by `site/build_site.py` |
| `site/` | Page builder, template, script and `build_data.py` (the page's data) |
| `data/story.json` | Every number the slides and the page use, written by `analysis/story.py` |
| `data/site.json`, `data/slide_text.json`, `data/places.json` | The page's riding data, the slides' headlines and lines, and the place index for "Find your riding" |
| `data/ridings.csv`, `data/*.csv` | One row per riding (results, census and federal figures) and the province, region, poll and close-race tables |
| `data/candidates_2026_as_of_2026-10-25_0149_PT.csv` | Elections BC's 2026 candidate results as posted October 25, 2026, 1:49 a.m. Pacific |
| `data/geo/` | The riding boundaries used by the page and the slides (TopoJSON and GeoJSON) |
| `data/SOURCES.md` | Every source with link and licence |
| `slides/make_slides.py`, `slides/out/` | The slide builder and the published slides (JPG) |
| `slides/photos/`, `slides/photos_used.json`, `slides/photos_new.json` | The slide photos (Wikimedia Commons, credited in NOTICE) |
| `analysis/story.py`, `analysis/build_map_detail.py` | The story's numbers, and the detailed map files for the slides and the page |
| `analysis/<thread>/` | One folder per research thread (results24, history, polls, census, geo, federal25, live, model, next): `scripts/`, `results.md` (findings and method), `manifest.json` (every downloaded file with its link) and output tables |
| `analysis/core/` | The joined analysis of 2026 against 2024, the 2025 federal vote, the 2021 Census, polls and history, with its checks |
| `methods/` | The METHODOLOGY.md builder and the verification record |

## Licence

- **Code:** Apache License 2.0 (LICENSE and NOTICE).
- **Text, charts, maps and slides:** CC BY 4.0 (LICENSE-CONTENT.md).
- **Photos in the slides:** Wikimedia Commons, each under its own licence, listed in NOTICE.
- **Data:** belongs to its publishers and is used under their terms (data/SOURCES.md).

The Median Canadian. A curious Canadian explaining Canada through numbers, every week.
