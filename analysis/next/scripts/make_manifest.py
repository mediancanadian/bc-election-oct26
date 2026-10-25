#!/usr/bin/env python3
"""Build manifest.json from raw/fetchlog.tsv plus manual entries (non-curl accesses).
Usage: python3 -I make_manifest.py analysis/next
"""
import sys
import os
import json
from urllib.parse import urlparse

base = sys.argv[1]
raw = os.path.join(base, "raw")

PRIMARY_HOSTS = {
    "conservativebc.ca": "primary: Conservative Party of BC (party website)",
    "www.conservativebc.ca": "primary: Conservative Party of BC (party website)",
    "elections.bc.ca": "primary: Elections BC",
    "results.elections.bc.ca": "primary: Elections BC results",
    "news.gov.bc.ca": "primary: Government of BC news",
    "ltgov.bc.ca": "primary: Office of the Lieutenant Governor",
    "www.ltgov.bc.ca": "primary: Office of the Lieutenant Governor",
    "www.leg.bc.ca": "primary: Legislative Assembly of BC",
    "www.bcndp.ca": "primary: BC NDP (party website)",
    "bcgreens.ca": "primary: BC Greens (party website)",
    "www.bcgreens.ca": "primary: BC Greens (party website)",
}


def role_for(url, status):
    h = urlparse(url).netloc
    if status not in ("200",):
        return "attempted: not used (HTTP " + status + ")"
    if "2102856519058669613" in url or "HS7YGCtaQAAKnZl" in url:
        return "primary: Conservative Party of BC official X account (@Conservative_BC), post and attached statement image"
    if "2114214081460855039" in url:
        return "primary: David Eby's own X account (@Dave_Eby), election-night post"
    if "timeline-profile" in url or "timeline/profile" in url:
        return "attempted: X embed timeline returned stale posts only; not used for facts"
    if "nitter" in h or "facebook.com" in h:
        return "attempted: not usable (block page / no posts); not used for facts"
    if "youtube.com" in h:
        return "primary: party YouTube channel metadata (titles, publish times); no transcript obtained"
    return PRIMARY_HOSTS.get(h, "other")


entries = []
with open(os.path.join(raw, "fetchlog.tsv"), encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 8:
            continue
        ts_utc, ts_et, url, local, status, size, final_url, sha = parts[:8]
        entries.append({
            "url": url,
            "final_url": final_url,
            "accessed_utc": ts_utc,
            "accessed_eastern": ts_et,
            "local_file": "raw/" + local,
            "http_status": int(status) if status.isdigit() else status,
            "bytes": int(size) if size.isdigit() else size,
            "sha256": sha,
            "method": "curl (generic browser user agent, no personal data)",
            "role": role_for(url, status),
        })

manual = [
    {"url": "https://www.conservativebc.ca/", "final_url": "https://conservativebc.ca/", "accessed_utc": "2026-10-25T12:28:21Z", "accessed_eastern": "2026-10-25 08:28 EDT", "local_file": "raw/conservativebc_home.html", "http_status": 200, "method": "curl", "role": "primary: Conservative Party of BC (party website), homepage used to find /plan/"},
    {"url": "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=6WQxxKzVrqM&format=json", "accessed_utc": "2026-10-25T12:35:06Z", "accessed_eastern": "2026-10-25 08:35 EDT", "local_file": "raw/yt_oembed/6WQxxKzVrqM.json", "http_status": 200, "method": "curl", "role": "primary: party YouTube video title 'LIVE: Election Night in BC' (author Conservative Party of BC)"},
    {"url": "https://www.youtube.com/oembed (9 other party video ids)", "accessed_utc": "2026-10-25T12:35:06Z to 12:35:08Z", "accessed_eastern": "2026-10-25 08:35 EDT", "local_file": "raw/yt_oembed/", "http_status": 200, "method": "curl", "role": "primary: party YouTube titles (metadata only)"},
    {"url": "https://www.youtube.com/api/timedtext?v=6WQxxKzVrqM&lang=en&kind=asr&fmt=json3", "accessed_utc": "2026-10-25T12:36:57Z", "accessed_eastern": "2026-10-25 08:36 EDT", "local_file": "raw/yt_timedtext_test.xml", "http_status": 200, "bytes": 0, "method": "curl", "role": "attempted: empty response, no captions obtained"},
    {"url": "https://conservativebc.ca/wp-content/uploads/2026/10/20261016_BCC_Platform2026_8-5x11-Draft-18_compressed.pdf", "accessed_utc": "2026-10-25T12:39:22Z", "accessed_eastern": "2026-10-25 08:39 EDT", "local_file": "(headers only)", "http_status": 200, "method": "curl header check", "role": "primary: last-modified: Mon, 19 Oct 2026 15:58:27 GMT"},
]
for m in manual:
    entries.append(m)

locators = [
    {"url": "https://www.narcity.com/b-c-conservatives-promise-2-6b-growth", "accessed_approx": "2026-10-25 ~12:27Z to 12:28Z (08:27 to 08:28 EDT)", "method": "WebFetch", "role": "locator only (Canadian Press via Narcity): told us the platform was a 71-page document released Oct 18; no fact taken from it"},
    {"url": "https://www.insauga.com/costed-b-c-conservative-platform-promises-2-6-b-in-growth-10-8b-deficit/", "accessed_approx": "2026-10-25 ~12:28Z", "method": "WebFetch", "role": "locator only: fetch failed"},
    {"url": "https://www.cp24.com/news/canada/2026/09/21/how-bc-conservatives-went-from-44-seats-to-a-party-in-turmoil/", "accessed_approx": "2026-10-25 ~12:32Z (08:32 EDT)", "method": "WebFetch", "role": "locator only: Findlay resignation Sept 20 and Doerkson interim appointment Sept 21 (news, unconfirmed by party source)"},
    {"url": "https://www.castanetkamloops.net/news/BC/634321/B-C-Conservatives-leader-Doerkson-rides-the-whirlwind-in-rise-from-obscurity", "accessed_approx": "2026-10-25 ~12:32Z", "method": "WebFetch", "role": "locator only: fetch failed"},
    {"url": "https://www.cp24.com/news/canada/2026/09/22/new-bc-conservative-leader-doerkson-to-appear-with-caucus-amid-election-speculation/", "accessed_approx": "2026-10-25 ~12:32Z", "method": "WebFetch", "role": "locator only"},
    {"url": "https://www.westernstandard.news/bc/bc-conservative-board-says-doerkson-stays-leader-if-the-party-wins/77278", "accessed_approx": "2026-10-25 ~12:33Z (08:33 EDT)", "method": "WebFetch", "role": "locator only: pointed to @Conservative_BC post 2102856519058669613, then verified on X"},
    {"url": "https://www.castanetkamloops.net/edition/news-story-632223-3-.htm", "accessed_approx": "2026-10-25 ~12:33Z", "method": "WebFetch", "role": "locator only"},
    {"url": "https://nationalnewswatch.com/2026/10/25/b-c-election-latest-conservatives-win-majority-in-election-eby-resigns-as-leader", "accessed_approx": "2026-10-25 ~12:34Z (08:34 EDT)", "method": "WebFetch", "role": "locator only: election-night timeline"},
    {"url": "https://www.cp24.com/politics/2026/10/25/bc-conservatives-win-majority-government-live-real-time-election-updates-here/", "accessed_approx": "2026-10-25 ~12:34Z (08:34 EDT)", "method": "WebFetch", "role": "locator only: pointed to @Dave_Eby post 2114214081460855039 (then verified on X); source of UNCONFIRMED Lowan quotes"},
    {"url": "https://dailyhive.com/vancouver/lorne-doerkson-david-eby-bc-ndp-conservative-election-night-speeches-full-text", "accessed_approx": "2026-10-25 ~12:36Z (08:36 EDT)", "method": "WebFetch", "role": "locator only: unattributed speech transcripts; source of UNCONFIRMED Doerkson and Eby speech quotes"},
    {"url": "https://www.theglobeandmail.com/canada/article-bc-election-david-eby-ndp-lorne-doerkson-conservatives/", "accessed_approx": "2026-10-25 ~12:37Z", "method": "WebFetch", "role": "locator only: blocked (robots)"},
    {"url": "https://www.cbc.ca/news/canada/british-columbia/bc-conservatives-majority-government-9.7394961", "accessed_approx": "2026-10-25 ~12:38Z", "method": "WebFetch", "role": "locator only: fetch failed"},
    {"url": "https://globalnews.ca/news/12114060/bc-election-day-2026-polls-live-results/", "accessed_approx": "2026-10-25 ~12:38Z", "method": "WebFetch", "role": "locator only: no party-channel posts embedded"},
]

out = {
    "project": "BC 2026 election post: platform, next steps, statements",
    "working_dir": base,
    "generated_utc": None,
    "privacy": "No personal details of the user were sent to any site; requests used a generic browser user agent only.",
    "sources_downloaded_or_checked": entries,
    "news_used_only_to_locate_documents": locators,
}
import datetime
out["generated_utc"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
with open(os.path.join(base, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("entries:", len(entries), "locators:", len(locators))
