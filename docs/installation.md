# Installation and lifecycle

Vercel Skills is the supported installer for this repository. Do not copy skill
folders into agent folders by hand.

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

## Install one skill

Install a single skill for known agents when an interactive selector is not
appropriate:

```bash
npx skills@latest add nathnael-desta/skills --skill writing-tests --agent opencode -y
npx skills@latest add nathnael-desta/skills --skill writing-tests --agent claude-code -y
```

Supported IDs used by this repository are `opencode`, `claude-code`, and
`codex`. For another agent, use the interactive installer rather than guessing
its identifier.

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
committed or reported as a reproducible source. Reinstall from the GitHub source
before claiming the setup is portable.

## Update

Update project or global installs from their recorded upstream sources:

```bash
npx skills@latest update --project
npx skills@latest update --global
```

Update one skill when only that workflow should move:

```bash
npx skills@latest update writing-tests --project
```

## Remove or move

Use Vercel Skills rather than moving directories manually:

```bash
npx skills@latest remove writing-tests
npx skills@latest remove writing-tests --global
```

To change scope or agents, remove the named skill at project and global scope as
needed, then add it again with the new `--global` or `--agent` selection. Avoid
wildcard removal because it can affect unrelated skills. Verify each selected
agent at both scopes afterward so stale copies do not shadow the intended
installation.

## Repository compatibility

Maintainers should run:

```bash
npm test
npm run verify:skills
```

The first command validates local skill structure and formatting. The second
asks the current Vercel Skills CLI to discover this repository without
installing anything.
