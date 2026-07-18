# Prerequisites and Recovery

Treat machine installation and repository configuration as separate layers.
Inspect each layer and explain every missing step before changing it.

## State table

| Check              | Scope            | Ready when                                        | Recovery                                                      |
| ------------------ | ---------------- | ------------------------------------------------- | ------------------------------------------------------------- |
| `gh auth status`   | User environment | The GitHub CLI is authenticated                   | Run `gh auth login`                                           |
| GitHub remote      | Repository       | It identifies the intended GitHub repository      | Add or correct the Git remote                                 |
| `bd version`       | Machine          | The CLI prints a version                          | Install Beads from its official installation guide            |
| `bd status`        | Repository       | It finds an active database                       | Initialize this repository with `bd init`                     |
| Beads GitHub auth  | User environment | `GITHUB_TOKEN` is available                       | Make `GITHUB_TOKEN` available through the user's environment  |
| `bd github status` | Repository       | It reports the intended repository and is healthy | Configure only the missing repository or authentication value |
| Agent integration  | Repository       | Every selected agent discovers Beads              | Run the applicable agent branch from the setup skill          |
| Matt skills        | Selected scope   | Requested skills appear for every selected agent  | Install through Vercel Skills for the chosen agents and scope |

An agent instruction file is not a prerequisite. The canonical GitHub + Beads
routing policy lives in `docs/agents/issue-tracker.md`. If neither root
`CLAUDE.md` nor `AGENTS.md` exists, follow the upstream setup's file-selection
rules; do not add a second instruction file.

## Manage skills

Use Vercel Skills as the installation authority. Inspect project and global
scope separately:

```bash
npx skills@latest list --json
npx skills@latest list --global --json
```

Filter with `--agent` when checking a selected environment. A skill found for
one agent or scope does not prove that another selected agent can discover it.
For project installs, inspect `skills-lock.json`; it records the source used for
updates. Preserve it when the source is a stable shared Git URL. Do not commit an
absolute local-path source as reproducible project configuration. Do not repair
installations by manually moving skill folders.

## Install the Beads CLI

Open the current official installation guide:

`https://github.com/gastownhall/beads/blob/main/docs/getting-started/installation.md`

Offer methods supported for the user's platform. Prefer a package manager the
user already trusts. Show the exact command and get approval before running a
remote installation script. After installation, verify `bd version` in a fresh
shell if PATH changed.

## Initialize a repository

From the intended Git repository, inspect `bd init --help`. When supported, use:

```bash
bd init --skip-agents
```

The flag prevents Beads from generating agent instructions before this setup
flow has chosen lean or official integration. Run plain `bd init` only when the
installed version lacks that flag. Never reinitialize an active database.

## Configure GitHub access

1. Verify the human-facing GitHub path with `gh auth status`; use `gh auth login`
   when needed.
2. Reuse `GITHUB_TOKEN` when it is already available for Beads. Otherwise ask
   the user to make `GITHUB_TOKEN` available through their shell, operating
   system, or secret manager. Do not request its value in chat or write it to a
   tracked file.
3. Run `bd github status`. When repository configuration is missing, infer
   `owner/repo` from the Git remote and store only that non-secret value:

```bash
bd config set github.repository "owner/repo"
bd github status
```

Do not pull the repository merely to test the connection.

## Resume behavior

When a prerequisite requires the user to restart a shell, reload an agent, or
finish authentication, stop at that boundary and give the exact command that
resumes verification. Do not claim setup is complete until every selected layer
in the state table is ready.
