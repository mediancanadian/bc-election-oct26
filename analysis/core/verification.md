# Verification of findings.md (BC 2026, results as of October 25, 2026, 1:49 a.m. Pacific)

Checked 2026-10-25 against snapshot 20261025T115814Z and the official 2024, census, federal, history, poll and model files. All values were recomputed with my own code (`analysis/verify/v1_core.py`, `v2_census.py`, `v3_extra.py`, `v4_specs.py`; logs `v*_log.txt`). I compared with `full.py` only afterwards, to explain differences.

Scorecard: 118 claims checked (counts in brackets in the Status column). 102 confirmed, 3 wrong, 3 unsupported, 10 need rewording. Plus 6 omissions.

## Errors (must fix)

| # | Claim | Correct value | Fix |
|---|---|---|---|
| E1 | 1928 Conservative share 53.60% | **53.30%** (192,867 of 361,814; Electoral History of BC 1871-1986, p.159) | 53.60 is the Conservative *family* (adds Independent Conservative, 0.29). Use 53.30% |
| E2 | Federal table: "Federal 2025 leader: Liberal 46, Conservative 47" | Federal winners on these ridings: LPC 42, CPC 44, NDP 6, GPC 1 | The 46/47 split is "Liberal share above Conservative share", which puts 6 NDP-led and 1 Green-led ridings into one of the two. Relabel the column "Liberal ahead of Conservative federally" (its numbers are then right), or use the 4 groups |
| E3 | Turnout change "no link to the swing (r -0.10)" | r with two-party swing = **+0.17**; -0.10 is r with the raw Conservative share change | Say "r -0.10 with the change in Conservative share" or "+0.17 with the two-party swing". Either way: weak |

## Claim table

Status: C = confirmed, W = wrong, U = unsupported, R = needs rewording.

| Sec | Claim | My value | Status | Fix |
|---|---|---|---|---|
| Hdr | 7,237 of 7,268 boxes | 7,237 / 7,268 | C | |
| Hdr | All 588 advance boxes | 588 / 588 | C | |
| Hdr | 31 boxes left in 6 ridings, leader ahead 5.3+ | FRN, LFH, NOI, PRO, SHU, VNS; min 5.32 (NOI) | C | |
| Hdr | Final count November 6 to 10 | No date in any downloaded source; counting-processes.pdf says "about two weeks after election day" | U | Cite a source or say "about two weeks after election day" |
| Hdr | Final count = "mail, absentee, out-of-district" | Elections BC: vote-by-mail, assisted telephone, out-of-district on Final Voting Day, in-district at a non-assigned place | R | Use Elections BC's list; "absentee" is not their term |
| 1 | Votes CON 861,258; NDP 669,901; GRN 196,593; CentreBC 28,998; OneBC 26,991; Other 8,494 | same (sum 1,792,235, matches Party.csv) | C (6) | |
| 1 | 2026 shares 48.05 / 37.38 / 10.97 / 1.62 / 1.51 / 0.47 | same | C (6) | |
| 1 | 2024 shares 43.28 / 44.87 / 8.24 / Other 3.62 | same | C (4) | |
| 1 | Changes +4.77 / -7.49 / +2.73 | same | C (3) | |
| 1 | Leading 64 / 27 / 2 / 0 / 0 / 0 | same | C | |
| 1 | Seats 2024 44 / 47 / 2 / 0 | same | C | |
| 1 | Majority line 47 | 93 seats | C | |
| 1 | Votes per riding led 13,457 / 24,811 / 98,296 | same | C (3) | |
| 1 | Two-party CON 49.1% (2024), 56.2% (2026) | 49.10, 56.25 | C (2) | |
| 2 | 48.05% highest for any party since 2001 (57.62%) | max any party 2005-2024: 47.69 (NDP 2020) | C | |
| 2 | BC Liberals 2005-2013: 44.13% to 45.82% | 45.80, 45.82, 44.13 | C | |
| 2 | 64 seats most since 2001 (77 of 79) | yes | C | |
| 2 | BC Liberals 46, 49, 49, 43 (2005-2017) | same | C | |
| 2 | Best Conservative share since 1928 | No Conservative share above 48.05 from 1933 to 2024 (2024: 43.28) | C | |
| 2 | 1928: 53.60%, 35 of 48 | 53.30%, 35 of 48 | **W** | E1 |
| 2 | NDP 37.38% lowest since 2001 (21.56%) | yes | C | |
| 3 | 22 seats changed hands | 22 ridings with a different leader | R | "22 ridings where the leader differs from the 2024 winner" (initial count, not yet seats) |
| 3 | NDP to CON 21; Metro 17 with the named list; Capital 2; Island 2; Okanagan 1 | same, names match | C | |
| 3 | CON to NDP 1, Courtenay-Comox | same | C | |
| 3 | 21 sitting MLAs trailing, 17 NDP + Day, Kealy, Sturko, Brodie | same (79 incumbents matched, 0 unmatched) | C | Sturko ran outside her own riding (Surrey-Cloverdale to Surrey South) |
| 3 | "(including cabinet-level names to be checked before naming)" | placeholder | R | Remove or finish before publishing |
| 4 | Regional table: ridings 46/8/8/5/6/20 | same | C | |
| 4 | All shares 2024 and 2026, all six rows | same, every cell | C | |
| 4 | Seats 2024 and 2026, all six rows | same, every cell | C | |
| 4 | Metro average two-party swing 9.0; all 46 toward CON; range 1.0 to 15.2 | 9.0 (mean of ridings; pooled 9.8); 46 of 46; 1.0 to 15.2 | C | Say "average riding swing" |
| 4 | Green blank in Fraser Valley and Okanagan | Green ran 5 of 6 Okanagan ridings in 2026 (3.1 to 7.0) | R (minor) | Fill in Okanagan or note why blank |
| 5 | Method: two-party share "so that 2024 independents and Green entry or exit do not distort" | Still distorted: West Vancouver-Capilano 13.3 (2024 Ind 20.6%), Richmond-Steveston 12.0 (Ind 10.1%, Green exit), Vernon-Lumby 8.4 (Ind 15.4%, Green entry); Green entry in North Vancouver-Lonsdale 11.8, Surrey South 14.6, Surrey-White Rock 13.2, Delta South 12.6 | R | "reduces, but does not remove" |
| 5 | Quartile table, all 10 rows (cut points, swings, r) | same with rank tie-breaking (as in full.py) | C (10) | Median-age row is tie-sensitive: 7.7 vs 6.0 with value-based quarters |
| 5 | Income r 0.57; 0.62 in 56 same-field; 0.70 in Metro | 0.57, 0.62 (n 56), 0.70 | C (3) | |
| 5 | Income holds with controls: 3.3 per SD, t 4.9 | 3.28, t 4.85 (Metro dummy); 3.51, t 4.82 with all 6 regions | C | "region" here is only a Metro dummy; say so |
| 5 | Immigrant, vis-min, Chinese, education links fade once income held constant | With income alone they do not fade (t 4.1, 3.2, 2.8, 4.1); they fade with income + age + renters + Metro (t 1.7, 0.0, 1.2, 0.6) | R | "fade once income, age and Metro are held constant" |
| 5 | South Asian t 2.3 (1.7 same-field) | 2.26 (1.69) | C | |
| 5 | Renters r -0.54 with two-party CON level | -0.54 | C | |
| 5 | Green change r 0.40 with university | 0.40 (25-64) | C | |
| 5 | High-income ridings: CON gained most | r 0.37 income vs CON change | C | |
| 5 | Men+ share: no robust link | r -0.23; t -0.3 with controls; -1.1 same-field | C | |
| 6 | Group sizes 46 / 47 labelled "Federal 2025 leader" | 42 LPC, 44 CPC, 6 NDP, 1 GPC | **W** | E2 |
| 6 | Row values (-10.7, +5.1, 8.7, 25, 19, 15; -4.3, +4.3, 4.5, 39, 8, 7) | same under "LPC share > CPC share" | C (12) | |
| 6 | r -0.59 (federal Liberal share vs NDP drop) | -0.586 | C | |
| 6 | 15 of 22 flips in Liberal-led ridings | 15 (also true by actual federal winner) | C | |
| 7 | Poll avg 43.84 / 38.87 / 12.00, frozen 03:41 PT | same | C | |
| 7 | Count minus poll +4.21 / -1.49 / -1.03 | same | C | |
| 7 | Metro CON 44.0 polled vs 48.4 | same | C | |
| 7 | Vancouver Island within 2 points for every party | Island (16 ridings): CON 36.8 vs 34.9, NDP 41.5 vs 42.2, GRN 19.9 vs 18.7 | C | Poll file stores Island figures under the "Capital Region" key; label it in the script |
| 7 | Seat estimate 58 / 33 / 2 | same | C | |
| 7 | Right leader 81 of 93 (proportional 83) | 81, 83 | C | |
| 7 | 13 uniform toss-ups went CON 11, NDP 2 | same | C | |
| 8 | 2024: 1,843,088 of 3,609,288 = 51.07% | same | R | These are valid votes, not ballots; and not a like-for-like scope (below) |
| 8 | 2026: 1,792,235 of 3,738,182 = 47.94% | same; Elections BC's own figure is 1,796,615 votes considered = 48.06% | R | Call it valid votes, or use 1,796,615 |
| 8 | Down in 82 of 93; median -3.4; Capital -1.4, FV -5.7, I&N -5.4 | same (on that definition) | C (5) | Only true on the 2024 definition chosen; see below |
| 8 | No link to swing (r -0.10) | +0.17 with two-party swing | **W** | E3 |
| 9 | CentreBC 35 ridings, 4.24% where ran | same | C | |
| 9 | Best Oak Bay-Gordon Head 10.4, Surrey South 10.1; Sturko third, 10.1 | same | C | |
| 9 | Sturko "Leader" | Not in Elections BC data; Research Co. and Pallas call her CentreBC leader | C (secondary) | |
| 9 | OneBC 33 ridings, 4.13%; best KLM 11.4 | same | C | |
| 9 | Brodie 4.0% in Vancouver-Quilchena | 4.04, fifth | C | |
| 9 | Brodie "Interim leader" | Only Wikipedia (non-official) says interim; removed Dec 13 2025, back Dec 21 2025 per house_changes (unverified dates) | U | Say "OneBC leader" (as Research Co. and Pallas do) or source it |
| 9 | CentreBC vote > margin in 4 named; OneBC in 6 named | same lists | C (2) | |
| 9 | Eby "holds" Point Grey 42.97 vs 40.01, 538 | numbers same | R | "leads" (initial count; final count pending) |
| 9 | Doerkson 77.1% | 77.09 | C | |
| 9 | Lowan "wins" SAN 48.5% | 48.48 | R | "leads" |
| 9 | Kealy 14.3% | 14.25, second | C | |
| 10 | 8 close races, leaders and margins | all 8 same | C | |
| 10 | 4 under 1 point; 18 under 5 (22 in 2024) | 4, 18, 22 | C | |
| Caut | Big raw swings in WVC, KOR, PRO, WKP, PCN from 2024 independents | Raw CON change 11 to 20 pts; two-party swing KOR 1.2, PRO 0.8, WKP 3.2 | C | WVC two-party swing is also inflated (13.3); PCN has no NDP candidate in 2026, so its two-party share is 100 |
| Caut | Mail and out-of-district ballots "leaned differently by region" in 2024 | Not tested by region in the files; province-wide they leaned NDP (below) | U | Replace with the province-wide figure |

## Turnout comparability (question 2)

Elections BC's 2026 counting-processes.pdf says the initial count includes **all advance ballots, DEO voting, in-district special voting and ballots at assigned voting places**. Final count holds mail, assisted telephone, out-of-district on Final Voting Day, and in-district voters at a non-assigned place.

The 2024 "election-night comparable" (in-district advance + voting day) is **not a fair comparison**:
- It leaves out 2024 out-of-district advance, DEO and special ballots, which the 2026 initial count includes. Adding them: 1,986,936 = 55.05%. Turnout is then down 7.1 points (median), in all 93 ridings.
- It keeps every 2024 in-district voting-day ballot, but in 2026 voters at a non-assigned place go to final count.
- The 2026 denominator is the Oct 14 list; 2024 uses the list at close of voting, which includes voting-day registrations. This pushes the 2026 rate up.
- The two biases point in opposite directions. The true drop is somewhere between about 3 and 7 points and cannot be pinned down before the final count. Show the range or wait. Do not publish riding-level turnout change as a finding.

## Omissions and misleading points (question 3)

1. **The final count will likely help the NDP.** In 2024, mail + out-of-district + telephone ballots gave CON 42.7% of the two-party vote, against 49.5% in the other ballots. The 2026 final count also holds non-assigned in-district ballots. CON leads of 89 (Ladysmith-Oceanside), 132 (Kelowna Centre), 150 (Cowichan Valley), 387 (Vancouver-Fraserview) and 395 (Surrey City Centre) are at risk. Say so in section 10.
2. **Peace River North**: no NDP candidate in 2026, so two-party share is 100 and it sits in every 93-riding statistic. Leave it out (the results barely change: income t 4.71).
3. **Seven of the 22 flips had Green entry or exit**: Burnaby Centre, Burnaby North, Coquitlam-Burke Mountain (Green entered); Delta North, Richmond-Steveston, Surrey City Centre (Green left); Vernon-Lumby (Green entered). Ladysmith-Oceanside (16.3%) and Vernon-Lumby (15.4%) also had large 2024 independents. Their swings are not clean.
4. **Median age**: r -0.08 alone, but positive and significant once income is held constant (t 3.2; 4.4 in the South Asian spec). The table on its own reads as "age doesn't matter".
5. **Ecological wording** is right in the Cautions, but section 5's "Where the NDP vote went" implies voters moving between parties. Reword: "in ridings with more degree holders the Green share rose most".
6. **Initial-count wording**: "seats", "changed hands", "holds" and "wins" should be "leading" throughout until final count.
