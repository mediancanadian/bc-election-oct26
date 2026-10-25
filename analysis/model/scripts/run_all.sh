#!/bin/sh
# Rebuild the pre-results estimate from inputs (does not freeze).
set -e
cd "$(dirname "$0")"
python3 01_regions.py
python3 02_poll_average.py
python3 03_project.py
# freeze (once, before 03:00 UTC Oct 25):  python3 04_freeze.py
# tonight:                                  python3 compare.py analysis/live/latest.csv
