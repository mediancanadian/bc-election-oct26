"""Download DA-level Population 2021 (char 1), Population 2016 (char 2) and Land area km2 (char 7) for all
7,848 BC dissemination areas from the Statistics Canada Census Profile SDMX API (DF_DA), total gender, counts.
www12.statcan.gc.ca returns a bot-check (403) to the shell; api.statcan.gc.ca works.
Output raw/statcan_sdmx/da_pop_area.csv (+ manifest entry). Generic User-Agent, no personal data.
"""
import csv, io, json, os, re, time, hashlib, datetime, urllib.request

ROOT = "analysis/census"
OUT = os.path.join(ROOT, "raw/statcan_sdmx")
API = "https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_DA/A5.{}.1.1+2+7.1"
HDR = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.sdmx.data+csv;version=1.0.0"}

t = open(os.path.join(OUT, "dsd_da.xml")).read()
s = t[t.find('Codelist id="CL_GEO_DA'):]
s = s[:s.find("</structure:Codelist>")]
das = re.findall(r'<structure:Code id="(2021S051259[^"]+)"', s)
print(len(das), "BC DAs in codelist", flush=True)
started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
rows, B = [], 300
for i in range(0, len(das), B):
    chunk = das[i:i + B]
    url = API.format("+".join(chunk))
    for a in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=600) as r:
                txt = r.read().decode("utf-8")
            break
        except Exception as e:
            print("retry", i, a, str(e)[:100], flush=True); time.sleep(10 * (a + 1))
    else:
        raise SystemExit("failed chunk %d" % i)
    for rec in csv.DictReader(io.StringIO(txt)):
        rows.append({k: rec[k] for k in ("REF_AREA", "ALT_GEO_CODE", "CHARACTERISTIC", "OBS_VALUE", "FLAG", "DATA_QUALITY_FLAG")})
    print(i + len(chunk), len(rows), flush=True)
fn = os.path.join(OUT, "da_pop_area.csv")
with open(fn, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
h = hashlib.sha256(open(fn, "rb").read()).hexdigest()
mp = os.path.join(ROOT, "raw/manifest_raw.json")
man = json.load(open(mp)) if os.path.exists(mp) else []
man = [m for m in man if m["file"] != "raw/statcan_sdmx/da_pop_area.csv"]
man.append({"file": "raw/statcan_sdmx/da_pop_area.csv", "url": API.format("<300 BC DGUIDs joined by +>") + " (Accept: SDMX-CSV 1.0)",
            "accessed_utc": started, "sha256": h, "rows": len(rows), "das_requested": len(das),
            "publisher": "Statistics Canada, Census Profile 2021 SDMX web service (dataflow STC_CP DF_DA v1.3)",
            "licence": "Statistics Canada Open Licence"})
json.dump(man, open(mp, "w"), indent=1)

# --- ADA (aggregate dissemination area): Population 2021 (1), Population 2016 (2), Land area (7); all ADAs, filtered to BC.
# Needed because 2016 population is "not applicable" (flag 2) at 2021 DA level but published for 2021 ADAs.
ADA_URL = "https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_ADA/A5..1.1+2+7.1?startPeriod=2021"
t0 = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
with urllib.request.urlopen(urllib.request.Request(ADA_URL, headers=HDR), timeout=600) as r:
    txt = r.read().decode("utf-8")
rows = [{k: rec[k] for k in ("REF_AREA", "ALT_GEO_CODE", "CHARACTERISTIC", "OBS_VALUE", "FLAG")}
        for rec in csv.DictReader(io.StringIO(txt)) if rec["REF_AREA"].startswith("2021S051659")]
fn = os.path.join(OUT, "ada_pop_area_bc.csv")
with open(fn, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
man = json.load(open(mp))
man = [m for m in man if m["file"] != "raw/statcan_sdmx/ada_pop_area_bc.csv"]
man.append({"file": "raw/statcan_sdmx/ada_pop_area_bc.csv", "url": ADA_URL + " (Accept: SDMX-CSV 1.0; rows filtered to BC ADAs 2021S051659*)",
            "accessed_utc": t0, "sha256": hashlib.sha256(open(fn, "rb").read()).hexdigest(), "rows": len(rows),
            "publisher": "Statistics Canada, Census Profile 2021 SDMX web service (dataflow STC_CP DF_ADA v1.3)",
            "licence": "Statistics Canada Open Licence"})
json.dump(man, open(mp, "w"), indent=1)
print("ADA rows", len(rows))
