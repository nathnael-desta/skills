# act: when you need it and how to run it safely

Reach for act only for a PR that changes `.github/workflows/`, or for a job that
ci-local reports as `UNSUPPORTED`. It proves the workflow runs as a workflow
(schema, `uses:` actions resolving, step wiring); ci-local proves the commands pass.

## Pitfalls (nektos/act v0.2.89, found 2026-10-19 on five parallel PR runs)

- **Name collisions.** The job container is named `act-<workflow name>-<job name>-<sha256 of those>`
  (`pkg/runner/run_context.go`, `jobContainerName` / `createContainerName`). Nothing
  in the name is per worktree. Two worktrees running the same job remove each other's
  container and volumes: exit 137, "RWLayer … unexpectedly nil", "volume is in use".
- **`-j` runs the `needs:` chain too**, outside any lock you hold for that job.
- **One shared site-packages.** `setup-python` installs into `/opt/hostedtoolcache`,
  which is the named volume `act-toolcache` that every act container on the machine
  shares. `uv pip install --system` writes there, so PRs see each other's packages:
  a package one PR removed stays installed for the others (false pass), and concurrent
  installs can tear it (false fail).
- **No memory cap.** Job containers are started by dockerd; `systemd-run` around act
  caps only the act process. `docker inspect` shows `Memory=0`.
- **Disk.** Each Python job container grows to ~1.7 GB (setup-uv restores its cache
  into it). Three at once took the disk from 5 GB to 2.4 GB free.
- **Services.** A job with `services:` gets its own Docker network. On a machine with many
  old compose networks that fails with "all predefined address pools have been fully
  subnetted". The job container is on that network, so `localhost:5432` does not reach
  the service; it needs the service name as host. Published `ports:` clash across runs.
- **paths-filter** asks the GitHub API for the PR's files **as pushed**, so unpushed
  commits are invisible to it and it can skip jobs on stale data.

## Safe recipe

1. Generate a private copy of the workflow: set `name:` to `CI-<worktree>` (unique
   container names), delete every `needs:`, and run each job explicitly.
2. Run **one act job at a time on the whole machine** (shared toolcache), e.g. behind
   `flock ~/temp/act.lock`.
3. Flags: `-W <copy> -j <job> --pull=false --action-offline-mode
   -P ubuntu-latest=catthehacker/ubuntu:act-latest`, plus an event file whose
   `pull_request.base.ref` is the PR's base.
4. Check `df -h /` before and after; stale `act-*` containers and volumes from
   killed runs keep their disk until removed.
