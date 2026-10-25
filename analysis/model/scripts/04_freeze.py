"""Freeze the estimate: record UTC/Pacific timestamp, seats, toss-ups, and SHA-256 of every input
and output, then make the outputs read-only. Refuses to run after polls close (2026-10-25 03:00 UTC)
or if model_frozen.json already exists."""
import os, sys, json, hashlib, datetime, glob, stat
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, MODEL, OUT

CLOSE = datetime.datetime(2026, 10, 25, 3, 0, tzinfo=datetime.timezone.utc)
now = datetime.datetime.now(datetime.timezone.utc)
dest = os.path.join(MODEL, "model_frozen.json")
if os.path.exists(dest):
    sys.exit("already frozen: " + dest)
if now >= CLOSE:
    sys.exit("polls have closed; refusing to freeze")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


inputs = ["results24/out/districts_2024.csv", "results24/out/districts_2024_summary.csv",
          "polls/polls.csv", "live/candidates_2026.csv", "live/house_changes_2024_2026.csv",
          "geo/out/da_to_ed2023_detail.csv"]
outputs = sorted(glob.glob(os.path.join(OUT, "*.csv")) + glob.glob(os.path.join(OUT, "*.json")))
scripts = sorted(glob.glob(os.path.join(MODEL, "scripts", "*.py")))
s = json.load(open(os.path.join(OUT, "projection_summary.json")))
pa = json.load(open(os.path.join(OUT, "poll_average.json")))
pac = now.astimezone(datetime.timezone(datetime.timedelta(hours=-7)))
frozen = {
    "frozen_utc": now.isoformat(timespec="seconds"),
    "frozen_pacific": pac.isoformat(timespec="seconds") + " (PDT)",
    "polls_close_utc": CLOSE.isoformat(),
    "minutes_before_close": int((CLOSE - now).total_seconds() // 60),
    "poll_average": pa["province"], "polls_used": pa["polls_used"],
    "seats": s["seats"], "majority": 47,
    "tossups": {k: [t["ed_code"] for t in v] for k, v in s["tossups"].items()},
    "inputs_sha256": {i: sha(os.path.join(ROOT, i)) for i in inputs if os.path.exists(os.path.join(ROOT, i))},
    "outputs_sha256": {os.path.relpath(o, MODEL): sha(o) for o in outputs},
    "scripts_sha256": {os.path.relpath(o, MODEL): sha(o) for o in scripts},
}
json.dump(frozen, open(dest, "w"), indent=1)
for p in outputs + [dest]:
    os.chmod(p, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
print(json.dumps({k: frozen[k] for k in ("frozen_utc", "frozen_pacific", "minutes_before_close", "seats")}, indent=1))
