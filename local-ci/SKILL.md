---
name: local-ci
description: Run a pull request's GitHub Actions CI on this machine and decide if it would pass on GitHub. Use when Actions is down or billing-blocked, before merging a PR on a local result, when several worktrees need CI at once, or when act runs collide, crawl, or fill the disk.
argument-hint: "[--pr N | --head REF --base BRANCH] [-j job,job]"
---

# Local CI

Goal: a local verdict you can merge on, one that matches what GitHub Actions would
say about the same PR. Say it the same way every time: **would pass on GitHub** or
**would fail on GitHub**, plus the job table.

The tool is `scripts/ci-local` (in this skill's folder). It reads the PR's own
workflow file and runs each job's `run:` steps natively, in a throwaway clone of
**the PR head merged into its base**, which is the commit GitHub tests. Setup actions become their local
equivalents at the versions the workflow pins: `setup-python` gives a fresh uv venv per job,
`setup-uv` gives the pinned uv, `setup-node` gives the official Node tarball, and `services:`
gives a Postgres container on a random port. Everything a run creates is
private to it, so any number of worktrees can run it at once.

## Steps

1. **Preflight.** Run `df -h /` and check `systemctl --user list-units 'run-*'`.
   Need ~3 GB free (the clone is ~370 MB; venvs hard-link from the uv cache).
   Done when disk is fine and no other full test suite is running.
2. **Run** from any checkout of the repo, under a memory cap:
   ```bash
   systemd-run --user --scope --quiet -p MemoryMax=6G \
     ~/.agents/skills/local-ci/scripts/ci-local --pr <N>     # or --head <ref> --base dev
   ```
   `--list` shows which jobs the event would run, without running them. `-j a,b` runs
   only those jobs, and `-p` sets how many run at once (default 3). It tests
   **committed** code only: commit or push first, or the result says nothing about
   your change. With `--pr`, it tests the head that is on GitHub.
   Done when it prints `PASS in` or `FAIL in` plus the path of `summary.md`.
3. **Read the verdict** from `~/temp/ci-local/runs/<id>/summary.md` and the job logs beside it:
   - `PASS`: this job would pass on GitHub.
   - `FAIL`: a real step failed. The log shows the command and its output. Fix it in the
     branch, commit, and re-run that job with `-j`.
   - `ERROR`: ci-local's own setup broke (a service never got healthy, a download
     failed). This is not a code result: fix the cause or re-run.
   - `UNSUPPORTED`: the job uses an action ci-local cannot reproduce (e.g. docker
     build). Run that one job with act ([`act.md`](act.md)), or report it as not run.
   Done when every job the event runs is `PASS`, or each one that isn't has a stated cause.
4. **Use act as well when the PR changes `.github/workflows/`.** ci-local trusts the
   workflow file; it cannot tell you that GitHub will reject it, or that an action
   version no longer exists. Follow [`act.md`](act.md) for those PRs.
5. **Report** the job table, how each job ran (ci-local, act, or skipped by its `if:`),
   and the head and base SHAs from the summary. A merge decision rests on this report.

## What ci-local matches, and what it does not

Matches GitHub: the commands (read from the workflow, never retyped), the merge
commit, the Python/uv/Node versions the workflow pins, the dependency locks
(every job gets a fresh environment from its own install step), a fresh database,
`CI=true`, and the job's `if:` for the event.

Differs from GitHub, by design: the OS is this machine rather than the runner image, Python
comes from uv's managed builds (same minor version), and every change filter
(`dorny/paths-filter`, `needs.*.outputs`) counts as matched, so ci-local runs **more**
jobs than GitHub, never fewer. Secrets are empty; a job that needs a real secret
fails, and the report says so.

Shared between runs: only the uv and npm download caches, both safe for concurrent
use. `npm ci` is replaced by a hard-linked copy of an existing worktree's
`node_modules` when that install matches the PR's `package-lock.json` exactly,
otherwise `npm ci --prefer-offline` runs.

## Measured (2026-10-19, Behigamlack)

- **PR #254** (all five jobs green on GitHub): ci-local gave the same five PASS in
  **169s wall** with `-p 3`, against ~4.6 min for GitHub's longest job. Warm per-job times:
  docs 27s, lint 18s, typecheck 74s, backend 151s (pgvector service on a random port),
  frontend 75s.
- **First run on a cold machine** is slower: Node download plus torch and the other
  wheels into the uv cache. Expect several minutes. A download or lock timeout on
  that run reports ERROR, not FAIL.
- **Known-bad commit** (#283 at `2737f869e`, before its fix): typecheck FAIL with the
  same 3 mypy errors act found, and frontend-checks FAIL with the same Vitest
  unhandled rejections, in 56s.
- The result is for the base you test against. With `--pr N` that is `origin/<base>`,
  as on GitHub. A hand-picked `--base-sha` can turn up a conflict, or hide one.

## Why not plain act for this

act imitates the runner in Docker. In parallel worktrees, that breaks in ways that
look like code failures: containers collide by name, every job shares one writable
site-packages, there is no memory cap, and each job costs ~1.7 GB of disk.
[`act.md`](act.md) has the evidence and the safe way to run act when you need it.
