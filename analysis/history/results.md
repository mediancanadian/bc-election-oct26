# BC general elections 1928 to 2024: official-data base

Accessed 24 Oct 2026 (UTC). All numbers come from Elections BC or Legislative Assembly documents listed in `manifest.json`. No Wikipedia or news numbers are used, so there is no "unverified" column. Contains information licenced under the Elections BC Open Data Licence.

## Files

| File | What it is |
|---|---|
| `province_series.csv` | 27 general elections, 1928 to 2024: seats and vote share by party family, turnout, government, premier, majority or minority |
| `province_party_detail.csv` | Every party line as printed in the official summaries (231 rows), with the family code used |
| `right_vs_left.csv` | Right-of-centre combined share against CCF/NDP share |
| `turnout_trend.csv` | Registered and eligible turnout, 1928 to 2024 |
| `districts_2001_2017.csv` | 1,958 candidate rows: 79 districts (2001, 2005), 85 (2009, 2013), 87 (2017) |
| `derived/sov2013_table2_comparison.csv` | 2013 Statement of Votes Table 2 (1928 to 2013), parsed |
| `scripts/` | `parse_districts_2001_2017.py`, `parse_sov2013_comparison.py`, `build_province_series.py`, `build_manifest.py` |

## Checks run

- Districts: the sum of candidate votes equals each district's Grand Totals row. Province sums by party match the official summaries exactly for 2001, 2009, 2013 and 2017. For 2005 they match the 2009 errata (NDP 731,783, GP 161,849), not the uncorrected supplement. Every computed winner matches the sheet's "Candidate elected" line. Registered voters, voters who voted and rejected ballots also sum to the official totals (2009: 1,651,566 against 1,651,567 published, a 1-vote difference inside the source).
- Province series: for every election, party votes sum to the printed total, seats sum to the house size, and the printed percentages match within 0.02. Exception: in 1945 the printed party lines sum to 467,641 against a printed total of 467,747. I kept the figures as printed and flagged the gap.

## Findings

| Year | Right core % | CCF/NDP % | Turnout (reg.) | Government |
|---|---|---|---|---|
| 1928 | 53.60 | n/a | 71.33 | Conservative, 35/48 |
| 1952 | 44.04 | 30.78 | 68.53 | Social Credit minority |
| 1972 | 43.83 | 39.59 | 68.60 | NDP, 38/55 |
| 1983 | 50.92 | 44.94 | 77.66 | Social Credit |
| 1991 | 57.33 | 40.71 | 75.07 | NDP, 51/75 |
| 2001 | 57.62 | 21.56 | 70.95 | BC Liberal, 77/79 |
| 2017 | 40.90 | 40.29 | 61.18 | NDP minority |
| 2020 | 35.68 | 47.69 | 53.86 | NDP |
| 2024 | 43.28 | 44.87 | 58.45 | NDP, 47/93 |

1. The 2024 Conservative share (43.28%, 44 seats) is the party's best since its 1928 win (53.30%, 35/48). In every election from 1945 to 2020 the Conservative label stayed at 16.84% (1952) or less.
2. Combined, the right in 2024 (43.28%) recovered from 35.68% in 2020. That is still below every Social Credit or BC Liberal win from 1952 to 2013 (44.04% to 57.62%).
3. Before 2017, the NDP won only when the right split: 1972 (SC 31.16 + PC 12.67), 1991 (SC 24.05 + BC Liberal 33.25) and 1996 (BC Liberal 41.82 + Reform 9.27, when the NDP won on 39.45%). The CCF led the vote in 1941 (33.36%) but did not govern.
4. Social Credit won 11 of 12 elections from 1952 to 1986 (losing 1972), with up to 49.76% (1983). It fell to 24.05% in 1991 and 0.40% in 1996.
5. Turnout of registered voters peaked at 77.66% (1983) and hit its lowest point at 53.86% (2020). The 2024 figure was 58.45%. Turnout of estimated eligible voters fell from 70.50% (1983) to 50.99% (2009).

## Methods and caveats

- **Party families.** `CON` covers Conservative, PC and BC Conservative, plus the 1933 Unionist and Non-Partisan Independent Group factions; the Conservative Party did not run officially in 1933. `SC` is Social Credit. `COAL` is the 1945 and 1949 Coalition (Liberal plus Conservative). `LIB` is the Liberal Party before 1991. `BCLIB` is the BC Liberal Party (1991 to 2020; it was renamed BC United and did not run in 2024). `LEFT` is the CCF (to 1960) and the NDP (1963 on). `GRN` is Green, `REF` is Reform BC, `OTH` is everything else.
  - "Right core" is CON + SC + COAL + BCLIB.
  - "Right broad" also adds Reform, Western Canada Concept and Unity.
  - COAL includes the Liberals, so 1945 and 1949 are not comparable with other years.
- **Multi-member districts (1928 to 1986).** Voters had as many votes as seats, so valid votes exceed ballots and shares are shares of votes. In 1986, for example, there were 1,935,453 votes from 1,366,193 voters, with 17 two-member districts. 1991 was the first election with only single-member districts.
- **1952 and 1953 alternative vote.** The volume's errata says this was the alternative vote, not STV. Shares in the series are first-count shares; final-count votes and shares are in `province_party_detail.csv`. In 1953 Social Credit had 37.75% on first count and 45.54% on final count.
- **1941.** No party won a majority (Liberal 21 seats). The Coalition (32 seats) formed after the vote.
- **1945 turnout.** The 1871-1986 volume gives 62.66% on 476,222 registered and notes the figure seems to omit active-service voters. The 2013 SOV Table 2 gives 65.29% on 457,017. Both are kept.
- **Gaps:**
  - 1996: the Progressive Conservative vote sits inside "Other" (0.76%).
  - 2001: the BC Conservative vote (2,417, from the district file) sits inside "Other".
  - There is no eligible-voter estimate before 1983 or for 2020 and 2024; neither the SOV nor the CEO report gives one.
  - Candidate counts per party were not extracted for 2020 and 2024.
  - District-level files were not built for 1928 to 1996 or for 2020 and 2024; that was out of scope.
- **Small source inconsistencies (all kept):**
  - The 2013 Table 2 lists 556 candidates for 1972; the volume lists 226.
  - The 2009 candidate count is 345 in Table 2 and 346 in the supplement.
  - 2017 had 371 candidates nominated and 369 on the ballot.
- **Premiers.** These come from the official volumes' premier lists to 2011, and from the Executive Council lists in Hansard indexes for 2013 to 2024. The Legislature's premiers web page could not be found (404), so I used the indexes.

## Data dictionary

**districts_2001_2017.csv** (one row per candidate)
- `year`, `election_date`, `district_count` (number of districts that year).
- `ed_code` (Elections BC 3-letter code), `electoral_district`. The 2001 names come from the 2005 code sheet, since the district set is the same; 2001 PKV is Penticton-Okanagan Valley.
- `candidate`, `party` (ballot abbreviation; `NA/IND(blank)` means none was printed), `votes` (Grand Totals across all voting opportunities).
- `vote_share_pct` (of district total valid votes), `rank`, `is_winner`, `district_winner`, `district_winner_party`.
- `winning_margin_votes`, `winning_margin_pct_pts` (first minus second).
- `total_valid_votes`, `rejected_ballots`, `registered_voters_who_voted`, `registered_voters`, `turnout_pct_registered`.
- `official_elected_line` (as printed in the sheet), `winner_matches_official` (1 = check passed).

**province_series.csv** (one row per general election)
- `seats_in_house`, `total_valid_votes` (first count for 1952 and 1953), `multi_member_districts`.
- `seats_<FAM>`, `share_<FAM>` (percentage of valid votes).
- `registered_voters`, `voters_who_voted`, `turnout_pct_registered`, `estimated_eligible_voters`, `turnout_pct_eligible`, `turnout_source`, `turnout_alt_source_note`.
- `governing_party_after_vote`, `premier`, `governing_seats`, `majority_or_minority`, `premier_source`, `party_summary_source` (volume page, with the PDF page in brackets), `notes`.

**right_vs_left.csv**
- `conservative_family_share`, `social_credit_share`, `coalition_share`, `bc_liberal_share`, `right_core_share`, `right_broad_share`.
- `ccf_ndp_share`, `left_label`, `right_minus_left_pts`, `liberal_pre1991_share`, `note`.

**province_party_detail.csv**
- `party_as_printed`, `family`, `votes`, `vote_share_pct` (recomputed), `printed_pct`, `seats`, `candidates`, `final_count_votes`, `final_count_share_pct`, `source`.
