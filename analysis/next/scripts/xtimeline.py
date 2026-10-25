#!/usr/bin/env python3
"""Parse X (Twitter) syndication timeline-profile HTML (__NEXT_DATA__) and print tweets.
Usage: python3 -I xtimeline.py FILE [--since 2026-10-24] [--full]
"""
import sys
import re
import json


def main():
    path = sys.argv[1]
    since = None
    if "--since" in sys.argv:
        since = sys.argv[sys.argv.index("--since") + 1]
    full = "--full" in sys.argv
    s = open(path, "rb").read().decode("utf-8", "replace")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', s, re.S)
    if not m:
        print("no __NEXT_DATA__")
        return
    d = json.loads(m.group(1))
    entries = d.get("props", {}).get("pageProps", {}).get("timeline", {}).get("entries", [])
    print(len(entries), "entries")
    for e in entries:
        t = e.get("content", {}).get("tweet")
        if not t:
            continue
        created = t.get("created_at", "")
        # created_at format like 'Sun Oct 25 04:34:51 +0000 2026'
        user = t.get("user", {}).get("screen_name", "")
        tid = t.get("id_str", "")
        text = t.get("full_text") or t.get("text") or ""
        rt = t.get("retweeted_status")
        if rt:
            text = "RT @" + rt.get("user", {}).get("screen_name", "") + ": " + (rt.get("full_text") or rt.get("text") or "")
        media = [x.get("media_url_https") for x in t.get("extended_entities", {}).get("media", [])] if t.get("extended_entities") else []
        line = f"{created} | @{user} | {tid} | {text if full else text[:280]} | media={media}"
        if since:
            # crude filter on year/month/day using parsed date
            mm = re.match(r"\w{3} (\w{3}) (\d{2}) (\d{2}:\d{2}:\d{2}) \+0000 (\d{4})", created)
            if mm:
                mon = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}[mm.group(1)]
                iso = f"{mm.group(4)}-{mon}-{mm.group(2)}"
                if iso < since:
                    continue
        print(line)


if __name__ == "__main__":
    main()
