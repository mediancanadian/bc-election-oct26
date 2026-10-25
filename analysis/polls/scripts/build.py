# Build polls.csv, campaign list and final-week average from figures transcribed
# out of each pollster's own release (file paths in the 'source_file' field).
# Run: python3 -I scripts/build.py   (from analysis/polls)
import csv, json, datetime, statistics

COLS = ["pollster", "field_start", "field_end", "release_date", "sample_size", "mode",
        "population", "NDP", "Conservative", "Green", "CentreBC", "OneBC", "other",
        "undecided_share", "regional_splits", "gender_splits", "age_splits",
        "leader_approval_or_best_premier", "top_issues", "seat_projection",
        "release_status", "source_url", "source_file", "notes"]

P = []  # opened releases
def add(**k):
    row = {c: "" for c in COLS}
    row.update(k)
    row.setdefault("release_status", "opened")
    row["release_status"] = row["release_status"] or "opened"
    P.append(row)

# ---------------- 2025 ----------------
add(pollster="Leger", field_start="2025-01-24", field_end="2025-01-26", release_date="2025-02-05",
    sample_size="1001 (decided 855 weighted)", mode="online panel", population="decided voters",
    NDP=44, Conservative=42, Green=10, other=4,
    gender_splits="Men: NDP 37 CPC 46 GRN 13; Women: NDP 51 CPC 38 GRN 7",
    age_splits="18-34: NDP 37 CPC 42 GRN 16; 35-54: NDP 36 CPC 51; 55+: NDP 53 CPC 36",
    leader_approval_or_best_premier="Eby approval 49%",
    source_url="https://leger360.com/wp-content/uploads/2025/02/Media-Report-BC-Government-Report-Card-February-5-2025.pdf",
    source_file="raw/leger/media_report_bc_government_report_card_february_5_2025.pdf",
    notes="Figures read from release charts (pages 6-7).")
add(pollster="Pallas Data", field_start="2025-02-15", field_end="2025-02-15", release_date="2025-02-18",
    sample_size="677 (decided+leaning 648)", mode="IVR", population="decided + leaning",
    NDP=48.8, Conservative=40.7, Green=7.6, other=2.9, undecided_share="8.8 (all voters); 4.2 after leaners",
    regional_splits="Metro Vancouver: NDP 56.2 CPC 34.3 GRN 5.8; Vancouver Island: NDP 45.3 CPC 39.9 GRN 12.4; Rest of BC: NDP 40.6 CPC 49.4 GRN 8.0",
    gender_splits="Male: NDP 38.8 CPC 52.1; Female: NDP 58.4 CPC 29.7",
    age_splits="18-34: NDP 50.5 CPC 39.3; 35-49: 40.2/50.5; 50-64: 50.1/39.3; 65+: 54.0/34.0 (NDP/CPC)",
    source_url="https://files.constantcontact.com/f737aa99901/1dd1cfd4-cd65-4515-aec0-27599a26da58.pdf",
    source_file="raw/pallas_data/1dd1cfd4_cd65_4515_aec0_27599a26da58.pdf")
add(pollster="Research Co.", field_start="2025-03-03", field_end="2025-03-05", release_date="2025-03-11",
    sample_size="802", mode="online panel", population="decided voters",
    NDP=44, Conservative=42, Green=11, other=3,
    regional_splits="Metro Vancouver: NDP 44 CPC 44; Vancouver Island: NDP 50 CPC 31; Southern BC: NDP 49 CPC 47; Fraser Valley: CPC 47 NDP 34; Northern BC: CPC 44 NDP 39",
    age_splits="55+: NDP 54; 35-49: CPC 49 (release text only)",
    top_issues="Housing/poverty/homelessness 36; health care 21; economy/jobs 20; crime 6",
    source_url="https://researchco.ca/2025/03/11/bcpoli-3/", source_file="raw/research_co/bcpoli_3.html",
    notes="Data tables PDF blocked (HTTP 429); figures from release page.")
add(pollster="Liaison Strategies", field_start="2025-05-02", field_end="2025-05-04", release_date="2025-05-07",
    sample_size="800", mode="IVR", population="decided voters",
    NDP=45, Conservative=47, Green=7, other="",
    regional_splits="Metro Vancouver: NDP 49 CPC 46; Vancouver Island: NDP 44 CPC 34 GRN 19",
    leader_approval_or_best_premier="Net favourability: Eby +11, Furstenau +13, Rustad -9; Eby favourable 50%",
    source_url="https://press.liaisonstrategies.ca/bc-conservatives-lead-ndp-47-to-45/",
    source_file="raw/liaison_strategies/bc_conservatives_lead_ndp_47_to_45.html",
    notes="Commissioned by National Ethnic Press and Media Council of Canada (NEPMCC). Other share not stated in release text; tables PDF raw/liaison_strategies/LS-BC-2025---May-2.pdf saved.")
add(pollster="Leger", field_start="2025-05-23", field_end="2025-05-25", release_date="2025-06-12",
    sample_size="1032 (decided 866 weighted)", mode="online panel", population="decided voters",
    NDP=45, Conservative=39, Green=11, other=5,
    gender_splits="Men: NDP 41 CPC 41 GRN 12; Women: NDP 49 CPC 37 GRN 10",
    age_splits="18-34: NDP 38 CPC 45 GRN 16; 35-54: NDP 42 CPC 41; 55+: NDP 50 CPC 35",
    leader_approval_or_best_premier="Eby approval 51%",
    source_url="https://leger360.com/wp-content/uploads/2025/06/BC-Gov-Report-Card-June-2025.pdf",
    source_file="raw/leger/bc_gov_report_card_june_2025.pdf",
    notes="Eligible voters sample. Figures read from release charts (pages 6-7).")
add(pollster="Research Co.", field_start="2025-06-07", field_end="2025-06-09", release_date="2025-06-16",
    sample_size="803", mode="online panel", population="decided voters",
    NDP=43, Conservative=42, Green=8, CentreBC=2, other="1 (prospective Brodie/Kealy/Armstrong party)",
    regional_splits="Metro Vancouver: NDP 47 CPC 41; Vancouver Island: NDP 43 CPC 34; Fraser Valley: CPC 53 NDP 34; Northern BC: CPC 52 NDP 29; Southern BC: 43/43",
    age_splits="55+: NDP 53; 18-34: CPC 49; 35-54: CPC 44 NDP 43",
    leader_approval_or_best_premier="Approval: Eby 56, Rustad 37",
    top_issues="Housing/poverty/homelessness 34; economy/jobs 22; health care 21",
    source_url="https://researchco.ca/2025/06/16/bcpoli-4/", source_file="raw/research_co/bcpoli_4.html",
    notes="Fielded before OneBC formed (June 14).")
add(pollster="Mainstreet Research", field_start="2025-06-23", field_end="2025-06-24", release_date="2025-06-25",
    sample_size="943", mode="IVR (Smart IVR + text)", population="decided voters",
    NDP=41, Conservative=44, Green=7, other=8, undecided_share="14 (all voters chart)",
    source_url="https://cdn.prod.website-files.com/66c8dfb086a015b3b519e988/685c59c0dc441ffa6e3e5211_Mainstreet_BC_June_2025_Public.pdf",
    source_file="raw/mainstreet_research/685c59c0dc441ffa6e3e5211_mainstreet_bc_june_2025_public.pdf",
    notes="Figures read from release chart (page 7). Public PDF leaves crosstab cells blank.")
add(pollster="Angus Reid Institute", field_start="2025-08-28", field_end="2025-09-05", release_date="2025-09-11",
    sample_size="BC decided n=695 (national survey n=4,330)", mode="online panel", population="decided + leaning",
    NDP=42, Conservative=44, Green=10, other=4,
    gender_splits="Male: CPC 51 NDP 37; Female: CPC 37 NDP 47",
    age_splits="18-34: CPC 31 NDP 55; 35-54: CPC 51 NDP 34",
    source_url="https://angusreid.org/cross-canada-outlook-sept-25-british-columbia/",
    source_file="raw/angus_reid/2025.09.11_Cross_canada_Press_release_tables.pdf",
    notes="Part of Cross-Canada Outlook.")
add(pollster="Research Co.", field_start="2025-10-01", field_end="2025-10-03", release_date="2025-10-06",
    sample_size="801", mode="online panel", population="decided voters",
    NDP=44, Conservative=38, Green=12, CentreBC=3, OneBC=1, other=1,
    regional_splits="CPC leads Northern BC 52 and Fraser Valley 52; NDP leads Vancouver Island 51, Southern BC 50, Metro Vancouver 44 (leader share only)",
    age_splits="55+: NDP 54 CPC 35; 35-54: CPC 40 NDP 38; 18-34: 40/40",
    leader_approval_or_best_premier="Best premier: Eby 37, Rustad 21, Lowan 12, Kirkpatrick 4, Brodie 2; Eby approval 53",
    top_issues="Housing/poverty/homelessness 30; economy/jobs 23; health care 23",
    source_url="https://researchco.ca/wp-content/uploads/2025/10/Tables_Politics_BC_06Oct2025.pdf",
    source_file="raw/research_co/Tables_Politics_BC_06Oct2025.pdf")
add(pollster="Leger", field_start="2025-10-10", field_end="2025-10-12", release_date="2025-10-29",
    sample_size="1035 (decided 851 weighted)", mode="online panel", population="decided voters",
    NDP=48, Conservative=38, Green=8, other=7,
    gender_splits="Men: NDP 43 CPC 42; Women: NDP 52 CPC 33",
    age_splits="18-34: NDP 47 CPC 35; 35-54: NDP 44 CPC 41; 55+: NDP 51 CPC 37",
    source_url="https://leger360.com/wp-content/uploads/2025/10/Media-Release-BC-Gov-Report-Card-Oct-2025.pdf",
    source_file="raw/leger/media_release_bc_gov_report_card_oct_2025.pdf",
    notes="Eligible voters sample (Leger cautions on comparisons). Read from chart page 16.")
add(pollster="Abacus Data", field_start="2025-10-09", field_end="2025-10-15", release_date="2025-10",
    sample_size="1000", mode="online panel", population="committed (decided) voters",
    NDP=47, Conservative=40, Green=8, CentreBC=3, OneBC=1, undecided_share="26",
    regional_splits="Metro Vancouver: NDP 50 CPC 41; Outside Lower Mainland: NDP 41 CPC 37",
    age_splits="65+ (seniors): NDP 53; under 30: NDP 43; 30-44: CPC 47",
    leader_approval_or_best_premier="Government approval 40, disapprove 31",
    source_url="https://abacusdata.ca/abacus-data-bc-poll-eby-government-holds-the-edge-a-year-after-the-provincial-election/",
    source_file="raw/abacus_data/_data_bc_poll_eby_government_holds_the_edge_a_year_after_the_provincial_election.html")
add(pollster="Angus Reid Institute", field_start="2025-10-23", field_end="2025-10-25", release_date="2025-10-26",
    sample_size="1044 (decided 819)", mode="online panel", population="decided + leaning",
    NDP=40, Conservative=41, Green=11, OneBC=5, CentreBC=1, other=1,
    regional_splits="Metro Van: NDP 49 CPC 33; Fraser Valley: NDP 40 CPC 46; Island/North Coast: NDP 38 CPC 36 GRN 22; Interior: NDP 28 CPC 55",
    gender_splits="Male: NDP 35 CPC 46; Female: NDP 45 CPC 37",
    age_splits="18-34: NDP 43 CPC 36; 35-54: NDP 31 CPC 49; 55+: NDP 45 CPC 39",
    source_url="https://angusreid.org/wp-content/uploads/2025/10/2025.10.26_BC_Rustad_tables.pdf",
    source_file="raw/angus_reid/2025.10.26_BC_Rustad_tables.pdf")
add(pollster="Yorkville Strategies", field_start="2025-11-24", field_end="2025-11-25", release_date="2025-11-26",
    sample_size="600", mode="IVR", population="not stated",
    NDP=40, Conservative=42, Green=8, OneBC=5, other=4,
    source_url="https://x.com/DPinBC/status/1993828038497403065",
    source_file="raw/yorkville_strategies/1993828038497403065.html",
    notes="Published only as an X post by Yorkville principal Dimitri Pantazopoulos; no PDF release.")
add(pollster="Angus Reid Institute", field_start="2025-11-26", field_end="2025-12-01", release_date="2025-12-18",
    sample_size="BC decided n=463", mode="online panel", population="decided + leaning",
    NDP=43, Conservative=40, Green=11, other=8,
    gender_splits="Male: CPC 42 NDP 42; Female: CPC 38 NDP 44",
    age_splits="18-34: CPC 25 NDP 56",
    source_url="https://angusreid.org/wp-content/uploads/2025/12/2025.12.16_provincial_outlook_PR_TABLES.pdf",
    source_file="raw/angus_reid/2025.12.16_provincial_outlook_PR_TABLES.pdf",
    notes="Collected before Rustad's removal (Dec 3-4).")
add(pollster="Pallas Data", field_start="2025-12-11", field_end="2025-12-13", release_date="2025-12-17",
    sample_size="923", mode="IVR", population="decided voters",
    NDP=44, Conservative=39, Green=9, OneBC=7,
    regional_splits="Metro Vancouver: NDP 49 CPC 32; Vancouver Island: NDP 43 CPC 27; Rest of BC: CPC 48 NDP 36",
    gender_splits="Women: NDP 52 CPC 33; Men: NDP 36 CPC 45",
    age_splits="50-64: CPC 44 NDP 38; 65+: NDP 50 CPC 34",
    source_url="https://pallas-data.ca/2025/12/22/pallas-british-columbia-poll-ndp-44-conservative-39-greens-9-onebc-7/",
    source_file="raw/pallas_data/pallas_british_columbia_poll_ndp_44_conservative_39_greens_9_onebc_7.html",
    notes="Commissioned by the Pacific Conservative Foundation.")
add(pollster="Mainstreet Research", field_start="2025-12-17", field_end="2025-12-18", release_date="2025-12-22",
    sample_size="1902", mode="IVR (Smart IVR)", population="all voters incl. leaners and undecided",
    NDP=34, Conservative=34, Green=8, OneBC=6, undecided_share="18",
    source_url="https://cdn.prod.website-files.com/66c8dfb086a015b3b519e988/69497c7df02eea7fc8befc0c_Mainstreet_BC_Con_Leadership_Dec_2025_Public.pdf",
    source_file="raw/mainstreet_research/69497c7df02eea7fc8befc0c_mainstreet_bc_con_leadership_dec_2025_public.pdf",
    notes="Release shows only all-voter chart (incl. 18% undecided). Excluding undecided gives about 41/41/10/7, which is what Wikipedia lists; that decided figure is derived, not printed by Mainstreet. Crosstab cells blank in public PDF.")

# ---------------- 2026 pre-campaign ----------------
add(pollster="Leger", field_start="2026-01-23", field_end="2026-01-26", release_date="2026-02-03",
    sample_size="1003 (decided 819 weighted)", mode="online panel", population="decided voters",
    NDP=44, Conservative=38, Green=9, OneBC=6, other=3,
    gender_splits="Men: NDP 43 CPC 39; Women: NDP 45 CPC 36",
    age_splits="18-34: NDP 46 CPC 33; 35-54: NDP 41 CPC 45; 55+: NDP 45 CPC 36",
    source_url="https://leger360.com/wp-content/uploads/2026/02/LEGER_BCGovReportCard_Jan2026.pdf",
    source_file="raw/leger/leger_bcgovreportcard_jan2026.pdf")
add(pollster="Pallas Data", field_start="2026-02-12", field_end="2026-02-14", release_date="2026-02-19",
    sample_size="988", mode="IVR", population="decided + leaning",
    NDP=42, Conservative=37, Green=13, OneBC=6,
    regional_splits="Metro Vancouver: NDP 42 CPC 33; Vancouver Island: NDP 49 CPC 28; Rest of BC: CPC 46 NDP 39",
    gender_splits="Women: NDP 49 CPC 31; Men: CPC 43 NDP 35",
    age_splits="18-34: NDP 37 CPC 40; 65+: NDP 50 CPC 36",
    source_url="https://pallas-data.ca/2026/02/19/pallas-british-columbia-poll-ndp-42-conservative-37-green-13/",
    source_file="raw/pallas_data/pallas_british_columbia_poll_ndp_42_conservative_37_green_13.html",
    notes="Release headline says OneBC 6%, body text says 7% (+1). Headline value used.")
add(pollster="Pallas Data", field_start="2026-02-12", field_end="2026-02-27", release_date="2026-03-02",
    sample_size="1256 (decided+leaning 1148)", mode="IVR", population="decided + leaning",
    NDP=41.6, Conservative=40.2, Green=11.2, OneBC=5.4, other=1.5, undecided_share="16.9 (all); 8.1 after leaners",
    regional_splits="Metro Vancouver: NDP 44.5 CPC 38.2 GRN 13.3; Vancouver Island: NDP 46.9 CPC 29.5 GRN 15.1 OneBC 8.5; Rest of BC: NDP 35.1 CPC 48.2",
    gender_splits="Male: NDP 36.8 CPC 43.8; Female: NDP 46.2 CPC 36.8",
    age_splits="18-34: 41.4/41.7; 35-49: 36.6/41.8; 50-64: 42.6/38.1; 65+: 45.9/39.1 (NDP/CPC)",
    source_url="https://files.constantcontact.com/f737aa99901/13d6b1a7-0809-454a-a8fe-f71830064bed.pdf",
    source_file="raw/pallas_data/13d6b1a7_0809_454a_a8fe_f71830064bed.pdf",
    notes="Overlaps the Feb 12-14 field period (appears to extend it).")
add(pollster="Mainstreet Research", field_start="2026-03-11", field_end="2026-03-13", release_date="2026-03-16",
    sample_size="1054", mode="IVR (Smart IVR)", population="decided + leaners (residual undecided 6.2% retained)",
    NDP=36.2, Conservative=34.6, Green=10.9, other=12.2, undecided_share="17.4 (all); 6.2 after leaners",
    seat_projection="Mainstreet scenario model by Conservative leader: Halford NDP 59 / CPC 32 / GRN 2; Elliott 45/46/2; Milobar 38/53/2; Black 45/46/2; Findlay 45/46/2",
    source_url="https://cdn.prod.website-files.com/66c8dfb086a015b3b519e988/69b8b3ba2cbf41965308eea3_BC_Mainstreet_March2026_public_Final.pdf",
    source_file="raw/mainstreet_research/69b8b3ba2cbf41965308eea3_bc_mainstreet_march2026_public_final.pdf",
    notes="Wikipedia's 39/37/12/13 is a renormalised version; Mainstreet prints these values with undecided retained.")
add(pollster="Angus Reid Institute", field_start="2026-03-11", field_end="2026-03-17", release_date="2026-04-01",
    sample_size="499 (decided+leaning 412)", mode="online panel", population="decided + leaning",
    NDP=42, Conservative=44, Green=9, other=7,
    regional_splits="Metro Van: NDP 45 CPC 41; LF/MV (Fraser Valley): NDP 37 CPC 48; Island/North Coast: NDP 42 CPC 41; BC Interior: NDP 38 CPC 51",
    gender_splits="Male: NDP 35 CPC 50; Female: NDP 49 CPC 38",
    age_splits="18-34: NDP 41 CPC 41; 35-54: NDP 34 CPC 51; 55+: NDP 48 CPC 42",
    source_url="https://angusreid.org/wp-content/uploads/2026/03/2026.04.01_BC_tables.pdf",
    source_file="raw/angus_reid/2026.04.01_BC_tables.pdf")
add(pollster="Leger", field_start="2026-04-03", field_end="2026-04-06", release_date="2026-04-10",
    sample_size="1003 (decided 779 weighted)", mode="online panel", population="decided voters",
    NDP=44, Conservative=40, Green=10, OneBC=3, other=4, undecided_share="14",
    regional_splits="Metro Van: NDP 49 CPC 38 GRN 8; Van Isle: NDP 40 CPC 36 GRN 14; Rest of BC: NDP 35 CPC 47 GRN 10",
    gender_splits="Men: NDP 41 CPC 43; Women: NDP 46 CPC 37",
    age_splits="18-34: NDP 43 CPC 36; 35-54: NDP 42 CPC 47; 55+: NDP 45 CPC 37",
    source_url="https://5233025.fs1.hubspotusercontent-na1.net/hubfs/5233025/%C3%89tudes%20M%C3%A9diatiques/%C3%89tudes%20M%C3%A9diatiques%20-%202026/4.%20%C3%89M%20-%20Avril%202026/20260410%20-%20AB%20-%20BC%20Government%20Poll/LEGER_BC%20Gov%20Report%20Card_EN_Apr2026.pdf",
    source_file="raw/leger/leger_bc_20gov_20report_20card_en_apr2026.pdf",
    notes="Undecided share from Leger's Oct 22 2026 trend chart.")
add(pollster="Mainstreet Research", field_start="2026-04-09", field_end="2026-04-13", release_date="2026-04-15",
    sample_size="1275", mode="IVR (Smart IVR)", population="decided voters",
    NDP=38.0, Conservative=32.8, Green=16.1, OneBC=10.9, other=2.2, undecided_share="16.9 (all voters)",
    seat_projection="Mainstreet scenario model: Halford NDP 59 / CPC 32 / GRN 2; Elliott, Black, Findlay CPC 46 / NDP 45; Milobar CPC 53 / NDP 38; Fulmer NDP minority with OneBC 4",
    source_url="https://cdn.prod.website-files.com/66c8dfb086a015b3b519e988/69dfa83b30c109ebd9686d02_BC_Survey_April2026_Teaser.pdf",
    source_file="raw/mainstreet_research/69dfa83b30c109ebd9686d02_bc_survey_april2026_teaser.pdf",
    notes="'Teaser' public deck.")
add(pollster="Angus Reid Institute", field_start="2026-04-24", field_end="2026-04-28", release_date="2026-05-05",
    sample_size="804 (decided 600)", mode="online panel", population="decided voters",
    NDP=36, Conservative=46, Green=13, other=4,
    regional_splits="Metro Van: NDP 44 CPC 44; Fraser Valley: NDP 27 CPC 54; Island/North Coast: NDP 38 CPC 37; Interior: NDP 32 CPC 52",
    gender_splits="Male: NDP 30 CPC 53; Female: NDP 44 CPC 38",
    source_url="https://angusreid.org/wp-content/uploads/2026/05/2026.05.05_BC_tables.pdf",
    source_file="raw/angus_reid/2026.05.05_BC_tables.pdf",
    notes="Conservatives leaderless at the time.")
add(pollster="Leger", field_start="2026-06-01", field_end="2026-06-02", release_date="2026-06-05",
    sample_size="1002 (decided 806 weighted)", mode="online panel", population="decided voters",
    NDP=41, Conservative=45, Green=8, other=6, undecided_share="13",
    regional_splits="Metro Van: NDP 43 CPC 44 GRN 6; Van Isle: NDP 35 CPC 40 GRN 18; Rest of BC: NDP 41 CPC 48 GRN 6",
    gender_splits="Men: NDP 37 CPC 48; Women: NDP 45 CPC 42",
    age_splits="18-34: NDP 40 CPC 44; 35-54: NDP 34 CPC 53; 55+: NDP 47 CPC 40",
    source_url="https://documents.leger360.com/hubfs/%C3%89tudes%20M%C3%A9diatiques/%C3%89tudes%20M%C3%A9diatiques%20-%202026/%C3%89tudes%20Juin%202026/Leger%20Poll%20-%20BC%20Pulse%20Check%20June%202026.pdf",
    source_file="raw/leger/leger_20poll_20_20bc_20pulse_20check_20june_202026.pdf")
add(pollster="Research Co.", field_start="2026-06-03", field_end="2026-06-05", release_date="2026-06-08",
    sample_size="803", mode="online panel", population="decided voters",
    NDP=42, Conservative=42, Green=9, CentreBC=3, OneBC=2,
    regional_splits="Southern BC: NDP 50 CPC 41; Metro Vancouver: NDP 43 CPC 39; Vancouver Island: NDP 42 CPC 39; Northern BC: CPC 57 NDP 23; Fraser Valley: CPC 56 NDP 36",
    gender_splits="Men: CPC 46 NDP 40; Women: NDP 42 CPC 39",
    age_splits="18-34: CPC 40 NDP 38; 35-54: CPC 44 NDP 39; 55+: NDP 47 CPC 42",
    leader_approval_or_best_premier="Approval: Eby 48, Lowan 34, Findlay 32, Brodie 20, Kirkpatrick 19",
    top_issues="Housing/poverty/homelessness 29; economy/jobs 26; health care 21; crime 8",
    source_url="https://researchco.ca/2026/06/08/bcpoli-june2026/", source_file="raw/research_co/bcpoli_june2026.html",
    notes="Alternative ballot with BC Liberals: NDP 35, CPC 34, Liberal 15, GRN 9, Centre 3, OneBC 3. Tables PDF blocked (429).")
add(pollster="Angus Reid Institute", field_start="2026-06-01", field_end="2026-06-12", release_date="2026-06-16",
    sample_size="755", mode="online panel", population="decided voters",
    NDP=36, Conservative=47, Green=11, other=6,
    regional_splits="Metro Van: NDP 41 CPC 46; Lower Mainland/Fraser Valley: NDP 40 CPC 48; Island/North Coast: NDP 29 CPC 43 GRN 24; Interior: NDP 30 CPC 53",
    source_url="https://angusreid.org/wp-content/uploads/2026/06/2026.06.15_BC_release_tables.pdf",
    source_file="raw/angus_reid/2026.06.15_BC_release_tables.pdf",
    notes="Release text also cites 42/38 on a separate consideration item; vote table is 47/36.")
add(pollster="Yorkville Strategies", field_start="2026-07-28", field_end="2026-08-03", release_date="2026-08-11",
    sample_size="1016", mode="online panel", population="decided voters",
    NDP=45.8, Conservative=39.8, undecided_share="about 20 ('one-in-five')",
    source_url="https://www.linkedin.com/posts/dimitri-pantazopoulos-03526a7_new-yorkville-strategies-survey-bc-conservatives-activity-7493045498778574848-g9KQ/",
    source_file="raw/yorkville_strategies/w_yorkville_strategies_survey_bc_conservatives_activity_7493045498778574848_g9kq.html",
    release_status="partly opened",
    notes="Pollster's own LinkedIn post gives only 'NDP leads by 6 among decided'. The 45.8/39.8 figures were seen in Sitka Media (raw/yorkville_strategies/bc_ndp_lead_conservatives_by_six_points_poll_shows.html). Green 12, OneBC 1, Centre 0, other 2 appear only on Wikipedia.")
add(pollster="604 Polling", field_start="2026-07-31", field_end="2026-08-08", release_date="2026-08-11",
    sample_size="1124", mode="IVR", population="decided voters",
    NDP=35.4, Conservative=44.6, Green=12.2, CentreBC=2.2, OneBC=1.9, other=3.6, undecided_share="9.0",
    leader_approval_or_best_premier="Preferred premier: Eby 26.9, Findlay 23.1, Lowan 7.7, Brodie 3.5, Bernier 2.5, undecided 28.1; govt approval 30.0, disapprove 53.7",
    source_url="https://604polling.ca/#results", source_file="raw/604_polling/results.html")
add(pollster="Research Co.", field_start="2026-08-12", field_end="2026-08-14", release_date="2026-08-18",
    sample_size="801", mode="online panel", population="decided voters",
    NDP=44, Conservative=39, Green=10, CentreBC=5, OneBC=1,
    regional_splits="Vancouver Island: NDP 52 CPC 26; Northern BC: CPC 53 NDP 32; Fraser Valley: 45/45; Metro Vancouver: NDP 42 CPC 40; Southern BC: NDP 47 CPC 45",
    gender_splits="Women: NDP 47 CPC 34; Men: CPC 45 NDP 40",
    age_splits="18-34: CPC 40 NDP 34; 35-54: NDP 44 CPC 41; 55+: NDP 52 CPC 37",
    leader_approval_or_best_premier="Approval: Eby 49, Lowan 38, Findlay 34, Bernier 24, Brodie 18",
    top_issues="Housing/poverty/homelessness 29; economy/jobs 24; health care 21; crime 8",
    source_url="https://researchco.ca/2026/08/18/bcpoli-aug2026/", source_file="raw/research_co/bcpoli_aug2026.html",
    notes="Tables PDF blocked (429).")
add(pollster="Ipsos", field_start="2026-09-08", field_end="2026-09-14", release_date="2026-09-15",
    sample_size="800", mode="online panel", population="decided voters",
    NDP=45, Conservative=35, Green=10, CentreBC=4, OneBC=2, other=4, undecided_share="28 (undecided or no preference)",
    regional_splits="Metro Vancouver: NDP 47 CPC 34; Vancouver Island: NDP 44 CPC 30; Southern Interior/North: NDP 41 CPC 41",
    gender_splits="Women: NDP 50 CPC 30; Men: NDP 40 CPC 40",
    age_splits="18-34: NDP 43 CPC 41; 35-54: 40/40; 55+: NDP 50 CPC 27",
    leader_approval_or_best_premier="Favourable/unfavourable: Eby 41/30, Findlay 17/46, Lowan 12/15, Brodie 10/24, Bernier 9/19",
    source_url="https://www.ipsos.com/sites/default/files/ct/news/documents/2026-09/BC%20Political%20Release%20for%20Sept%2015_0.pdf",
    source_file="raw/ipsos/2026-09_BC_Political_Release_for_Sept_15_0.pdf")
add(pollster="Angus Reid Institute", field_start="2026-09-08", field_end="2026-09-15", release_date="2026-09-17",
    sample_size="749 (decided+leaning 640)", mode="online panel", population="decided + leaning",
    NDP=41, Conservative=37, Green=13, other=9,
    regional_splits="Metro Van: NDP 43 CPC 34 GRN 14; Fraser Valley/Lower Mainland: NDP 43 CPC 41; Island/North Coast: NDP 44 CPC 29 GRN 20; Interior: NDP 33 CPC 48",
    gender_splits="Male: NDP 38 CPC 37; Female: NDP 44 CPC 36",
    age_splits="18-34: NDP 50 CPC 27 GRN 20",
    source_url="https://angusreid.org/wp-content/uploads/2026/09/2026.09.17_BC_Spotlight_final.pdf",
    source_file="raw/angus_reid/2026.09.17_BC_Spotlight_final.pdf")
add(pollster="Innovative Research Group", field_start="2026-09-04", field_end="2026-09-18", release_date="2026-09-22",
    sample_size="500 (decided 399)", mode="online panel", population="decided + leaning",
    NDP=43, Conservative=39, Green=14, other=4,
    source_url="https://innovativeresearch.ca/wp-content/uploads/2026/09/CTM2609-BC-Report-RELEASE-2.pdf",
    source_file="raw/innovative_research/ctm2609_bc_report_release_2.pdf",
    notes="Cover says field Sept 4-18; methodology page says Sept 4-15.")
add(pollster="Liaison Strategies", field_start="2026-09-21", field_end="2026-09-22", release_date="2026-09-23",
    sample_size="1000", mode="IVR", population="decided + leaning",
    NDP=41, Conservative=36, Green=12, CentreBC=4, OneBC=4, other=3,
    regional_splits="Vancouver metro area: NDP 43 CPC 34; Vancouver Island: NDP 45 CPC 32; Rest of BC: CPC 42 NDP 35",
    gender_splits="Women: NDP 45 CPC 33; Men: CPC 41 NDP 37",
    leader_approval_or_best_premier="Eby approve 42 / disapprove 43; Doerkson fav 21 / unfav 29; Lowan 20/20",
    source_url="https://press.liaisonstrategies.ca/bc-ndp-leads-conservatives-41-to-36-as-election-begins/",
    source_file="raw/liaison_strategies/bc_ndp_leads_conservatives_41_to_36_as_election_begins.html",
    notes="Fieldwork straddles the Sept 22 election call (began the day before).")

# ---------------- campaign (Sept 22 - Oct 23, 2026) ----------------
add(pollster="Angus Reid Institute", field_start="2026-09-22", field_end="2026-09-24", release_date="2026-09-24",
    sample_size="801 (decided 682)", mode="online panel", population="decided + leaning",
    NDP=35, Conservative=43, Green=12, CentreBC=3, OneBC=4, other="3 (independent)", undecided_share="20 (all respondents)",
    regional_splits="Metro Van: NDP 34 CPC 44; Fraser Valley: NDP 36 CPC 51; Island/North: NDP 39 CPC 30 GRN 26; BC Interior: NDP 31 CPC 51 OneBC 9",
    gender_splits="Male: NDP 34 CPC 47; Female: NDP 36 CPC 40",
    age_splits="18-34: NDP 43 CPC 29 GRN 21; 35-54: NDP 30 CPC 48; 55+: NDP 33 CPC 49",
    leader_approval_or_best_premier="Eby favourable 33 / unfavourable 60",
    top_issues="Cost of living 59; health care 42; economy/jobs 28; housing 25; crime 25; deficit 24; US tariffs 15",
    source_url="https://angusreid.org/wp-content/uploads/2026/09/2026.09.24_BC_Elxn_1_PR_tables.pdf",
    source_file="raw/angus_reid/2026_09_24_bc_elxn_1_pr_tables.pdf")
add(pollster="Pollara", field_start="2026-09-23", field_end="2026-09-30", release_date="2026-10-05",
    sample_size="3017 (2509 online + 508 IVR)", mode="online panel + IVR", population="decided voters",
    NDP=38, Conservative=38, Green=13, OneBC=5, CentreBC=4,
    regional_splits="Wave tables (no leader names, online decided): Metro Vancouver NDP 39 CPC 42; Fraser Valley 35/34; Vancouver Island 41/32; Interior 33/37; North 20/57",
    gender_splits="Tables (no names): Female NDP 40 CPC 38; Male 34/41",
    age_splits="Tables (no names): 18-34 33/46; 35-49 36/35; 50-64 33/41; 65+ 43/39 (NDP/CPC)",
    leader_approval_or_best_premier="Best premier: Eby 28, Doerkson 23; Doerkson 44% don't know, net fav +12",
    source_url="https://pollarastrategicinsights.substack.com/p/even-flow",
    source_file="raw/pollara/even_flow.html; raw/pollara/pollara_wave1_tables.pdf",
    notes="Headline 38-38 from Pollara Substack. Tables give two versions: without leader names 37/40/12/5/4 and with names 39/36/14/5/4.")
add(pollster="Leger", field_start="2026-09-24", field_end="2026-09-28", release_date="2026-09-29",
    sample_size="1003 (decided 810 weighted)", mode="online panel", population="decided voters",
    NDP=36, Conservative=39, Green=13, CentreBC=5, OneBC=5, other=2, undecided_share="13",
    regional_splits="Metro Van: NDP 39 CPC 37 GRN 12; Van Island: NDP 37 CPC 37 GRN 16; Rest of BC: NDP 31 CPC 44 OneBC 7",
    gender_splits="Men: NDP 31 CPC 42; Women: NDP 41 CPC 36",
    age_splits="18-34: NDP 27 CPC 43 GRN 23; 35-54: NDP 34 CPC 36; 55+: NDP 43 CPC 39",
    leader_approval_or_best_premier="Preferred premier: Eby 39, Doerkson 35, Lowan 15, Brodie 6",
    top_issues="Health care 15; housing 14; economy 13 (single most important issue)",
    source_url="https://documents.leger360.com/hubfs/%C3%89tudes%20M%C3%A9diatiques/%C3%89tudes%20M%C3%A9diatiques%20-%202026/9.%20%C3%89tudes%20m%C3%A9diatiques%20septembre%202026/BC%20Politics/Media%20Release%20-%20BC%20Election%20Polling%20September%2029%2c%202026.pdf",
    source_file="raw/leger/leger_bc_sept29_2026.pdf")
add(pollster="Ipsos", field_start="2026-09-25", field_end="2026-09-29", release_date="2026-10-01",
    sample_size="1001", mode="online panel", population="decided voters",
    NDP=40, Conservative=42, Green=10, CentreBC=3, OneBC=3, other=2, undecided_share="27 (undecided or no preference)",
    regional_splits="Metro Vancouver: NDP 43 CPC 41; Vancouver Island: NDP 48 CPC 30; Southern Interior/North: CPC 49 NDP 31",
    gender_splits="Women: NDP 42 CPC 40; Men: CPC 43 NDP 39",
    age_splits="18-34: CPC 41 NDP 38; 35-54: NDP 40 CPC 39; 55+: CPC 44 NDP 42",
    leader_approval_or_best_premier="Best premier: Eby 33, Doerkson 17, Lowan 6, Brodie 6, Sturko 4, undecided 36",
    top_issues="Cost of living 56; health care 39; housing 31",
    source_url="https://www.ipsos.com/sites/default/files/ct/news/documents/2026-10/BC%20Poll%201%20Release.pdf",
    source_file="raw/ipsos/2026-10_BC_Poll_1_Release.pdf",
    notes="In partnership with Global BC.")
add(pollster="Innovative Research Group", field_start="2026-09-25", field_end="2026-09-28", release_date="2026-09-28",
    sample_size="500 (decided 411)", mode="online panel", population="decided + leaning",
    NDP=41, Conservative=39, Green=11, OneBC=4, CentreBC=3, other=3, undecided_share="13 (combined vote)",
    regional_splits="Combined vote incl. undecided: Lower Mainland & Fraser Valley NDP 38 CPC 30; Vancouver Island & Sunshine Coast NDP 30 CPC 29; Interior & North CPC 38 NDP 26",
    age_splits="Combined vote: 18-34 NDP 37 CPC 31; 35-54 CPC 32 NDP 29; 55+ NDP 36 CPC 32",
    leader_approval_or_best_premier="Best premier: Eby 27, Doerksen 23",
    source_url="https://innovativeresearch.ca/wp-content/uploads/2026/09/CTM2609-W4-BC-Election-Short-Deck-RELEASE.pdf",
    source_file="raw/innovative_research/ctm2609_w4_bc_election_short_deck_release.pdf",
    notes="Decided figures read from chart labels; OneBC n=15 and CentreBC n=14 folded into Other in breakdowns.")
add(pollster="Liaison Strategies", field_start="2026-09-26", field_end="2026-09-27", release_date="2026-09-29",
    sample_size="1000 (decided+leaning 848)", mode="IVR", population="decided + leaning",
    NDP=39, Conservative=40, Green=11, CentreBC=4, OneBC=3, other=3, undecided_share="25 (initial vote question)",
    regional_splits="Metro Vancouver: NDP 40 CPC 37 GRN 13; Vancouver Island: NDP 47 CPC 28 GRN 15; Rest of BC: NDP 32 CPC 51",
    gender_splits="Female: NDP 40 CPC 40; Male: NDP 37 CPC 41",
    age_splits="18-34: NDP 41 CPC 40; 35-54: 39/40; 55+: 37/40",
    leader_approval_or_best_premier="Eby approve 38 / disapprove 45; Doerkson fav 27 / unfav 32",
    source_url="https://press.liaisonstrategies.ca/content/files/2026/09/2026.09.29-BC-Tables.pdf",
    source_file="raw/liaison_strategies/2026.09.29-BC-Tables.pdf")
add(pollster="Mainstreet Research", field_start="2026-09-30", field_end="2026-10-01", release_date="2026-10-06",
    sample_size="827", mode="IVR", population="decided (undecided removed after leaners)",
    NDP=37.2, Conservative=44.7, Green=11.2, CentreBC=1.1, OneBC=5.7, undecided_share="13.1 (all); 4.8 after leaners",
    leader_approval_or_best_premier="Snap election call: approve 29.4, disapprove 59.3",
    source_url="https://cdn.prod.website-files.com/66c8dfb086a015b3b519e988/6ac48198ecd4d93eff6c39ef_British_Columbia_October_2026_Public.pdf",
    source_file="raw/mainstreet_research/6ac48198ecd4d93eff6c39ef_british_columbia_october_2026_public.pdf",
    notes="Public PDF leaves regional/gender/age cells blank.")
add(pollster="Angus Reid Institute", field_start="2026-10-01", field_end="2026-10-03", release_date="2026-10-05",
    sample_size="1013 (decided+leaning 846)", mode="online panel", population="decided + leaning",
    NDP=43, Conservative=48, Green=7, other=2,
    regional_splits="Metro Van: NDP 48 CPC 44; Fraser Valley: NDP 28 CPC 62; Island/North Coast: NDP 48 CPC 39 GRN 12; Interior: NDP 36 CPC 57",
    gender_splits="Male: NDP 35 CPC 55; Female: NDP 51 CPC 40",
    age_splits="18-34: NDP 55 CPC 28; 35-54: NDP 35 CPC 57; 55+: NDP 44 CPC 49",
    leader_approval_or_best_premier="Best premier: Doerkson 36, Eby 33, neither 31; Eby fav 36 / unfav 58; Doerkson 38/37",
    top_issues="Cost of living 57; health care 42; economy/jobs 26; housing 24; deficit 24; public safety 24; US tariffs 10",
    source_url="https://angusreid.org/wp-content/uploads/2026/10/2026.10.05_BC_Elxn_2_tables.pdf",
    source_file="raw/angus_reid/2026.10.05_BC_Elxn_2_tables.pdf")
add(pollster="Ipsos", field_start="2026-10-07", field_end="2026-10-11", release_date="2026-10-13",
    sample_size="1356", mode="online panel + live phone", population="decided voters",
    NDP=38, Conservative=43, Green=11, CentreBC=2, OneBC=4, other=2, undecided_share="25 (18 undecided + 7 no preference)",
    regional_splits="Metro Vancouver: CPC 42 NDP 39; Vancouver Island: NDP 47 CPC 27; Southern Interior/North: CPC 53 NDP 32",
    gender_splits="Men: CPC 49 NDP 31; Women: NDP 45 CPC 36",
    age_splits="18-34: CPC 40 NDP 36; 35-54: CPC 48 NDP 34; 55+: NDP 43 CPC 41",
    leader_approval_or_best_premier="Best premier: Eby 30, Doerkson 19, Lowan 7, Brodie 5, Sturko 4, undecided 35",
    top_issues="Cost of living 57; health care 39; housing 30",
    source_url="https://www.ipsos.com/sites/default/files/ct/news/documents/2026-10/BC%20Poll%202%20Release.pdf",
    source_file="raw/ipsos/2026-10_BC_Poll_2_Release.pdf",
    notes="In partnership with Global BC.")
add(pollster="Liaison Strategies", field_start="2026-10-07", field_end="2026-10-08", release_date="2026-10-09",
    sample_size="1000 (decided+leaning 882)", mode="IVR", population="decided + leaning",
    NDP=37, Conservative=43, Green=10, CentreBC=3, OneBC=4, other=4, undecided_share="23 (initial vote question)",
    regional_splits="Metro Vancouver: NDP 38 CPC 40; Vancouver Island: NDP 44 CPC 32; Rest of BC: NDP 30 CPC 54",
    gender_splits="Female: NDP 38 CPC 40; Male: NDP 36 CPC 46",
    age_splits="18-34: NDP 45 CPC 36; 35-54: NDP 37 CPC 42; 55+: NDP 32 CPC 47",
    leader_approval_or_best_premier="Eby approve 34 / disapprove 48; Doerkson fav 30 / unfav 35; Lowan 24/23",
    source_url="https://press.liaisonstrategies.ca/content/files/2026/10/2026.10.09-British-Columbia-Tables.pdf",
    source_file="raw/liaison_strategies/2026.10.09-British-Columbia-Tables.pdf")
add(pollster="Research Co.", field_start="2026-10-09", field_end="2026-10-11", release_date="2026-10-13",
    sample_size="808 likely voters (decided 687)", mode="online panel", population="decided likely voters",
    NDP=42, Conservative=44, Green=8, CentreBC=2, OneBC=2, other=1, undecided_share="14 (tables; release text says 15)",
    regional_splits="Northern BC: CPC 55 NDP 39; Fraser Valley: CPC 49 NDP 43; Vancouver Island: NDP 52 CPC 34; Southern BC: CPC 44 NDP 40; Metro Vancouver: CPC 45 NDP 43",
    age_splits="18-34: CPC 47 NDP 41 GRN 14; 35-54: CPC 43 NDP 41; 55+: NDP 52 CPC 41",
    leader_approval_or_best_premier="Approval: Eby 49, Doerkson 45, Lowan 39, Sturko 26, Brodie 26. Best premier: Eby 36, Doerkson 25, Lowan 7, Brodie 4, Sturko 4",
    top_issues="Economy/jobs 25; housing/poverty/homelessness 23; health care 21; crime 9; accountability 7",
    source_url="https://researchco.ca/wp-content/uploads/2026/10/Tables_Politics_BC_13Oct2026.pdf",
    source_file="raw/research_co/Tables_Politics_BC_13Oct2026.pdf; raw/research_co/bcpoli_oct13.html")
add(pollster="Leger", field_start="2026-10-09", field_end="2026-10-12", release_date="2026-10-13",
    sample_size="1000 (decided 816 weighted)", mode="online panel", population="decided voters",
    NDP=40, Conservative=42, Green=9, CentreBC=3, OneBC=4, other=2, undecided_share="12",
    regional_splits="Metro Van: NDP 42 CPC 41; Van Island: NDP 44 CPC 39; Rest of BC: NDP 33 CPC 45 GRN 12",
    gender_splits="Men: NDP 34 CPC 47; Women: NDP 46 CPC 37",
    age_splits="18-34: NDP 31 CPC 41 GRN 16; 35-54: NDP 38 CPC 43; 55+: NDP 46 CPC 41",
    leader_approval_or_best_premier="Opinion worsened past week: Eby 39%, Doerkson 20%",
    source_url="https://documents.leger360.com/hubfs/%C3%89tudes%20M%C3%A9diatiques/%C3%89tudes%20M%C3%A9diatiques%20-%202026/10.%20October%202026/Media%20Release%20-%20BC%20Election%20Polling%20October%2013%2c%202026.pdf",
    source_file="raw/leger/Media_20Release_20-_20BC_20Election_20Polling_20October_2013_2c_202026.pdf")
add(pollster="Pallas Data", field_start="2026-10-10", field_end="2026-10-11", release_date="2026-10-13",
    sample_size="513", mode="IVR", population="decided + leaning",
    NDP=38, Conservative=43, Green=11, CentreBC=2, OneBC=5, other=1,
    regional_splits="Metro Vancouver: NDP 41 CPC 41; Rest of BC: CPC 51 NDP 37; Vancouver Island: CPC 35 NDP 33 GRN 18 OneBC 13",
    gender_splits="Men: CPC 46 NDP 37; Women: CPC 41 NDP 39 GRN 14",
    age_splits="18-34: CPC 51 NDP 35 (46 interviews); 35-49: CPC 42 NDP 40; 50-64: 36/36; 65+: CPC 45 NDP 41",
    leader_approval_or_best_premier="Best premier: Doerkson 35, Eby 29, Lowan 13, Brodie 6, Sturko 2",
    source_url="https://pallas-data.ca/2026/10/13/pallas-british-columbia-poll-conservative-43-ndp-38-green-11-onebc-5-and-doerkson-leads-eby-on-best-premier/",
    source_file="raw/pallas_data/l_conservative_43_ndp_38_green_11_onebc_5_and_doerkson_leads_eby_on_best_premier.html")
add(pollster="Mainstreet Research", field_start="2026-10-17", field_end="2026-10-18", release_date="2026-10-21",
    sample_size="907", mode="IVR", population="decided (undecided removed after leaners)",
    NDP=36.0, Conservative=41.7, Green=14.6, CentreBC=2.6, OneBC=5.0, undecided_share="10.6 (all); 5.4 after leaners",
    leader_approval_or_best_premier="Snap election call: approve 37.4, disapprove 52.6",
    source_url="https://cdn.prod.website-files.com/66c8dfb086a015b3b519e988/6ad861a55f3843e8a922c51f_British_Columbia_October_18_2026_Public.pdf",
    source_file="raw/mainstreet_research/6ad861a55f3843e8a922c51f_british_columbia_october_18_2026_public.pdf",
    notes="Public PDF leaves breakdown cells blank.")
add(pollster="Angus Reid Institute", field_start="2026-10-15", field_end="2026-10-19", release_date="2026-10-20",
    sample_size="793 (decided+leaning 723)", mode="online panel", population="decided + leaning",
    NDP=43, Conservative=46, Green=8, CentreBC=1, OneBC=1, other="1 (independent)", undecided_share="7 (all respondents)",
    regional_splits="Metro Van: NDP 46 CPC 45; Fraser Valley: NDP 36 CPC 56; Island/North Coast: NDP 48 CPC 34 GRN 17; Interior: NDP 35 CPC 52",
    gender_splits="Male: NDP 33 CPC 54; Female: NDP 52 CPC 38",
    age_splits="18-34: NDP 51 CPC 31 GRN 15; 35-54: NDP 39 CPC 50; 55+: NDP 43 CPC 49",
    leader_approval_or_best_premier="Best premier: Doerkson 36, Eby 34, neither 30. Favourable: Eby 36 (net -24), Doerkson 39 (net -6), Lowan 44 (net +10)",
    top_issues="Cost of living 58; health care 44; housing 28; economy/jobs 25; crime 24; deficit 22",
    source_url="https://angusreid.org/wp-content/uploads/2026/10/2026.10.19_BC_Poll_3_tables.pdf",
    source_file="raw/angus_reid/2026_10_19_bc_poll_3_tables.pdf")
add(pollster="Innovative Research Group", field_start="2026-10-15", field_end="2026-10-19", release_date="2026-10-20",
    sample_size="1000 weighted (1153 unweighted; decided 908)", mode="online panel", population="decided + leaning",
    NDP=38, Conservative=43, Green=12, other="7 (OneBC, CentreBC and others combined in headline chart)",
    regional_splits="Lower Mainland North/Central: CPC 42 NDP 38 GRN 13; Lower Mainland South/East: CPC 47 NDP 37; Island/Sunshine Coast: CPC 42 NDP 40 GRN 12; Interior/North: CPC 40 NDP 36 OneBC 7",
    leader_approval_or_best_premier="Best premier: Doerksen 32, Eby 30, Lowan 10",
    top_issues="Party best on: cost of living CPC 33 / NDP 26; health NDP 30 / CPC 28; housing CPC 28 / NDP 27",
    source_url="https://innovativeresearch.ca/wp-content/uploads/2026/10/IRG.34-2026-BC-Election-BLOG-POST-RELEASE.pdf",
    source_file="raw/innovative_research/irg_34_2026_bc_election_blog_post_release.pdf",
    notes="Wikipedia splits other as OneBC 4 / Centre 2 / other 1; the release's regional table shows OneBC 2-7 and CentreBC 2-3 by region but the provincewide split is only in chart form as 'Other 7%'.")
add(pollster="Pollara", field_start="2026-10-15", field_end="2026-10-21", release_date="2026-10-23",
    sample_size="2202 (1502 online + 700 IVR; decided 1950)", mode="online panel + IVR", population="decided voters (incl. leaners)",
    NDP=37, Conservative=42, Green=13, OneBC=4, CentreBC=3, other=1, undecided_share="8 (+5 would not vote, 1 prefer not to say)",
    regional_splits="Metro Vancouver: NDP 37 CPC 44 GRN 11; Vancouver Island: NDP 39 CPC 35 GRN 18; Interior/North/Fraser Valley: NDP 34 CPC 45",
    gender_splits="Women: NDP 39 CPC 40; Men: NDP 34 CPC 45",
    age_splits="18-34: NDP 28 CPC 45; 35-49: 36/41; 50-64: 35/42; 65+: 42/42",
    source_url="https://www.pollara.com/wp-content/uploads/2026/10/BC_2026_Election_Syndicate_Wave_3_Final_xtabs.pdf",
    source_file="raw/pollara/bc_2026_election_syndicate_wave_3_final_xtabs.pdf",
    notes="Pollara also publishes a 'projected popular vote' adjusted for candidates on the ballot: NDP 39, CPC 45, GRN 12, OneBC 2, Centre 2, other 1. Release page (pollara.com) blocked (HTTP 429, WebFetch not approved).")
add(pollster="Leger", field_start="2026-10-20", field_end="2026-10-22", release_date="2026-10-22",
    sample_size="1072 (decided 916 weighted)", mode="online panel", population="decided voters",
    NDP=39, Conservative=44, Green=13, CentreBC=1, OneBC=2, other=1, undecided_share="6",
    regional_splits="Metro Van: NDP 40 CPC 44 GRN 12; Van Island: NDP 40 CPC 39 GRN 17; Rest of BC: NDP 36 CPC 46 GRN 13",
    gender_splits="Men: NDP 35 CPC 47; Women: NDP 43 CPC 41",
    age_splits="18-34: NDP 36 CPC 38 GRN 20; 35-54: NDP 34 CPC 48; 55+: NDP 44 CPC 44",
    source_url="https://documents.leger360.com/hubfs/%C3%89tudes%20M%C3%A9diatiques/%C3%89tudes%20M%C3%A9diatiques%20-%202026/10.%20October%202026/Media%20Release%20-%20BC%20Election%20Polling%20October%2022%2c%202026%20-%20SHORT.pdf",
    source_file="raw/leger/a_20release_20_20bc_20election_20polling_20october_2022_2c_202026_20_20short.pdf")
add(pollster="Ipsos", field_start="2026-10-20", field_end="2026-10-22", release_date="2026-10-23",
    sample_size="1260 (801 online + 459 live phone)", mode="online panel + live phone", population="decided voters",
    NDP=39, Conservative=44, Green=13, CentreBC=1, OneBC=2, other=1, undecided_share="18 (12 undecided + 7 no preference)",
    regional_splits="Metro Vancouver: CPC 44 NDP 40; Vancouver Island: NDP 46 CPC 32 GRN 18; Southern Interior/North: CPC 53 NDP 31",
    gender_splits="Men: CPC 50 NDP 35 GRN 10; Women: NDP 42 CPC 38 GRN 17",
    age_splits="18-34: CPC 42 NDP 32 GRN 23; 35-54: CPC 48 NDP 35; 55+: NDP 45 CPC 42",
    leader_approval_or_best_premier="Best premier: Eby 30, Doerkson 23, Lowan 10, Brodie 6, Sturko 2, undecided 28. Fav/unfav: Eby 35/40, Doerkson 31/33, Lowan 30/18",
    source_url="https://www.ipsos.com/sites/default/files/ct/news/documents/2026-10/BC%20Call%20Poll%20Release.pdf",
    source_file="raw/ipsos/2026-10_BC_Call_Poll_Release.pdf",
    notes="In partnership with Global BC. Time for change 53, deserves re-election 31.")
add(pollster="Mainstreet Research", field_start="2026-10-21", field_end="2026-10-23", release_date="2026-10-23",
    sample_size="1043 (decided 1012)", mode="IVR", population="decided (undecided removed after leaners)",
    NDP=37.2, Conservative=42.9, Green=17.0, CentreBC=1.0, OneBC=1.8, undecided_share="8.0 (all); 4.3 after leaners",
    source_url="https://cdn.prod.website-files.com/66c8dfb086a015b3b519e988/6adc1db0f13a4f502b3e5b9a_British_Columbia_October_23_2026_Public.pdf",
    source_file="raw/mainstreet_research/6adc1db0f13a4f502b3e5b9a_british_columbia_october_23_2026_public.pdf",
    notes="Regions defined as Vancouver Island, Vancouver, Lower Mainland, Rest of BC, but the public PDF leaves all breakdown cells blank (checked rendered page). 550 of 1012 decided say they already voted.")
add(pollster="Research Co.", field_start="2026-10-21", field_end="2026-10-23", release_date="2026-10-23",
    sample_size="802 likely voters (decided 722)", mode="online panel", population="decided likely voters",
    NDP=40, Conservative=44, Green=10, CentreBC=2, OneBC=2, other=1, undecided_share="10",
    regional_splits="Metro Vancouver: CPC 45 NDP 41; Fraser Valley: CPC 58 NDP 33; Vancouver Island: NDP 46 CPC 35 GRN 16; Southern BC: CPC 48 NDP 39; Northern BC: CPC 51 NDP 29",
    gender_splits="Male: CPC 45 NDP 39; Female: CPC 43 NDP 40",
    age_splits="18-34: CPC 43 NDP 34 GRN 17; 35-54: 41/41; 55+: CPC 48 NDP 41",
    leader_approval_or_best_premier="Approval: Doerkson 48, Lowan 46, Eby 44, Sturko 26, Brodie 25. Best premier: Eby 34, Doerkson 34, Lowan 11, Brodie 3, Sturko 2",
    top_issues="Economy/jobs 28; housing/poverty/homelessness 23; health care 20; crime 7; accountability 7",
    source_url="https://researchco.ca/wp-content/uploads/2026/10/Tables_Politics_BC_23Oct2026.pdf",
    source_file="raw/research_co/tables_politics_bc_23oct2026.pdf; raw/research_co/Release_Politics_BC_23Oct2026.pdf",
    notes="Release text gives 18-34 split as 43/34 and 55+ 48/41, matching tables. Release HTML page blocked (429); release PDF and tables opened.")
add(pollster="Pallas Data", field_start="2026-10-22", field_end="2026-10-22", release_date="2026-10-23",
    sample_size="702", mode="IVR", population="decided + leaning",
    NDP=39, Conservative=45, Green=12,
    regional_splits="Metro Vancouver: CPC 46 NDP 41; BC Interior (Rest of BC): CPC 50 NDP 36; Vancouver Island: NDP 42 CPC 32 GRN 24",
    gender_splits="Men: CPC 47 NDP 35; Women: CPC 44 NDP 43",
    age_splits="18-34: NDP leads by 4; 35-49: CPC 43 NDP 38; 65+: CPC 49 NDP 39",
    leader_approval_or_best_premier="Best premier: Doerkson 32, Eby 27, Lowan 16",
    source_url="https://pallas-data.ca/2026/10/24/pallas-british-columbia-poll-conservatives-45-ndp-39-green-12/",
    source_file="raw/pallas_data/pallas_british_columbia_poll_conservatives_45_ndp_39_green_12.html",
    notes="Release does not give OneBC/CentreBC/other (Wikipedia shows other 4).")
add(pollster="Forum Research", field_start="2026-10-23", field_end="2026-10-23", release_date="2026-10-23",
    sample_size="765 (decided+leaning 731)", mode="IVR", population="decided + leaning",
    NDP=39.5, Conservative=44.5, Green=12.0, other=4.0,
    regional_splits="Vancouver Lower Mainland: NDP 41.6 CPC 43.9 GRN 11.5; Vancouver Island: NDP 38.3 CPC 39.2 GRN 19.0; Interior North: NDP 35.6 CPC 50.7 GRN 6.8",
    gender_splits="Male: NDP 39.0 CPC 49.4; Female: NDP 41.1 CPC 40.6",
    age_splits="18-24: 35.0/45.5; 25-34: 40.4/40.9; 35-44: 40.6/42.0; 45-54: 26.2/51.7; 55-64: 42.0/46.7; 65+: 43.9/42.3 (NDP/CPC)",
    seat_projection="Forum: CPC 56, NDP 35, GRN 2 (release PDF). Forum's web article text says CPC 53, NDP 38, GRN 2.",
    source_url="https://www.forumresearch.com/news/attachments/23310996-1c29-403c-ad66-c0c0c3899c67.pdf",
    source_file="raw/forum_research/forum_bc_release_20261023.pdf; raw/forum_research/forum_bc_2026-10-23.json",
    notes="Seat projection differs between Forum's own PDF (56/35/2) and its web article (53/38/2). PDF file name says 'Federal Election'; question text says election 'held on October 23rd'.")

# ---------------- release not opened ----------------
NOT_OPENED = [
    dict(pollster="Canadian Election Study", field="2025-04-29 to 2025-05-13", figures="NDP 42, CPC 34, GRN 6, Liberal 18 (n=1,649, online)",
         seen_at="Wikipedia; source is Harvard Dataverse doi:10.7910/DVN/2YAQ8D (returned HTTP 202, empty)", note="Academic dataset, not a published voting-intention release; provincial figure is a re-tabulation."),
    dict(pollster="Cardinal Research", field="2025-10-04 to 2025-10-06", figures="NDP 42.5, CPC 41.3, GRN 10, OneBC 3.8, other 2.5 (n=1,088, IVR)",
         seen_at="Wikipedia; https://cardinalresearch.ca/?research=british-columbia-provincial-poll-oct-2025", note="Proxy refused (CONNECT 502), retried once."),
    dict(pollster="EKOS", field="2025-11-20 to 2025-11-25", figures="NDP 44, CPC 35, GRN 9, OneBC 8, Centre 2, other 3 (n=889, phone)",
         seen_at="Wikipedia, cited to Polling Canada (canadianpolling.ca/BC-2024)", note="No EKOS release URL found."),
    dict(pollster="One Persuasion", field="2026-02-21 to 2026-02-24", figures="CPC 41, NDP 37, GRN 11, OneBC 6, other 5 (n=1,005, online)",
         seen_at="Rob Shaw X post (raw/one_persuasion/2031751527573111178.html) and Wikipedia", note="Privately commissioned; leaked to a journalist, no pollster release."),
    dict(pollster="Innovative Research Group", field="2026-02-06 to 2026-03-03", figures="NDP 39, CPC 47, GRN 10, other 4 (n=991, online)",
         seen_at="Wikipedia; https://innovativeresearch.ca/wp-content/uploads/2026/03/CTM2602-BC-Budget-Report-FINAL.pdf", note="URL returned an HTML 404 page."),
    dict(pollster="Fairview Strategy", field="2026-07-06 to 2026-07-17", figures="NDP 44, CPC 40, GRN 12, other 5 (n=896, online)",
         seen_at="Wikipedia, cited to Polling Canada and Sitka Media", note="No Fairview release URL found."),
    dict(pollster="Pollara (Hotel Pacifico podcast)", field="2026-10-01 to 2026-10-07", figures="NDP 38, CPC 41, GRN 11, OneBC 5, Centre 4, other 1 (n=1,438)",
         seen_at="Wikipedia, cited to YouTube episode 'Tax Me If You Can' at 4:24", note="YouTube returned HTTP 429; no written Pollara release."),
    dict(pollster="Pollara (Hotel Pacifico podcast)", field="2026-10-08 to 2026-10-13", figures="NDP 36, CPC 41, GRN 13, OneBC 5, Centre 4, other 1 (n=1,212)",
         seen_at="Wikipedia, cited to YouTube episode 'To Mars and Back' at 6:14", note="YouTube returned HTTP 429. Pollara Substack (Oct 16) confirms a wave 2 (n=1,483) but prints no horse race."),
    dict(pollster="Pollara (Hotel Pacifico podcast)", field="2026-10-15 to 2026-10-18", figures="NDP 36, CPC 43, GRN 12, OneBC 4, Centre 3, other 2 (n=973)",
         seen_at="Wikipedia, cited to YouTube episode 'Fully Completely' at 47:06", note="YouTube returned HTTP 429. Likely a partial read of the Oct 15-21 wave 3."),
]
EXCLUDED = [
    "Mainstreet Research, Surrey South riding poll, Oct 10-12 2026 (commissioned by the BC Conservatives): riding-level, not provincial. File raw/mainstreet_research/6ad12bf6cab94d5f98ddeead_surrey_south_october_2026.pdf.",
    "Yorkville Strategies first Nov 2025 study (n=800, CPC +8-9) mentioned in the principal's X thread but never published with figures.",
]

def num(x):
    try: return float(str(x).split()[0])
    except Exception: return None

P.sort(key=lambda r: (r["field_end"], r["pollster"]))
with open("polls.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
    for r in P: w.writerow(r)
    for n in NOT_OPENED:
        a, b = n["field"].split(" to ")
        w.writerow({**{c: "" for c in COLS}, "pollster": n["pollster"], "field_start": a, "field_end": b,
                    "release_status": "release not opened", "notes": f"Figures seen: {n['figures']}. Where seen: {n['seen_at']}. {n['note']}"})

# campaign list and final-week average
campaign = [r for r in P if r["field_end"] >= "2026-09-22"]
fw_start, fw_end = "2026-10-17", "2026-10-23"
last = {}
for r in P:
    if fw_start <= r["field_end"] <= fw_end:
        k = r["pollster"]
        if k not in last or r["field_end"] > last[k]["field_end"]: last[k] = r
avg = {}
for party in ["NDP", "Conservative", "Green", "OneBC", "CentreBC"]:
    vals = [num(r[party]) for r in last.values() if num(r[party]) is not None]
    avg[party] = (round(statistics.mean(vals), 1), len(vals))

with open("results.md", "w") as f:
    f.write("# BC 2026 provincial polls: official-release base\n\n")
    f.write(f"Built {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M} UTC by scripts/build.py from pollster releases in raw/. Full detail in polls.csv.\n\n")
    f.write(f"- Province-wide polls with pollster release opened: {sum(1 for r in P if r['release_status']=='opened')}; partly opened: {sum(1 for r in P if r['release_status']!='opened')}; release not opened: {len(NOT_OPENED)}.\n")
    f.write("- Vote shares are as printed by each pollster (decided, or decided + leaning). Bases differ; see population column.\n\n")
    f.write("## Final-week average (last poll by each pollster, field end Oct 17-23, 2026)\n\n")
    f.write("| Pollster | Field dates | NDP | CPC | GRN | OneBC | CentreBC |\n|---|---|---|---|---|---|---|\n")
    for r in sorted(last.values(), key=lambda r: r["field_end"]):
        f.write(f"| {r['pollster']} | {r['field_start']} to {r['field_end']} | {r['NDP']} | {r['Conservative']} | {r['Green']} | {r['OneBC'] or 'n/a'} | {r['CentreBC'] or 'n/a'} |\n")
    f.write(f"| **Simple average** | {len(last)} pollsters | **{avg['NDP'][0]}** | **{avg['Conservative'][0]}** | **{avg['Green'][0]}** | {avg['OneBC'][0]} (n={avg['OneBC'][1]}) | {avg['CentreBC'][0]} (n={avg['CentreBC'][1]}) |\n\n")
    f.write("Pollara uses its decided vote (Table 2), not its candidate-adjusted 'projected popular vote' (39/45/12). Mainstreet uses 'undecideds removed'. Innovative folds OneBC and CentreBC into 'other 7'. Pallas and Forum do not report OneBC/CentreBC separately.\n\n")
    f.write("## Campaign polls (field end Sept 22 to Oct 23, 2026)\n\n| Pollster | Field | n | Mode | NDP | CPC | GRN | Status |\n|---|---|---|---|---|---|---|---|\n")
    for r in campaign:
        f.write(f"| {r['pollster']} | {r['field_start']} to {r['field_end']} | {r['sample_size'].split(' ')[0]} | {r['mode']} | {r['NDP']} | {r['Conservative']} | {r['Green']} | {r['release_status']} |\n")
    for n in NOT_OPENED:
        if n["field"] >= "2026-09-22":
            f.write(f"| {n['pollster']} | {n['field']} | | | see note | | | release not opened |\n")
    f.write("\n## Seat projections published by pollsters\n\n")
    for r in P:
        if r["seat_projection"]:
            f.write(f"- {r['pollster']} ({r['field_start']} to {r['field_end']}): {r['seat_projection']} Source: {r['source_url']}\n")
    f.write("- No seat projection found in the Angus Reid, Leger, Ipsos, Research Co., Pallas, Liaison, Innovative or Pollara releases opened. Pollara's final release page was not opened.\n\n")
    f.write("## Release not opened (kept, flagged)\n\n")
    for n in NOT_OPENED:
        f.write(f"- {n['pollster']}, {n['field']}: {n['figures']}. Seen at: {n['seen_at']}. {n['note']}\n")
    f.write("\n## Excluded\n\n" + "".join(f"- {e}\n" for e in EXCLUDED))
print(len(P), "opened rows;", len(NOT_OPENED), "not opened;", len(campaign), "campaign;", "final-week avg", avg, sorted(last))
