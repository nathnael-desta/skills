# Bug classes in push-to-deploy pipelines

Findings from reviewing one GitHub Actions to SSH to docker compose pipeline on a single 4 GB VPS. Detection first, then the fix.

## 1. Rollback is a no-op

- **Detect.** Find where the previous commit or image tag is read. If the workflow runs `git pull` before the deploy script runs, the script's "previous commit" is the new one. Then find what rollback redeploys: if it pulls `:latest`, it re-pulls the new image anyway.
- **Fix.** Record the last release that passed its health check in a file on the server (`.deployed-commit`), written only after the health gate passes. Roll back to that commit's own tag, and check out its code.

## 2. The server does not run the tested SHA

- **Detect.** Compose references `image: ...:latest` while CI also pushes `:<sha>` that nothing consumes. Code on the server comes from `git reset --hard origin/main` or `git pull`. Race: merge B lands while A deploys, and A's deploy gets B's compose and scripts with A's image.
- **Fix.** Tag images with the short SHA of the commit CI tested, make compose use `image: ...:${IMAGE_TAG:-latest}`, and pass the SHA into the deploy: `DEPLOY_SHA=<full sha> bash deploy.sh`. The script checks out that SHA, exports `IMAGE_TAG`, and never resets to the branch head. Run the script from that commit too: `git show "$DEPLOY_SHA:scripts/deploy.sh" > "$tmp"; bash "$tmp"`, so the deploy logic is the logic that was tested.

## 3. Silent on-server build fallback

- **Detect.** `docker compose pull ... 2>/dev/null || docker compose build`. Any auth or network blip starts a 15 to 20 minute build on a small box; the SSH action's command timeout (10 minutes by default in appleboy/ssh-action v1.2.2) kills the session mid-build with containers half swapped.
- **Fix.** Pull explicit image names first, before changing anything; on failure print which image failed and exit non-zero. Never build on the server.

## 4. No image pruning

- **Detect.** `grep -rn "prune\|rmi"` finds nothing. Check `docker system df` on the server.
- **Fix.** After a healthy deploy, remove every tag of your images except the current and previous (rollback needs the previous), then `docker image prune -f` for dangling layers. Prune after the health gate, never before.

## 5. Health gate after the swap, and only two services

- **Detect.** A `curl` loop on the API and frontend that runs after `up -d --force-recreate`. Workers, schedulers, and the database are never gated.
- **Fix.** `docker compose up -d --wait --wait-timeout <s>` gates on every service's healthcheck; give each long-starting service a `start_period` and size the timeout above the largest one. Keep a public-URL smoke test in the workflow after the script, because tests cannot see environment and production-data effects.

## 6. Databases recreated every deploy

- **Detect.** `up -d --force-recreate` with a push trigger that has no `paths:` filter: every docs-only merge restarts Postgres and Redis.
- **Fix.** Drop `--force-recreate`; compose recreates only services whose image or config changed. Reload the proxy afterwards if it caches upstream addresses.

## 7. `sudo` under non-tty SSH

- **Detect.** `sudo nginx -t`, `sudo systemctl reload` in the script. With a password policy, the prompt hangs or fails after the containers swapped, and rollback never starts.
- **Fix.** `sudo -n` (never prompt), a sudoers drop-in scoped to exactly those two commands, and treat a failed reload as reported but non-fatal when the smoke test covers the symptom.

## 8. A duplicated "final tests" job drifts from CI

- **Detect.** Compare the deploy workflow's test steps with CI's: different dependency install, no database service, a subset of suites. Each drift ships as a deploy-only failure (one case: CUDA wheels filled the runner's disk because only CI had the CPU-wheel step).
- **Fix.** Delete the duplicate. Trigger deploy from CI's success:

  ```yaml
  on:
    workflow_run:
      workflows: [CI]
      types: [completed]
      branches: [main]
    workflow_dispatch:
  env:
    DEPLOY_SHA: ${{ github.event.workflow_run.head_sha || github.sha }}
  jobs:
    build:
      if: >-
        github.event_name == 'workflow_dispatch' ||
        (github.event.workflow_run.conclusion == 'success' &&
         github.event.workflow_run.event == 'push')
      steps:
        - uses: actions/checkout@v4
          with: { ref: "${{ env.DEPLOY_SHA }}" }
  ```

  - `workflow_run` fires on any conclusion: check `conclusion == 'success'`.
  - Use `workflow_run.head_sha`, the commit CI tested. `github.sha` there is the branch head when the event fired, which a later merge may have moved.
  - It runs the workflow file from the default branch and gets secrets; only trigger on `push` events, not on forks' PRs.
  - Keep `workflow_dispatch` for redeploys and emergencies; say in the file that it skips the CI gate.
  - Alternatives: `workflow_call` of the CI workflow (removes drift, not time); skip when the pushed tree hash equals the PR head that passed CI (`git rev-parse <sha>^{tree}`); a merge queue (the tested commit is the one that lands, but needs a plan that supports it).

## 9. Rollback does not reverse migrations

- **Detect.** Migrations run while the old release is still serving; rollback restores old code and images only. Any migration that drops or renames a column breaks the old release, and a failure fallback such as `alembic stamp head` records an unapplied migration as applied.
- **Fix.** Expand, then contract: one release adds columns and tables (nullable or defaulted), the next switches the code, a later one drops the old. A failed migration aborts the deploy with the old release still serving and no automatic stamping. Write this rule where migration authors read it.

## 10. Environment and credentials

- Deploy job names an `environment:` with a deployment branch policy; required reviewers need a plan that supports them for this repository type (check, do not assume).
- `GITHUB_TOKEN` with `packages: read` is enough to pull an image built by the same repository; a long-lived classic PAT passed to the server is not needed and persists in the server's Docker config.
- Secrets are scoped to the environment, not the repository.

## Mechanics

- `set -euo pipefail` in the script; for the SSH step, `set -eu` and an explicit exit code (`STATUS=0; bash script || STATUS=$?; exit $STATUS`) when cleanup runs after.
- The SSH action's `command_timeout` exceeds the longest wait in the script (health gate plus pulls).
- Concurrency: group `deploy-production`, `cancel-in-progress: false`. One run pending per group; a newer one replaces it. That is fine only when the deploy deploys the commit it was triggered for, not "main now".
- Every failure path leaves the old release serving or says plainly that it does not; the script's last line exits non-zero whenever anything failed, including a successful rollback (the deploy still failed).
- Manual and automatic deploys use the same script, so the manual path cannot drift.
