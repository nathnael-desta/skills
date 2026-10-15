# Per-test coverage for delete and merge candidates

## Recording

```bash
pytest --cov=<package> --cov-context=test --cov-branch tests/unit -p no:cacheprovider
```

- `--cov-context=test` stores which test executed each line, in the `context` table, labelled like `tests/unit/test_x.py::TestA::test_b|run`.
- With `--cov-branch` the executed lines live in the **`arc`** table (`file_id, context_id, fromno, tono`), not `line_bits`. Without branch coverage they live in `line_bits` as `numbits` blobs (`coverage.numbits.numbits_to_nums`). `scripts/unique_cov.py` reads whichever the file holds; a script written against `line_bits` alone reports zero for every test on a branch run.
- In `arc`, negative `fromno`/`tono` are function entry and exit markers; only positive numbers are source lines.
- Record on the unit tier, or the tier the candidates live in. Candidates from a tier you did not run show `in_coverage: false`; that means "unknown", not "safe".

## Reading the result

- **Remove the whole candidate set together.** A line is "unique" when every test that runs it is a candidate. Two duplicate tests both report the line, and deleting both loses it: keep one. This is the point of computing it for the set, not per test.
- **Lines run outside any test** (import time, collection) get the empty context and count as not lost. The script treats them that way, and ignores test files themselves (override with `--exclude`).
- `in_coverage: false` covers skipped tests, a different suite, and a name mismatch between the verdict row and the node id. Resolve the mismatch before trusting a zero.
- Parametrized tests collapse to one candidate by base name; a verdict that applies to only some parameters needs a manual look.
- **Coverage cannot see assertions.** A test can run unique lines and assert nothing (delete it and add the assertion elsewhere), and a test with no unique lines can still be the only one asserting a value. Use the count to refute deletes, never to approve one.

## When the numbers are surprising

- Zero candidates found in coverage: the context label format changed (plugin or version), or the run was not `--cov-context=test`. Print a few `context` rows and adjust the pattern in `context_key`.
- Very large `unique_lines` on a "delete": the candidate is the only test of a module. Almost always a wrong verdict.
