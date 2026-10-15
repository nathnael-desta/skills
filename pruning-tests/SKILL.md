---
name: pruning-tests
description: Audit an existing test suite and remove, merge, or rewrite low-value tests safely. Load when the user asks to clean up, trim, de-bloat, or review the quality of a whole suite or a set of test files.
---

# Pruning tests

Goal: a suite where every test catches a bug that matters, and no test is deleted on a guess. The audit produces verdicts; deletions happen only after evidence and the user's approval.

The rubric the auditors apply, including the calibration rules for what is never deleted, is [references/rubric.md](references/rubric.md). Fill in its project block before dispatching anything.

## Process

1. **Batch.** List every test file with its line count. Group files into batches of about 800 lines. Split a larger file by line range; each range audits the tests whose definition starts inside it. Done when every test file sits in exactly one batch.
2. **Fan out.** Give each batch to a cheap-model subagent, a few at a time, named by exact model ID. The brief carries the rubric path, the batch, and an output path. Each subagent appends one JSONL verdict per test the moment it decides it (`keep`, `rewrite`, `merge`, `move_down`, `delete`), so a subagent that runs out of context leaves finished verdicts on disk. Subagents edit nothing and start no servers or full suites.
3. **Merge.** Concatenate the JSONL into one report grouped by file and verdict. Done when the verdict count per batch equals its test-function count; redo any batch that falls short.
4. **Spot-check.** Sample verdicts from every batch, weighted toward `delete` and `merge`. Open the source yourself and judge each sampled test. A batch with a sampled verdict that would remove a test catching a real bug is redone on a stronger model. Done when every batch has passed a sample.
5. **Confirm candidates empirically.** For each `delete` or `merge` candidate, run mutation testing on the code it exercises (mutmut, Stryker, or your stack's equivalent), or collect per-test coverage (`coverage.py` dynamic contexts, or your stack's equivalent). A candidate that is the only killer of a mutant or the only cover of a line is refuted and returns to `keep` or `rewrite`. Done when every candidate is marked confirmed or refuted.
6. **Approval per file.** Show the user, one file at a time: each test, its `bug_caught`, the evidence, and the confirmation result. Apply only what they approve. After applying, run the suite and compare coverage and mutants against the baseline.
7. **Land it.** One commit per approved file group; the message lists what was removed or merged and the evidence.

## Report

Counts per verdict, the refuted candidates, the batches that were redone and why, and what was not confirmed (a stack without a mutation tool, files skipped).
