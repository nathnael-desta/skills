---
name: writing-tests
description: Rules for an agent that adds, changes, or deletes a test, so the suite does not fill with tests that catch nothing. Load before writing any test, before fixing a bug that could earn a regression test, and before editing or skipping an existing test. Not for auditing a whole suite (that is pruning-tests).
---

# Writing tests

A test earns its place by catching a bug that matters. Volume and coverage are not goals; every test costs CI time, review time, and refactor friction forever.

## Before writing

1. **Name the bug.** Write one sentence: the realistic bug this test would catch, and why it matters. Done when the sentence exists. No sentence, no test.
2. **Extend first.** Find the nearest existing test for the same behaviour and extend or parametrize it. Add a new test, and certainly a new file, only when nothing fits.
3. **Pick the cheapest level that owns the logic**, cheapest first: pure function, service with fakes, real database, HTTP, UI or end-to-end. Cover each behaviour once, at that level. Slow levels dominate CI time.
4. **Prefer no test over a bad one.** A bad test mostly tests its own mocks, restates the implementation, depends on timing, or needs heavy setup for a small fix. Glue or UI code that needs heavy mocking is verified on the running app instead; say so in the commit message.

## Writing it

- **Public seam.** Drive the endpoint, the service function, or what the user sees. Internals stay free to change.
- **Independent expectations.** Take expected values from a literal, a worked example, or the spec, never recomputed the way the code computes them.
- **Mock at system boundaries only.** Payment providers, email/SMS, third-party and AI APIs, the clock, randomness, queue dispatch. Use the project's own fakes and its real test database for everything it owns.
- **Deletion check.** If every imported project function returned `None`/`undefined`, the test must fail. If it would still pass, rewrite the assertion or drop the test.
- **Specific assertions.** `is not None`, "element exists", and unreviewed snapshots are weak. Assert the value, the status, the row, the text.
- **No sleeps.** Wait on an event or freeze the clock. Unit tests stay off the network.
- **Bug fix: red first.** Write the regression test, watch it fail against the unfixed code, then fix. Done when you have seen it red. If the only possible test restates the fix, skip it and say so in the commit message.

## Changing or deleting tests

- Keep every existing test as strict as it was. A change that turns a test red is a finding: fix the code, or explain in the commit message why the test's expectation was wrong. Loosening an assertion to get green is never the fix.
- Deleting or skipping a test needs the user's approval, one test at a time, with the reason.
- A whole-suite clean-up is a different job with its own safeguards: load `pruning-tests`.

## Report

In the final summary, list each new test with the one-sentence bug it catches, and each test you chose not to write with why. Wiring: a project loads this from `AGENTS.md` with one line, for example "Load `writing-tests` before adding, changing, or deleting a test."

Evidence behind the rules, with what each source does and does not show: [references/evidence.md](references/evidence.md).
