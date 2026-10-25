"""Shared helpers: paths, party-name normalisation, column detection."""
import csv, os, re

ROOT = "bc2026"
MODEL = os.path.join(ROOT, "model")
OUT = os.path.join(MODEL, "out")

# Canonical party codes used throughout the model
PARTY_ALIASES = {
    "NDP": ["ndp", "bc ndp", "new democratic", "bc new democratic party", "new democratic party"],
    "CON": ["con", "con.", "cons", "conservative", "bc conservative", "conservative party",
            "conservative party of british columbia", "bcc", "bc con"],
    "GRN": ["grn", "green", "bc green", "green party", "green party of british columbia", "bcg", "gp"],
    "CENTRE": ["centre", "centrebc", "centre bc", "bc centre", "cbc", "bcu", "bc united", "united"],
    "ONEBC": ["onebc", "one bc", "obc"],
}
MAIN = ["NDP", "CON", "GRN", "CENTRE", "ONEBC"]


def norm_party(p):
    s = re.sub(r"\s+", " ", str(p or "").strip().lower())
    for code, al in PARTY_ALIASES.items():
        if s == code.lower() or s in al:
            return code
    for code, al in PARTY_ALIASES.items():
        for a in al:
            if len(a) > 3 and a in s:
                return code
    return "OTH"


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def pick(cols, *cands, required=True):
    low = {c.lower().strip(): c for c in cols}
    for c in cands:
        if c in low:
            return low[c]
    for c in cands:
        for k, v in low.items():
            if c in k:
                return v
    if required:
        raise KeyError(f"none of {cands} in {cols}")
    return None


def num(x):
    s = str(x or "").replace(",", "").replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def tier(margin):
    """Tiers from the earlier post: toss-up <3, lean <8, likely <15, else safe (points)."""
    if margin < 3:
        return "toss-up"
    if margin < 8:
        return "lean"
    if margin < 15:
        return "likely"
    return "safe"
