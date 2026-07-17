# Prerequisites and Recovery

Treat machine installation and repository configuration as separate layers.
Inspect each layer and explain every missing step before changing it.

## State table

| Check              | Scope            | Ready when                                                    | Recovery                                                      |
| ------------------ | ---------------- | ------------------------------------------------------------- | ------------------------------------------------------------- |
| `bd version`       | Machine          | The CLI prints a version                                      | Install Beads from its official installation guide            |
| `bd status`        | Repository       | It finds an active database                                   | Initialize this repository with `bd init`                     |
| Linear credentials | User environment | Beads OAuth or `LINEAR_API_KEY` is available                  | Authenticate with a supported method                          |
| `bd linear teams`  | Linear account   | It lists the intended team                                    | Fix credentials or workspace access                           |
| Beads team config  | Repository       | `linear.team_id` or `linear.team_ids` names the intended team | Select a listed team and store its ID with `bd config set`    |
| `bd linear status` | Repository       | It reports a healthy configuration                            | Resolve the specific credential, team, or database error      |
| Agent integration  | Repository       | Every selected agent discovers Beads                          | Run the applicable agent branch from the setup skill          |
| Matt skills        | Selected scope   | Requested skills appear for every selected agent              | Install through Vercel Skills for the chosen agents and scope |

An agent instruction file is not a prerequisite. The canonical Linear + Beads
routing policy lives in `docs/agents/issue-tracker.md`. If neither root
`CLAUDE.md` nor `AGENTS.md` exists, ask which one to create for the pointer to
that policy; do not choose one silently.

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
user already trusts. Current common choices include Homebrew and Mise. Show the
exact command and get approval before running a remote installation script.
After installation, verify `bd version` in a fresh shell if PATH changed.

## Initialize a repository

From the intended Git repository, inspect `bd init --help`. When supported, use:

```bash
bd init --skip-agents
```

The flag prevents Beads from generating agent instructions before this setup
flow has chosen lean or official integration. Run plain `bd init` only when the
installed version lacks that flag. Never reinitialize an active database.

## Configure Linear access

1. Reuse supported Beads OAuth when it is already configured. Otherwise, ask
   the user to create a personal API key in Linear under **Settings > API >
   Personal API keys**. Workspace policy may require an administrator to enable
   personal keys.
2. For personal-key authentication, ask the user to expose it as
   `LINEAR_API_KEY` through their shell, operating system, or secret manager. Do
   not request the value in chat and do not write it into a tracked file.
3. Verify the selected authentication method and choose a team:

```bash
bd linear teams
bd config set linear.team_id "TEAM_ID"
bd linear status
```

Use `linear.team_ids` only when the user intentionally selects multiple teams.
Do not import the whole Linear workspace merely to test the connection.

## Resume behavior

When a prerequisite requires the user to restart a shell, reload an agent, or
finish authentication, stop at that boundary and give the exact command that
resumes verification. Do not claim setup is complete until every selected layer
in the state table is ready.
