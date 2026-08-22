---
name: plan-feature
description: Turn a settled Wayfinder or grilling outcome into one canonical spec issue and approved, dependency-aware implementation tickets linked to that spec. Use when planning is complete and you want to run to-spec and to-tickets without starting implementation.
argument-hint: "[feature, Wayfinder map, or planning context]"
disable-model-invocation: true
---

# Plan Feature

Create the planning artifacts that `/implement-spec` and `/execute-feature` consume. This skill
plans only; it never starts implementation or closes the parent issue.

## Preconditions

1. Confirm the settled planning conversation, Wayfinder map, or existing spec is
   available. In a codebase, prefer `/grill-with-docs`; use `/grill-me` only for
   work without a codebase or durable project context.
2. Confirm the repository's issue-tracker instructions exist. If they do not,
   stop and run `/setup-matt-pocock-skills`; do not invent tracker commands.
3. Inspect the active git environment and worktree state (`git branch --show-current`,
   `git worktree list`, and recent commit history). Identify the exact base branch and
   working directory containing the active codebase state. If prior feature or spec work
   was completed in a specific branch or worktree that has not yet landed on the default branch,
   explicitly record that lineage as the base for the new spec.
4. If a spec or ticket set already exists, inspect and reuse it. Do not create
   duplicates when resuming.

## Create the spec

1. Run `/to-spec` using the settled context or Wayfinder destination.
2. Let `/to-spec` explore the codebase, use the domain vocabulary, identify
   testing seams, and publish the spec through the configured tracker.
3. Stop and obtain the user's approval of the proposed testing seams before
   continuing.
4. Capture the canonical spec issue's title and ID, URL, or local path. This is
   the parent reference for every implementation ticket.

## Create and link tickets

1. Run `/to-tickets` with the canonical spec issue as its source.
2. Let it draft tracer-bullet vertical slices and their blocking edges.
3. Stop and obtain the user's approval of ticket granularity, order, and every
   blocking edge. Do not guess approval.
4. Publish the approved tickets through the configured tracker.
5. Verify every ticket links back to the canonical spec issue. Use the tracker's
   native parent/sub-issue relationship when available; otherwise preserve the
   spec reference in the ticket's `## Parent` section or local-ticket metadata.
6. Verify every ticket has a dependency edge or an explicit `None — can start
   immediately` state. The ticket order must be dependency-safe, with blockers
   before dependents.

Do not close or modify the spec issue after publishing tickets. If a ticket is
missing its parent link or has an incorrect blocker, stop and report the exact
repair instead of silently changing the approved plan.

## Handoff

Report:

1. **Canonical spec issue**: Title, issue number, and URL.
2. **Approved tickets & Task Graph**: Titles, references, blockers, and readiness state.
3. **First ready ticket**: The initial unblocked ticket to claim.
4. **Copy-Pasteable Prompt for New Agent Session**: Always provide a standalone, concise copy-pasteable prompt block with the spec command, base branch/commit, and working directory:

```text
/implement-spec the spec is on issue number #<spec-number>

Base Branch: <branch-name> (commit <hash>)
Working Directory: <path/to/worktree>
```

Do not start implementation in this skill.
