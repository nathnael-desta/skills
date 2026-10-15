#!/usr/bin/env python3
"""Lines covered ONLY by a candidate set of tests, with every candidate removed together.

For each delete/merge candidate this reports how many source lines no test outside the
candidate set executes. A candidate with unique lines is the only guard of that code and
needs a human look before it is deleted. Coverage shows what a test runs, not what it
asserts: zero unique lines does not make a test worthless, and unique lines do not make
it valuable.

Produce the input with per-test contexts (dynamic contexts record which test ran a line):

    pytest --cov=<package> --cov-context=test --cov-branch tests/unit

Branch coverage stores executed lines in the `arc` table; line-only coverage uses
`line_bits`. This script reads whichever the data file holds.

Verdicts file: JSON list of {"file": "tests/x.py", "test": "name or Class::name",
"verdict": "delete|merge|..."}; only rows whose verdict is in --verdicts are candidates.

    unique_cov.py .coverage verdicts.json --out unique_cov.json
"""
import argparse
import collections
import json
import re
import sqlite3
import sys

NODE = re.compile(r"^(?P<file>[^:|]+?)::(?:.*::)?(?P<test>[^:\[|]+)")
TEST_FILE = r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]*\.py$|(^|/)conftest\.py$"
OUTSIDE = ("", "<outside-test>")  # import-time and fixture-free lines: never "lost"


def context_key(context):
    m = NODE.match(context or "")
    return (m.group("file"), m.group("test")) if m else OUTSIDE


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("coverage_db", help="SQLite .coverage file recorded with --cov-context=test")
    ap.add_argument("verdicts", help="JSON list of per-test verdicts")
    ap.add_argument("--out", default="unique_cov.json")
    ap.add_argument("--verdicts", dest="kinds", default="delete,merge",
                    help="comma-separated verdicts treated as candidates")
    ap.add_argument("--exclude", default=TEST_FILE,
                    help="regex of measured files to ignore (default: test files)")
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()

    kinds = set(args.kinds.split(","))
    cand = {}
    for row in json.load(open(args.verdicts)):
        if row.get("verdict") in kinds:
            base = row["test"].split("[")[0].split("::")[-1]
            cand[(row["file"], base)] = row

    con = sqlite3.connect(args.coverage_db)
    tables = {r[0] for r in con.execute("select name from sqlite_master where type='table'")}
    contexts = dict(con.execute("select id, context from context"))
    files = dict(con.execute("select id, path from file"))
    skip = re.compile(args.exclude)

    covered = collections.defaultdict(set)  # (path, line) -> {test keys}
    if "arc" in tables and con.execute("select 1 from arc limit 1").fetchone():
        for fid, cid, a, b in con.execute("select file_id, context_id, fromno, tono from arc"):
            if skip.search(files[fid]):
                continue
            key = context_key(contexts[cid])
            for n in (a, b):
                if n > 0:  # negative numbers are function entry/exit markers
                    covered[(files[fid], n)].add(key)
    else:
        from coverage.numbits import numbits_to_nums
        for fid, cid, bits in con.execute("select file_id, context_id, numbits from line_bits"):
            if skip.search(files[fid]):
                continue
            key = context_key(contexts[cid])
            for n in numbits_to_nums(bits):
                covered[(files[fid], n)].add(key)

    seen = {k for keys in covered.values() for k in keys if k in cand}
    unique = collections.defaultdict(list)
    candidates = set(cand)
    for place, keys in covered.items():
        if keys <= candidates:
            for k in keys:
                unique[k].append(place)

    out = []
    for key, row in cand.items():
        lines = unique.get(key, [])
        out.append({
            "file": key[0], "test": key[1], "verdict": row["verdict"],
            "in_coverage": key in seen,  # False: skipped, other suite, or name mismatch
            "unique_lines": len(lines),
            "sample": sorted(f"{p}:{n}" for p, n in lines)[:8],
        })
    json.dump(out, open(args.out, "w"), indent=1)

    print(f"candidates {len(cand)}, found in coverage {len(seen)}, "
          f"not in coverage {sum(not o['in_coverage'] for o in out)}")
    tally = collections.Counter((o["verdict"], o["unique_lines"] > 0) for o in out)
    for (verdict, has_unique), n in sorted(tally.items()):
        print(f"  {verdict}: {n} {'with' if has_unique else 'without'} unique lines")
    for o in sorted(out, key=lambda o: -o["unique_lines"])[: args.top]:
        if o["unique_lines"]:
            print(f"  {o['unique_lines']:4d} {o['verdict']} {o['file']}::{o['test']} {o['sample'][:3]}")


if __name__ == "__main__":
    sys.exit(main())
