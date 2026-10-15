---
name: reviewing-deploys
description: Review a push-to-deploy pipeline (GitHub Actions to SSH to docker compose or a similar script) for correctness and safety. Load when asked to review, audit, harden, or debug a CD workflow, a deploy script, or a rollback path.
---

# Reviewing deploys

Output: a list of findings, each marked BUG (wrong now) or RISK (fails under a condition), each with `file:line`, the quoted line, and the failure it causes.

## Verify every claim against the file

Read each file in full and quote the line before you report it. A previous review of one pipeline reported "`set -euo pipefail` is missing" when it sat on line 14 of the script. A claim you have not quoted does not go in the report. A thing you could not check (an API that returned 404 for a non-admin, a plan limit) goes under "Not verified".

## 1. Map the path

List every file from trigger to running container (workflow, SSH step, deploy script, compose file, nginx or proxy reload), with the order commands run in. Done when each step has a file and line.

## 2. Check the classic failures

- **Tested SHA is the deployed SHA.** The image tag is the commit SHA, compose references that tag, and the server's code matches that SHA. `:latest` plus `git reset --hard origin/main` deploys whatever `main` is now: merge B landing during A's deploy gives A's image B's scripts.
- **Rollback target is captured first.** Find where the previous commit or image tag is read. If a `git pull` or `reset` in the workflow ran before the script saved it, the "previous" value is the new commit. Rollback must redeploy the previous image tag, not `:latest`, and cannot undo a migration.
- **No silent fallback to building on the server.** `pull ... || build` turns a registry or auth error into a 15-20 minute build that an SSH command timeout can kill midway. Fail loudly instead.
- **Disk is reclaimed.** Search for `docker image prune`/`system prune`; each deploy otherwise leaves a multi-GB image behind.
- **Health gate precedes the switch.** Look for a health check that runs only after containers were replaced. Prefer `docker compose up --wait` with healthchecks on every service, workers and schedulers included, not two `curl`s.
- **Migrations are safe for the old release.** The old app keeps serving during migration, so a migration must be backward-compatible (expand, then contract). A failure aborts the deploy, with no `alembic stamp head`-style fallback that records an unapplied migration as applied.
- **Environment protection.** The deploy job names an `environment` with a branch policy or required reviewers, and secrets are scoped to it. Confirm the plan supports reviewers for this repo type. Check for long-lived PATs where `GITHUB_TOKEN` suffices.
- **Deploy gates on the tree that passed CI.** Re-running a different subset of tests in the deploy workflow drifts from CI and spends minutes. Options, cheapest first: skip when the pushed tree hash equals the PR head that passed CI (look up the PR from the SHA, find its successful CI run, compare `git rev-parse <sha>^{tree}`), fall back to the full tests for a direct push; reuse CI through `workflow_call`; a merge queue. Add a post-deploy smoke test either way.

## 3. Check the mechanics

- Script strictness: `set -euo pipefail`; what the SSH action does on a non-zero exit; the action's command timeout (appleboy/ssh-action: 10 minutes by default at v1.2.2).
- `sudo` calls under a non-interactive SSH session fail if they prompt.
- Concurrency: the deploy group's `cancel-in-progress` is false, and you know what happens to the pending run (one pending per group; a newer one replaces it).
- Scope: `--force-recreate` on stateful services (database, cache) for every merge, including docs-only ones; a missing `paths` filter on the trigger.
- Failure paths leave the old release serving, and the script's last line is a non-zero exit when anything failed.

## Report

BUG list, then RISK list, then Not verified; each item with `file:line`, the quote, the failure, and the smallest fix.
