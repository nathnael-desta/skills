---
name: speeding-up-ci
description: Diagnose and speed up a slow or wasteful GitHub Actions CI pipeline, including a slow database-backed pytest suite or a slow Vitest suite. Load when the user reports slow CI, long PR checks, duplicate workflow runs, runner-minute cost, or a test suite that dominates the pipeline.
---

# Speeding up CI

Order of work: measure, remove waste, cache, fix the slow tests, and only then parallelise or buy hardware. Each step ends with a re-measurement; a change that does not move a number is reverted. Done when you can show before and after seconds per job and for the critical path, with an identical pass/skip set.

## 1. Measure first

Never change anything before you hold these:

- Per-job and per-step timings for the last 10 to 20 runs: [references/measuring.md](references/measuring.md) has the `gh` and `jq` commands.
- The critical path: the longest chain of `needs`, and the share each job holds.
- The slowest tests: `pytest --durations=50 --durations-min=0.5` (add `--setup-show` when setup is suspect), the Vitest reporter's per-file times, or Jest `--verbose`.
- How many runs one change triggers. Two runs per commit is the most common waste.

## 2. Remove waste (minutes of effort, large effect)

Workflow YAML for each item: [references/workflow.md](references/workflow.md).

- **One run per change.** `push` triggers only on the default and release branches, `pull_request` covers everything else. Concurrency group keyed on the PR number, `cancel-in-progress: true`. Merge-queue runs get a unique key and are never cancelled.
- **Don't re-test a merged tree.** If push to the default branch is the deploy gate, let it reuse a PR run that passed on the same git tree hash (`head_commit.tree_id` in the runs API). Find the PR through `commits/{sha}/pulls` (a run's `pull_requests` list empties after merge), and require a job that only runs for PRs into that branch, so a run path-filtered against another base never counts. `skip-duplicate-actions` matches on tree too, but accepts any passing run of the workflow.
- **Required checks stay honest.** A workflow skipped by `paths:` leaves its required check Pending forever; a job skipped by `if:` reports success. Put path logic in job-level `if:` and require one aggregator job (`if: always()`, `needs: [all jobs]`).
- **Timeouts on every job.** `timeout-minutes` from measured time plus margin; the default is 360.
- **Split lint and typecheck** into jobs that install only what they need and run in parallel with the heavy install. A formatter queued behind a multi-GB dependency install wastes minutes. A type checker that needs the dependencies stays with them.
- **Trim setup.** Drop unused services, toolchains, and steps from jobs that never use them. One project's Python SDK suite halved its run time (10 to 5 minutes) by dropping unused setup alone.

## 3. Cache and install

- Dependencies keyed on the lockfile hash. On GitHub-hosted runners the unpack-and-install step often costs more than the download, so a download cache alone moves little: cache the installed environment, or use a fast installer such as `uv`.
- CPU-only wheels for heavy ML packages when CI has no GPU: it avoids multi-GB CUDA downloads and "no space left on device".
- Docker builds: `type=gha` cache with a distinct `scope` per image (builds sharing the default scope overwrite each other). Pull-request builds read the cache and omit `cache-to`, because a PR-scoped cache restores only for that PR and counts against the 10 GB repository cap.
- Model and data downloads: cache them keyed on id and revision, or stub them in unit tests.

## 4. Test-suite time

- **Database-backed pytest**: [references/db-tests.md](references/db-tests.md). Schema once per session, savepoint isolation, a database per xdist worker, a marker for tests that must really commit. In one project a unit suite went from 810 s to 113 s on 2 cores with an identical pass/skip set.
- **Vitest or Jest**: [references/frontend.md](references/frontend.md). Default environment `node`, annotate the files that need a DOM. In one project: 24.4 s to 18.5 s.
- **Expensive artifacts**: cache a parse or build that tests redo on every run, keyed on a hash of the file's text (never its mtime). This was one of the changes in the 810 s to 113 s result above.
- **Sleeps**: replace with waits on events or a frozen clock; a sleep is paid on every run and every shard.

## 5. Parallelism and hardware (last; each costs complexity or money)

- Sharding with a matrix and duration-balanced splits (`pytest-split`, durations file committed), or `pytest-xdist` inside a job. Per-shard setup repeats. On a 2-vCPU runner expect about 1.6x from xdist at best; the database competes for the same cores.
- Test selection (testmon, vendor test-impact tools) cannot see dependency, config, or data-file changes, so the default branch must still run everything.
- Slow tests marked for a nightly or weekly job: ship the marker and the scheduled workflow in the same change, or those tests silently stop running.
- Larger or third-party runners cut wall time at a per-minute price. Compare cost per run, and check plan concurrency caps before switching: a capped plan queues jobs and can make runs slower.

## Report

Before and after seconds for each job and the critical path; the change that earned each saving; the pass/skip counts before and after; what was tried and reverted (for example Vitest `isolate: false` broke tests and the `threads` pool was slower in the measured project).
