# Evidence behind the rules

Each claim below was fetched from its source and checked. Where a source shows less than the rule needs, the gap is stated; the rules stand on judgement, not on these studies alone.

## Agents mock more

- A mining study of 1,254,878 commits in 2,168 repositories (2025; Hora and Robbes, arXiv 2602.00409) found 36% of coding-agent test commits add mocks, against 26% of non-agent test commits. Denominators: 3,934 of 11,035 agent test commits; 40,966 of 158,326 non-agent ones.
- It counts how often mocks appear, not whether the tests are worse. It supports "agents reach for mocks by default, so say when mocks are allowed", not "mocked tests are bad".

## Red before green

- "It's important to confirm that the tests fail before implementing the code to make them pass." Simon Willison, agentic engineering patterns, red/green TDD. A test never seen red may pass for the wrong reason.
- An argument piece ("Why testing after with AI is even worse") recommends not delegating test writing to the end of the work. Argument only, no measurements.

## Rules taken from published agent skills

- "Mock at system boundaries only", and "Test only at pre-agreed seams" (Matt Pocock's `tdd` skill and its mocking guide).
- "Prefer no new test over a bad test. A bad test is one that mostly tests mocks, encodes current implementation details, ..." and "If the test would still pass when every imported function returns `undefined`, rewrite the assertion or delete the test." (the `tdd` and `poteto-mode` skills in Cursor's `pstack` plugin).

## Give the agent something to run, and show the output

- Claude Code best practices: "Give Claude a check it can run: tests, a build, a screenshot to compare", and have it "show evidence rather than asserting success: the test output, the command it ran and what it returned". This is why the report step lists each test with its bug and why a regression test is shown red.

## Checked and not used

- A widely repeated pair of figures (high line coverage with a low mutation kill rate for AI-written tests) traces to one illustrative chart in a vendor blog post. The source page was gone and the figures were not from a measured study. Do not quote them.
- "Agents frequently edit a test to make it pass" appears in a reader comment, with no frequency. The rule against loosening assertions rests on the cost of the failure mode, not on a measured rate.
