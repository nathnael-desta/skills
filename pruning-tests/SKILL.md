---
name: pruning-tests
description: Audit an existing test suite and remove, merge, or rewrite low-value tests without losing a real guard. Load when the user asks to clean up, trim, de-bloat, or judge the quality of a whole suite or a set of test files, or when a suite grew mostly from agent-written tests. For adding a single test, load writing-tests instead.
---

# Pruning tests

Goal: a suite where every test catches a bug that matters, and no test is deleted on a guess. A cheap model proposes; coverage and a stronger model check; the user approves per file; only then does anything change.

**Never act on the first pass alone.** In one audit a spot-check by a stronger model, over 84 sampled verdicts, agreed with 20 of 24 deletes (3 of the 24 would have removed the only test of a real guard), 16 of 24 merges, 11 of 21 rewrites, and 14 of 15 keeps. The cheap pass is a candidate generator, not a verdict.

Rubric the auditors apply (fill its project block first): [references/rubric.md](references/rubric.md). Briefs for the later stages: [references/briefs.md](references/briefs.md).

## Process

1. **Batch.** List every test file with its line count; group into batches of about 800 lines. Split a larger file by line range; each range audits the tests whose definition starts inside it. Write `batches.json`. Done when every test file sits in exactly one batch.
2. **First pass on a cheap model**, a few batches at a time, named by exact model ID. Each brief carries the rubric path, the batch, and an output path. Each subagent appends one JSONL verdict per test the moment it decides, so one that runs out of context leaves its finished verdicts on disk. Subagents edit nothing and start no servers or full suites.
3. **Check completeness.** `python3 scripts/completeness.py batches.json --root <repo> --out-dir out` compares verdict lines to test counts and writes the batch ids still to run. Re-dispatch exactly those. Done when no batch is short (a dispatch that dies midway is normal; resume, do not restart).
4. **Merge** the JSONL into one table: file, test, verdict, category, bug_caught. Expect most rows `keep`; in one audit of 5,882 tests the first pass said 4,969 keep, 678 rewrite, 155 merge, 72 delete, 8 move_down.
5. **Per-test coverage with contexts**, on the delete and merge candidates. Run the unit suite once with `pytest --cov=<pkg> --cov-context=test --cov-branch`. Then `python3 scripts/unique_cov.py .coverage verdicts.json` reports the source lines executed by no test outside the candidate set, with every candidate removed together. Done when each candidate has a unique-line count. Details and traps: [references/coverage.md](references/coverage.md).
6. **Re-review on a stronger model**, every delete and merge candidate, with its coverage result attached to the row. The reviewer forms its own view before reading the first pass, and names the surviving test for each merge. Unique lines count as strong evidence against delete unless trivial (logging, a re-raise); assertions decide, because coverage sees what a test runs, not what it checks.
7. **Approval per file.** Show the user one file at a time: each test, its bug_caught, the first-pass and second-pass verdicts, the unique lines. Apply only what they approve. Keep, rewrite, and move_down items are proposals too; list them but never apply them unasked.
8. **Apply in parallel**, non-overlapping files: one subagent per group of files, each editing only its own files, each with its own test database (`agent1_test`, `agent2_test`, ...). Each records the baseline test count before editing and the count after, runs the linter and formatter on what it touched, and writes one done-line per item (deleted, merged, skipped plus why). A subagent skips an item whose merge target does not assert what the plan assumed.
9. **Full suite after**, once, capped, by you. Compare pass count, skip set, and coverage with the baseline. Done when the only differences are the removed tests and the unique lines the user knowingly accepted.
10. **Land it**: one commit per approved file group; the message lists what was removed or merged and the evidence.

## Report

Counts per verdict at each stage, the candidates the second pass overturned (first-pass precision), tests kept because they hold unique lines, batches re-run and why, and what was not confirmed (a stack without per-test coverage, files skipped, skipped tests invisible to coverage).
