---
name: setup-linear-beads
description: Configure Linear, Beads, supported coding agents, and optional Matt Pocock engineering skills through one repository setup flow.
disable-model-invocation: true
---

# Setup Linear + Beads

Configure one repository. This is a setup skill, not a daily execution
workflow. Preserve existing tracker instructions and user configuration. Matt
Pocock's engineering skills are supported when installed, but are not required.

## 1. Inspect the repository

Confirm all of the following before proposing changes:

- The current directory is the intended git repository.
- Existing agent instructions, skills, and issue-tracker policy files. Their
  absence is valid in a new repository; do not create `AGENTS.md` as a
  prerequisite.
- Whether the repository already defines how agents read and update Linear. If
  it does not, ask the user which supported Linear client to configure and
  follow that client's official setup instructions.
- `bd version`, `bd status`, existing `.beads/`, and `bd setup --list`.
- Whether the user runs OpenCode, Claude Code, Codex, multiple agents, or
  another environment supported by Vercel Skills.
- How those agents currently access Linear. Reuse that adapter; do not create a
  second credential path.
- Skills installed for the selected agents and scope. Use
  `npx skills@latest list --json` for project scope and add `--global` for
  global scope; do not infer installation from one agent's directory.
- Whether the recommended Matt Pocock workflow skills are already installed.
  Their absence is an installable setup choice, not a failed prerequisite.

Classify missing pieces with the state table in
[prerequisites and recovery](references/PREREQUISITES.md). Tell the user what is
missing, whether it is machine-wide or repository-specific, and the exact next
steps before proceeding.

## 2. Present the setup

Show the exact files and commands before mutating anything. Confirm:

- Agent environments to configure: OpenCode, Claude Code, both, or another
  user-named environment. Do not infer this from an empty repository.
- Completion mode: `review` by default, or explicit `auto-complete`.
- Beads storage: embedded for sequential writers; server for concurrent writers.
- OpenCode mode: lean project skill by default, or explicit official managed
  `AGENTS.md` setup. Explain the tradeoff from
  [OpenCode integration](references/OPENCODE.md).
- Matt Pocock skills choice: install the recommended workflow bundle, choose
  skills interactively with Vercel Skills, install all, or skip. For an install,
  also ask for project or global scope. Treat that interactive selection as
  approval to run the displayed command; do not require preinstallation.
- Where the Linear + Beads routing policy should live. Offer an existing
  canonical instruction file first, then an agent-appropriate file such as
  `AGENTS.md` for OpenCode/shared use or `CLAUDE.md` for Claude-only use, then a
  dedicated `docs/agents/issue-tracker.md`, plus a user-specified path. Create
  only the selected target and only after confirmation.

## 3. Configure Beads

Follow [prerequisites and recovery](references/PREREQUISITES.md). If `bd`, Linear
access, or repository initialization is missing, explain and complete that
prerequisite before agent integration. Then:

1. Run `bd init` only when the repository has no active Beads database. If the
   installed CLI supports it, use `bd init --skip-agents` so this flow controls
   agent integration without generating duplicate instructions.
2. Run `bd setup --list`, then configure each selected agent as described below.
   Do not assume a recipe exists in the installed version.
3. Reuse supported Beads OAuth when already configured. If using
   `LINEAR_API_KEY`, keep it in the environment, never a tracked file.
4. Select the Linear team with `bd linear teams`, then set
   `linear.team_id` or `linear.team_ids`.
5. Run `bd linear status`. Do not pull the whole Linear workspace.

Use the installed CLI's `bd prime` and `bd <command> --help` output as the
command source of truth.

## 4. Configure agents

### Claude Code

Run `bd setup claude`. This installs the official `bd prime --hook-json`
session hook and a minimal managed pointer. Use `--check` after setup. Do not
also install the lean Beads skill for Claude unless the user explicitly wants
both mechanisms.

### OpenCode

In lean mode, generate `.agents/skills/beads/SKILL.md` from the installed
Beads version's OpenCode recipe. Run `bd setup opencode --print`, then write the
bundled [skill frontmatter](templates/beads/FRONTMATTER.md) followed by a blank
line and the command's complete, unmodified stdout. Do not run
`bd setup opencode` without `--print`; that installs the recipe into
`AGENTS.md`. If such a managed section already exists, offer to remove it with
`bd setup opencode --remove` before installing the generated skill.

Check the generated skill for upstream drift with:

```bash
diff -u <(bd setup opencode --print) <(tail -n +5 .agents/skills/beads/SKILL.md)
```

The bundled frontmatter is exactly three lines followed by one blank line, so
line 5 begins the unmodified upstream recipe. Exit status 0 means the skill is
current. A diff means the installed Beads version changed its OpenCode recipe;
regenerate the skill with the same procedure and rerun the check. This is the
lean mode's supported equivalent of `bd setup opencode --check`.

In official mode, run `bd setup opencode` and accept its managed `AGENTS.md`
section. Do not install the lean skill unless the user explicitly requests both.
Use `bd setup opencode --check` to detect stale generated guidance and rerun the
setup command after Beads upgrades when it reports stale.

For both agents, perform both selected branches. The generated OpenCode skill
is a snapshot of the installed Beads version's actively maintained OpenCode
recipe. Its recipe still delegates complete operational guidance to `bd prime`.

### Codex

When `bd setup --list` includes `codex`, run `bd setup codex` and use
`bd setup codex --check` afterward. The installed Beads version owns the Codex
recipe. Explain every file it will create before running it and preserve existing
agent instructions.

### Other agents

For another selected environment, use its recipe only when the installed
`bd setup --list` reports one. Inspect the recipe's help or printed template,
show its target files, and obtain approval before installation. If Beads has no
recipe, do not improvise a generated integration; report that Beads setup for
that agent remains unsupported and let the user choose a supported agent or a
manually reviewed custom integration.

## 5. Configure optional Matt skills

Matt's skills remain owned by `mattpocock/skills`; never copy their skill bodies
into this repository or recreate their setup. Manage them through Vercel's
`skills` CLI so provenance is recorded in `skills-lock.json` and later updates
come from upstream.

Map selected environments to Vercel Skills agent IDs:

| Environment | Agent ID      |
| ----------- | ------------- |
| OpenCode    | `opencode`    |
| Claude Code | `claude-code` |
| Codex       | `codex`       |

For another environment, let `npx skills@latest add mattpocock/skills` present
its supported-agent selector instead of guessing an ID. For multiple known
agents, pass all IDs after one `--agent` flag.

The recommended Linear + Beads workflow bundle is:

```text
setup-matt-pocock-skills wayfinder to-spec to-tickets implement code-review
```

If the skills are absent, ask the user to choose recommended bundle, interactive
selection, all skills, or skip, plus project or global scope. Show and run the
matching command after that selection. For example, for project-local OpenCode:

```bash
npx skills@latest add mattpocock/skills --skill setup-matt-pocock-skills wayfinder to-spec to-tickets implement code-review --agent opencode -y
```

Add `--global` for global scope. Omit `--skill` and `-y` for Vercel Skills'
interactive skill selector. Use `--skill '*'` with `-y` only when the user chose
all skills. Declining skips Matt-specific setup without failing Linear + Beads
setup.

After installation, verify the selected scope and agents with the appropriate
command:

```bash
npx skills@latest list --agent opencode --json
npx skills@latest list --global --agent opencode --json
```

Require every requested workflow skill to appear for every selected agent. If
the skills were already installed, offer the scope-appropriate upstream update:

```bash
npx skills@latest update setup-matt-pocock-skills wayfinder to-spec to-tickets implement code-review --project
npx skills@latest update setup-matt-pocock-skills wayfinder to-spec to-tickets implement code-review --global
```

Do not manually move, copy, or synchronize installed skill directories.

After installation, load the upstream `setup-matt-pocock-skills` and run its
setup with Linear as the issue tracker. If newly installed skills cannot be
loaded in the current session, tell the user to reload the agent and give the
exact instruction needed to resume this step; do not recreate that setup skill's
behavior from memory.

## 6. Install the routing policy

Append or update a marked `Linear + Beads routing` section in the user-selected
canonical instruction or issue-tracker policy file using
[POLICY.md](references/POLICY.md). Do not require or silently create
`AGENTS.md`. Preserve existing Linear access instructions around the managed
section.

The resulting policy must route a Linear feature to one selectively mirrored
parent Bead, route implementation slices to its Beads descendants, and scope
execution with `bd ready --parent <parent-id>`. It must require explicit user
selection or authorization before choosing or starting a Linear issue. Once a
Linear feature is authorized, agents may autonomously choose and claim ready
Beads descendants within that feature's parent graph. If Matt's skills are
installed, record `/to-spec`, `/to-tickets`, `/implement`, and `/code-review` as
the corresponding workflow commands; otherwise record the operations without
slash commands.

## 7. Verify

Run `bd doctor`, `bd linear status`, and the documented check for each official
integration. Verify Vercel Skills installation with `npx skills@latest list
--json` at the selected scope and for each selected agent. In lean OpenCode mode,
confirm
`.agents/skills/beads/SKILL.md` contains the bundled frontmatter followed by a
blank line and the exact current output of `bd setup opencode --print`. Run the
documented `diff` check and require exit status 0, then confirm that OpenCode
discovers the skill. This check replaces `bd setup opencode --check`, which
checks the managed `AGENTS.md` target. Confirm the policy names one completion
mode and contains no secret. Report setup state without importing or creating
product work.

Setup is complete only when existing human-facing workflows still target
Linear, Beads is healthy, every selected agent can discover Beads, and the
routing policy is unambiguous. For daily behavior, point the user to
[WORKFLOW.md](references/WORKFLOW.md).
