# Linear + Beads Routing Policy

Add the following managed section to the repository's canonical issue-tracker
policy. Replace the completion-mode placeholder with exactly one value. Keep
the repository's existing Linear access instructions as the authority for
reading and updating Linear.

```markdown
<!-- BEGIN LINEAR BEADS ROUTING -->

## Linear + Beads routing

Linear is the human planning and approval surface. Beads is the implementation
execution graph. They are not interchangeable mirrors.

Completion mode: `{review|auto-complete}`

### Selection authority

- Do not choose, import, or begin a Linear issue unless the user identifies it
  or explicitly authorizes autonomous Linear selection.
- If the user asks what to work on, inspect Linear and recommend options without
  importing, changing, or starting any issue. Wait for the user's selection.
- After the user authorizes a Linear feature, agents may autonomously choose and
  claim ready Beads descendants within that feature's parent graph.

### Route by operation

| Work                                                              | Authority |
| ----------------------------------------------------------------- | --------- |
| Roadmap, priority, product requirements, triage, human discussion | Linear    |
| Product maps, decision tickets, and feature specifications        | Linear    |
| Tracer-bullet implementation slices                               | Beads     |
| Dependencies, claims, implementation discoveries, and handoffs    | Beads     |
| Final feature acceptance and human-visible status                 | Linear    |

### Start a Linear feature

1. Confirm that the user selected this Linear feature or explicitly authorized
   autonomous Linear selection.
2. Read the latest Linear feature through the repository's configured Linear
   client.
3. Selectively pull only that feature into Beads to create or refresh exactly
   one parent Bead. Never pull the whole workspace as a routine start step.
4. Find the parent by its Linear `external_ref`; do not create a duplicate.
5. Create tracer-bullet implementation slices as descendants of that parent
   with native blocking dependencies. Use `/to-tickets` when installed.

### Execute

- Query only `bd ready --parent <parent-bead-id>`.
- Atomically claim one issue before work.
- Follow the repository's coding, testing, review, and commit workflow. Use
  `/implement` when installed.
- Close a child only after its acceptance criteria and verification pass.
- Required feature work is a parent-child descendant.
- Record unrelated discoveries with `discovered-from` but without the feature
  parent, so they do not silently expand its completion gate.

### Finish

Closing the final child does not itself complete the Linear feature. Run the
feature finish checkpoint in the Linear + Beads workflow. Follow the completion
mode declared above, then refresh the parent Bead from Linear.

### Sync safety

- Linear owns the mirrored parent's title, requirements, priority, and status.
- Beads owns implementation descendants and their execution state.
- Use selective parent pulls and the repository's Linear client for status.
- Never run an unscoped Linear push.
- Never use `bd linear sync --push --parent`; it includes Beads-only descendants.
<!-- END LINEAR BEADS ROUTING -->
```
