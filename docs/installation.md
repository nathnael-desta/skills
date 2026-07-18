# Installation and Lifecycle

Vercel Skills is the supported installer for this repository. Do not manually
copy individual skill directories into agent-specific locations.

## Interactive installation

Install from GitHub with owner/repository shorthand or a full repository URL:

```bash
npx skills@latest add nathnael-desta/skills
npx skills@latest add https://github.com/nathnael-desta/skills
```

For development, install from a local clone:

```bash
npx skills@latest add /absolute/path/to/skills
```

The CLI asks which discovered skills to install and which detected agents to
target. Project scope is the default. Pass `--global` for user scope.

## Setup entry point

Install only the GitHub + Beads setup skill for known agents when an interactive
selector is not appropriate:

```bash
npx skills@latest add nathnael-desta/skills --skill setup-github-beads --agent opencode -y
npx skills@latest add nathnael-desta/skills --skill setup-github-beads --agent claude-code -y
npx skills@latest add nathnael-desta/skills --skill setup-github-beads --agent opencode claude-code -y
```

Supported IDs used by this repository are `opencode`, `claude-code`, and
`codex`. For another agent, use the interactive installer rather than guessing
its identifier.

After installation, restart or reload the agent when required and invoke
`setup-github-beads` from the target project. The setup runs the currently
installed Matt Pocock setup as its base flow and lets that upstream process own
GitHub Issues, labels, and domain docs. It adds only Beads defaults, GitHub sync
access, and routing policy to the same draft and confirmation. It does not
require an existing `AGENTS.md` and does not select an issue to implement.

## Verify installation

List project installs for a selected agent:

```bash
npx skills@latest list --agent opencode --json
```

List global installs:

```bash
npx skills@latest list --global --agent opencode --json
```

A project install records source provenance in `skills-lock.json`. Review and
commit that lockfile when it points to a stable shared source such as GitHub and
the project should reproduce the same skill source. A lockfile created from an
absolute local path is machine-specific development state and should not be
committed as a reproducible source.

## Update

Update project or global installs from their recorded upstream sources:

```bash
npx skills@latest update --project
npx skills@latest update --global
```

Update one skill when only that workflow should move:

```bash
npx skills@latest update setup-github-beads --project
```

After updating `setup-github-beads`, rerun it in the target repository. It
checks agent integrations and regenerates the lean OpenCode Beads skill when the
installed Beads OpenCode recipe changed.

## Remove or move

Use Vercel Skills rather than moving directories manually:

```bash
npx skills@latest remove setup-github-beads
npx skills@latest remove setup-github-beads --global
```

To change scope or agents, remove the old installation and add it again with the
new `--global` or `--agent` selection. Verify both scopes afterward so stale
copies do not shadow the intended installation.

## Repository compatibility

Maintainers should run:

```bash
npm test
npm run verify:skills
```

The first command validates local skill structure and formatting. The second
asks the current Vercel Skills CLI to discover this repository without
installing anything.
