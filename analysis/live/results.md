# BC 2026 election-night capture: setup notes (prepared 2026-10-24, ~10:20 UTC)

## 1. How Elections BC publishes results
- Entry point named by Elections BC (news release "Final Voting Day is Saturday, October 24"): **https://results.elections.bc.ca**. Right now it returns **301** to the static archive page https://elections.bc.ca/resources/results/provincial-election-results/ (2024 SOV and DataBC links only).
- Results pages are served from Elections BC's Azure ENR container **https://electionsbcenr.blob.core.windows.net/electionsbcenr/**. Anyone can list it: `?restype=container&comp=list` gives 125 blobs, all of them assets.
  - 2026 assets are already uploaded: `replaceCanName.js` (2026-10-13; it fixes accented 2026 candidate names in the `#tblReport` table), `electionresults.css` (2026-10-20), `counting-processes.pdf` (2026-10-23).
  - There are **no 2026 result files yet**, and no JSON/XML API. The 2024 pages were static HTML: `Results_<n>_GE-2024-10-19_Party.html` and `..._Candidate.html` (cited at the time by Indo-Canadian Voice). They now return 404 (removed).
  - Expected 2026 pattern: `Results_<n>_GE-2026-10-24_{Party,Candidate}.html`. This is an inference from 2024 and is not confirmed.
- Fields, inferred from the 2026 CSS column ids (not yet seen in data): electoral district (`edname`), candidate, affiliation, votes, popular vote %, total valid votes, ballot boxes reported (`prov_ballotboxesreported`), districts leading/won (`prov_districts_lead_won`), popular vote by party, % who voted (`prov_percentwhovoted`), a CSV download link (`#reportdownloadcsv`), and a datestamp (`.datestamp`).
- Before 8 p.m. the endpoints answer, but with no results and no 2024 test data.

## 2–3. Scripts
- `scripts/fetch.py` (run with `python3 -I`). Each run: checks results.elections.bc.ca, lists the container, downloads every 2026 result file (plus any CSV/JSON it links to) into `raw/snapshots/<UTC>/`, then writes `latest.csv` and `latest_summary.csv`.
  - Only official hosts are allowed. The 120 s per-URL minimum interval is enforced.
  - Tested live at 10:16 UTC: it exits 0 with "NO RESULTS POSTED YET". Parsing was tested on a synthetic page (`scratch/fixture/`) and works.
  - The real table layout is unknown. If the log says "FILES FOUND BUT NOT PARSEABLE", adjust `COLS` and run `fetch.py --reparse <snapshot_dir>`.
- `scripts/loop.sh <hours>` runs fetch.py every 5 min and logs to `logs/loop_<UTC>.log`. It has not been started.

## 4. Candidates and House changes
- `candidates_2026.csv` has 353 candidates in 93 districts.
  - Count check: 355 at close, plus 2 added by CEO order (Yamagata, OneBC, Burnaby North; Sandhu, Green, Langley-Willowbrook), minus 4 withdrawn. The withdrawn are Lenoski (NWC), Thiele (NVS), Webster (VNY) and DePaco (BNN). They are still on the ballot and still in the list.
  - Party counts: CP 93, NDP 92, Green 73, CentreBC 35, OneBC 33, Independent 7, Unaffiliated 6 (shown as blank or "Other"), Libertarian 4, Communist 4, CHP 3, CWP 2, Freedom 1.
  - Incumbency comes from the LIMS records: 79 of the 91 seated MLAs are running. Two are running in a different district: Lynne Block (to NVS) and Elenore Sturko (to SUS, as CentreBC).
  - Not running: Boultbee, Bailey, Chapman, Chow, Chan, Rustad, Greene, Popham, Hepner, Kahlon, Botterell, Armstrong.
- `house_changes_2024_2026.csv` and `standings_dissolution_2026.csv` come from Legislative Assembly LIMS (api.lims.leg.bc.ca/graphql, the API behind leg.bc.ca member pages).
  - **At dissolution (Sept 22, 2026), per LIMS:** NDP 47, Conservative 29, Independent 13, Green 2, vacant 2 (Abbotsford-Mission: Gasper resigned; Vancouver-Strathcona: Phillip died).
  - **Conflict:** the static leg.bc.ca "Current Party Standings" page says NDP 47, CP 39, Green 2, Ind 5, total 93. That page appears stale.
  - LIMS has no event dates or caucus names (CentreBC and OneBC MLAs are recorded as Independent). The dates in the CSV come from Wikipedia and are flagged unverified.
  - LIMS still lists Brent Chapman as Conservative, while Wikipedia says he moved to OneBC on dissolution day.

## 5. Turnout (`advance_turnout_2026_vs_2024.csv`)
- 2026 advance voting, by district and day (Elections BC PDF, updated 2026-10-22, preliminary): **891,348** voters, which is 23.84% of **3,738,182** registered (as of Oct 14).
  - By day: 137,832 / 201,774 / 105,049 / 128,636 / 139,101 / 178,956.
  - Six district-day cells are blank ("-"): ABW, KEC, KLM, VNS, WKP, WVS. The province totals therefore appear to include figures not shown by district.
- 2024 comparison: **1,002,004** advance ballots (953,025 in-district, 48,979 out-of-district; SOV), from 3,609,288 registered (final). 2024 by day is in the CEO report.
- Definitions differ: 2026 counts voters in the district where they voted; 2024 SOV counts ballots in the voter's home district.

## Gaps
- Results file names and the CSV schema are unconfirmed until about 8 p.m. PDT.
- The official dated record of MLA party moves was not found.
- Elections BC has not published 2026 final registered-voter counts.
