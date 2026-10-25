#!/usr/bin/env python3
"""Find which PDF page(s) contain each search phrase (whitespace-insensitive).
Usage: python3 -I findpages.py PDF_TEXT_DIR PHRASE [PHRASE...]
PDF_TEXT_DIR holds files p001.txt ... produced by pdftotext per page.
"""
import sys
import os
import re


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"-\s*\n\s*", "", s)  # join hyphenated line breaks
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    d = sys.argv[1]
    pages = {}
    for f in sorted(os.listdir(d)):
        if f.endswith(".txt"):
            n = int(re.sub(r"\D", "", f))
            pages[n] = norm(open(os.path.join(d, f), encoding="utf-8", errors="replace").read())
    for ph in sys.argv[2:]:
        p = norm(ph)
        hits = [n for n, t in sorted(pages.items()) if p in t]
        print(f"{hits} :: {ph}")


if __name__ == "__main__":
    main()
