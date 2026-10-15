---
name: writing-tests
description: Rules for deciding whether and how to add a test. Load before writing, changing, or deleting any test, and before fixing a bug that could earn a regression test.
---

# Writing tests

A test earns its place by catching a bug that matters. Volume and coverage are not goals.

## Before writing

1. Write one sentence naming the realistic bug this test would catch and why it matters. Done when the sentence exists; no sentence, no test.
2. Find the nearest existing test and extend or parametrize it. Add a new test or file only when nothing fits.
3. Pick the cheapest level that catches the bug: pure function, then service with fakes, then real database, then HTTP or UI. Slow levels dominate CI time. Cover each behaviour once, at the lowest level that owns the logic.
4. Prefer no new test over a bad one: a test that mostly tests mocks, restates the implementation, depends on timing, or needs heavy setup for a small fix. Glue or UI code that needs heavy mocking to unit-test gets verified on the running app instead; say so in the commit.

## Writing it

- Test behaviour at the public seam: the endpoint, the service function, what the user sees. Internals stay free to change.
- Take expected values from an independent source (a literal, a worked example, the spec), never recomputed the way the code computes them.
- Mock only at system boundaries: payment providers, email/SMS, third-party and AI APIs, time, randomness. Use your project's own fakes and the real test database for everything you own.
- Deletion check: if every imported function returned `None`/`undefined`, the test must fail.
- Assert specific values. `is not None`, "element exists", and unreviewed snapshots are weak.
- Wait on an event or freeze the clock instead of sleeping. Unit tests stay off the network.
- Bug fix: write the regression test first and watch it go red against the unfixed code. If the only possible test restates the fix, skip it and say so in the commit.

## Changing or deleting tests

- Keep every existing test as strict as it was. A change that turns a test red is a finding: fix the code, or explain in the commit why the test's expectation was wrong.
- Ask the user before deleting or skipping a test.
- Auditing a whole suite is a different job: load `pruning-tests`.

## Report

List each new test in the final summary with the one-sentence bug it catches.

## Why

- Coding agents add mocks to 36% of their test commits against 26% for non-agents (Hora & Robbes, arXiv 2602.00409, 1.25M commits). The study counts mock frequency, not test value.
- Red first: "It's important to confirm that the tests fail before implementing the code to make them pass" (Simon Willison, agentic-engineering-patterns, red/green TDD).
- The deletion check and "prefer no new test over a bad test" come from the pstack `poteto-mode` and `tdd` skills (github.com/cursor/plugins, `pstack`).
