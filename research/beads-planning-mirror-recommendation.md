# Beads Planning Mirror Recommendation

Research date: 2026-07-19

## Recommendation

Adopt a **bounded, pull-only planning mirror** in Beads, but do not make Beads
the planning source of truth and do not enable general bidirectional sync.

GitHub remains where the skills create and edit Wayfinder decisions,
specifications, tracer tickets, priorities, approvals, and final status. Beads
becomes the convenient local viewer for a user-selected planning scope, in
addition to its existing role as the execution graph.

This addresses the actual pain: the user can open the Beads viewer to see the
feature's task tree and blockers without visiting GitHub or asking an agent to
recap it. It does not create two editable copies of the same plan.

## Why Not Full Sync

- `bd github sync` is bidirectional by default. A local planning edit can be
  pushed to GitHub, and a GitHub edit can conflict with it. Beads provides
  conflict preferences, but a preference only selects a loser; it does not
  create a trustworthy shared editing workflow.
- Beads explicitly defines tracker integrations as an adoption bridge, not a
  replacement for a tracker's UI or workflow. It excludes UI parity and full
  comment/thread mirroring. GitHub should therefore remain the review and
  approval surface.
- Planning work such as research and grilling is often a request to use a
  particular skill, not execution work that an agent may automatically claim.
  Mixing it into the default ready queue would make autonomous agents treat
  planning prompts as implementation tasks.
- `bd github pull` accepts explicit issue references. The documented command
  does not promise to recursively import GitHub sub-issues, so a parent pull
  alone must not be assumed to produce the full planning tree.

## Proposed Model

| Concern                                                                  | Owner                                   | Beads behavior                                     |
| ------------------------------------------------------------------------ | --------------------------------------- | -------------------------------------------------- |
| Maps, decisions, specs, tracer tickets, priority, approval, final status | GitHub Issues                           | Pull-only mirror for a selected scope              |
| Planning actions such as research, grilling, and specification work      | GitHub Issues and the appropriate skill | Visible, but never automatically claimed or closed |
| Implementation subtasks, claims, discoveries, and verification evidence  | Beads                                   | Native Beads work, as today                        |

Every mirrored issue retains its GitHub `external_ref`. Mirrored planning items
receive a GitHub-owned label such as `phase:planning`; execution commands
exclude that label. This keeps a planning item visible in the viewer while
preventing `bd ready` from offering it for autonomous implementation.

The mirror is deliberately bounded. Refresh only a feature, Wayfinder decision,
or other scope the user chooses. Do not bulk-import the repository backlog or
run unscoped `bd github sync`.

## Daily Experience

1. Existing skills publish the normal GitHub issue hierarchy.
2. The user requests a planning refresh for a named parent or project scope.
3. A small adapter obtains the parent and its known GitHub sub-issue and
   dependency references, then runs `bd github pull <ref...>` for that explicit
   set. It runs pull-only, never push.
4. The user opens the Beads viewer or runs `bd list --tree` to browse the local
   tree. The links return to GitHub for comments, priority changes, approval,
   or editing requirements.
5. When implementation begins, the existing selected-parent workflow continues:
   native Beads execution descendants can be claimed and completed, while
   mirrored planning work remains GitHub-owned.

The adapter should be a narrow command or skill, for example `refresh-plan`,
not a background daemon. It should report which GitHub issues were refreshed,
which hierarchy edges were mapped, and any relationship it could not mirror.

## Pilot Before Policy Change

Run one feature through this workflow before changing the default setup skill.

1. Create a feature issue with at least one decision or research ticket, two
   tracer tickets, a GitHub sub-issue relationship, and one blocking edge.
2. Run the adapter in dry-run mode and verify its explicit import set.
3. Refresh the scope into an isolated Beads database or a clearly labeled test
   namespace.
4. Verify the viewer shows every expected item, the parent-child structure, and
   the blocking relationship. Record whether the installed Beads version maps
   GitHub sub-issues and dependencies automatically or whether the adapter must
   create missing local edges.
5. Verify that the standard implementation query excludes planning items and
   that a close or claim of a mirrored item cannot alter GitHub.
6. Change a title and close a planning ticket in GitHub, refresh, and verify
   that Beads reflects the change without creating duplicates.

Only after this pilot should the routing policy change from "do not duplicate
planning artifacts" to "GitHub-owned planning artifacts may be pull-only
mirrored into Beads for scoped viewing." The policy must also specify the
planning label and require execution queries to exclude it.

## Rejected Alternatives

| Alternative                          | Reason                                                                                                                 |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Full two-way sync of all GitHub work | Two editable status authorities and conflict resolution create a worse planning experience.                            |
| Move all planning creation to Beads  | Would require replacing the installed skills' GitHub publication behavior and loses GitHub-native review and approval. |
| Keep Beads implementation-only       | Preserves the current clean boundary but does not solve the user's need for a single task view.                        |
| Import the entire GitHub backlog     | Makes the viewer noisy, makes ready-work queries unsafe, and provides little value for inactive work.                  |

## Primary Sources

- Local current architecture: [`docs/architecture.md`](../docs/architecture.md)
- Local current workflow: [`setup-github-beads/references/WORKFLOW.md`](../setup-github-beads/references/WORKFLOW.md)
- Local current routing policy: [`setup-github-beads/references/POLICY.md`](../setup-github-beads/references/POLICY.md)
- [Beads GitHub CLI reference](https://raw.githubusercontent.com/gastownhall/beads/main/docs/cli-reference/github.md): selective `pull` and `push`; bidirectional sync defaults; conflict controls.
- [Beads integration charter](https://raw.githubusercontent.com/gastownhall/beads/main/engdocs/INTEGRATION_CHARTER.md): tracker integrations are an adoption bridge; metadata and dependency mapping; no UI parity or full comment mirroring.
- [Beads ready CLI reference](https://raw.githubusercontent.com/gastownhall/beads/main/docs/cli-reference/ready.md): ready queries support label exclusion and parent scoping.
- [Beads dependency CLI reference](https://raw.githubusercontent.com/gastownhall/beads/main/docs/cli-reference/dep.md): native parent-child and blocking relationships.
