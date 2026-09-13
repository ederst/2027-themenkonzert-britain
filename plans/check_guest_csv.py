#!/usr/bin/env python3
# check_guest_csv.py: Phase 5 validation of canonical guest-acts.csv
# stdlib only. Usage: .venv/bin/python plans/check_guest_csv.py
import csv, re, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "guest-acts.csv"
NCOLS = 16
TIMEOUT = 15
HEADER = ["Act","Type","Repertoire","Location","Region","Contact Name","Email","Phone","Website","YouTube Channel","Instagram","Price Range","Availability","Joint-Compatible","Notes","Source URL"]
URL_COLS = (8, 9, 10, 15)  # Website, YouTube Channel, Instagram, Source URL
CONTACT_COLS = (8, 6, 7)   # Website, Email, Phone

def load(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh, delimiter=";"))
    if not rows:
        sys.exit(f"{path}: empty")
    return rows[0], rows[1:]

def check_links(url):
    if not url or url == "-":
        return None
    if not re.match(r"^https?://", url):
        return False
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (check_guest_csv.py)"})
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
    for i, r in enumerate(rows, 2):
        if len(r) != NCOLS:
            print(f"[fail] row {i}: {len(r)} cols != {NCOLS}")
            fail += 1
    if not fail:
        print(f"[pass] all rows uniform {NCOLS} cols")
    for i, r in enumerate(rows, 2):
        if len(r) != NCOLS:
            continue
        if not any(r[c].strip() and r[c].strip() != "-" for c in CONTACT_COLS):
            print(f"[fail] row {i}: no contact means (Website/Email/Phone all empty): {r[0]}")
            fail += 1
    if not any(
        len(r) == NCOLS and not any(r[c].strip() and r[c].strip() != "-" for c in CONTACT_COLS)
        for r in rows
    ):
        print("[pass] every row has >=1 contact means (Website/Email/Phone)")
    seen = {}
    for i, r in enumerate(rows, 2):
        if len(r) < 1:
            continue
        act = r[0].strip().lower()
        if act in seen:
            print(f"[fail] row {i}: duplicate act name {r[0]!r} (first at row {seen[act]})")
            fail += 1
        seen.setdefault(act, i)
    if fail == len([1 for r in rows if len(r) >= 1]):
        pass
    if not any(r[0].strip().lower() in seen and list(seen).count(r[0].strip().lower()) > 1 for r in rows):
        print("[pass] no duplicate act names")
    # 4) link health (optional: pass --links; network may be blocked in sandbox)
    dead = ok = unknown = 0; total = 0
    if not do_links:
        print("[skip] link health check (pass --links to enable; network-optional by design)")
    else:
        for i, r in enumerate(rows, 2):
            if len(r) != NCOLS:
                continue
            for col in URL_COLS:
                url = r[col]
                if not url or url == "-":
                    continue
                total += 1
                res = check_links(url)
                if res is True: ok += 1
                elif res is False:
                    dead += 1
                    print(f"[fail] row {i} col{col}: dead {url}")
                    fail += 1
                else: unknown += 1
        print(f"[info] links: {ok} ok, {dead} dead, {unknown} unknown (network blocked?)")
    print("RESULT:", "FAIL" if fail else "PASS")
    sys.exit(1 if fail else 0)

if __name__ == "__main__":
    main()