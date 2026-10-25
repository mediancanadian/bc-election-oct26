"""Build manifest.json from scratch/dl.log. Usage: python3 -I make_manifest.py <root>"""
import sys, json, hashlib, os
R = sys.argv[1]
EBC = "Elections BC Open Data Licence (https://www.elections.bc.ca/docs/EBC-Open-Data-Licence.pdf)"
LIC = {"ebc_va_results": EBC, "ebc_vp_results": EBC, "ebc_edva_conv": EBC, "ebc_regvoters": EBC, "ebc_va_shp_2017": EBC,
       "ebc_sva_shp_2017": EBC, "ebc_voting_places": EBC, "bcgw_ed2023": EBC, "bcgw_va2024": EBC, "bcgw_vavp2024": EBC,
       "ebc_sov": "Elections BC publication (copyright Elections BC; no open licence stated on the PDF)",
       "ebc_ceo_reports": "Elections BC publication (copyright Elections BC; no open licence stated on the PDF)",
       "bcebc_reports": "Elections BC / BC Electoral Boundaries Commission publication (no open licence stated)",
       "ebc_licence": "Licence text itself",
       "leg_bc": "Legislative Assembly of BC website/API; copyright Legislative Assembly (see https://www.leg.bc.ca disclaimer/copyright)"}
items = []
for ln in open(f"{R}/scratch/dl.log"):
    ts, src, fn, code, size, url = ln.rstrip("\n").split("|", 5)
    p = f"raw/{src}/{fn}"
    h = hashlib.sha256(open(f"{R}/{p}", "rb").read()).hexdigest() if os.path.exists(f"{R}/{p}") else None
    items.append({"file": p, "url": url, "accessed_utc": ts, "http_status": int(code), "bytes": int(size), "sha256": h, "licence": LIC.get(src, "")})
items.append({"note": "StatCan 2021 Geographic Attribute File (dissemination block population) at https://www12.statcan.gc.ca/census-recensement/2021/geo/aip-pia/attribute-attribs/files-fichiers/2021_92-151_X.zip returned HTTP 403 (bot-check page) on 2026-10-24T10:06:15Z; not used, file deleted."})
json.dump({"generated_utc_from": "scratch/dl.log", "user_agent": "Mozilla/5.0 (X11; Linux x86_64) research-script", "files": items}, open(f"{R}/manifest.json", "w"), indent=1)
print(len(items))
