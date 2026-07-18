# GitHub + Beads Architecture

GitHub Issues is the human-facing source of truth for product work. Beads is the
agent-facing implementation graph. A user-authorized GitHub implementation
issue is selectively mirrored as one parent Bead; lower-level execution work
may stay as local descendants.

This split follows Beads' own integration charter: external tracker support is
an adoption bridge, not an attempt to replace the external tracker's UI and
workflow.

## Ownership

| Data                                                               | Owner                      |
| ------------------------------------------------------------------ | -------------------------- |
| Maps, decisions, specs, tracer tickets, priority, status, approval | GitHub Issues              |
| Implementation subtasks, claims, notes, discoveries                | Beads                      |
| GitHub issue identity and URL                                      | Parent Bead `external_ref` |

## Safety Invariants

- Exactly one parent Bead corresponds to a selected GitHub implementation issue.
- A user selects the GitHub issue or explicitly authorizes autonomous selection
  before it is imported or started.
- Autonomous ready-work queries are scoped to that parent.
- Matt's skills continue publishing their normal artifacts to GitHub Issues.
- Beads-only execution work is not pushed to GitHub unless it needs separate
  human prioritization or discussion.
- GitHub completion follows a feature finish checkpoint, not a child count.
- Unscoped GitHub pulls and pushes are outside the workflow.

See `setup-github-beads/references/WORKFLOW.md` for the operational flow.
