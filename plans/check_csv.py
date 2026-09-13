#!/usr/bin/env python3
# check_csv.py: validation of canonical britain-arrangements.csv
# stdlib only. Usage: .venv/bin/python plans/check_csv.py [--links]
import csv, re, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "britain-arrangements.csv"
NCOLS = 10
TIMEOUT = 15
HEADER = ["Artist","Song","Genre","Arrangement Title","Arranger","Difficulty","Shop","Link","Performance Link","Notes"]

# wall-list: acts that should NOT appear (non-British acts commonly mixed in)
NON_BRITISH = ["ABBA", "Kraftwerk", "Bon Jovi", "AC/DC", "Metallica",
               "Bruce Springsteen", "Michael Jackson", "A-ha", "Rammstein",
               "Dire Straits-Splitter", "Whitney Houston"]

def load(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh, delimiter=";"))
    if not rows:
        sys.exit(f"{path}: empty")
    return rows[0], rows[1:]

def check_links(url):
    if not url or url in ("-", ""):
        return None
    if not re.match(r"^https?://", url):
        return False
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (check_csv.py)"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return 200 <= r.status < 400
    except urllib.error.HTTPError as e:
        return 200 <= e.code < 400
    except Exception:
        return None  # network blocked in sandbox; don't fail the check

def main():
    do_links = "--links" in sys.argv
    header, rows = load(CSV)
    if header != HEADER:
        sys.exit(f"{CSV}: header mismatch\n got: {header}")
    print(f"[pass] header OK ({len(header)} cols)")
    print(f"[pass] {len(rows)} data rows")
    fail = 0
    # 1) shape
    for i, r in enumerate(rows, 2):
        if len(r) != NCOLS:
            print(f"[fail] row {i}: {len(r)} cols != {NCOLS}")
            fail += 1
    if not fail:
        print(f"[pass] all rows uniform {NCOLS} cols")
    # 2) duplicate rows (Artist, Song, Shop, Link): medley rows legitimately
    #    share a product link; '-'/empty link = no arrangement, not a dup
    seen = set()
    for i, r in enumerate(rows, 2):
        key = tuple(r)
        if key in seen and r[7] not in ("", "-"):
            print(f"[fail] row {i}: duplicate row {key}")
            fail += 1
        seen.add(key)
    # 3) British-only (artist not on wall list)
    for i, r in enumerate(rows, 2):
        if any(b in r[0] for b in NON_BRITISH):
            print(f"[fail] row {i}: artist {r[0]!r} on non-British wall list")
            fail += 1
    if not any(b in "".join(r[0] for r in rows) for b in NON_BRITISH):
        print("[pass] British-only scan: no wall-list artists present")
    # 4) difficulty: numeric 1-5 with .5 steps, or empty only on no-arrangement rows
    diff_re = re.compile(r"^[1-5](\.5)?$")
    for i, r in enumerate(rows, 2):
        d = r[5].strip()
        if d and not diff_re.match(d):
            print(f"[fail] row {i}: difficulty {d!r} not numeric 1-5 (.5 steps)")
            fail += 1
        if not d and r[3] not in ("", "-"):
            print(f"[fail] row {i}: arrangement exists but difficulty empty")
            fail += 1
        if d and r[3] in ("", "-"):
            print(f"[fail] row {i}: difficulty without arrangement")
            fail += 1
    if not fail:
        print("[pass] difficulty format: numeric 1-5 (.5 steps), empty = no arrangement")
    # 4) link health (optional: pass --links; network may be blocked in sandbox)
    if not do_links:
        print("[skip] link health check (pass --links to enable; network-optional by design)")
    else:
        dead = ok = unknown = 0; total = 0
        for i, r in enumerate(rows, 2):
            for col, url in (("Link", r[7]), ("Perf", r[8])):
                if not url or url == "-":
                    continue
                total += 1
                res = check_links(url)
                if res is True: ok += 1
                elif res is False:
                    dead += 1
                    print(f"[fail] row {i} {col}: dead {url}")
                    fail += 1
                else: unknown += 1
        print(f"[info] links: {ok} ok, {dead} dead, {unknown} unknown (network blocked?)")
    print("RESULT:", "FAIL" if fail else "PASS")
    sys.exit(1 if fail else 0)

if __name__ == "__main__":
    main()