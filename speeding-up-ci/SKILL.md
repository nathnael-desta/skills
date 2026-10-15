---
name: speeding-up-ci
description: Diagnose and fix slow or wasteful GitHub Actions CI. Load when the user reports slow CI, long PR checks, duplicate workflow runs, a slow test suite in CI, or CI minutes cost.
---

# Speeding up CI

Order of work: measure, then the cheapest wins, then the expensive ones. Each step ends with a re-measurement; a change that does not move a number is reverted.

## 1. Measure first

- Pull per-job and per-step timings for the last 10-20 runs (`gh run list`, then `gh run view <id> --json jobs`) and find the critical path: the longest chain of `needs`.
- Find slow tests: `pytest --durations=25`, or the runner's reporter for Vitest/Jest.
- Done when you hold a table of job, minutes, and share of the critical path, plus the 25 slowest tests.

## 2. Remove waste (minutes of effort, large effect)

- **Duplicate runs.** A push run and a PR run for the same commit both execute. Trigger `push` only on the default branch, `pull_request` for the rest, and give concurrency a key by PR number: `group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}` with `cancel-in-progress: true`. Merge-queue runs get a unique key and are never cancelled.
- **Required checks.** A workflow skipped by a `paths:` filter leaves its required check Pending forever; a job skipped by `if:` counts as success. Put path logic in job-level `if:` and gate merges on one aggregator job (`if: always()`, `needs: [all jobs]`).
- **Timeouts.** Set `timeout-minutes` on every job; the default is 360. Base it on the measured time plus margin.
- **Fast gates.** Lint and typecheck run as their own jobs that install only what they need, in parallel with the heavy install. A formatter that waits behind a multi-GB dependency install wastes minutes.
- **Setup trimming.** Remove unused services, language toolchains, and steps from jobs that do not use them. Sentry's Python SDK cut a 10-minute run to 5 by dropping unused setup steps and services, with tests unchanged.

## 3. Cache and install

- Cache dependencies keyed on the lockfile hash. With uv, `setup-uv` caches by default; on GitHub-hosted runners the unpack-and-install step, not the download, is often what costs.
- Pull CPU-only wheels for heavy ML packages when CI has no GPU.
- Docker builds: `docker/build-push-action` with `cache-from: type=gha` and a distinct `scope` per image, because builds sharing the default scope overwrite each other. Pull-request builds read the cache and skip `cache-to`: a PR-scoped cache is restorable only by that PR, and it counts against the 10 GB repository cap.

## 4. Test-suite time

- Database-backed suites: see [references/db-tests.md](references/db-tests.md). One repo measured a unit suite at 810 s down to 113 s on 2 cores.
- Frontend: default the test environment to `node` and annotate the files that need a DOM (`// @vitest-environment jsdom`). One repo measured 24.4 s down to 18.5 s.
- Cache an expensive parsed or built artifact that tests reload on every run.
- Replace sleeps with waits on events; a sleep is paid on every run.

## 5. Parallelism and hardware (last; each costs complexity or money)

- Shard with a matrix and duration-balanced splits (`pytest-split`, durations file committed), or `pytest-xdist` inside a job. Per-shard setup repeats, and a 2-vCPU runner gives about 1.6x from xdist at best.
- Test selection (testmon, vendor test-impact tools) needs the default branch to run everything, since it cannot see dependency, config, or data-file changes.
- Mark genuinely slow tests for a nightly or weekly job, and ship the marker and the scheduled workflow in the same change; otherwise those tests are unrun.
- Larger or third-party runners cut wall time at a per-minute price; compare cost per run, and check plan concurrency caps before switching.

## Report

Before and after minutes for each job and for the critical path, the change that earned each saving, and what was tried and reverted.
