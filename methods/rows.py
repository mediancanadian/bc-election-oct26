"""The rows of METHODOLOGY.md's table: every number published on the slides, in slide order, then the site-only numbers.
Read by build_methodology.py, which fills them from data/story.json."""


def build_rows(S, r0, r1, span):
    W, P, L = S['who_pooled'], S['promises'], S['last_con_majority']
    y24 = next(y for y in S['rise']['years'] if y['year'] == 2024)
    y20 = next(y for y in S['rise']['years'] if y['year'] == 2020)
    asof = 'as of October 25, 2026, 1:49 a.m. Pacific'
    res = 'data/candidates_2026_as_of_2026-10-25_0149_PT.csv'
    hist = 'analysis/history/province_series.csv'
    fed = 'analysis/federal25/fed2025_on_ed2023.csv'
    n_con = sum(1 for d in S['switched'] if d['to'] == 'CON')
    G, MS, VS = S['middle_pooled']['LPC'], S['middle_swing'], S['vancouver_suburbs']
    IG = S['income_groups']
    return [
        # cover
        ('Nine years of NDP government', 'July 18, 2017 to October 2026', 'Cover', hist,
         'John Horgan (NDP) became premier on July 18, 2017 (Executive Council lists in the Hansard indexes, as recorded in province_series.csv); the NDP governed until the 2026 election.'),
        ('First Conservative majority since 1928', f"1928: Conservative {L['seats']} of {L['of']} seats ({r1(L['share'])}% of the vote); no Conservative majority in the {L['n_after']} elections from 1933 to 2024",
         'Cover, site', hist,
         'Seats by party after each general election (Electoral History of British Columbia 1871 to 1986; Elections BC Statements of Votes). The 1945 and 1949 majorities belonged to the Liberal-Conservative Coalition (1941 to 1952), in which the Conservatives were the junior partner. 53.3% is the Conservative Party\'s own share (53.6% with Independent Conservatives).'),
        ('Seats by party, 2026', f"Conservative {S['seats']['CON']}, NDP {S['seats']['NDP']}, Green {S['seats']['GRN']} of {S['n_ridings']}",
         'Cover (majority), slide 2 (Conservative 64, NDP 27), site', res, f"Candidate with the most votes in each riding in Elections BC's results files {asof}."),
        # slide 2
        ('Seats by party, 2024', f"NDP {S['seats24']['NDP']}, Conservative {S['seats24']['CON']}, Green {S['seats24']['GRN']}",
         'Slide 2 (Conservative 44, NDP 47), site', hist, 'Certified winners, Elections BC Statement of Votes, 2024 (final count).'),
        ('Margin between the Conservatives and the NDP, 2026', f"Conservative {r1(S['share']['CON'] - S['share']['NDP'])} points over the NDP", 'Slide 2 (line), site', res,
         f'Conservative share of all valid votes minus the NDP share, {asof}.'),
        ('Margin between the NDP and the Conservatives, 2024', f"NDP {r1(y24['NDP'] - y24['CON'])} points over the Conservatives", 'Slide 2 (line), site', hist,
         'NDP share of all valid votes minus the Conservative share; Elections BC Statement of Votes, 2024 (final count).'),
        ('Vote shares, 2024 and 2026', f"2024: NDP {r1(y24['NDP'])}%, Conservative {r1(y24['CON'])}%; 2026: NDP {r1(S['share']['NDP'])}%, Conservative {r1(S['share']['CON'])}%",
         'Slide 2 (chart; also the last two points of the slide 3 chart), site', hist + '; ' + res, f"Party votes over all valid votes; 2026 {asof}."),
        ('Seats needed for a majority', str(S['majority']), 'Slide 2 (foot and dotted lines), site', '', 'Half of 93 ridings, rounded down, plus one.'),
        ('Seats to spare', str(S['seats']['CON'] - S['majority']), 'Slide 2 (foot)', res, f"Conservative seats ({S['seats']['CON']}) minus the {S['majority']} needed for a majority."),
        ('Final count dates', 'November 6 to 10, 2026 (planned)', 'Slide 2 (foot), site', S['next']['source'], 'Elections BC, 2026 Provincial General Election page.'),
        # slide 3
        ('Conservative share in 2020', f"{r0(y20['CON'])}%", 'Slide 3 (headline), site', hist, 'Elections BC Statement of Votes, 2020.'),
        ('Second party by share of the vote, 2020 and 2024', f"2020: BC Liberal {r1(y20['BCLIB'])}% (NDP {r1(y20['NDP'])}%); 2024: Conservative {r1(y24['CON'])}% (NDP {r1(y24['NDP'])}%)",
         'Slide 3 (line), site', hist, 'Party votes over all valid votes; the BC Liberal Party was renamed BC United in 2023 and had no candidates in 2024.'),
        ('Shares by election, 2001 to 2026', '; '.join(f"{d['year']}: BC Liberal {r1(d['BCLIB'])}%, Conservative {r1(d['CON'])}%, NDP {r1(d['NDP'])}%" for d in S['rise_long']),
         'Slide 3 (chart), site', hist + '; analysis/history/districts_2001_2017.csv',
         f"Elections BC Statements of Votes and the Electoral History of British Columbia. The 2001 Conservative share is from Elections BC's 2001 results by district (2,417 votes), since the series counts it under Other. 2026 {asof}."),
        ('Ridings the BC Liberals would have held in 2020 that elected a Conservative in 2026', f"{S['rise']['lib_ridings_2020_con_lead']} of {S['rise']['lib_ridings_2020']}",
         'Site', 'analysis/results24/out/transposed_2020_on_2023_eds.csv',
         '2020 results moved onto the 2023 ridings by voting area, weighted by 2024 registered voters; the party first in 2020 on the new map compared with the party elected in 2026. West Vancouver-Sea to Sky, where the BC Liberals finished first in 2020 on the old map by 0.2 points, has a Green plurality once moved onto the new map (Green 38.2%, BC Liberal 36.1%), and elected a Green in 2026.'),
        # slide 4
        ('Suburban ridings that elected a Conservative', f"{VS['con26']} of {VS['n']} (2024: {VS['con24']})", 'Slide 4 (line), site', 'data/ridings.csv',
         f'Metro Vancouver ridings outside the City of Vancouver (names that do not start with "Vancouver-"); the party elected in 2026 ({asof}) and the 2024 certified winner.'),
        ('Surrey ridings that elected a Conservative', f"{S['surrey']['con26']} of {S['surrey']['n']} (2024: {S['surrey']['con24']})", 'Slide 4 (foot), site', 'data/ridings.csv',
         f'Ridings whose names begin with Surrey; the party elected in 2026 ({asof}) and the 2024 certified winner.'),
        ('Ridings that changed party', f"{S['n_switched']}: {n_con} to the Conservatives and {S['n_switched'] - n_con} to the NDP; {S['n_switched_metro']} in Metro Vancouver, "
         f"{sum(1 for d in S['switched'] if d['region'] != 'Metro Vancouver' and d['to'] == 'CON')} more to the Conservatives elsewhere", 'Slide 2 (ringed seats), slide 4 (map and foot), site', 'data/ridings.csv',
         'The party elected in 2026 compared with the 2024 certified winner.'),
        ('Swing: suburbs against active cores and rural ridings', f"{r1(S['suburb_swing'])} against {r1(S['core_rural_swing'])} points", 'Site',
         'analysis/core/meta/place_types.csv', 'Change in the Conservative share of the Conservative and NDP vote, 2024 to 2026, averaged over ridings of each place type (commuting method of the Canadian Suburbs project, Queen\'s University, applied to whole ridings with the density test first); Peace River North left out.'),
        # slide 5
        ('Swing by riding income', f"{', '.join(r1(g['swing']) for g in IG[:3])} and {r1(IG[3]['swing'])} points; typical riding incomes "
         f"{', '.join('$' + r0(g['income'] / 1000) + 'k' for g in IG[:3])} and ${r0(IG[3]['income'] / 1000)}k", 'Slide 5 (bars for the groups, a dot for each riding), site', 'data/ridings.csv',
         f"Ridings ranked by median household income (2020 incomes, 2021 Census) and cut into four groups of {IG[0]['n']}, with Peace River North (no NDP candidate) left out; each group's swing is the average change in the Conservative share of the Conservative and NDP vote, 2024 to 2026, and its income is the median of its ridings' medians."),
        ('Link between riding income and swing', f"r = {S['income_r']} ({sum(g['n'] for g in IG)} ridings)", 'Site', 'data/ridings.csv',
         'Pearson correlation of median household income with the swing across ridings; Peace River North left out.'),
        ('Visible minorities, owners, car commuters: ridings that switched to the Conservatives against ridings that stayed NDP',
         f"visible minorities {r0(W['switched']['vismin'])}% against {r0(W['stayed_ndp']['vismin'])}% ({r1(W['switched']['vismin'])} and {r1(W['stayed_ndp']['vismin'])}); own {r0(W['switched']['own'])}% against {r0(W['stayed_ndp']['own'])}%; "
         f"to work by car {r0(W['switched']['drive'])}% against {r0(W['stayed_ndp']['drive'])}%", 'Site', 'data/ridings.csv',
         '2021 Census counts summed over each group of ridings, each over its own universe: owner and renter households for owners (band housing left out); commuters for travel to work by car (driver or passenger); population in private households for visible minorities. The 21 ridings that changed to the Conservatives; Courtenay-Comox, which changed to the NDP, and the two ridings that elected Greens both years are left out.'),
        ('Median household income, typical riding, switched against stayed NDP', f"${r0(W['switched']['income'] / 1000)}k against ${r0(W['stayed_ndp']['income'] / 1000)}k", 'Site', 'data/ridings.csv',
         'Median of the riding medians (2020 incomes, 2021 Census) in each group.'),
        # slide 6
        ('Provincial vote and seats in the ridings where the Liberals came first federally',
         f"{G['n']} ridings. Vote: NDP {r1(G['y2024']['NDP'])}% to {r1(G['y2026']['NDP'])}%, Conservative {r1(G['y2024']['CON'])}% to {r1(G['y2026']['CON'])}%, Green {r1(G['y2024']['GRN'])}% to {r1(G['y2026']['GRN'])}%. "
         f"Seats: Conservative {G['seats24']['CON']} to {G['seats26']['CON']}, NDP {G['seats24']['NDP']} to {G['seats26']['NDP']}, Green {G['seats24']['GRN']} to {G['seats26']['GRN']}",
         'Slide 6 (chart, note and foot), site', 'analysis/results24/out/districts_2024.csv; ' + res + '; ' + fed,
         f'Party votes over all valid votes, summed over the provincial ridings where the Liberals had the most votes in the April 28, 2025 federal election. Federal votes are allocated to provincial ridings by 2021 block population, so the grouping is an estimate: five ridings are within 0.5 point (Kelowna-Mission, Liberal by 0.01 point or 5 votes, is in the group; without it the 41 ridings go NDP 50.4% to 39.6% and Conservative 38.8% to 44.3%). 2024: final count; 2026: {asof}.'),
        ('Conservative seats added, and how many were in ridings where the Liberals came first federally',
         f"{S['seats']['CON'] - S['seats24']['CON']} more than in 2024 ({S['seats24']['CON']} to {S['seats']['CON']}); {G['seats26']['CON'] - G['seats24']['CON']} of them in the {G['n']} ridings where the Liberals came first federally: three of every four",
         'Slide 6 (line), site', 'data/ridings.csv', 'Net change in Conservative seats (21 gained, Courtenay-Comox to the NDP), 2024 certified winners against the members elected in 2026; the federal group is the party with the most votes in the April 28, 2025 federal election.'),
        ('Ridings that changed to the Conservatives where the Liberals came first federally', f"{S['middle_flows']['LPC']['NDP>CON']} of {n_con}", 'Site', fed,
         'The 2025 federal party with the most votes in each riding that changed from NDP to Conservative.'),
        ('Provincial seats by 2025 federal group', '; '.join(f"{lab} first federally ({S['middle'][g]['n']}): Conservative {S['middle'][g]['y2024']['CON']} to {S['middle'][g]['y2026']['CON']}, NDP {S['middle'][g]['y2024']['NDP']} to {S['middle'][g]['y2026']['NDP']}"
                                                              for g, lab in (('LPC', 'Liberals'), ('CPC', 'Conservatives'), ('NDP', 'NDP'))) + '; Green first federally (1): Green both years',
         'Site', fed, 'Elections Canada 2025 poll-by-poll votes allocated to provincial ridings by 2021 block population; the party with the most votes in each riding\'s area.'),
        ('Swing toward the Conservatives by 2025 federal group', f"Liberals first federally {r1(MS['LPC'])} points; Conservatives first {r1(MS['CPC'])}; NDP first ({S['middle']['NDP']['n']} ridings) {r1(MS['NDP'])}; "
         f"Saanich North and the Islands (Green first) {r1(MS['GPC'])}", 'Site', fed,
         'Average over ridings of the change in the Conservative share of the Conservative and NDP vote, 2024 to 2026; Peace River North left out.'),
        # slide 7
        ('Top worries', '; '.join(f"{i['issue']} {i['pct']}%" for i in S['why']['issues']), 'Slide 7 (and the order of slide 8), site', S['why']['issues_source']['url'],
         f"{S['why']['issues_source']['pollster']}, {span(S['why']['issues_source']['field'])}; B.C. adults, up to three answers."),
        ('Party rated best on each worry', '; '.join(f"{i['issue']}: " + ', '.join(f"{ {'CON': 'Conservative', 'NDP': 'NDP'}[k]} {v}%" for k, v in i['best'].items()) + (' (about even)' if i['lead'] == 'even' else '')
                                                for i in S['why']['issues']), 'Slide 7 (numbers for cost of living only), site', S['why']['best_source']['url'],
         f"{S['why']['best_source']['pollster']}, {span(S['why']['best_source']['field'])}, weighted sample of {S['why']['best_source']['n']:,}. A party is shown as rated best only when its margin is larger than the 95% margin of error that a probability sample of the same size would have on the gap between two shares (" + ', '.join(f"{i['issue'].lower()} {i['moe']} points" for i in S['why']['issues']) + "); smaller gaps are shown as about even. The pollster notes that a margin of error cannot be calculated for its online panel."),
        # slide 8
        ('Platform promises', '; '.join(i['short'] for b in P for i in b['items']), 'Slide 8 (the first promise for each worry), site', S['platform']['url'],
         'Quoted or summarised from the platform, with page numbers on the site; the pledge not to raise taxes is from the party\'s plan page.'),
        # site only
        ('Votes and seats', '; '.join(f"{p} {r1(v['votes'])}% of votes, {r1(v['seats'])}% of seats" for p, v in S['votes_seats'].items()), 'Site', 'data/ridings.csv', 'Seats over 93.'),
        ('Ridings decided by 150 votes or fewer', str(S['n_within_150']), 'Site', 'data/ridings.csv', f'Margin of the first candidate over the second, {asof}.'),
        ('Voters switching that would remove the majority', f"{S['tipping']['voters']:,} in {S['tipping']['seats_to_lose']} ridings", 'Site', 'data/ridings.csv',
         'Half of each margin plus one, summed over the narrowest Conservative seats until the party falls below 47.'),
    ]
