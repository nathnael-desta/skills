# GitHub Issues vs Linear for Beads + Matt Pocock Skills

Research date: 2026-07-18

## Recommendation

Use **GitHub Issues + GitHub Projects + Beads**, and keep **Notion only for
long-lived research and personal project documents**.

For the workflow described here, GitHub is the better default than Linear:

- The required human workflow is small: capture work and move it among
  `Future`, `Now`, `Paused`, and `Done`.
- Matt Pocock's installed setup explicitly says the skills were designed for
  GitHub and uses `gh issue create` by default.
- `/to-spec` can publish the parent feature as a GitHub issue, while
  `/to-tickets` can create native sub-issues and blocking relationships.
- Current Beads has an official GitHub integration with selective pull and push,
  so the selected parent issue can be mirrored into Beads without copying the
  whole backlog.
- GitHub already owns the repository, pull requests, reviews, and CI. Using its
  tracker removes one service and one GitHub-to-Linear integration boundary.

Linear remains the better choice if its focused planning experience, cycles,
triage inbox, roadmap, or multi-team workflow is valuable enough to justify a
separate product. None of those appears central to the stated use case.

## Recommended Division Of Responsibility

| Surface | Responsibility |
| --- | --- |
| GitHub Issues | Human-visible feature requests, bugs, specifications, priority, and approval |
| GitHub Project | The personal Kanban view: `Future`, `Now`, `Paused`, `Done` |
| Beads | Agent execution graph, tracer-bullet descendants, dependencies, claims, discoveries, and handoffs |
| Notion | Research notes, broad project thinking, and reference material that is not an executable requirement |
| Repository Markdown | ADRs, domain context, and technical documentation that agents and code changes must version together |

Do not keep the same task editable in GitHub, Beads, and Notion. GitHub owns the
human-facing parent; Beads owns implementation children. A Notion page may link
to the GitHub issue, but should not be another status authority.

## How The Daily Flow Would Work

1. Capture an idea as a GitHub issue and add it to the project in `Future`.
2. Move it to `Now` when it is selected, or `Paused` when deliberately stopped.
3. Use `/to-spec` to create or improve the parent feature issue.
4. Selectively pull that one issue into Beads, for example with `bd github pull
   <GitHub issue URL>`.
5. Use `/to-tickets` to create tracer-bullet descendants in Beads, not duplicate
   Kanban cards for every implementation detail.
6. Work the scoped frontier with `bd ready --parent <parent-bead-id>` and
   `/implement`.
7. After the feature finish checkpoint, update the GitHub issue/project to
   `Done`; leave unrelated discoveries in Beads until they need human priority.

If the user wants implementation slices visible in GitHub, `/to-tickets` can
instead publish them as native GitHub sub-issues with blocking relationships.
That is supported by the generic Matt skill, but it duplicates more of Beads'
execution graph. For a solo agent workflow, keeping children only in Beads is
the cleaner default.

## Capability Comparison

| Need | GitHub | Linear | Consequence here |
| --- | --- | --- | --- |
| Simple Kanban | Projects supports board views, custom fields, filters, and automation | Custom issue statuses and project statuses provide a polished workflow | Both satisfy `Future / Now / Paused`; GitHub is sufficient |
| Parent and child work | Native sub-issues with hierarchy progress | Native parent and sub-issues | Both fit `/to-tickets` |
| Blocking edges | Native issue dependencies | Native blocking and related issue relations | Both can represent ticket frontiers |
| Agent access | First-party `gh` CLI plus REST/GraphQL | GraphQL API and official MCP | GitHub matches Matt's built-in path; Linear requires a recorded custom adapter |
| Beads bridge | Official `bd github pull`, `push`, `sync`, and `status` | Richer `bd linear` mapping and sync controls | Both are viable; Linear is richer, but GitHub has the selective bridge this workflow needs |
| Code linkage | Issues, PRs, commits, Actions, and Projects share one platform | Strong official GitHub integration | GitHub removes an integration boundary |
| Long-form knowledge | Repository Markdown, issue bodies, discussions, and wikis | Issue/project documents | Keep Notion for personal research rather than choosing a tracker for its docs |

## Fit With The Installed Skills

The upstream `setup-matt-pocock-skills` skill says:

- GitHub is the default tracker when the repository has a GitHub remote.
- GitHub uses the `gh` CLI.
- Linear is supported as an `Other` tracker whose workflow is recorded as
  freeform repository policy.

The generic `/to-tickets` skill is tracker-neutral after setup. On a real
tracker it creates one issue per approved slice and uses native blocking and
sub-issue relationships when available. `/to-spec` publishes its specification
to whichever tracker the repository policy selects.

This repository's `setup-linear-beads` skill is intentionally not neutral. It
preselects Linear and defines Linear as the human planning authority. That makes
Linear the path currently implemented by this repository, but it does not make
Linear inherently better for the user's needs. Choosing GitHub means replacing
or generalizing that overlay; it should not be run unchanged.

## What To Keep In Notion

Keep existing Notion pages when they contain exploratory research, reading
notes, personal context, or material spanning repositories. There is little
benefit in migrating those pages solely to make Linear or GitHub the only tool.

Move or summarize information into the GitHub feature issue when it becomes an
acceptance criterion, product decision, or implementation constraint. Move
technical decisions that must evolve with the code into repository ADRs or
other versioned Markdown. Link back to the full Notion research when useful.

## When Linear Would Win

Prefer Linear instead if several of these become true:

- Planning speed and keyboard-first issue management matter every day.
- Cycles, roadmap views, project updates, or a dedicated triage inbox are used.
- Multiple teams need consistent workflows outside a single GitHub repository.
- Non-code collaborators should not work primarily in GitHub.
- The existing Linear + Beads setup is already deployed broadly and migration
  cost is greater than the benefit of reducing tools.

Otherwise, GitHub provides the requested workflow with less operational
surface area.

## Primary Sources

- Local upstream setup contract:
  [`setup-matt-pocock-skills/SKILL.md`](file:///home/nate/.agents/skills/setup-matt-pocock-skills/SKILL.md)
- Local ticket publishing contract:
  [`to-tickets/SKILL.md`](file:///home/nate/.agents/skills/to-tickets/SKILL.md)
- Local specification publishing contract:
  [`to-spec/SKILL.md`](file:///home/nate/.agents/skills/to-spec/SKILL.md)
- Current Linear-specific overlay:
  [`setup-linear-beads/SKILL.md`](../setup-linear-beads/SKILL.md)
- [GitHub: About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)
- [GitHub: Adding sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)
- [GitHub: Creating issue dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)
- [GitHub CLI: `gh issue`](https://cli.github.com/manual/gh_issue)
- [Beads: `bd github`](https://github.com/gastownhall/beads/blob/main/docs/cli-reference/github.md)
- [Beads: `bd linear`](https://github.com/gastownhall/beads/blob/main/docs/cli-reference/linear.md)
- [Beads integration charter](https://github.com/gastownhall/beads/blob/main/engdocs/INTEGRATION_CHARTER.md)
- [Linear: Issue status](https://linear.app/docs/configuring-workflows)
- [Linear: Parent and sub-issues](https://linear.app/docs/parent-and-sub-issues)
- [Linear: GitHub integration](https://linear.app/docs/github)
- [Linear: Project documents](https://linear.app/docs/project-documents)
- [Notion: Board view](https://www.notion.com/help/boards)
- [Notion: GitHub integration](https://www.notion.com/help/github)
