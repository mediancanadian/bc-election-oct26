"""Build the province-wide series 1928-2024 from official summaries.

Sources (all in ../raw/, see manifest.json):
  V1  = Electoral History of BC 1871-1986 (Elections BC), per-election SUMMARY tables and General Election Summary (pp. 2-3)
  V2  = Electoral History of BC 1987-2001 (Elections BC), SUMMARY tables
  V3  = Electoral History of BC Supplement 2002-2013 (Elections BC), SUMMARY tables
  E05 = Errata to 2005 Statement of Votes (Elections BC, 20 Apr 2009)
  T2  = 2013 Statement of Votes, Table 2 (comparison with previous general elections) -> parsed by parse_sov2013_comparison.py
  C17 = Report of the CEO, 2017 PGE (Statement of votes, Summary of results by political party; Statistics at a glance)
  S20 = Statement of Votes 2020 (Table 19 and Table 21 totals)
  S24 = Statement of Votes 2024 (Summary of results by political party; Summary of results by electoral district totals)
  P   = Premiers lists in V1 (pp. 545-547), V2 (p. 83), V3 (p. 124) and Hansard index pages (lims.leg.bc.ca) for 2013-2024

Party lines were transcribed by hand from the OCR text of the summaries (OCR artefacts such as footnote digits glued to numbers
were removed; see results.md). Every election is checked: party votes sum to the printed total, seats sum to the house size,
and printed percentages match votes/total within rounding.
Usage: python3 -I build_province_series.py <t2_csv> <out_dir>
"""
import sys, csv, os

t2_csv, outdir = sys.argv[1], sys.argv[2]

# family codes: CON = Conservative / PC / BC Conservative and Conservative-labelled factions; LIB = Liberal (pre-1991 Liberal Party);
# BCLIB = BC Liberal Party 1991-2020 (BC United name adopted 2023; did not run in 2024); SC = Social Credit; COAL = Coalition (Lib+Con);
# LEFT = CCF (1933-1960) / NDP (1963-); GRN = Green; REF = Reform BC; OTH = everything else
E = {}
def el(year, date, src, total, house, cands, lines, final_total=None, notes=''):
    E[year] = dict(date=date, src=src, total=total, house=house, cands=cands, lines=lines, final_total=final_total, notes=notes)

# line = (label, votes, printed_pct, seats, candidates, family [, final_votes, final_pct])
el(1928, '1928-07-18', 'V1 p.159 (PDF p.169)', 361814, 48, 117, [
    ('Conservative Party', 192867, 53.30, 35, 48, 'CON'), ('Independent', 3658, 1.01, 0, 9, 'OTH'),
    ('Independent Conservative', 1064, 0.29, 0, 2, 'CON'), ('Independent Farmer', 128, 0.04, 0, 1, 'OTH'),
    ('Independent Labour', 316, 0.09, 0, 1, 'OTH'), ('Independent Labour Party', 17908, 4.95, 1, 9, 'OTH'),
    ('Independent Liberal', 1001, 0.28, 0, 2, 'LIB'), ('Liberal Party', 144872, 40.04, 12, 45, 'LIB')],
    notes='Multi-member districts (Vancouver City 6, Victoria City 4): votes exceed ballots; shares are of votes. Last Conservative government (Tolmie).')
el(1933, '1933-11-02', 'V1 p.173 (PDF p.183)', 381223, 47, 210, [
    ('Co-operative Commonwealth Federation', 120185, 31.53, 7, 46, 'LEFT'), ('Independent', 29506, 7.74, 2, 29, 'OTH'),
    ('Independent Co-operative Commonwealth Federation', 2266, 0.59, 0, 8, 'OTH'), ('Independent Conservative', 7114, 1.87, 0, 6, 'CON'),
    ('Independent Liberal', 1076, 0.28, 0, 2, 'LIB'), ('Labour/Independent Labour', 2357, 0.62, 1, 4, 'OTH'),
    ('Liberal Party', 159131, 41.74, 34, 47, 'LIB'), ('Non Partisan Independent Group', 38836, 10.19, 2, 30, 'CON'),
    ('Progressive Liberal', 353, 0.09, 0, 1, 'LIB'), ('Socialist Party of Canada', 370, 0.10, 0, 5, 'OTH'),
    ('Unionist Party of British Columbia', 15445, 4.05, 1, 12, 'CON'), ('United Front Party', 4584, 1.20, 0, 20, 'OTH')],
    notes='Conservative Party did not run officially (V1 note 7): Tolmie supporters ran as Unionists, Bowser group as Non-Partisan Independent Group; both counted as CON family. "Independent" (7.74%) also includes some Conservatives running as straight Independents (V1 note 6), not separable. Vancouver Centre and Victoria City polled later (Bowser died).')
el(1937, '1937-06-01', 'V1 p.183 (PDF p.193)', 417929, 48, 186, [
    ('British Columbia Constructive Party', 8086, 1.93, 0, 14, 'OTH'), ('Communist Party of Canada', 567, 0.14, 0, 1, 'OTH'),
    ('Conservative Party', 119521, 28.60, 8, 43, 'CON'), ('Co-operative Commonwealth Federation', 119400, 28.57, 7, 46, 'LEFT'),
    ('Financial Justice Party', 54, 0.01, 0, 1, 'OTH'), ('Independent', 7341, 1.76, 1, 11, 'OTH'), ('Labour', 1787, 0.43, 1, 2, 'OTH'),
    ('Liberal Party', 156074, 37.34, 31, 48, 'LIB'), ('Social Credit League of British Columbia', 4812, 1.15, 0, 18, 'SC'),
    ('Socialist Party of Canada', 287, 0.07, 0, 2, 'OTH')])
el(1941, '1941-10-21', 'V1 p.193 (PDF p.203)', 453893, 48, 156, [
    ('Conservative Party', 140282, 30.91, 12, 43, 'CON'), ('Co-operative Commonwealth Federation', 151440, 33.36, 14, 45, 'LEFT'),
    ('Emancipation Party', 265, 0.06, 0, 1, 'OTH'), ('Independent', 1638, 0.36, 0, 4, 'OTH'), ('Independent Farmer', 388, 0.09, 0, 1, 'OTH'),
    ('Independent Socialist', 56, 0.01, 0, 1, 'OTH'), ('Labour/Independent Labour', 7141, 1.57, 1, 6, 'OTH'),
    ('Liberal Party', 149525, 32.94, 21, 48, 'LIB'), ('Official Conservative', 2161, 0.48, 0, 1, 'CON'),
    ('Religious Political Brotherhood', 105, 0.02, 0, 1, 'OTH'), ('Socialist Labour Party', 683, 0.15, 0, 4, 'OTH'),
    ('Victory Without Debt Party', 209, 0.05, 0, 1, 'OTH')],
    notes='No majority. After the election Liberals and Conservatives formed a Coalition (32 seats per V1 note 2); Pattullo resigned, Hart premier 9 Dec 1941. CCF led the popular vote.')
el(1945, '1945-10-25', 'V1 p.203 (PDF p.213)', 467747, 48, 147, [
    ('Coalition', 261147, 55.83, 37, 47, 'COAL'), ('Co-operative Commonwealth Federation', 175960, 37.62, 10, 48, 'LEFT'),
    ('Democratic Party of Canada', 423, 0.09, 0, 1, 'OTH'), ('Independent', 1532, 0.33, 0, 2, 'OTH'), ('Independent Liberal', 199, 0.04, 0, 1, 'LIB'),
    ('Independent Progressive Conservative', 748, 0.16, 0, 2, 'CON'), ('Labour/Independent Labour', 1289, 0.28, 1, 2, 'OTH'),
    ('Labour Progressive Party', 16479, 3.52, 0, 21, 'OTH'), ("People's Co-operative Commonwealth Federation", 2786, 0.60, 0, 2, 'OTH'),
    ('Progressive Liberal', 61, 0.01, 0, 1, 'LIB'), ('Social Credit (alliance)', 6627, 1.42, 0, 16, 'SC'),
    ('Socialist Labour Party', 285, 0.06, 0, 3, 'OTH'), ('Socialist Party of Canada', 105, 0.02, 0, 1, 'OTH')],
    notes='Liberal-Conservative Coalition ran joint candidates. SOURCE GAP: printed party votes sum to 467,641, printed total 467,747 (106 votes unaccounted in V1 summary); shares computed on the printed total.')
el(1949, '1949-06-15', 'V1 p.213 (PDF p.223)', 698823, 48, 138, [
    ('British Columbia Social Credit League', 3072, 0.44, 0, 9, 'SC'), ('Coalition', 428773, 61.35, 39, 48, 'COAL'),
    ('Co-operative Commonwealth Federation', 245284, 35.10, 7, 48, 'LEFT'), ('Independent', 5163, 0.74, 1, 7, 'OTH'),
    ('[Independent] Conservative', 1241, 0.18, 0, 1, 'CON'), ('Labour (Party)', 1483, 0.21, 1, 1, 'OTH'),
    ('Labour Progressive Party', 1660, 0.24, 0, 2, 'OTH'), ("People's Party (of British Columbia)", 137, 0.02, 0, 1, 'OTH'),
    ("People's Co-operative Commonwealth Federation", 470, 0.07, 0, 1, 'OTH'), ('Social Credit Party', 8464, 1.21, 0, 7, 'SC'),
    ('Socialist Labour Party', 286, 0.04, 0, 1, 'OTH'), ('Union of Electors', 2790, 0.40, 0, 12, 'OTH')])
el(1952, '1952-06-12', 'V1 p.221 (PDF p.231)', 768561, 48, 212, [
    ('Christian Democratic Party', 7176, 0.93, 0, 8, 'OTH', 1318, 0.20),
    ('Co-operative Commonwealth Federation', 236562, 30.78, 18, 48, 'LEFT', 231756, 34.30),
    ('Independent', 1312, 0.17, 0, 5, 'OTH', 0, 0.0), ('Labour (Party)', 1290, 0.16, 1, 1, 'OTH', 1758, 0.26),
    ('Labour Progressive Party', 2514, 0.33, 0, 5, 'OTH', 931, 0.14), ('Labour Representation Committee', 654, 0.09, 0, 1, 'OTH', 0, 0.0),
    ('Liberal Party', 180289, 23.46, 6, 48, 'LIB', 170674, 25.26), ('Progressive Conservative Party', 129439, 16.84, 4, 48, 'CON', 65285, 9.66),
    ('Social Credit (BCSCL)', 209049, 27.20, 19, 47, 'SC', 203932, 30.18), ('Socialist Party of Canada', 276, 0.04, 0, 1, 'OTH', 0, 0.0)],
    final_total=675654,
    notes='Alternative (preferential) vote, first use (V1 note 1; the volume errata page states it was alternative voting, not STV). Shares here are FIRST-COUNT; final-count columns also given. Multi-member districts used separate ballots per seat. Social Credit minority (19/48), Bennett premier 1 Aug 1952.')
el(1953, '1953-06-09', 'V1 p.243 (PDF p.253)', 727839, 48, 229, [
    ('Christian Democratic Party', 5036, 0.69, 0, 14, 'OTH', 752, 0.12),
    ('Co-operative Commonwealth Federation', 224513, 30.85, 14, 47, 'LEFT', 194414, 29.48),
    ('Independent', 1971, 0.27, 0, 7, 'OTH', 0, 0.0), ('Labour (Party)', 1601, 0.22, 1, 1, 'OTH', 1793, 0.27),
    ('Labour Progressive Party', 7496, 1.03, 0, 25, 'OTH', 816, 0.12), ('Liberal Party', 171671, 23.59, 4, 48, 'LIB', 154090, 23.36),
    ('Progressive Conservative Party', 40780, 5.60, 1, 39, 'CON', 7326, 1.11), ('Social Credit (Party)', 274771, 37.75, 28, 48, 'SC', 300372, 45.54)],
    final_total=659563,
    notes='Alternative vote, last use. FIRST-COUNT shares; final-count columns given. General Election Summary (V1 p.2) lists valid votes 659,563 (= final count total); T2 lists 727,839 (= first count).')
el(1956, '1956-09-19', 'V1 p.265 (PDF p.275)', 817397, 52, 199, [
    ('Co-operative Commonwealth Federation', 231511, 28.32, 10, 51, 'LEFT'), ('Independent and other', 3178, 0.39, 0, 7, 'OTH'),
    ('Labour (Party)', 1321, 0.16, 1, 1, 'OTH'), ('Labour Progressive Party', 3381, 0.41, 0, 14, 'OTH'),
    ('Liberal Party', 177922, 21.77, 2, 52, 'LIB'), ('Progressive Conservative Party', 25373, 3.11, 0, 22, 'CON'),
    ('Social Credit (Party)', 374711, 45.84, 39, 52, 'SC')])
el(1960, '1960-09-12', 'V1 p.275 (PDF p.285)', 996404, 52, 230, [
    ('Communist Party of Canada', 5675, 0.57, 0, 19, 'OTH'), ('Co-operative Commonwealth Federation', 326094, 32.73, 16, 52, 'LEFT'),
    ('Independent', 2557, 0.25, 0, 5, 'OTH'), ('Liberal Party of Canada', 208249, 20.90, 4, 50, 'LIB'),
    ('Progressive Conservative Party', 66943, 6.72, 0, 52, 'CON'), ('Social Credit (Party)', 386886, 38.83, 32, 52, 'SC')])
el(1963, '1963-09-30', 'V1 p.285 (PDF p.295)', 967675, 52, 205, [
    ('Communist Party of Canada', 849, 0.09, 0, 4, 'OTH'), ('Independent and other', 290, 0.03, 0, 2, 'OTH'),
    ('Liberal Party', 193363, 19.98, 5, 51, 'LIB'), ('New Democratic Party', 269004, 27.80, 14, 52, 'LEFT'),
    ('Progressive Conservative Party', 109090, 11.27, 0, 44, 'CON'), ('Social Credit (Party)', 395079, 40.83, 33, 52, 'SC')])
el(1966, '1966-09-12', 'V1 p.293 (PDF p.303)', 751876, 55, 178, [
    ('Communist Party of Canada', 1097, 0.14, 0, 6, 'OTH'), ('Independent', 1711, 0.23, 0, 6, 'OTH'),
    ('Liberal Party', 152155, 20.24, 6, 53, 'LIB'), ('New Democratic Party', 252753, 33.62, 16, 55, 'LEFT'),
    ('Progressive Conservative Party', 1409, 0.18, 0, 3, 'CON'), ('Social Credit (Party)', 342751, 45.59, 33, 55, 'SC')])
el(1969, '1969-08-27', 'V1 p.303 (PDF p.313)', 978356, 55, 177, [
    ('Communist Party of Canada', 482, 0.05, 0, 4, 'OTH'), ('Independent and other', 962, 0.10, 0, 7, 'OTH'),
    ('Liberal Party', 186235, 19.03, 5, 55, 'LIB'), ('New Democratic Party', 331813, 33.92, 12, 55, 'LEFT'),
    ('Progressive Conservative Party', 1087, 0.11, 0, 1, 'CON'), ('Social Credit (Party)', 457777, 46.79, 38, 55, 'SC')])
el(1972, '1972-08-30', 'V1 p.311 (PDF p.321)', 1132172, 55, 226, [
    ('Communist Party of Canada', 862, 0.08, 0, 5, 'OTH'), ('Independent', 1184, 0.10, 0, 9, 'OTH'),
    ('Liberal Party', 185640, 16.40, 5, 53, 'LIB'), ('New Democratic Party', 448260, 39.59, 38, 55, 'LEFT'),
    ('Progressive Conservative Party', 143450, 12.67, 2, 49, 'CON'), ('Social Credit (Party)', 352776, 31.16, 10, 55, 'SC')],
    notes='T2 lists 556 candidates for 1972; V1 summary lists 226 (T2 figure appears to be a typo).')
el(1975, '1975-12-11', 'V1 p.321 (PDF p.331)', 1290451, 55, 221, [
    ('Communist Party of Canada', 1441, 0.11, 0, 13, 'OTH'), ('Independent and other', 4816, 0.37, 0, 16, 'OTH'),
    ('Liberal Party', 93379, 7.24, 1, 49, 'LIB'), ('New Democratic Party', 505396, 39.16, 18, 55, 'LEFT'),
    ('North American Labour Party', 141, 0.01, 0, 4, 'OTH'), ('Progressive Conservative Party', 49796, 3.86, 1, 29, 'CON'),
    ('Social Credit Party', 635482, 49.25, 35, 55, 'SC')])
el(1979, '1979-05-10', 'V1 p.331 (PDF p.341)', 1405077, 57, 178, [
    ('Communist', 1394, 0.10, 0, 9, 'OTH'), ('Independent and others', 1296, 0.09, 0, 7, 'OTH'), ('Liberal Party', 6662, 0.47, 0, 5, 'LIB'),
    ('New Democratic Party', 646188, 45.99, 26, 57, 'LEFT'), ('North American Labour Party', 297, 0.02, 0, 4, 'OTH'),
    ('Progressive Conservative Party', 71078, 5.06, 0, 37, 'CON'), ('Social Credit Party', 677607, 48.23, 31, 57, 'SC'),
    ('Western Independence Party', 555, 0.04, 0, 2, 'OTH')])
el(1983, '1983-05-05', 'V1 p.339 (PDF p.349)', 1649533, 57, 224, [
    ('Communist Party of Canada', 837, 0.05, 0, 4, 'OTH'), ('Green Party', 3078, 0.19, 0, 4, 'GRN'), ('Independent', 5225, 0.32, 0, 18, 'OTH'),
    ('Liberal Party', 44442, 2.69, 0, 52, 'LIB'), ('New Democratic Party', 741354, 44.94, 22, 57, 'LEFT'),
    ('Progressive Conservative Party', 19131, 1.16, 0, 12, 'CON'), ('Social Credit Party', 820807, 49.76, 35, 57, 'SC'),
    ('Western Canada Concept', 14185, 0.86, 0, 18, 'OTH'), ('Western National Party', 474, 0.03, 0, 2, 'OTH')])
el(1986, '1986-10-22', 'V1 p.349 (PDF p.359)', 1935453, 69, 237, [
    ('British Columbia Libertarian Party', 341, 0.02, 0, 3, 'OTH'), ('Communist Party of Canada', 722, 0.03, 0, 3, 'OTH'),
    ('Green Party of British Columbia', 4660, 0.24, 0, 9, 'GRN'), ('Independent', 2470, 0.13, 0, 6, 'OTH'),
    ('Liberal Party', 130505, 6.74, 0, 55, 'LIB'), ('Libertas of British Columbia', 1552, 0.08, 0, 1, 'OTH'),
    ('New Democratic Party', 824544, 42.60, 22, 69, 'LEFT'), ('New Republic Party For British Columbia', 245, 0.01, 0, 1, 'OTH'),
    ("People's Front", 1502, 0.08, 0, 8, 'OTH'), ('Progressive Conservative Party', 14074, 0.73, 0, 12, 'CON'),
    ('Social Credit Party', 954516, 49.32, 47, 69, 'SC'), ('Western Canada Concept', 322, 0.02, 0, 1, 'OTH')],
    notes='Last election with multi-member districts (17 two-member districts); valid votes (1,935,453) exceed voters who voted (1,366,193).')
el(1991, '1991-10-17', 'V2 p.4 (PDF p.13)', 1462467, 75, 317, [
    ('B.C. Conservative Party', 426, 0.03, 0, 4, 'CON'), ('B.C. Liberal Party', 486208, 33.25, 17, 71, 'BCLIB'),
    ('Communist League', 92, 0.01, 0, 3, 'OTH'), ('Family Coalition Party', 1310, 0.09, 0, 8, 'OTH'),
    ('Green Go (Green Wing/Rhino)', 93, 0.01, 0, 1, 'OTH'), ('Green Party of British Columbia', 12650, 0.86, 0, 42, 'GRN'),
    ('The Human Race Party', 110, 0.01, 0, 2, 'OTH'), ('Independent', 10281, 0.70, 0, 16, 'OTH'),
    ('Interdependence Party', 62, 0.00, 0, 1, 'OTH'), ('Libertarian', 860, 0.06, 0, 11, 'OTH'),
    ('NDP/New Democratic', 595391, 40.71, 51, 75, 'LEFT'), ('Reform Party of B.C.', 2673, 0.18, 0, 4, 'REF'),
    ('Social Credit', 351660, 24.05, 7, 74, 'SC'), ('Western Canada Concept', 651, 0.04, 0, 5, 'OTH')],
    notes='First election with all single-member districts (75). Interdependence Party printed as .001%.')
el(1996, '1996-05-28', 'V2 p.20 (PDF p.28)', 1582704, 75, 513, [
    ('British Columbia Liberal Party', 661929, 41.82, 33, 75, 'BCLIB'), ('British Columbia Libertarian Party', 2041, 0.13, 0, 17, 'OTH'),
    ('British Columbia Social Credit Party', 6276, 0.40, 0, 38, 'SC'), ('The Family Coalition Party of British Columbia', 4150, 0.26, 0, 14, 'OTH'),
    ('Green Party Political Association of British Columbia', 31511, 1.99, 0, 71, 'GRN'), ('Natural Law Party', 2919, 0.18, 0, 38, 'OTH'),
    ('New Democratic Party of B.C.', 624395, 39.45, 39, 75, 'LEFT'), ('Progressive Democratic Alliance', 90797, 5.74, 1, 66, 'OTH'),
    ('Reform Party of British Columbia', 146734, 9.27, 2, 75, 'REF'), ('Other (incl. Progressive Conservative, 8 candidates)', 11952, 0.76, 0, 44, 'OTH')],
    notes='BC Liberals won the popular vote but NDP won the seats. PC vote is inside "Other" and not separable from the summary.')
el(2001, '2001-05-16', 'V2 p.36 (PDF p.43)', 1591306, 79, 456, [
    ('B.C. Liberal Party', 916888, 57.62, 77, 79, 'BCLIB'), ('British Columbia Marijuana Party', 51206, 3.22, 0, 79, 'OTH'),
    ('Green Party Political Association of British Columbia', 197231, 12.39, 0, 72, 'GRN'),
    ('New Democratic Party of British Columbia', 343156, 21.56, 2, 79, 'LEFT'), ('Unity Party of British Columbia', 51426, 3.23, 0, 56, 'OTH'),
    ('Other Affiliations (incl. BC Conservative Party)', 31399, 1.98, 0, 91, 'OTH')],
    notes='BC Conservative (CP) vote is inside "Other"; from the district file CP = 2,417 votes.')
el(2005, '2005-05-17', 'V3 p.6 (PDF p.17) with E05 corrections', 1762343, 79, 412, [
    ('BC Conservative Party', 9623, 0.55, 0, 7, 'CON'), ('BC Liberal Party', 807118, 45.80, 46, 79, 'BCLIB'),
    ('British Columbia Marijuana Party', 11449, 0.65, 0, 44, 'OTH'), ('DR BC', 14022, 0.80, 0, 32, 'OTH'),
    ('Green Party of BC', 161849, 9.18, 0, 79, 'GRN'), ('New Democratic Party of B.C.', 731783, 41.52, 33, 79, 'LEFT'),
    ('Independent', 16152, 0.92, 0, 23, 'OTH'), ('Other affiliations', 10347, 0.59, 0, 69, 'OTH')],
    notes='E05 (2009) corrected BCM 11,519->11,449, GP 161,842->161,849, NDP 731,719->731,783, Other 10,348->10,347. V3 (2014) still prints the uncorrected figures; the district spreadsheet agrees with E05. Corrected figures used. GP printed pct 9.17 recomputed 9.18.')
el(2009, '2009-05-12', 'V3 p.20 (PDF p.31)', 1640542, 85, 346, [
    ('BC Liberal Party', 751661, 45.82, 49, 85, 'BCLIB'), ('BC NDP', 691564, 42.15, 35, 85, 'LEFT'),
    ('Conservatives', 34451, 2.10, 0, 24, 'CON'), ('Green Party of BC', 134616, 8.21, 0, 85, 'GRN'),
    ('Independent', 17253, 1.05, 1, 15, 'OTH'), ('Other affiliations', 10997, 0.67, 0, 52, 'OTH')],
    notes='T2 lists 345 candidates, V3 346; the 2009 district spreadsheet has 345 candidates.')
el(2013, '2013-05-14', 'V3 p.34 (PDF p.45)', 1802149, 85, 376, [
    ('BC Conservative Party', 85637, 4.75, 0, 56, 'CON'), ('BC Liberal Party', 795274, 44.13, 49, 85, 'BCLIB'),
    ('BC NDP', 715855, 39.72, 34, 85, 'LEFT'), ('Green Party of BC', 146685, 8.14, 1, 61, 'GRN'),
    ('Independent', 42559, 2.36, 1, 35, 'OTH'), ('Other affiliations', 16139, 0.89, 0, 54, 'OTH')],
    notes='GP printed 8.15%, recomputed 8.14%.')
el(2017, '2017-05-09', 'C17 p.74 (Summary of results by political party)', 1974712, 87, 369, [
    ('BC Conservative Party', 10421, 0.53, 0, 10, 'CON'), ('BC Green Party', 332331, 16.83, 3, 83, 'GRN'),
    ('BC Liberal Party', 797194, 40.37, 43, 87, 'BCLIB'), ('BC NDP', 795527, 40.29, 41, 87, 'LEFT'),
    ('Christian Heritage Party of B.C.', 3398, 0.17, 0, 5, 'OTH'), ('Libertarian', 7743, 0.39, 0, 30, 'OTH'),
    ('Independent', 20971, 1.06, 0, 31, 'OTH'), ('Other (12 parties) and no affiliation', 7127, 0.36, 0, 36, 'OTH')],
    notes='Candidate counts per party from the 2017 district spreadsheet (369 on the ballot; C17 reports 371 nominated, 2 withdrew). No party won a majority; BC Liberal government (Clark) continued until 18 Jul 2017, then NDP minority (Horgan) per Hansard index 41st Parl. 1st Sess. C17: "first minority government in more than 60 years".')
el(2020, '2020-10-24', 'S20 Table 19 (report p.89)', 1883632, 87, None, [
    ('BC NDP', 898384, 47.69, 57, None, 'LEFT'), ('BC Liberal Party', 636148, 33.77, 28, None, 'BCLIB'),
    ('BC Green Party', 284151, 15.09, 2, None, 'GRN'), ('Conservative', 35902, 1.91, 0, None, 'CON'),
    ('Libertarian', 8360, 0.44, 0, None, 'OTH'), ('Christian Heritage Party of B.C.', 3895, 0.21, 0, None, 'OTH'),
    ('B.C. Vision', 761, 0.04, 0, None, 'OTH'), ('Communist Party of BC', 786, 0.04, 0, None, 'OTH'),
    ('Rural BC Party', 754, 0.04, 0, None, 'OTH'), ('Wexit BC', 673, 0.04, 0, None, 'OTH'), ('Independent', 13818, 0.73, 0, None, 'OTH')],
    notes='Candidate counts not extracted.')
el(2024, '2024-10-19', 'S24 p.4 (Summary of results by political party)', 2105341, 93, None, [
    ('BC Green Party', 173377, 8.24, 2, None, 'GRN'), ('BC NDP', 944579, 44.87, 47, None, 'LEFT'),
    ('Christian Heritage Party of B.C.', 365, 0.02, 0, None, 'OTH'), ('Communist Party of BC', 639, 0.03, 0, None, 'OTH'),
    ('Conservative Party', 911153, 43.28, 44, None, 'CON'), ('Freedom Party of BC', 1267, 0.06, 0, None, 'OTH'),
    ('Independent', 47117, 2.24, 0, None, 'OTH'), ('Libertarian', 1380, 0.07, 0, None, 'OTH'),
    ('Unaffiliated', 25464, 1.21, 0, None, 'OTH')],
    notes='BC United (formerly BC Liberal) suspended its campaign 28 Aug 2024 and endorsed no candidates; its 31 standing nominees became unaffiliated (CEO 2024 report p.49). Candidate counts not extracted.')

GOV = {  # governing party after the vote, premier(s), source
    1928: ('Conservative', 'Simon Fraser Tolmie (from 21 Aug 1928)', 'P V1 p.546'),
    1933: ('Liberal', 'Thomas Dufferin Pattullo (from 15 Nov 1933)', 'P V1 p.546'),
    1937: ('Liberal', 'T.D. Pattullo', 'P V1 p.546'),
    1941: ('Coalition (Liberal + Conservative), formed after the vote', 'Pattullo to 9 Dec 1941; John Hart (Coalition) from 9 Dec 1941', 'P V1 p.546; V1 1941 note 2'),
    1945: ('Coalition', 'John Hart (to 29 Dec 1947, then Byron Johnson)', 'P V1 p.546'),
    1949: ('Coalition', 'Byron Ingemar Johnson', 'P V1 p.546'),
    1952: ('Social Credit', 'W.A.C. Bennett (from 1 Aug 1952)', 'P V1 p.546'),
    1953: ('Social Credit', 'W.A.C. Bennett', 'P V1 p.546'),
    1956: ('Social Credit', 'W.A.C. Bennett', 'P V1 p.546'), 1960: ('Social Credit', 'W.A.C. Bennett', 'P V1 p.546'),
    1963: ('Social Credit', 'W.A.C. Bennett', 'P V1 p.546'), 1966: ('Social Credit', 'W.A.C. Bennett', 'P V1 p.546'),
    1969: ('Social Credit', 'W.A.C. Bennett', 'P V1 p.546'),
    1972: ('NDP', 'David Barrett (from 15 Sep 1972)', 'P V1 p.547'),
    1975: ('Social Credit', 'William Richards Bennett (from 22 Dec 1975)', 'P V1 p.547'),
    1979: ('Social Credit', 'W.R. Bennett', 'P V1 p.547'), 1983: ('Social Credit', 'W.R. Bennett', 'P V1 p.547'),
    1986: ('Social Credit', 'William Vander Zalm', 'P V1 p.547; V2 p.83'),
    1991: ('NDP', 'Michael Harcourt (from 5 Nov 1991)', 'P V2 p.83'),
    1996: ('NDP', 'Glen Clark', 'P V2 p.83'),
    2001: ('BC Liberal', 'Gordon Campbell (from 5 Jun 2001)', 'P V2 p.83; V3 p.124'),
    2005: ('BC Liberal', 'Gordon Campbell', 'P V3 p.124; Hansard index 38th Parl.'),
    2009: ('BC Liberal', 'Gordon Campbell (to 14 Mar 2011, then Christy Clark)', 'P V3 p.124; Hansard index 39th Parl.'),
    2013: ('BC Liberal', 'Christy Clark', 'Hansard index 40th Parl. 1st Sess.'),
    2017: ('BC Liberal to 18 Jul 2017, then NDP', 'Christy Clark to 18 Jul 2017; John Horgan from 18 Jul 2017', 'Hansard index 41st Parl. 1st Sess.'),
    2020: ('NDP', 'John Horgan (to 18 Nov 2022, then David Eby)', 'Hansard index 42nd Parl. 1st and 3rd Sess.'),
    2024: ('NDP', 'David Eby', 'Hansard index 43rd Parl. 1st Sess.; BC Gov news release 2024PREM0061'),
}
GOV_FAMILY = {1928: 'CON', 1933: 'LIB', 1937: 'LIB', 1941: 'COAL', 1945: 'COAL', 1949: 'COAL', 1972: 'LEFT', 1991: 'LEFT', 1996: 'LEFT',
              2001: 'BCLIB', 2005: 'BCLIB', 2009: 'BCLIB', 2013: 'BCLIB', 2017: 'LEFT', 2020: 'LEFT', 2024: 'LEFT'}

# turnout: V1 General Election Summary (1928-1986) is primary; T2 for 1991-2013; C17/S20/S24 after
t2 = {int(r['year']): r for r in csv.DictReader(open(t2_csv))}
def n(s):
    s = (s or '').replace(',', '').replace('%', '').replace('$', '').strip()
    try: return float(s)
    except ValueError: return None
V1T = {  # year: (registered, voters_who_voted, pct)
    1928: (245240, 174934, 71.33), 1933: (323540, 236415, 73.07), 1937: (372781, 265446, 71.20), 1941: (417839, 303901, 72.73),
    1945: (476222, 298387, 62.66), 1949: (649019, 477999, 73.64), 1952: (793073, 543456, 68.53), 1953: (740006, 522052, 70.55),
    1956: (778587, 509409, 65.43), 1960: (874267, 628031, 71.84), 1963: (873140, 608672, 69.71), 1966: (873927, 596716, 68.28),
    1969: (1152598, 794696, 68.95), 1972: (1343357, 921496, 68.60), 1975: (1559633, 1088001, 69.76), 1979: (1673111, 1155505, 69.06),
    1983: (1768063, 1373018, 77.66), 1986: (1770000, 1366193, 77.19)}
LATE = {2005: (2845284, 1774269, 3049153, 'T2 + E05 (voters who voted corrected to 1,774,269; eligible turnout 58.19%)'),
        2017: (3246647, 1986374, 3441054, 'C17 Statistics at a glance'),
        2020: (3524812, 1898553, None, 'S20 Table 21 total; no eligible-voter estimate found in the 2020 SOV or CEO report'),
        2024: (3609288, 2109658, None, 'S24 p.1 and district summary total; no eligible-voter estimate found in the 2024 SOV or CEO report')}

problems = []
# Printed party lines that do not add to the printed total in the official source (kept as printed, flagged in notes)
KNOWN_SUM_GAPS = {1945: 'Printed party votes sum to 467,641; printed total 467,747 (gap 106). Printed percentages use 467,747. Kept as printed.'}
fam_rows, party_rows = [], []
for y in sorted(E):
    e = E[y]; L = e['lines']
    sv = sum(l[1] for l in L)
    if sv != e['total'] and y not in KNOWN_SUM_GAPS: problems.append(f'{y}: votes sum {sv} != total {e["total"]}')
    ss = sum(l[3] for l in L)
    if ss != e['house']: problems.append(f'{y}: seats sum {ss} != house {e["house"]}')
    for l in L:
        calc = 100 * l[1] / e['total']
        if abs(calc - l[2]) > 0.02: problems.append(f'{y} {l[0]}: printed {l[2]} vs calc {calc:.3f}')
        if len(l) > 6 and e['final_total']:
            cf = 100 * l[6] / e['final_total']
            if abs(cf - l[7]) > 0.02: problems.append(f'{y} {l[0]} final: printed {l[7]} vs calc {cf:.3f}')
    if e['final_total'] and sum(l[6] for l in L) != e['final_total']:
        problems.append(f'{y}: final sum {sum(l[6] for l in L)} != {e["final_total"]}')
    if e['cands'] and all(l[4] is not None for l in L) and sum(l[4] for l in L) != e['cands']:
        problems.append(f'{y}: candidates sum {sum(l[4] for l in L)} != {e["cands"]}')
    for l in L:
        party_rows.append(dict(year=y, election_date=e['date'], party_as_printed=l[0], family=l[5], votes=l[1],
                               vote_share_pct=round(100 * l[1] / e['total'], 2), printed_pct=l[2], seats=l[3],
                               candidates='' if l[4] is None else l[4],
                               final_count_votes=l[6] if len(l) > 6 else '', final_count_share_pct=l[7] if len(l) > 6 else '',
                               source=e['src']))

print('\n'.join(problems) if problems else 'all checks passed')

FAMS = ['CON', 'SC', 'COAL', 'LIB', 'BCLIB', 'LEFT', 'GRN', 'REF', 'OTH']
series = []
for y in sorted(E):
    e = E[y]; L = e['lines']
    fv = {f: sum(l[1] for l in L if l[5] == f) for f in FAMS}
    fs = {f: sum(l[3] for l in L if l[5] == f) for f in FAMS}
    gov, prem, psrc = GOV[y]
    gfam = GOV_FAMILY.get(y, 'SC')
    gseats = fs[gfam] if y != 1941 else 32
    if y == 2017: gseats = fs['LEFT']
    maj = 'majority' if gseats > e['house'] / 2 else 'minority'
    if y == 1941: maj = 'no majority at the vote (Liberal 21/48); Coalition majority (32) formed after'
    if y == 2017: maj = 'minority (no party won a majority; NDP 41/87 governed from 18 Jul 2017)'
    if y in V1T:
        reg, voted, pct = V1T[y]; elig = n(t2[y]['estimated_eligible_voters']) if y in t2 else None; tsrc = 'V1 General Election Summary pp.2-3'
    elif y in LATE:
        reg, voted, elig, tsrc = LATE[y]; pct = round(100 * voted / reg, 2)
    else:
        r = t2[y]; reg, voted, pct, elig = n(r['registered_voters']), n(r['voters_who_voted']), n(r['pct_registered_who_voted']), n(r['estimated_eligible_voters']); tsrc = '2013 SOV Table 2'
    alt = ''
    if y in t2 and y in V1T:
        r = t2[y]
        if (n(r['registered_voters']), n(r['voters_who_voted'])) != (reg, voted) or abs(n(r['pct_registered_who_voted']) - pct) > 0.011:
            alt = f"T2 gives registered {r['registered_voters']}, voted {r['voters_who_voted']}, {r['pct_registered_who_voted']}"
    if y == 1945: alt += '; V1 note: the 1945 percentage appears to omit active service voters'
    if y == 1986: alt += 'registered voters printed as a rounded 1,770,000 in both V1 and T2'
    row = dict(year=y, election_date=e['date'], seats_in_house=e['house'], total_valid_votes=e['total'],
               first_count_note='first-count (alternative vote); final-count total %d' % e['final_total'] if e['final_total'] else '',
               multi_member_districts='yes' if y <= 1986 else 'no')
    for f in FAMS:
        row[f'seats_{f}'] = fs[f]
    for f in FAMS:
        row[f'share_{f}'] = round(100 * fv[f] / e['total'], 2)
    row.update(dict(registered_voters=int(reg), voters_who_voted=int(voted), turnout_pct_registered=round(pct, 2),
                    estimated_eligible_voters='' if not elig else int(elig),
                    turnout_pct_eligible='' if not elig else round(100 * voted / elig, 2),
                    turnout_source=tsrc, turnout_alt_source_note=alt.strip('; '),
                    governing_party_after_vote=gov, premier=prem, governing_seats=gseats, majority_or_minority=maj,
                    premier_source=psrc, party_summary_source=e['src'], notes=e['notes']))
    series.append(row)

os.makedirs(outdir, exist_ok=True)
def write(name, rows):
    with open(os.path.join(outdir, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
write('province_series.csv', series)
write('province_party_detail.csv', party_rows)

# right vs left table
rl = []
for r in series:
    y = r['year']
    core = r['share_CON'] + r['share_SC'] + r['share_COAL'] + r['share_BCLIB']
    broad_extra = r['share_REF']
    if y in (1983, 1986): broad_extra += sum(p['vote_share_pct'] for p in party_rows if p['year'] == y and 'Western Canada Concept' in p['party_as_printed'])
    if y == 2001: broad_extra += sum(p['vote_share_pct'] for p in party_rows if p['year'] == y and 'Unity' in p['party_as_printed'])
    rl.append(dict(year=y, conservative_family_share=r['share_CON'], social_credit_share=r['share_SC'], coalition_share=r['share_COAL'],
                   bc_liberal_share=r['share_BCLIB'], right_core_share=round(core, 2),
                   right_broad_share=round(core + broad_extra, 2), ccf_ndp_share=r['share_LEFT'],
                   left_label='CCF' if y <= 1960 else 'NDP', right_minus_left_pts=round(core - r['share_LEFT'], 2),
                   liberal_pre1991_share=r['share_LIB'], note=('first-count shares' if y in (1952, 1953) else '') +
                   ('; coalition includes Liberals' if y in (1945, 1949) else '') +
                   ('; 1996 PC vote sits in Other' if y == 1996 else '') + ('; 2001 BC Conservative vote (0.15%) sits in Other' if y == 2001 else '')))
write('right_vs_left.csv', rl)
write('turnout_trend.csv', [{k: r[k] for k in ('year', 'election_date', 'registered_voters', 'voters_who_voted', 'turnout_pct_registered',
                                               'estimated_eligible_voters', 'turnout_pct_eligible', 'turnout_source', 'turnout_alt_source_note')} for r in series])
print('wrote', len(series), 'elections')
