# Intended Workflow

## Shape

```text
idea
  -> Wayfinder decisions
  -> feature specification
  -> GitHub tracer tickets
  -> user selects one implementation issue
  -> selective GitHub pull
  -> one parent Bead
  -> optional Beads execution descendants
  -> scoped implementation
  -> feature finish checkpoint
  -> GitHub review or completion
```

## Planning

GitHub Issues holds work a human should browse, prioritize, discuss, or approve.
The installed Matt skills remain responsible for publishing Wayfinder maps and
decision tickets, specifications, and tracer tickets there. Their behavior is
not reproduced by this overlay.

The user controls which GitHub implementation issue enters Beads. Do not choose,
import, or start one without explicit selection or authorization to select
autonomously. If the user asks what to do next, inspect GitHub and recommend
options without changing or importing them, then wait for the user's choice.

Selectively pull the chosen issue into Beads. The resulting parent is a local
execution anchor, not a second editable product specification. Create Beads
descendants only when the selected ticket needs lower-level work that benefits
from persistent dependencies, claims, discoveries, or handoffs.

## Execution

After the user has authorized a GitHub issue, each fresh implementation session:

1. Refresh that GitHub parent selectively.
2. Inspect the selected parent or `bd ready --parent <parent-id>` when it has
   descendants.
3. Claim one ready item atomically.
4. Follow the repository's implementation, testing, and review workflow. Use
   `/implement` when installed.
5. Record implementation discoveries immediately.
6. Close Beads work only with verification evidence.
7. Continue only when the user requested autonomous frontier execution.

Separate agents may claim different ready descendants. Embedded Beads is
suitable for sequential writers; use server mode when agents truly write
concurrently.

## Finish Checkpoint

Closing the last Bead is a signal to run the checkpoint, not an event that
blindly closes GitHub. The feature passes when:

- Every required Beads item is closed and no required item remains blocked or
  claimed.
- Every acceptance criterion has evidence.
- Required tests, type checks, lint, build, migrations, and documentation pass.
- The repository's required code review has no unresolved blocking finding.
- The GitHub requirements have not changed incompatibly since work started.
- The implementation summary and unrelated discoveries are recorded.

### Review mode

Post a concise completion summary to the GitHub issue using the repository's
upstream tracker policy. A human reviews the result and closes the issue.

### Auto-complete mode

For a solo repository, setup may explicitly allow the agent to close the GitHub
issue after every finish gate passes. Human approval is waived by repository
policy in advance, never inferred from the last Bead closing.

## Discoveries

Required implementation discoveries become Beads descendants and gate
completion. Unrelated improvements receive a `discovered-from` relationship but
no feature parent. Create a GitHub issue when a discovery needs human priority,
product discussion, scheduling, or separate release approval.

## Sync Rules

Use `bd github pull <issue-url>` to selectively refresh the parent. Use the
GitHub operations already defined by the upstream issue-tracker policy for
human-visible updates. Do not continuously synchronize both systems, perform
unscoped pulls or pushes, or push Beads-only descendants to GitHub.
