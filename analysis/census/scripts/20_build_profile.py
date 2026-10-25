"""Build 2021 Census demographic profile for the 93 BC provincial electoral districts (2023 boundaries).
Primary source: BC Stats "Census Profiles for BC Provincial Electoral Districts", 2021 Census / 2023 Redistribution
(StatCan tabulation on the 93 districts; true district medians, rates and counts, randomly rounded).
Supplementary (not in the BC Stats file): Population 2016 and land area, built bottom-up:
  land area  = sum over 2021 dissemination blocks (GAF DBAREA2021, km2) x block-to-district fraction (geo thread db_to_ed2023.csv)
  pop 2016   = 2021 ADA "Population, 2016" (StatCan SDMX DF_ADA) shared to DAs by DA 2021 population within the ADA,
               then DA -> district by geo thread da_to_ed2023.csv pop_share. Approximation (assumes uniform 2016-21 growth
               inside an ADA where an ADA straddles a district boundary).
Outputs (out/): ed2023_profile.csv (wide), ed2023_profile_long.csv (every derived variable), bcstats_ped93_tidy.csv.gz
(every BC Stats cell, long), suppression_log.csv, checks.json.
"""
import os, json, re
import pandas as pd, numpy as np

ROOT = "analysis/census"; RAW = os.path.join(ROOT, "raw"); OUT = os.path.join(ROOT, "out")
GEO = "analysis/geo"
os.makedirs(OUT, exist_ok=True)
BC_TOTAL_2021 = 5000879

# ---------- district master list: Elections BC 2026 candidate list (codes+names) cross-checked to BCGW 2023 layer
cand = pd.read_csv("analysis/live/raw/candidates_2026_ebc.csv", dtype=str, encoding="cp1252",
                   usecols=["ED Code", "Electoral District"]).drop_duplicates()
cand.columns = ["ed_code", "ed_name"]
cand["ed_code"] = cand.ed_code.str.strip(); cand["ed_name"] = cand.ed_name.str.strip()
import geopandas as gpd
bcgw = gpd.read_file(os.path.join(GEO, "raw/bcgw/ed2023.geojson"), ignore_geometry=True)[["ED_ABBREVIATION", "ED_NAME"]]
chk = cand.merge(bcgw, left_on="ed_code", right_on="ED_ABBREVIATION", how="outer")
assert len(cand) == 93 and (chk.ed_name == chk.ED_NAME).all(), "district list mismatch"
eds = cand.sort_values("ed_code").reset_index(drop=True)

# ---------- BC Stats tidy
def load(part):
    d = pd.read_csv(os.path.join(RAW, "bcstats/census_profile_2021_ped93_%s.csv" % part), dtype=str, keep_default_na=False)
    d.columns = [c.strip() for c in d.columns]
    d["row"] = np.arange(len(d)) // 3 if False else d.groupby("Gender").cumcount()
    d["indent"] = d.Characteristics.str.len() - d.Characteristics.str.lstrip().str.len()
    d["char"] = d.Characteristics.str.replace("\xa0", " ").str.strip(); d["group"] = d["Characteristics Group"].str.replace("\xa0", " ").str.strip()
    d["part"] = part
    return d

P1, P2 = load("part1"), load("part2")
geo_cols = [c for c in P1.columns if c not in ("Census Profile", "Gender", "Characteristics", "Characteristics Group", "row", "indent", "char", "group", "part")]
assert geo_cols[0] == "British Columbia" and len(geo_cols) == 94
name2code = dict(zip(eds.ed_name, eds.ed_code))
assert set(geo_cols[1:]) == set(eds.ed_name), set(geo_cols[1:]) ^ set(eds.ed_name)

tidy = []
for d in (P1, P2):
    m = d.melt(id_vars=["part", "row", "group", "char", "indent", "Gender"], value_vars=geo_cols, var_name="geo", value_name="raw")
    tidy.append(m)
tidy = pd.concat(tidy, ignore_index=True)
tidy["ed_code"] = tidy.geo.map(name2code).fillna("BC")
tidy["value"] = pd.to_numeric(tidy.raw, errors="coerce")
tidy["flag"] = np.where(tidy.raw == "x", "x suppressed", np.where(tidy.raw == "...", "... not applicable", ""))
tidy[["part", "row", "group", "char", "indent", "Gender", "ed_code", "geo", "raw", "value", "flag"]].to_csv(
    os.path.join(OUT, "bcstats_ped93_tidy.csv.gz"), index=False, compression="gzip")

used = []  # (part,row) used, for suppression log


def get(part, group_prefix, char, gender="Total", nth=0):
    d = P1 if part == "part1" else P2
    s = d[(d.group.str.startswith(group_prefix)) & (d.char == char) & (d.Gender == gender)]
    if len(s) <= nth:
        raise KeyError((part, group_prefix, char))
    r = s.iloc[nth]
    used.append((part, int(r.row), gender, group_prefix, char))
    return pd.Series({name2code[g]: pd.to_numeric(r[g], errors="coerce") for g in geo_cols[1:]} | {"BC": pd.to_numeric(r["British Columbia"], errors="coerce")})


V = {}       # var -> Series indexed by ed_code (+BC)
META = {}    # var -> (unit, universe/denominator, source)


def put(name, s, unit, universe, source):
    V[name] = s; META[name] = (unit, universe, source)


def share(name, num, den, universe, source):
    put(name, (num / den * 100).round(2), "%", universe, source)


S1 = "BC Stats PED93 2021 part1 (100% data)"; S2 = "BC Stats PED93 2021 part2 (25% sample data)"
AG = "Age groups of the population - 100% data"
# Population and gender (100% data)
pop = get("part1", AG, "Total - Age groups of the population - 100% data")
put("pop_2021", pop, "persons", "Total population", S1)
put("pop_men_plus", get("part1", AG, "Total - Age groups of the population - 100% data", "Men+"), "persons", "Total population", S1)
put("pop_women_plus", get("part1", AG, "Total - Age groups of the population - 100% data", "Women+"), "persons", "Total population", S1)
share("pct_men_plus", V["pop_men_plus"], V["pop_men_plus"] + V["pop_women_plus"], "Men+ / (Men+ + Women+)", S1)
share("pct_women_plus", V["pop_women_plus"], V["pop_men_plus"] + V["pop_women_plus"], "Women+ / (Men+ + Women+)", S1)
# Age (100% data, 5-year bands)
a = {c: get("part1", AG, c) for c in ["0 to 14 years", "15 to 19 years", "20 to 24 years", "25 to 29 years", "30 to 34 years",
                                       "15 to 64 years", "65 years and over", "85 years and over"]}
put("age_0_14", a["0 to 14 years"], "persons", "Total population", S1)
put("age_15_19", a["15 to 19 years"], "persons", "Total population", S1)
put("age_20_34", a["20 to 24 years"] + a["25 to 29 years"] + a["30 to 34 years"], "persons", "Total population", S1)
put("age_35_64", a["15 to 64 years"] - a["15 to 19 years"] - V["age_20_34"], "persons", "Total population", S1)
put("age_65_plus", a["65 years and over"], "persons", "Total population", S1)
for k in ["age_0_14", "age_15_19", "age_20_34", "age_35_64", "age_65_plus"]:
    share("pct_" + k, V[k], pop, "Total population (100% data)", S1)
put("median_age", get("part1", "Distribution (%) of the population by broad age groups", "Median age of the population"), "years", "Total population", S1)
put("average_age", get("part1", "Distribution (%) of the population by broad age groups", "Average age of the population"), "years", "Total population", S1)
# Exact 0-17 / 18-64 / 65+ (LIM universe: population in private households, 25% sample)
LG = "LIM low-income status"
lim_tot = get("part2", LG, "Total - LIM low-income status in 2020 for the population in private households - 25% sample data")
put("age_0_17_privhh", get("part2", LG, "0 to 17 years", nth=0), "persons", "Population in private households (25% sample)", S2)
put("age_18_64_privhh", get("part2", LG, "18 to 64 years", nth=0), "persons", "Population in private households (25% sample)", S2)
put("age_65_plus_privhh", get("part2", LG, "65 years and over", nth=0), "persons", "Population in private households (25% sample)", S2)
for k in ["age_0_17_privhh", "age_18_64_privhh", "age_65_plus_privhh"]:
    share("pct_" + k, V[k], lim_tot, "Population in private households (25% sample)", S2)

# Income (25% sample; true district medians from StatCan tabulation)
IH = "Income statistics for private households"
put("hh_income_median", get("part2", IH, "Median total income of household in 2020 ($)"), "CAD 2020", "Private households", S2)
put("hh_income_median_after_tax", get("part2", IH, "Median after-tax income of household in 2020 ($)"), "CAD 2020", "Private households", S2)
put("hh_income_average", get("part2", IH, "Average total income of household in 2020 ($)"), "CAD 2020", "Private households", S2)
put("hh_income_average_after_tax", get("part2", IH, "Average after-tax income of household in 2020 ($)"), "CAD 2020", "Private households", S2)
II = "Income statistics in 2020 for the population aged 15 years and over"
put("ind_income_median", get("part2", II, "Median total income in 2020 among recipients ($)"), "CAD 2020", "Income recipients 15+ in private households", S2)
put("ind_income_average", get("part2", II, "Average total income in 2020 among recipients ($)"), "CAD 2020", "Income recipients 15+ in private households", S2)
put("pct_low_income_lim_at", get("part2", LG, "Prevalence of low income based on the Low-income measure, after tax (LIM-AT) (%)"), "%", "Population in private households (published rate)", S2)
put("low_income_lim_at", get("part2", LG, "In low income based on the Low-income measure, after tax (LIM-AT)"), "persons", "Population in private households", S2)
HG = "Household total income groups in 2020"
hb = {c: get("part2", HG, c) for c in ["Total - Household total income groups in 2020 for private households - 25% sample data",
      "Under $5,000", "$5,000 to $9,999", "$10,000 to $14,999", "$15,000 to $19,999", "$20,000 to $24,999", "$25,000 to $29,999",
      "$30,000 to $34,999", "$35,000 to $39,999", "$40,000 to $44,999", "$45,000 to $49,999", "$50,000 to $59,999",
      "$60,000 to $69,999", "$70,000 to $79,999", "$80,000 to $89,999", "$90,000 to $99,999", "$100,000 to $124,999",
      "$125,000 to $149,999", "$150,000 to $199,999", "$200,000 and over"]}
ks = list(hb)
hht = hb[ks[0]]
bands = {"hh_inc_under_50k": ks[1:11], "hh_inc_50k_100k": ks[11:16], "hh_inc_100k_150k": ks[16:18],
         "hh_inc_150k_200k": ks[18:19], "hh_inc_200k_plus": ks[19:20]}
for b, cs in bands.items():
    put(b, sum(hb[c] for c in cs), "households", "Private households", S2)
    share("pct_" + b, V[b], hht, "Private households (household total income 2020)", S2)

# Visible minority / Indigenous (25%)
VM = "Visible minority for the population in private households"
vmt = get("part2", VM, "Total - Visible minority for the population in private households - 25% sample data")
for c, k in [("Total visible minority population", "vm_total"), ("South Asian", "vm_south_asian"), ("Chinese", "vm_chinese"),
             ("Black", "vm_black"), ("Filipino", "vm_filipino"), ("Arab", "vm_arab"), ("Latin American", "vm_latin_american"),
             ("Southeast Asian", "vm_southeast_asian"), ("West Asian", "vm_west_asian"), ("Korean", "vm_korean"),
             ("Japanese", "vm_japanese"), ("Visible minority, n.i.e.", "vm_nie"), ("Multiple visible minorities", "vm_multiple"),
             ("Not a visible minority", "not_vm")]:
    put(k, get("part2", VM, c), "persons", "Population in private households", S2)
    share("pct_" + k, V[k], vmt, "Population in private households", S2)
IG = "Indigenous identity for the population in private households"
igt = get("part2", IG, "Total - Indigenous identity for the population in private households - 25% sample data")
for c, k in [("Indigenous identity", "indigenous"), ("First Nations (North American Indian)", "indigenous_first_nations"),
             ("Métis", "indigenous_metis"), ("Inuk (Inuit)", "indigenous_inuk")]:
    put(k, get("part2", IG, c), "persons", "Population in private households", S2)
    share("pct_" + k, V[k], igt, "Population in private households", S2)
# Immigration (25%)
IM = "Immigrant status and period of immigration"
imt = get("part2", IM, "Total - Immigrant status and period of immigration for the population in private households - 25% sample data")
for c, k in [("Immigrants", "immigrants"), ("2016 to 2021", "recent_immigrants_2016_2021"), ("Non-permanent residents", "non_permanent_residents"),
             ("Non-immigrants", "non_immigrants")]:
    put(k, get("part2", IM, c), "persons", "Population in private households", S2)
    share("pct_" + k, V[k], imt, "Population in private households", S2)
# Religion (25%), top-level categories (indent 2)
RG = "Religion for the population in private households"
rgt = get("part2", RG, "Total - Religion for the population in private households - 25% sample data")
for c, k in [("Buddhist", "rel_buddhist"), ("Christian", "rel_christian"), ("Catholic", "rel_catholic"), ("Hindu", "rel_hindu"),
             ("Jewish", "rel_jewish"), ("Muslim", "rel_muslim"), ("Sikh", "rel_sikh"),
             ("Traditional (North American Indigenous) spirituality", "rel_indigenous_spirituality"),
             ("Other religions and spiritual traditions", "rel_other"), ("No religion and secular perspectives", "rel_none_secular")]:
    put(k, get("part2", RG, c), "persons", "Population in private households", S2)
    share("pct_" + k, V[k], rgt, "Population in private households", S2)

# Housing
TN = "Private households by tenure"
tnt = get("part2", TN, "Total - Private households by tenure - 25% sample data")
for c, k in [("Owner", "hh_owner"), ("Renter", "hh_renter"), ("Dwelling provided by the local government, First Nation or Indian band", "hh_band_housing")]:
    put(k, get("part2", TN, c), "households", "Private households", S2)
    share("pct_" + k, V[k], tnt, "Private households", S2)
SC = "Owner and tenant households with household total income greater than zero, in non-farm, non-reserve private dwellings by shelter-cost"
sct = get("part2", SC, "Total - Owner and tenant households with household total income greater than zero, in non-farm, non-reserve private dwellings by shelter-cost-to-income ratio - 25% sample data")
put("hh_shelter_30plus", get("part2", SC, "Spending 30% or more of income on shelter costs"), "households", "Owner+tenant hh, income>0, non-farm non-reserve", S2)
share("pct_hh_shelter_30plus", V["hh_shelter_30plus"], sct, "Owner+tenant hh, income>0, non-farm non-reserve", S2)
CN = "Owner and tenant households with household total income greater than zero and shelter-cost-to-income ratio less than 100%"
cnt = get("part2", CN, "Total - Owner and tenant households with household total income greater than zero and shelter-cost-to-income ratio less than 100%, in non-farm, non-reserve private dwellings - 25% sample data")
put("hh_core_need", get("part2", CN, "In core need"), "households", "Owner+tenant hh, income>0, STIR<100%, non-farm non-reserve", S2)
share("pct_hh_core_need", V["hh_core_need"], cnt, "Owner+tenant hh, income>0, STIR<100%, non-farm non-reserve", S2)
put("pct_tenant_shelter_30plus", get("part2", "Tenant households in non-farm", "% of tenant households spending 30% or more of its income on shelter costs"), "%", "Tenant households (published rate)", S2)
put("median_dwelling_value", get("part2", "Owner households in non-farm", "Median value of dwellings ($)"), "CAD", "Owner households, non-farm non-reserve", S2)
put("median_rent", get("part2", "Tenant households in non-farm", "Median monthly shelter costs for rented dwellings ($)"), "CAD/month", "Tenant households, non-farm non-reserve", S2)
CD = "Occupied private dwellings by condominium status"
cdt = get("part2", CD, "Total - Occupied private dwellings by condominium status - 25% sample data")
put("dw_condo", get("part2", CD, "Condominium"), "dwellings", "Occupied private dwellings", S2)
share("pct_dw_condo", V["dw_condo"], cdt, "Occupied private dwellings", S2)
DT = "Occupied private dwellings by structural type of dwelling - 100% data"
dtt = get("part1", DT, "Total - Occupied private dwellings by structural type of dwelling - 100% data")
put("dw_single_detached", get("part1", DT, "Single-detached house"), "dwellings", "Occupied private dwellings", S1)
put("dw_apartment", get("part1", DT, "Apartment or flat in a duplex") + get("part1", DT, "Apartment in a building that has fewer than five storeys")
    + get("part1", DT, "Apartment in a building that has five or more storeys"), "dwellings", "Occupied private dwellings", S1)
put("dw_apartment_5plus_storeys", get("part1", DT, "Apartment in a building that has five or more storeys"), "dwellings", "Occupied private dwellings", S1)
for k in ["dw_single_detached", "dw_apartment", "dw_apartment_5plus_storeys"]:
    share("pct_" + k, V[k], dtt, "Occupied private dwellings (100% data)", S1)

# Education
ED = "Highest certificate, diploma or degree for the population aged 25 to 64"
edt = get("part2", ED, "Total - Highest certificate, diploma or degree for the population aged 25 to 64 years in private households - 25% sample data")
put("bachelor_plus_25_64", get("part2", ED, "Bachelor’s degree or higher"), "persons", "Population 25-64 in private households", S2)
share("pct_bachelor_plus_25_64", V["bachelor_plus_25_64"], edt, "Population 25-64 in private households", S2)
put("no_certificate_25_64", get("part2", ED, "No certificate, diploma or degree"), "persons", "Population 25-64 in private households", S2)
share("pct_no_certificate_25_64", V["no_certificate_25_64"], edt, "Population 25-64 in private households", S2)
ED15 = "Highest certificate, diploma or degree for the population aged 15 years"
ed15t = get("part2", ED15, "Total - Highest certificate, diploma or degree for the population aged 15 years and over in private households - 25% sample data")
put("bachelor_plus_15plus", get("part2", ED15, "Bachelor’s degree or higher"), "persons", "Population 15+ in private households", S2)
share("pct_bachelor_plus_15plus", V["bachelor_plus_15plus"], ed15t, "Population 15+ in private households", S2)
# Labour
LF = "Population aged 15 years and over by labour force status"
put("participation_rate", get("part2", LF, "Participation rate"), "%", "Population 15+ (published rate)", S2)
put("employment_rate", get("part2", LF, "Employment rate"), "%", "Population 15+ (published rate)", S2)
put("unemployment_rate", get("part2", LF, "Unemployment rate"), "%", "Labour force 15+ (published rate; May 2021 reference week)", S2)
IN = "Labour force aged 15 years and over by industry"
ind_all = get("part2", IN, "All industries")
inds = P2[(P2.group.str.startswith(IN)) & (P2.Gender == "Total") & P2.char.str.match(r"^\d")].char.tolist()
indv = {}
for c in inds:
    k = "ind_" + re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_")
    indv[c] = get("part2", IN, c)
    share("pct_" + k, indv[c], ind_all, "Labour force 15+ with an industry", S2)
# Commute
CM = "Main mode of commuting"
cmt = get("part2", CM, "Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data")
for c, k in [("Car, truck or van", "commute_car"), ("Public transit", "commute_transit"), ("Walked", "commute_walk"), ("Bicycle", "commute_bike"),
             ("Other method", "commute_other")]:
    put(k, get("part2", CM, c), "persons", "Employed 15+ commuters (usual place / no fixed address)", S2)
    share("pct_" + k, V[k], cmt, "Employed 15+ commuters", S2)
put("commute_walk_bike", V["commute_walk"] + V["commute_bike"], "persons", "Employed 15+ commuters", S2)
share("pct_commute_walk_bike", V["commute_walk_bike"], cmt, "Employed 15+ commuters", S2)
PW = "Place of work status"
pwt = get("part2", PW, "Total - Place of work status for the employed labour force aged 15 years and over - 25% sample data")
put("worked_at_home", get("part2", PW, "Worked at home"), "persons", "Employed labour force 15+", S2)
share("pct_worked_at_home", V["worked_at_home"], pwt, "Employed labour force 15+ (May 2021, pandemic period)", S2)

# Languages: leaves under 'Single responses > Non-official languages' (part2 most often at home, part1 mother tongue 100%)
def leaves(d, group_prefix):
    s = d[(d.group.str.startswith(group_prefix)) & (d.Gender == "Total")].reset_index(drop=True)
    out = []; in_nonoff = False; base = None
    for i, r in s.iterrows():
        if r.char == "Non-official languages" and base is None:
            in_nonoff, base = True, r.indent; continue
        if in_nonoff and r.indent <= base:
            break
        if in_nonoff:
            nxt = s.indent.iloc[i + 1] if i + 1 < len(s) else -1
            if nxt <= r.indent:
                out.append(r)
    return out, s

LANG = {}
for part, d, gp, tag in [("part2", P2, "Language spoken most often at home", "home"), ("part1", P1, "Mother tongue for the total population excluding institutional residents - 100% data", "mt")]:
    lv, s = leaves(d, gp)
    tot_row = s.iloc[0]
    tot = pd.Series({name2code[g]: pd.to_numeric(tot_row[g], errors="coerce") for g in geo_cols[1:]} | {"BC": pd.to_numeric(tot_row["British Columbia"], errors="coerce")})
    used.append((part, int(tot_row.row), "Total", gp, tot_row.char))
    eng_row = s[s.char == "English"].iloc[0]
    eng = pd.Series({name2code[g]: pd.to_numeric(eng_row[g], errors="coerce") for g in geo_cols[1:]} | {"BC": pd.to_numeric(eng_row["British Columbia"], errors="coerce")})
    share("pct_lang_%s_english" % tag, eng, tot, "Total pop. excl. institutional residents (single responses)", S2 if part == "part2" else S1)
    frame = pd.DataFrame({r.char: pd.Series({name2code[g]: pd.to_numeric(r[g], errors="coerce") for g in geo_cols[1:]} | {"BC": pd.to_numeric(r["British Columbia"], errors="coerce")}) for r in lv})
    frame = frame.loc[:, ~frame.columns.duplicated()]
    LANG[tag] = (frame, tot)
    for r in lv:
        used.append((part, int(r.row), "Total", gp, r.char))
    top = frame.loc["BC"].sort_values(ascending=False).head(10).index
    for c in top:
        k = "pct_lang_%s_" % tag + re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_")
        share(k, frame[c], tot, "Total pop. excl. institutional residents", S2 if part == "part2" else S1)

# ---------- supplementary: land area (DB) and pop 2016 (ADA -> DA -> ED)
gaf = pd.read_csv(os.path.join(GEO, "raw/statcan/2021_92-151_x_bc.csv"), dtype=str, encoding="latin-1",
                  usecols=["DBUID_IDIDU", "DAUID_ADIDU", "DADGUID_ADIDUGD", "DBPOP2021_IDPOP2021", "DBAREA2021_IDSUP2021", "ADADGUID_ADAIDUGD"])
gaf.columns = ["DAUID", "DADGUID", "DBUID", "dbpop", "dbarea", "ADADGUID"]
gaf["dbarea"] = pd.to_numeric(gaf.dbarea); gaf["dbpop"] = pd.to_numeric(gaf.dbpop)
db2ed = pd.read_csv(os.path.join(GEO, "out/db_to_ed2023.csv"), dtype={"DBUID": str, "DAUID": str})
x = db2ed.merge(gaf[["DBUID", "dbarea"]], on="DBUID", how="left", validate="m:1")
assert x.dbarea.notna().all()
land = (x.dbarea * x.frac).groupby(x.ED_ABBREVIATION).sum()
land["BC"] = gaf.dbarea.sum()
put("land_area_km2", land.round(2), "km2", "Land area of 2021 dissemination blocks allocated to district", "StatCan GAF 2021 DB land area x geo/out/db_to_ed2023.csv")
put("density_per_km2", (V["pop_2021"] / V["land_area_km2"]).round(1), "persons/km2", "pop_2021 / land_area_km2", "derived")

da = pd.read_csv(os.path.join(RAW, "statcan_sdmx/da_pop_area.csv"), dtype=str)
dap = da[da.CHARACTERISTIC == "1"].set_index("REF_AREA")
da_pop = pd.to_numeric(dap.OBS_VALUE)
ada = pd.read_csv(os.path.join(RAW, "statcan_sdmx/ada_pop_area_bc.csv"), dtype=str)
ada16 = ada[ada.CHARACTERISTIC == "2"].set_index("REF_AREA")
ada21 = pd.to_numeric(ada[ada.CHARACTERISTIC == "1"].set_index("REF_AREA").OBS_VALUE)
da2ada = gaf[["DADGUID", "ADADGUID"]].drop_duplicates().set_index("DADGUID").ADADGUID
assert da2ada.index.is_unique and set(da2ada.index) == set(da_pop.index)
dd = pd.DataFrame({"pop21": da_pop.reindex(da2ada.index).fillna(0), "ada": da2ada})
dd["ada_pop21_sum"] = dd.groupby("ada").pop21.transform("sum")
dd["ada_pop16"] = pd.to_numeric(ada16.OBS_VALUE.reindex(dd.ada).values, errors="coerce")
dd["ada_n_da"] = dd.groupby("ada").pop21.transform("size")
dd["w"] = np.where(dd.ada_pop21_sum > 0, dd.pop21 / dd.ada_pop21_sum.replace(0, np.nan), 1 / dd.ada_n_da)
dd["pop16"] = dd.ada_pop16 * dd.w
xw = pd.read_csv(os.path.join(GEO, "out/da_to_ed2023.csv"))
assert set(xw.dguid) == set(dd.index), "crosswalk does not cover all DAs"
xx = xw.merge(dd, left_on="dguid", right_index=True)
pop16 = (xx.pop16 * xx.pop_share).groupby(xx.ed_code).sum(min_count=1)
pop16["BC"] = pd.to_numeric(ada16.OBS_VALUE, errors="coerce").sum()
put("pop_2016_approx", pop16.round(0), "persons", "2016 population on 2021 ADA geography, allocated to 2021 DAs by 2021 pop then to districts",
    "StatCan SDMX DF_ADA (Population, 2016) + DF_DA (Population, 2021) + geo/out/da_to_ed2023.csv")
put("pop_2021_from_da", (xx.pop21 * xx.pop_share).groupby(xx.ed_code).sum().round(1).reindex(list(eds.ed_code)).fillna(0).pipe(lambda s: pd.concat([s, pd.Series({"BC": da_pop.sum()})])),
    "persons", "Total population (DA rollup cross-check)", "StatCan SDMX DF_DA + geo/out/da_to_ed2023.csv")
put("pop_growth_2016_2021_pct_approx", ((V["pop_2021_from_da"] / V["pop_2016_approx"] - 1) * 100).round(2), "%",
    "pop_2021_from_da / pop_2016_approx - 1 (same allocation for both years)", "derived")

# ---------- top industries per district
order = list(eds.ed_code)
indf = pd.DataFrame(indv)
top_ind = {}
for code in order + ["BC"]:
    r = indf.loc[code].sort_values(ascending=False).head(3)
    top_ind[code] = ["%s (%.1f%%)" % (re.sub(r"^[\d\-]+ ", "", c), v / ind_all[code] * 100) for c, v in r.items()]
# top 3 non-English home languages per district
fr, tot = LANG["home"]
top_lang = {code: ["%s (%.1f%%)" % (c, v / tot[code] * 100) for c, v in fr.loc[code].sort_values(ascending=False).head(3).items()] for code in order + ["BC"]}

# ---------- assemble
wide = pd.DataFrame(V).reindex(order + ["BC"])
wide.insert(0, "ed_name", list(eds.ed_name) + ["British Columbia"])
wide.index.name = "ed_code"
for i in range(3):
    wide["top_industry_%d" % (i + 1)] = [top_ind[c][i] for c in wide.index]
    wide["top_home_language_non_english_%d" % (i + 1)] = [top_lang[c][i] for c in wide.index]
# suppression per district among used cells
usedset = pd.DataFrame(used, columns=["part", "row", "Gender", "grp", "char"]).drop_duplicates(["part", "row", "Gender"])
tk = tidy.merge(usedset[["part", "row", "Gender"]], on=["part", "row", "Gender"])
sup = tk[tk.flag != ""].groupby(["ed_code", "flag"]).size().unstack(fill_value=0)
wide["n_cells_used"] = tk.groupby("ed_code").size().reindex(wide.index)
wide["n_cells_suppressed_x"] = sup.get("x suppressed", pd.Series(dtype=int)).reindex(wide.index).fillna(0).astype(int)
wide["n_cells_not_applicable"] = sup.get("... not applicable", pd.Series(dtype=int)).reindex(wide.index).fillna(0).astype(int)
tidy[tidy.flag != ""].groupby(["ed_code", "part", "group", "char", "Gender", "flag"]).size().rename("n").reset_index().to_csv(
    os.path.join(OUT, "suppression_log.csv"), index=False)
wide.reset_index().to_csv(os.path.join(OUT, "ed2023_profile.csv"), index=False)

long = wide.drop(columns=["ed_name"]).reset_index().melt(id_vars="ed_code", var_name="variable", value_name="value")
long = long.merge(eds.rename(columns={"ed_name": "ed_name"}), on="ed_code", how="left")
long.loc[long.ed_code == "BC", "ed_name"] = "British Columbia"
long["unit"] = long.variable.map(lambda v: META.get(v, ("text" if v.startswith("top_") else "count", "", ""))[0])
long["universe"] = long.variable.map(lambda v: META.get(v, ("", "", ""))[1])
long["source"] = long.variable.map(lambda v: META.get(v, ("", "", S2 if v.startswith("top_") else "derived (QA)"))[2])
long[["ed_code", "ed_name", "variable", "value", "unit", "universe", "source"]].to_csv(os.path.join(OUT, "ed2023_profile_long.csv"), index=False)

# ---------- checks
geo_pop = pd.read_csv(os.path.join(GEO, "out/ed2023_pop2021_from_db.csv")).set_index("ED_ABBREVIATION").pop2021
d_bcs_vs_db = (wide.loc[order, "pop_2021"] - geo_pop.reindex(order))
checks = {
    "n_districts": int(len(order)),
    "names_match_elections_bc_2026_and_bcgw_2023": True,
    "sum_pop_2021_bcstats_districts": int(wide.loc[order, "pop_2021"].sum()),
    "bc_total_official": BC_TOTAL_2021,
    "bcstats_bc_column_pop_2021": int(wide.loc["BC", "pop_2021"]),
    "diff_sum_vs_official": int(wide.loc[order, "pop_2021"].sum() - BC_TOTAL_2021),
    "sum_pop_2021_da_rollup": round(float(wide.loc[order, "pop_2021_from_da"].sum()), 1),
    "max_abs_diff_bcstats_vs_db_allocation_persons": float(d_bcs_vs_db.abs().max().round(1)),
    "max_abs_diff_bcstats_vs_db_allocation_pct": float((d_bcs_vs_db / wide.loc[order, "pop_2021"] * 100).abs().max().round(3)),
    "worst_district_vs_db": d_bcs_vs_db.abs().idxmax(),
    "sum_land_area_km2": round(float(wide.loc[order, "land_area_km2"].sum()), 2), "bc_land_area_gaf_km2": round(float(gaf.dbarea.sum()), 2),
    "sum_pop_2016_approx": round(float(wide.loc[order, "pop_2016_approx"].sum()), 0),
    "bc_pop_2016_ada_sum": float(pd.to_numeric(ada16.OBS_VALUE, errors="coerce").sum()),
    "ada_2016_flags": ada16.FLAG.fillna("none").value_counts().to_dict(),
    "ada_2016_missing_value_adas": int(pd.to_numeric(ada16.OBS_VALUE, errors="coerce").isna().sum()),
    "da_count": int(len(dd)), "da_pop2021_flag1_not_available": int((dap.FLAG == "1").sum()),
    "da_crosswalk_rows": int(len(xw)), "da_crosswalk_unique_das": int(xw.dguid.nunique()),
    "bcstats_cells_total": int(len(tidy)), "bcstats_cells_x_suppressed": int((tidy.flag == "x suppressed").sum()),
    "bcstats_cells_not_applicable": int((tidy.flag == "... not applicable").sum()),
    "used_cells_x_suppressed": int((tk.flag == "x suppressed").sum()), "used_cells_not_applicable": int((tk.flag == "... not applicable").sum()),
    "variables_wide": int(wide.shape[1] - 1),
}
json.dump(checks, open(os.path.join(OUT, "checks.json"), "w"), indent=1, default=str)
print(json.dumps(checks, indent=1, default=str))
