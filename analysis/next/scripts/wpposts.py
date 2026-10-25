#!/usr/bin/env python3
"""Parse WordPress REST API posts JSON files and print index or full text.
Usage: python3 -I wpposts.py --index FILE [FILE...]
       python3 -I wpposts.py --text OUTFILE FILE [FILE...]
       python3 -I wpposts.py --grep PATTERN FILE [FILE...]
"""
import sys
import json
import re
import html as htmlmod


def strip_html(s):
    s = re.sub(r"(?is)<(script|style).*?</\1>", "", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|li|h[1-6]|div|tr|blockquote)>", "\n", s)
    s = re.sub(r"(?i)<li[^>]*>", "\n- ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmlmod.unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def load(files):
    posts = []
    for f in files:
        with open(f, "rb") as fh:
            data = json.loads(fh.read().decode("utf-8", "replace"))
        posts.extend(data)
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    return posts


def main():
    mode = sys.argv[1]
    if mode == "--index":
        posts = load(sys.argv[2:])
        print(len(posts), "posts")
        for p in posts:
            print(p.get("date"), "|", p.get("modified"), "|", htmlmod.unescape(p["title"]["rendered"]), "|", p.get("link"))
    elif mode == "--text":
        out = sys.argv[2]
        posts = load(sys.argv[3:])
        with open(out, "w", encoding="utf-8") as fo:
            for p in posts:
                fo.write("=" * 80 + "\n")
                fo.write(f"DATE: {p.get('date')}  MODIFIED: {p.get('modified')}\n")
                fo.write(f"TITLE: {htmlmod.unescape(p['title']['rendered'])}\n")
                fo.write(f"LINK: {p.get('link')}\n\n")
                fo.write(strip_html(p.get("content", {}).get("rendered", "")) + "\n")
                links = re.findall(r'href="([^"]+)"', p.get("content", {}).get("rendered", ""))
                if links:
                    fo.write("LINKS IN POST: " + " ; ".join(sorted(set(links))) + "\n")
        print("wrote", out, len(posts))
    elif mode == "--grep":
        pat = re.compile(sys.argv[2], re.I)
        posts = load(sys.argv[3:])
        for p in posts:
            t = strip_html(p.get("content", {}).get("rendered", ""))
            for line in t.split("\n"):
                if pat.search(line):
                    print(p.get("date")[:10], "|", p.get("slug"), "|", line.strip()[:400])


if __name__ == "__main__":
    main()
