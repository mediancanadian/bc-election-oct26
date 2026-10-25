#!/usr/bin/env bash
# Run fetch.py every 5 minutes for N hours (default 6). Usage: loop.sh <hours>
# Not started automatically; the main session schedules it.
set -u
HOURS="${1:-6}"
BASE=analysis/live
mkdir -p "$BASE/logs"
LOG="$BASE/logs/loop_$(date -u +%Y%m%dT%H%M%SZ).log"
END=$(( $(date +%s) + $(printf '%.0f' "$(echo "$HOURS * 3600" | bc)") ))
echo "$(date -u +%FT%TZ) loop start, hours=$HOURS, until $(date -u -d @$END +%FT%TZ)" >> "$LOG"
cd /tmp || exit 1   # neutral cwd: never run python from a download directory
while [ "$(date +%s)" -lt "$END" ]; do
  python3 -I "$BASE/scripts/fetch.py" >> "$LOG" 2>&1
  echo "$(date -u +%FT%TZ) exit=$?" >> "$LOG"
  NEXT=$(( $(date +%s) + 300 ))
  [ "$NEXT" -ge "$END" ] && break
  while [ "$(date +%s)" -lt "$NEXT" ]; do sleep 10; done
done
echo "$(date -u +%FT%TZ) loop end" >> "$LOG"
