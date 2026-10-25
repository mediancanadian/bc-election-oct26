#!/usr/bin/env python3
"""Extract links (href + anchor text) and visible text from an HTML file.
Usage: python3 -I links.py FILE [--text] [--grep PATTERN]
"""
import sys
import re
import html
from html.parser import HTMLParser


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.cur = None
        self.text = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag == "a":
            self.cur = [a.get("href", ""), ""]
        if tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr", "section", "article"):
            self.text.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
        if tag == "a" and self.cur is not None:
            self.links.append((self.cur[0], " ".join(self.cur[1].split())))
            self.cur = None

    def handle_data(self, data):
        if self.skip:
            return
        if self.cur is not None:
            self.cur[1] += data
        self.text.append(data)


def main():
    path = sys.argv[1]
    args = sys.argv[2:]
    with open(path, "rb") as f:
        raw = f.read().decode("utf-8", "replace")
    p = P()
    p.feed(raw)
    if "--text" in args:
        t = "".join(p.text)
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        t = re.sub(r"\n\s*\n+", "\n", t)
        print(t)
        return
    pat = None
    if "--grep" in args:
        pat = re.compile(args[args.index("--grep") + 1], re.I)
    seen = set()
    for href, txt in p.links:
        key = (href, txt)
        if key in seen:
            continue
        seen.add(key)
        if pat and not (pat.search(href) or pat.search(txt)):
            continue
        print(f"{href}\t{txt}")


if __name__ == "__main__":
    main()
