#!/usr/bin/env bash
# Usage: fetch.sh URL OUTNAME
# Downloads URL into analysis/next/raw/OUTNAME with a generic browser UA (no personal data),
# and appends a log line (UTC time, ET time, http code, bytes, sha256, final URL) to raw/fetchlog.tsv
set -u
URL="$1"
OUT="analysis/next/raw/$2"
LOG="analysis/next/raw/fetchlog.tsv"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
TS_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TS_ET=$(TZ=America/Toronto date +"%Y-%m-%d %H:%M %Z")
RES=$(curl -sS -L --max-time 90 -A "$UA" -H "Accept-Language: en-CA,en;q=0.9" -o "$OUT" -w "%{http_code}\t%{size_download}\t%{url_effective}" "$URL" 2>&1)
SHA=$( [ -f "$OUT" ] && sha256sum "$OUT" | cut -d' ' -f1 || echo "-")
printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$TS_UTC" "$TS_ET" "$URL" "$2" "$RES" "$SHA" >> "$LOG"
echo "$TS_UTC $RES -> $2"
