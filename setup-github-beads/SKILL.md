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
- Run `bd version`, `bd status`, `bd setup --list`, `bd github status`, and the
  installed CLI's relevant `bd <command> --help` output.
- Inspect `.beads/`, selected-agent integrations, and installed skills at project
  and global scope with `npx skills@latest list --json` and `--global`.
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
use recipes listed by `bd setup --list`.

### Overlay B: GitHub access for Beads

Reuse the repository inferred from the Git remote when `bd github status` is
healthy. Otherwise configure only the missing `github.repository` value from
that remote. Reuse `GITHUB_TOKEN` when available; otherwise ask the user to make
`GITHUB_TOKEN` available through their shell or secret manager. Never request or
write the token value. GitHub operations outside Beads continue to use the
upstream skill's configured `gh` CLI path.

### Overlay C: Beads execution

Use these defaults without asking:

- Embedded storage for sequential writers.
- `review` completion mode.
- Lean OpenCode integration.

Ask about server storage only when the user says agents will write concurrently
or inspection shows an existing server setup. Ask about `auto-complete` only
when the user requests autonomous completion. Ask about official OpenCode mode
only when a managed Beads section already exists or the user requests
always-loaded instructions.

Initialize only when no active Beads database exists. Prefer `bd init
--skip-agents`; add `--server` only for the server choice. Then configure:

- Claude Code: `bd setup claude`, followed by `bd setup claude --check`.
- OpenCode lean: generate `.agents/skills/beads/SKILL.md` from `bd setup
  opencode --print` using [the bundled frontmatter](templates/beads/FRONTMATTER.md),
  then run the documented diff check in
  [OpenCode integration](references/OPENCODE.md).
- OpenCode official: `bd setup opencode`, followed by `--check`.
- Codex: use `bd setup codex` and `--check` only when listed by the CLI.

## 3. Draft and confirm

Show one coherent setup draft containing:

- Every draft and artifact the currently loaded upstream setup requires.
- The upstream GitHub issue-tracker document with the managed section from
  [routing policy](references/POLICY.md) appended.
- Every command and file mutation, including generated agent integration files.

Explain that GitHub remains the human-visible tracker for the existing Matt
workflows, while Beads receives only user-authorized implementation work. Let
the user edit the draft, then obtain one confirmation.

## 4. Apply and verify

Run the confirmed commands and write the confirmed drafts. Preserve existing
instructions and update marked sections in place.

Verify `gh auth status`, `bd doctor`, `bd github status`, each selected agent
integration, and skill discovery at its selected scope. In lean OpenCode mode,
require an exact match between the generated skill body and `bd setup opencode
--print`. Confirm that the policy declares one completion mode and contains no
secret.

Setup is complete only when:

- The loaded upstream setup's current completion criteria pass with GitHub as
  the issue tracker.
- Beads is healthy and every selected agent can discover it.
- The GitHub + Beads routing policy is unambiguous.

Finish by pointing to [the daily workflow](references/WORKFLOW.md). Do not select
or import product work during setup.
