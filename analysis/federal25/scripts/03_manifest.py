# Writes manifest.json (sources, access times, licences, sha256) for the federal25 layer.
import json, hashlib, os
R = "analysis/federal25"
def h(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
EC = "https://www.elections.ca/res/rep/off/ovrGE45/62/data_donnees/"
OGL = "Open Government Licence - Canada (https://open.canada.ca/en/open-government-licence-canada); stated on the open.canada.ca record for the 45th GE boundary files and on earlier Elections Canada poll-by-poll records; not separately confirmed for the 45th GE results record"
items = [
 ("raw/ec_results/pollresults_resultatsbureau59.zip", EC + "pollresults_resultatsbureau59.zip", "2026-10-24T10:07:41Z", "Elections Canada, 45th GE official voting results, poll results (long format), BC 43 ridings", OGL),
 ("raw/ec_results/pollbypoll_bureauparbureau59.zip", EC + "pollbypoll_bureauparbureau59.zip", "2026-10-24T10:07:41Z", "Elections Canada, 45th GE poll-by-poll (wide format), BC; downloaded for reference", OGL),
 ("raw/ec_results/table_tableau03.csv", EC + "table_tableau03.csv", "2026-10-24T10:07:44Z", "Table 3, valid/rejected ballots and electors by province (check totals)", OGL),
 ("raw/ec_results/table_tableau07.csv", EC + "table_tableau07.csv", "2026-10-24T10:07:42Z", "Table 7, candidates by party and gender (reference)", OGL),
 ("raw/ec_results/table_tableau08.csv", EC + "table_tableau08.csv", "2026-10-24T10:07:42Z", "Table 8, valid votes by party and province (check totals)", OGL),
 ("raw/ec_results/table_tableau11.csv", EC + "table_tableau11.csv", "2026-10-24T10:07:43Z", "Table 11, results by riding (reference)", OGL),
 ("raw/ec_results/table_tableau12.csv", EC + "table_tableau12.csv", "2026-10-24T10:07:43Z", "Table 12, candidate votes by riding (riding check)", OGL),
 ("raw/ec_geo/PollingDivisionBoundaries_2025_SHP.zip", "https://www.elections.ca/res/cir/mapsCorner/vector/PollingDivisionBoundaries_2025_SHP.zip", "2026-10-24T10:08:08Z", "Elections Canada polling division boundaries, 45th GE (2025), shapefile; found via open.canada.ca dataset 97a2a33c-54cc-4f2e-82c1-047ad8212f05", OGL),
 ("raw/ec_geo/package.json", "https://open.canada.ca/data/api/action/package_show?id=97a2a33c-54cc-4f2e-82c1-047ad8212f05", "2026-10-24T10:08Z (approx., fetched just before the shapefile)", "open.canada.ca record for the boundary files (licence evidence)", OGL),
 ("raw/statcan/2021_92-151_x_bc.csv", "https://catalogue.data.gov.bc.ca/dataset/4ed0c389-43ed-4b00-b1be-7c259f47b6a0/resource/6c8eeb86-bb56-48e8-b734-0d25d6a51a7b/download/2021_92-151_x_bc.csv", "2026-10-24T10:09:05Z", "Statistics Canada 2021 Geographic Attribute File (92-151-X), BC extract republished on BC Data Catalogue; source of 2021 dissemination block populations (DBPOP2021)", "Statistics Canada Open Licence (https://www.statcan.gc.ca/eng/reference/licence)"),
 ("raw/bcgw/db2021.geojson", "https://openmaps.gov.bc.ca/geo/pub/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=pub:WHSE_HUMAN_CULTURAL_ECONOMIC.CEN_CENSUS_DISSEM_BLOCKS_SVW&outputFormat=application/json&srsName=EPSG:3005 (paged, count=10000, sortBy=OBJECTID)", "2026-10-24T10:10:04Z", "2021 census dissemination block polygons (Statistics Canada, served by BC Geographic Warehouse), 52,423 features", "Statistics Canada Open Licence (https://www.statcan.gc.ca/eng/reference/licence)"),
 ("analysis/geo/raw/bcgw/ed2023.geojson", "https://openmaps.gov.bc.ca/geo/pub/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=pub:WHSE_ADMIN_BOUNDARIES.EBC_ELECTORAL_DISTS_BS11_SVW&outputFormat=application/json&srsName=EPSG:3005", "2026-10-24T10:03:34Z", "BC provincial electoral districts, 2023 boundaries (93), prepared by the geo thread; not land-clipped", "Open Government Licence - British Columbia"),
]
out = {"layer": "2025 federal election (BC) re-allocated to 2023 BC provincial electoral districts",
       "built_by": ["scripts/01_download_db.py", "scripts/02_allocate.py", "scripts/03_manifest.py"],
       "notes": "www12.statcan.gc.ca returned HTTP 403 (Cloudflare challenge) on 2026-10-24, so the BC Data Catalogue copies of the StatCan files were used.",
       "files": []}
for f, u, t, d, l in items:
    p = f if f.startswith("/") else os.path.join(R, f)
    out["files"].append({"path": f, "url": u, "accessed_utc": t, "description": d, "licence": l, "sha256": h(p)})
out["outputs"] = [{"path": p, "sha256": h(os.path.join(R, p))} for p in ["fed2025_on_ed2023.csv", "scripts/allocation_log.json"]]
json.dump(out, open(os.path.join(R, "manifest.json"), "w"), indent=1)
print("ok")
