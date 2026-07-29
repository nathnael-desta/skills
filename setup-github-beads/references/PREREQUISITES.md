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
| Beads GitHub auth  | User environment | An ephemeral `GITHUB_TOKEN` can be resolved       | Reuse `gh auth token` or authenticate with `gh auth login`    |
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
Record each skill's name, agent, scope, discovered path, and source provenance.
For project installs, inspect `skills-lock.json`; it records the source used for
updates. Classify a shared Git or published-package source as reproducible, an
absolute local source as development-only, and a manual copy or missing source
as unmanaged. Do not claim portable setup completion for development-only or
unmanaged installs. Do not repair installations by manually moving skill
folders.

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
2. Resolve Beads authentication in this order: an existing `GITHUB_TOKEN`, an
   ephemeral token from `gh auth token`, a user-managed shell or secret-manager
   token, then `gh auth login`. Pass the token only to the Beads process:

   ```bash
   GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token)}" bd github status
   ```

   Show this expression in the draft, never the resolved value. Do not request
   the token in chat, enable shell tracing, persist it in Beads configuration,
   write it to a tracked file, shell profile, lockfile, log, or report.

3. Inspect current configuration with `bd config list`.
4. Inspect `bd config get github.owner`, `bd config get github.repo`, and
   `bd github status`.
5. Infer owner and repository from the Git remote. Store only missing non-secret
   values supported by the installed CLI:

   ```bash
   bd config set github.owner "owner"
   bd config set github.repo "repo"
   GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token)}" bd github status
   ```

Do not pull the repository merely to test the connection.

## Verify storage health

Use `bd where` to identify the active database and storage mode. For embedded
storage, run `bd version`, `bd where`, `bd status`, and `bd list --json`, and
confirm that the resolved database exists. Use `bd doctor` only when the
installed CLI supports it for the active mode. Never use `bd init --force` as a
routine repair, and never reinitialize a database that existed before setup.

Record the issue count before and after setup. If no database exists initially,
record that state and require a newly initialized database to contain zero
issues. Otherwise, setup passes only when the counts match.

## Resume behavior

When a prerequisite requires the user to restart a shell, reload an agent, or
finish authentication, stop at that boundary and give the exact command that
resumes verification. Do not claim setup is complete until every selected layer
in the state table is ready.
