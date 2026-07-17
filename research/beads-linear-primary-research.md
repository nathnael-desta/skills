# Beads + Linear Primary Research

Research date: 2026-07-17

## Confirmed Current State

- Beads 1.1.0 was released on 2026-07-04 and uses embedded Dolt by default.
  Sources: [README](https://github.com/gastownhall/beads/blob/main/README.md),
  [CHANGELOG](https://github.com/gastownhall/beads/blob/main/CHANGELOG.md).
- The official Linear integration includes `bd linear pull`, `push`, `sync`,
  `status`, and `teams`, with dry runs, selective issue sync, stale pulls,
  relation import, conflict strategies, and multi-team configuration. Source:
  [Linear CLI reference](https://github.com/gastownhall/beads/blob/main/docs/cli-reference/linear.md).
- The sync engine records a last-sync watermark and detects edits on both sides.
  Source: [sync engine](https://github.com/gastownhall/beads/blob/main/internal/tracker/engine.go).
- Beads' integration charter treats tracker integrations as adoption bridges.
  It excludes webhooks, UI parity, attachment sync, and full comment mirroring.
  Source: [Integration Charter](https://github.com/gastownhall/beads/blob/main/engdocs/INTEGRATION_CHARTER.md).
- `bd ready --parent <id>` scopes ready work to transitive descendants, and
  claims are atomic. Sources: [ready CLI](https://github.com/gastownhall/beads/blob/main/docs/cli-reference/ready.md),
  [coordination](https://github.com/gastownhall/beads/blob/main/docs/multi-agent/coordination.md).
- Beads recommends CLI plus hooks when shell access exists; MCP has higher
  context overhead and does not expose sync. Source: [MCP server](https://github.com/gastownhall/beads/blob/main/docs/integrations/mcp-server.md).

## Consequences For This Workflow

- `bd linear sync --push --parent <id>` pushes descendants and is unsafe when
  implementation children should remain Beads-only.
- A global push can create Linear issues for local Beads without an
  `external_ref`; global push is therefore excluded.
- JSONL is interchange, not the full database backup. Use `bd backup` for Dolt
  history and `bd export --all` as an issue-level migration safeguard.
- The official Beads setup and `bd prime` should own CLI mechanics. A custom
  skill should contain only the Linear/Beads routing policy.
- Beads records completion state but does not prove code correctness. Matt's
  `/implement`, `/tdd`, and `/code-review` retain that responsibility.

## Recommended Pilot

Use one repository and one feature. Keep Linear specs and decisions human
visible, selectively mirror one parent into Beads, create `/to-tickets` output
as descendants, and query the scoped frontier. Default to a review handoff in
Linear after feature-level verification. Add wrappers, MCP, or plugin packaging
only in response to observed failures.
