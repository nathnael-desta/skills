# Linear + Beads Architecture

Linear is the human-facing source of truth for product work. Beads is the
agent-facing implementation graph. A Linear feature is selectively mirrored as
one parent Bead; implementation slices stay as local descendants.

This split follows Beads' own integration charter: external tracker support is
an adoption bridge, not an attempt to replace the external tracker's UI and
workflow.

## Ownership

| Data                                                            | Owner                      |
| --------------------------------------------------------------- | -------------------------- |
| Product title, requirements, priority, status, approval         | Linear                     |
| Implementation slices, dependencies, claims, notes, discoveries | Beads                      |
| Linear identity and URL                                         | Parent Bead `external_ref` |

## Safety Invariants

- Exactly one parent Bead corresponds to a Linear feature.
- A user selects the Linear feature or explicitly authorizes autonomous Linear
  selection before it is imported or started.
- Autonomous ready-work queries are scoped to that parent.
- A Beads child is not published to Linear unless a human-facing decision needs
  separate prioritization.
- Linear completion follows a feature finish checkpoint, not a child count.
- Unscoped Linear pushes are outside the workflow.

See `setup-linear-beads/references/WORKFLOW.md` for the operational flow.
