#!/usr/bin/env python3
"""Merge lane JSONs (research sources of truth) into britain-arrangements.csv.
Globs: tier1-results/lane-*.json, full-results/*.json, tier3-results/*.json.
Rules: full-row dedupe only where Link not in ("", "-"); genre sort order
[pop/rock, film, classical, folk] then artist then song; exact header with
spaces; semicolon delimiter, UTF-8, LF, no BOM.
"""
import csv
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "britain-arrangements.csv")
HEADER = ["Artist", "Song", "Genre", "Arrangement Title", "Arranger",
          "Difficulty", "Shop", "Link", "Performance Link", "Notes"]
GENRE_ORDER = ["pop/rock", "film", "classical", "folk"]
# lane JSON keys -> CSV header names
KEYMAP = {
    "artist": "Artist", "song": "Song", "genre": "Genre",
    "arrangement_title": "Arrangement Title", "arranger": "Arranger",
    "difficulty": "Difficulty", "shop": "Shop", "link": "Link",
    "performance_link": "Performance Link", "notes": "Notes",
}


def normalize(r):
    return {KEYMAP.get(k, k): v for k, v in r.items()}


def load_lanes():
    patterns = [
        os.path.join(HERE, "tier1-results", "lane-*.json"),
        os.path.join(HERE, "full-results", "*.json"),
        os.path.join(HERE, "tier3-results", "*.json"),
    ]
    files = []
    for pat in patterns:
        files.extend(sorted(glob.glob(pat)))
    rows = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            rows.extend(normalize(r) for r in json.load(fh))
    return rows


def dedupe(rows):
    seen = set()
    out = []
    for r in rows:
        key = tuple(r[h] for h in HEADER)
        if r["Link"] not in ("", "-"):
            if key in seen:
                continue
            seen.add(key)
        out.append(r)
    return out


def drop_obsolete_gaps(rows):
    """A gap(-) row is obsolete once any real row covers same artist+song,
    or once any real row exists for that artist when the gap is an
    artist-level placeholder (Song in ('-', ''))."""
    real_pairs = {(r["Artist"].lower(), r["Song"].lower()) for r in rows
                  if r["Link"] not in ("", "-")}
    real_artists = {a for a, _ in real_pairs}
    out = []
    for r in rows:
        if r["Link"] in ("", "-"):
            key = (r["Artist"].lower(), r["Song"].lower())
            if key in real_pairs:
                continue
            if r["Song"].strip() in ("-", "") and r["Artist"].lower() in real_artists:
                continue
        out.append(r)
    return out


def sort_key(r):
    try:
        g = GENRE_ORDER.index(r["Genre"].lower())
    except (ValueError, AttributeError):
        g = len(GENRE_ORDER)
    return (g, r["Artist"].lower(), r["Song"].lower())


def main():
    rows = drop_obsolete_gaps(dedupe(load_lanes()))
    rows.sort(key=sort_key)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER, delimiter=";")
        w.writeheader()
        w.writerows(rows)
    artists = {r["Artist"] for r in rows}
    gap = sum(1 for r in rows if r["Link"] in ("", "-"))
    print(f"[merge] {len(rows)} rows, {len(artists)} distinct artists, {gap} gap(-) rows")


if __name__ == "__main__":
    main()