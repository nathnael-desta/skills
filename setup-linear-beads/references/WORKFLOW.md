# Intended Workflow

## Shape

```text
idea
  -> product discovery and decisions
  -> feature specification
  -> Linear feature
  -> selective Linear pull
  -> one parent Bead
  -> tracer-bullet slicing
  -> Beads tracer-bullet descendants
  -> scoped implementation sessions
  -> feature finish checkpoint
  -> Linear review or completion
```

## Planning

Use Linear for work a human should browse, prioritize, discuss, schedule, or
approve. Product decisions and feature specifications therefore remain in
Linear. When Matt's skills are installed, `/wayfinder` and `/to-spec` perform
these operations.

When the route is clear, selectively mirror the Linear feature into Beads. That
parent is a reference anchor, not a second editable product specification.
Create vertical implementation slices beneath it in Beads. Use `/to-tickets`
when installed.

The user controls which Linear feature enters this flow. Do not choose, import,
or start a Linear issue without the user's explicit selection or explicit
authorization to select autonomously. If the user asks what to do next, inspect
Linear and recommend options without changing or importing them, then wait for
the user's choice.

## Execution

After the user has authorized a Linear feature, each fresh implementation
session for that feature:

1. Refresh the Linear parent selectively.
2. Inspect `bd ready --parent <parent-id>`.
3. Claim one ready child atomically.
4. Follow the repository's implementation, testing, and review workflow. Use
   `/implement` when installed.
5. Record implementation discoveries immediately.
6. Close the child only with verification evidence.
7. Continue only when the user requested autonomous frontier execution.

Steps 2 and 3 may be autonomous within the authorized parent graph. They do not
authorize selecting a different Linear feature.

Separate agents may claim different ready children. Embedded Beads is suitable
for sequential writers; use server mode when agents truly write concurrently.

## What Happens When Children Finish

Closing the last child is a signal to run the finish checkpoint, not an event
that blindly closes Linear. The agent performs the checkpoint during the same
session or the next session that resumes the feature.

The feature passes the checkpoint when:

- Every required descendant is closed.
- No required descendant is blocked or still claimed.
- Every ticket's acceptance criteria have evidence.
- Feature-level tests, type checks, lint, build, migrations, and documentation
  required by the Linear spec pass.
- The repository's required code review has no unresolved blocking finding.
- The Linear requirements have not changed incompatibly since work started.
- The implementation summary and remaining unrelated discoveries are recorded.

### Review mode

The agent uses the repository's Linear adapter to move the feature to its review
state and posts a concise completion summary. A human inspects the result and
moves it to Done. The next selective pull aligns the parent Bead with Linear.

### Auto-complete mode

For a solo repository, setup may explicitly allow the agent to move Linear to
Done after every finish gate passes. Human approval is not guessed from the
last Bead; it is waived by repository policy in advance.

## Discoveries

Required discoveries become descendants and therefore gate completion.
Unrelated improvements receive a `discovered-from` relationship but no feature
parent. Promote a discovery to Linear when it needs human priority, product
discussion, scheduling, cross-team work, or separate release approval.

## Sync Rules

Use the official Beads Linear integration to selectively pull the parent. Use
the repository's configured Linear client to update human-visible status. Do
not continuously synchronize both systems and do not push the Beads parent
tree, because that would publish implementation children.
