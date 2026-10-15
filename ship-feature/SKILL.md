---
name: ship-feature
description: Turn an approved Wayfinder or grilling outcome into a spec, dependency-aware tickets, sequential implementation work, and a final integrated acceptance report. Use when a plan is ready to become tickets and you want fresh subagents to implement every unblocked ticket one at a time.
argument-hint: "[feature, Wayfinder map, spec, or ticket context]"
disable-model-invocation: true
---

# Ship Feature

Use this as the complete convenience flow:

1. Run `/plan-feature` to create or reuse the canonical spec issue, create the
   approved dependency-aware tickets, and link every ticket to that spec.
2. Run `/execute-feature <spec-reference>` to implement the approved tickets
   one at a time by default, respecting blockers, reviews, and recorded progress.
   If the user explicitly requests parallel independent tickets, it uses isolated
   worktrees, merges them on the main branch, resolves conflicts, and reviews the
   integration before continuing.

The `/ship-feature` flow is orchestration-only. The parent agent must not edit
application or test files, run tests/typechecks/builds, run code review, or fix
implementation findings directly. `/execute-feature` must start exactly one
fresh implementation subagent for the current ready ticket, wait for its
complete non-empty result packet, and advance only after that ticket's worker
has implemented, verified, reviewed, and committed it. An empty, malformed, or
interrupted worker result leaves the ticket incomplete and must be retried with
a fresh worker before any dependent ticket starts.

If the spec and linked tickets already exist and are approved, skip
`/plan-feature` and begin with `/execute-feature`.

Do not duplicate planning logic here. The two component skills are also
available independently when the user wants to pause between planning and
execution.
