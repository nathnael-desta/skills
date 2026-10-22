#!/usr/bin/env python3
"""Check which audit batches finished, by comparing verdict lines to test counts.

A subagent that runs out of context leaves a partial JSONL. This counts the test
functions each batch should contain and the verdict lines it holds, then writes the
batch ids still to run so the next dispatch is exactly the remainder.

batches.json: [{"id": "b001", "files": [{"path": "tests/a.py", "lines": "1-800" | null}]}]
Verdicts:     <out-dir>/<batch id>.jsonl, one JSON object per test.

    completeness.py batches.json --root . --out-dir out --state state.json
"""

import argparse
import json
import os
import re
import sys

TEST_DEF = re.compile(
    r"""^\s*(async\s+def\s+test_\w+|def\s+test_\w+|(it|test)(\.each\([^)]*\))?\(\s*['"`])"""
)


def expected(root, files):
    total = 0
    for f in files:
        with open(os.path.join(root, f["path"]), errors="ignore") as fh:
            lines = fh.read().splitlines()
        lo, hi = map(int, f["lines"].split("-")) if f.get("lines") else (1, len(lines))
        total += sum(1 for line in lines[lo - 1 : hi] if TEST_DEF.match(line))
    return total


def verdicts(path):
    seen = set()
    if os.path.exists(path):
        for line in open(path):
            try:
                row = json.loads(line)
            except ValueError:
                continue  # a half-written last line
            seen.add((row.get("file"), row.get("test"), row.get("line")))
    return len(seen)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("batches")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--state", default="state.json")
    ap.add_argument(
        "--threshold",
        type=float,
        default=0.9,
        help="fraction of expected tests that counts a batch as done",
    )
    args = ap.parse_args()

    done, todo = [], []
    for batch in json.load(open(args.batches)):
        want = expected(args.root, batch["files"])
        got = verdicts(os.path.join(args.out_dir, f"{batch['id']}.jsonl"))
        ok = got > 0 and (want == 0 or got / want >= args.threshold)
        (done if ok else todo).append((batch["id"], got, want))
    print(f"done {len(done)}, todo {len(todo)}")
    for batch_id, got, want in todo:
        print(f"  {batch_id}: {got}/{want}")
    json.dump(
        {"done": [d[0] for d in done], "todo": [t[0] for t in todo]},
        open(args.state, "w"),
        indent=1,
    )
    return 1 if todo else 0


if __name__ == "__main__":
    sys.exit(main())
