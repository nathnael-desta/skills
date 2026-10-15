---
name: execute-feature
description: Implement an approved spec's linked tickets sequentially by default, or in explicit parallel worktree batches for independent tickets, through dependency-aware subagents, reviews, and final acceptance. Use when a canonical to-spec issue and approved to-tickets breakdown already exist and you want to finish the feature.
argument-hint: "[canonical spec issue, ticket set, or feature]"
disable-model-invocation: true
---

# Execute Feature

Consume the approved output of `/plan-feature`. This skill executes work; it
does not redesign the spec or create a second ticket breakdown.

## Preconditions

1. Find the canonical spec issue from the argument, current context, or tracker.
2. Load the spec, its linked implementation tickets, comments, accepted
   decisions, and blocker relationships.
3. Confirm every implementation ticket links to that spec and has an approved
   blocking edge. If planning is incomplete or links are missing, stop and
   direct the user to `/plan-feature`.
4. Reuse recorded execution state when resuming. Never restart completed work
   or create duplicate tickets.

## Execution modes

Sequential execution is the default. Never infer permission to parallelize merely
because several tickets are unblocked. Switch modes only when the user explicitly
asks to run independent tickets in parallel.

## Execute the frontier

Maintain progress in the tracker or ticket files. A ticket is ready only when
every ticket blocking it is complete. Choose the first ready ticket in the
approved order, using priority as the tie-breaker. Never start a blocked ticket.

## Orchestrator Boundary

The parent agent is an orchestrator, not the implementation worker. During this
workflow it must not edit application or test files, run tests/typechecks/builds,
run code review, or fix worker findings directly. It delegates those actions to
the current ticket's implementation subagent and records the returned evidence.

For every ticket, the orchestrator must:

1. Start exactly one fresh implementation subagent for the current ticket.
2. Wait for that subagent to finish before doing anything with the next ticket.
3. Require the subagent to implement, verify, review, and commit the ticket.
4. Require a non-empty result packet with the ticket, status, commit, commands
   and results, review findings/resolutions, and remaining concerns.
5. Treat an empty, malformed, interrupted, or missing result packet as a failed
   attempt. Preserve the ticket as incomplete and resume it with a fresh
   implementation subagent; never advance to a dependent ticket.

The orchestrator may inspect tracker state, worker responses, and repository
metadata needed to coordinate execution, but must not substitute its own coding,
testing, review, or cleanup for the worker.

### Sequential mode (default)

For each ready ticket:

1. Start exactly one fresh implementation subagent and wait for its complete
   result before starting another.
2. Give it the ticket, canonical spec, accepted blocker resolutions, and repo
   instructions. Tell it to run `/implement` and to return the required result
   packet. The worker owns all code edits, verification, review, and commit work.
3. Require TDD where possible, targeted checks, required typecheck/lint/build
   checks, `/code-review`, and a commit as specified by `/implement`.
4. Require a result packet with ticket, status, commit, commands and results,
   review findings, and remaining concerns.
5. Inspect the result packet and tracker/repository metadata without doing the
   implementation work yourself. Record completion only when the implementation
   and review actually pass. If findings remain, resume the same ticket with a
   fresh worker before advancing.

The default worker is `openai/gpt-5.6-luna` with `xhigh` reasoning. Honor an
explicit model or reasoning override in the invocation or skill instructions.
If the host cannot honor the requested configuration, stop and report it rather
than silently substituting a model.

If no ticket is ready while open tickets remain, report the dependency deadlock.
If a worker fails, preserve its state and resume that ticket before advancing.

### Explicit parallel mode

When the user explicitly requests parallel work:

1. Select only the current ready frontier. Every ticket in the batch must have
   all blockers complete and no ticket in the batch may block another.
2. Check independence beyond tracker edges. If tickets may edit the same files,
   migrations, generated outputs, shared configuration, or integration seams,
   keep them sequential unless the user explicitly resolves that collision.
3. Confirm the integration worktree is clean and record its base commit. Never
   discard unrelated user changes to make it clean.
4. Create one sibling Git worktree and branch per ticket from that base commit.
   Give each worker only its assigned worktree and ticket. Workers must not edit
   another worktree or update tracker relationships.
5. Start one fresh implementation subagent per worktree concurrently. Each
   worker runs `/implement`, its checks, `/code-review`, and commits on its own
   branch, then returns the required result packet.
6. Wait for the whole batch. Merge successful branches into the integration
   branch one at a time. The main agent owns conflict resolution; inspect every
   conflict resolution and run affected tests afterward.
7. Run an integration-focused `/code-review` against the batch base commit to
   detect cross-ticket conflicts, duplicate behavior, and broken assumptions.
   Resolve findings before advancing. Do not create unbounded review loops.
8. Remove a worktree only after its branch is merged and clean. Preserve failed
   worktrees for debugging or retry.
9. Record successful tickets, preserve failed tickets as incomplete, recompute
   the frontier, and continue. Never start dependents of a failed ticket.

The main agent is the only tracker-state writer during a parallel batch. If the
tracker cannot safely support concurrent claims or writes, use sequential mode.

## Final gate

When every linked ticket is complete and all ticket-level reviews are finished:

1. Run `/finish-ticket` against the complete integrated feature.
2. Run a consolidated final `/code-review` when the last integration review did
   not already cover the complete feature, using the agreed fixed point. Do not
   create unbounded review loops.
3. Report `DONE: READY FOR HUMAN ACCEPTANCE` only when all acceptance criteria
   have evidence, required checks pass, no ticket is open or blocked, and every
   review finding is resolved or explicitly accepted by the user.

Do not close the spec issue or child tickets, push, or claim human acceptance.
Give the user the final evidence and a concise closure note to review and apply.
