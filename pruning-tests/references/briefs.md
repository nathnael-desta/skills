# Briefs for the later stages

Fill the angle brackets. Each brief states the goal, the code to read, the output file, the hard rules, and the short report to send back.

## Re-verify (stronger model, read-only)

```
A cheaper model proposed deleting or merging the tests in <input.jsonl>. A spot-check found it
right about <80>% of the time on deletes and <67>% on merges, and in <3 of 24> deletes it would
have thrown away the only test of a real guard. The user approves the final list file by file, so
every "delete" you sign off on must be defensible.

Code (read-only; do not edit, commit, branch, or change git state): <checkout path>
Line numbers in the input may be stale; find tests by name. Rubric: <rubric path>

Each row has the first pass's verdict, evidence, merge_with, and `coverage`: measured with
per-test coverage over the whole suite, assuming ALL candidates are removed at once. "only test
covering: X" means removing it leaves those lines with no test. Treat that as strong evidence
against delete unless the lines are trivial.

Form your own view before reading the first pass's. Decide per row:
- delete: catches no realistic bug a remaining test does not also catch. High-stakes areas
  (<money, auth, permissions, ...>): only an exact duplicate.
- merge: name the surviving test and say exactly how (parametrize case to add, assertion to move).
  The merged test keeps every assertion that matters from both.
- keep / rewrite (one sentence for the fix).
Coverage cannot see what a test asserts. Judge the assertions.

Append one JSON line per row as you go to <output.jsonl>: file, test, first_pass_verdict,
final_verdict, merge_into, plan, bug_caught, reason (cite file:line), confidence.
Rules: no dev servers, browsers or full suites; one test file at a time against <your database>.
Report back (short): counts by final_verdict, how many deletes you overturned, anything surprising.
```

## Apply (cheap or mid model, one per file group)

```
The user approved every item in <items.jsonl>. Each was flagged by one model, re-judged by a
second against current code, and checked against per-test coverage. Carry them out faithfully;
skip an item only if applying it would clearly lose a check that matters (the merge target does
not exist or does not assert what the plan assumes), and say why.

Checkout: <path, branch already created>. Line numbers may be stale; find tests by name.

Hard rules
- Edit ONLY the test files named in your items. Other agents own the other files. Do not touch
  production code, even where a plan says "optionally".
- Do not commit, stash, switch branches, or run git commands that change state.
- delete: remove the test and anything only it used (a helper or fixture nobody else references).
  Leave imports clean.
- merge: the surviving test keeps every meaningful assertion from both; prefer parametrize with
  readable ids; keep the surviving test's name unless the plan says otherwise.
- Match the surrounding style; add no comments beyond what is needed.

Verify each file before and after, against your own database <agentN_test> (never another
agent's): the file's tests, then the linter and formatter on the files you touched.
No full suites, dev servers, or browsers.

Write one JSON line per item to <doneN.jsonl>: file, test, action (deleted|merged|skipped), note.
Report back (short): applied and skipped counts, per-file test count before and after, any file
whose tests fail after your edit (there should be none).
```

## Parallel-apply hygiene

- Non-overlapping files per agent, at most 3 or 4 agents at once.
- A database per agent, created up front; a suite that drops tables must never point at a shared dev database.
- You run the one full suite afterwards, not the agents.
