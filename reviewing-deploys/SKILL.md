---
name: reviewing-deploys
description: Review, harden, or debug a push-to-deploy pipeline (GitHub Actions to SSH to docker compose or a shell script on one server), including its rollback path and its test gate. Load when asked to review, audit, or fix a CD workflow, a deploy script, a rollback, or "why did the deploy run the wrong code".
---

# Reviewing deploys

Output: findings each marked BUG (wrong now) or RISK (fails under a condition), with `file:line`, the quoted line, the failure it causes, and the smallest fix. Done when every check in step 2 has a verdict and every claim is quoted.

## 0. Verify every claim against the file

Read each file in full and quote the line before reporting it. A review once claimed "`set -euo pipefail` is missing" when it was on line 14. Anything you could not check (an API that 404s for a non-admin, a plan limit, an action's undocumented default) goes under "Not verified" and is never presented as a finding.

## 1. Map the path

List every file from trigger to running container, in execution order: workflow trigger and concurrency, build job, deploy job, the SSH step's own commands, the deploy script, the compose file, the proxy reload, the post-deploy check. Done when each step has a file and a line.

## 2. Check the bug classes

Each class has its detection recipe and fix in [references/checklist.md](references/checklist.md).

1. **Rollback captured too late.** The previous release is read after the workflow already pulled or reset, so "previous" equals the new release and rollback is a no-op.
2. **Server runs `:latest`, not the tested SHA.** Images are tagged with the commit SHA but compose references `:latest`, and the code is `git reset --hard origin/main` (whatever main is now).
3. **Silent build fallback.** `pull || build` turns a registry or auth error into a long on-server build that an SSH timeout kills midway.
4. **No image pruning.** Each deploy leaves a multi-GB image; the disk fills in weeks.
5. **Health gate after the swap, on two services.** The old containers are already gone when the check runs, and workers and schedulers are never gated.
6. **Databases force-recreated every deploy**, including docs-only merges.
7. **`sudo` prompts under non-tty SSH**, hanging or failing after containers were swapped.
8. **A second, hand-kept "final tests" job** that drifted from CI.
9. **Migrations assume rollback reverses them.** It does not.
10. **Environment and credentials**: no protection rules, long-lived PATs where `GITHUB_TOKEN` suffices.

Also check the mechanics in the checklist's last section: script strictness, SSH action exit and timeout semantics, concurrency of the deploy group, and failure paths that exit 0.

## 3. Prove fixes by simulating the script

Do not trust a rewritten deploy script on reading alone. `scripts/simulate-deploy.sh <deploy.sh>` runs it against a scratch git repo with shimmed `docker`, `curl`, `sudo`, `nginx`, `systemctl` and asserts five scenarios (happy path, pull failure, migration failure, unhealthy release with rollback, rollback images missing). Run it on the old script first and watch it fail, then on the new one. How it works and how to adapt it: [references/simulating.md](references/simulating.md).

## 4. Land it

- Fix in the order the checklist lists; each change is independently revertable.
- Document the new rollback semantics next to the migration rules: **expand, then contract**. Add the rule to the project's migrations doc in the same change.
- Report what you could not exercise (real registry auth, a real multi-service health gate, the SSH action's timeout behaviour): the simulation covers the script's logic, not the network.

## Report

BUG list, then RISK list, then Not verified; each item with `file:line`, quote, failure, smallest fix; plus the simulation's before and after.
