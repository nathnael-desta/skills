# Test audit rubric

You audit existing tests and give a verdict per test; you edit nothing. Goal: a suite where every test catches a bug that matters.

## Project block (fill in before dispatch)

- Where tests live and how they are named: `<paths, test-function pattern>`
- Test levels, cheapest first: `<pure function | service with fakes | database | HTTP | UI | end-to-end>`
- System boundaries that may be mocked: `<payment providers, email/SMS, third-party and AI APIs, object storage, time, randomness, job-queue dispatch>`
- High-stakes areas: `<money, auth, permissions, legal content, notifications, data deletion, migrations>`

## For each test function (a parametrized test counts as one)

1. Read the test, then open the source it exercises (follow the import) far enough to know what behaviour it pins down.
2. Write `bug_caught`: one sentence naming the realistic bug in this project's code the test would catch. If you cannot write one, that is the finding.
3. Pick one `verdict`:
   - `keep`: catches a realistic bug through public behaviour; assertions are specific.
   - `rewrite`: protects something real but is implementation-coupled or weak (fakes the project's own modules, asserts on internal calls or private attributes, only checks "is not None", a snapshot nobody reviews). Say what the assertion should be.
   - `merge`: same behaviour as another test (give `merge_with`: file::test). Prefer folding into a parametrized test.
   - `move_down`: a database/HTTP/UI test whose bug a pure-function or service test would catch. Name the target level.
   - `delete`: catches no realistic bug. Typical: asserts a constant or enum equals its own literal; asserts a mock returns what it was configured to return; tests language, ORM, validation-library, or UI-framework behaviour instead of the project's; a render-only test whose sole check is that something exists; still passes if every function it imports from the project returned `None`.
4. `category`: behavior | implementation_coupled | tautological | mock_only | framework_mechanics | duplicate | weak_assertion | slow | other.
5. `confidence`: high | medium | low. Use low whenever you did not open the source.

## Calibration (read twice)

- Mocks at system boundaries are fine and often the point. "The payment/notification call was made with X" is behaviour.
- Faking the project's own services or modules is the implementation-coupled smell, unless the faked thing itself wraps a boundary.
- A cheap-model pass over-deletes: when the call is close between `delete` and `keep`, or `merge` and `keep`, say `keep` with confidence `low` and let the second pass decide.
- High-stakes areas: default to `keep` or `rewrite`; `delete` only for an exact duplicate.
- A regression test for a past bug (name or docstring mentions an issue, "regression", "used to") is `keep` unless clearly a duplicate.
- Do not judge by length or style. A long test that pins real behaviour is `keep`.
- If you did not open the source, say so and use confidence `low`.

## Output

Append one JSON object per test, one per line, to the JSONL file named in your task. Write each line as soon as that test's verdict is decided (`cat >> file <<'EOF'`), not all at the end. If a file entry has a line range, audit only tests whose definition starts inside it.

```json
{
  "file": "tests/unit/x.py",
  "test": "test_name or Class::test_name",
  "line": 42,
  "verdict": "keep|rewrite|merge|move_down|delete",
  "merge_with": null,
  "category": "...",
  "confidence": "high|medium|low",
  "bug_caught": "one sentence or null",
  "evidence": "<=2 sentences, cite the source file:line you checked",
  "suggestion": "for rewrite/merge/move_down/delete: what to do, <=1 sentence"
}
```

Every test function in your files gets exactly one line. Finish by counting: the JSONL line count must equal the number of test functions in your files (`grep -cE '^\s*(async\s+)?def test_'` for Python; count `it(`/`test(` calls for JS/TS).
