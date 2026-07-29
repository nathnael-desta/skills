---
name: setup-github-beads
description: Extend the installed Matt Pocock repository setup with opinionated Beads configuration for GitHub repositories.
disable-model-invocation: true
---

# Setup GitHub + Beads

Configure one repository by composing the currently installed
`setup-matt-pocock-skills` with this skill's Beads overlay. The upstream skill
owns GitHub Issues, labels, and domain docs; this skill adds Beads without
recreating that behavior.

## Interaction contract

- The first action is a skill-loader call for `setup-matt-pocock-skills`. Do not
  inspect the repository or address the user until its current body is in
  context. If the loader is unavailable or fails, stop and report that blocker.
- Explore first, then give a short summary of what is present and missing.
- Ask one section at a time and wait for the answer before continuing.
- Lead with the recommended answer so the user can accept it in one word.
- Skip choices settled by inspection and apply documented defaults silently.
- After the questions, show draft documents plus the exact commands and file
  mutations. Write only after the user confirms.

The first user-facing setup turn may contain findings and exactly one question.
Every subsequent turn asks at most one unresolved section. Never print a
numbered questionnaire, request all choices in one reply, or show the mutation
plan before the upstream process reaches its draft-confirmation step.

## 1. Explore

The interaction contract's loader call is a hard gate. Read the loaded skill's
current instructions and bundled templates; they are authoritative for every
behavior they own.

If it is not installed, ask whether to install the recommended Matt bundle
(recommended), only the setup dependency, choose interactively, or install all,
plus project or global scope. Install through Vercel Skills as described in
[Matt skills](references/MATT-SKILLS.md). If the user declines, stop and explain
that this unified setup requires the upstream setup skill. If newly installed
skills cannot be loaded in the current session, give the exact reload and resume
instruction and stop.

Perform upstream's current exploration plus these checks:

- Confirm that the intended repository has a GitHub remote and inspect existing
  GitHub tracker policy without replacing it.
- Run `gh auth status`.
- Run `bd version`, `bd where`, `bd status`, `bd list --json`, `bd config list`,
  `bd setup --list`, `bd github status`, and the installed CLI's relevant
  `bd <command> --help` output. Record the storage mode and issue count before
  making changes.
- Inspect `.beads/`, selected-agent integrations, and installed skills at project
  and global scope. Query every selected agent separately. Use
  `npx skills@latest list --agent <agent-id> --json` and its `--global`
  equivalent.
- Inspect `scripts/refresh-beads-plan.mjs` when present. It is setup-owned only
  when it matches the bundled template; otherwise preserve it and ask before
  replacing it.
- Check whether the recommended Matt workflow bundle is available for every
  selected agent and scope.

Classify missing prerequisites with
[prerequisites and recovery](references/PREREQUISITES.md). A missing repository
database or credential is setup work, not a reason to emit a questionnaire.

Present a compact findings summary. If the current directory could plausibly be
the wrong repository, ask first:

> Recommended: configure `<path>`. Is this the intended repository?

## 2. Run the composed setup

Execute the loaded upstream process as the base flow in this conversation. Do
not invoke it as a separate setup before or afterward. Preserve its current
question order, defaults, skip conditions, templates, confirmation gate, and
write rules.

Let upstream select and configure GitHub from the repository remote. Its GitHub
issue-tracker template remains authoritative and unmodified except for appending
the managed routing section from this skill. Do not restate its GitHub commands,
labels, Wayfinder operations, hierarchy, dependencies, or project conventions.

When upstream reaches draft confirmation, pause it, merge the Beads commands and
routing section into that draft, and request one combined confirmation. Then
resume upstream's write and completion steps together with this overlay.

### Overlay A: Agents

Skip when existing repository configuration settles the target agents.
Otherwise ask one question, recommending the agent running this setup:

> Recommended: configure `<detected agent>`. Which agents should this repository support?

Offer OpenCode, Claude Code, Codex, multiple, or a user-named environment. Only
use recipes listed by `bd setup --list`. Before drafting, resolve every recipe's
output paths and assign exactly one generator to each path. Use the compatibility
matrix in [OpenCode integration](references/OPENCODE.md); selecting Codex makes
official OpenCode mode mandatory when OpenCode is also selected.

### Overlay B: GitHub access for Beads

Follow [prerequisites and recovery](references/PREREQUISITES.md) as the single
source of truth for repository keys and authentication. Never request, display,
or persist a token. GitHub operations outside Beads continue to use the upstream
skill's configured `gh` CLI path.

### Overlay C: Beads execution

Use these defaults without asking:

- Embedded storage for sequential writers.
- `review` completion mode.
- Lean OpenCode integration when Codex is not selected.

Ask about server storage only when the user says agents will write concurrently
or inspection shows an existing server setup. Ask about `auto-complete` only
when the user requests autonomous completion. Ask about official OpenCode mode
only when Codex is absent and a managed Beads section already exists or the user
requests always-loaded instructions.

Initialize only when no active Beads database exists. Prefer `bd init
--skip-agents`; add `--server` only for the server choice. Then configure:

- Claude Code: `bd setup claude`, followed by `bd setup claude --check`.
- OpenCode lean: generate `.agents/skills/beads/SKILL.md` using [the bundled
  frontmatter](templates/beads/FRONTMATTER.md) and the complete, unmodified
  output from `bd setup opencode --print`, then run the documented diff check in
  [OpenCode integration](references/OPENCODE.md).
- OpenCode official: `bd setup opencode`, followed by `--check`.
- Codex: use `bd setup codex` and `--check` only when listed by the CLI.

After all selected recipes run, place the managed block from [tracker
precedence](templates/TRACKER-PRECEDENCE.md) after their generated Beads
sections in each selected agent's automatically loaded instruction file. Never
edit inside an official managed section or modify the official shared Beads
skill; either change would invalidate its integration check. Append the override
outside the managed section in `AGENTS.md` or `CLAUDE.md`. Lean OpenCode is
setup-owned, so append the block to its generated skill and exclude that marked
block from the recipe freshness diff.

### Overlay D: Planning mirror

Install `scripts/refresh-beads-plan.mjs` from [the bundled planning-mirror
template](templates/REFRESH-BEADS-PLAN.md). It is a pull-only adapter: a user
selects one or more GitHub roots, and it mirrors every nested sub-issue and
blocking prerequisite into Beads, recreates local parent/dependency edges, and
labels Wayfinder items `phase:planning`. Never run it without an explicit root,
replace a user-owned script, or use it to push changes to GitHub.

## 3. Draft and confirm

Show one coherent setup draft containing:

- Every draft and artifact the currently loaded upstream setup requires.
- The upstream GitHub issue-tracker document with the managed section from
  [routing policy](references/POLICY.md) appended.
- Every command and file mutation, including generated agent integration files,
  their resolved output paths, and the generator that owns each path.
- The setup-owned `scripts/refresh-beads-plan.mjs` template and its pull-only
  behavior.

Explain that GitHub remains the human-visible tracker for the existing Matt
workflows, while Beads receives user-authorized implementation work and a
pull-only mirror of user-selected planning scopes. Let the user edit the draft,
then obtain one confirmation.

## 4. Apply and verify

Run the confirmed commands and write the confirmed drafts. Preserve existing
instructions and update marked sections in place.

Verify `gh auth status`, Beads with the storage-aware checks in
[prerequisites and recovery](references/PREREQUISITES.md), `bd github status`,
each selected agent integration, and skill discovery at its selected scope. In
lean OpenCode mode, require an exact match between the generated recipe body and
`bd setup opencode --print`, ignoring only frontmatter and the managed
precedence block. Scan the selected instruction files for generic directives to
use Beads for all tracking; every such directive must occur before the final
precedence block. Run `node scripts/refresh-beads-plan.mjs --dry-run <selected
root>` only when the user selected a root during setup. Confirm that the routing
policy declares one completion mode, requires `phase:planning` exclusion from
ready queries, and that no draft, file, command output, or report contains a
secret.

Setup is complete only when:

- The loaded upstream setup's current completion criteria pass with GitHub as
  the issue tracker.
- Beads is healthy and every selected agent can discover it.
- The GitHub + Beads routing policy is unambiguous.
- Every managed output path has one generator, and all selected integration
  checks pass at the same time.
- Every managed marker has exactly one balanced begin/end pair, and no generated
  section silently overwrote another integration.
- The Beads issue count is unchanged, local-path skill provenance is reported as
  development-only, and a second setup pass proposes no changes.

Finish by pointing to [the daily workflow](references/WORKFLOW.md). Do not select
or import product work during setup.
