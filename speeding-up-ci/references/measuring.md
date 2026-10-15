# Measuring CI

## Run list and run duration

```bash
gh run list --workflow ci.yml --limit 20 \
  --json databaseId,event,headBranch,conclusion,createdAt,updatedAt \
  --jq '.[] | [.databaseId, .event, .headBranch, .conclusion, ((.updatedAt|fromdate) - (.createdAt|fromdate))] | @tsv'
```

Count runs per commit: group by `headSha` (add it to `--json`). Two runs for one SHA, one with `push` and one with `pull_request`, is the duplicate-run waste.

## Per job and per step

```bash
gh api repos/{owner}/{repo}/actions/runs/<run-id>/jobs --paginate --jq '
  .jobs[] | {job: .name, secs: ((.completed_at|fromdate) - (.started_at|fromdate)),
             queued: ((.started_at|fromdate) - (.created_at|fromdate)),
             slow_steps: [.steps[] | {name, secs: ((.completed_at|fromdate) - (.started_at|fromdate))} | select(.secs > 20)]}'
```

- `queued` is time waiting for a runner, not your code; a large value points at concurrency caps.
- Steps over 20 s are the shortlist. Typical finds: dependency install, a Docker build with no cache hit, `npm ci`, schema setup inside the test step.

## Critical path

Read `needs:` in the workflow, sum job seconds along each chain, take the longest. Speeding a job off the critical path saves nothing in wall time (it still saves minutes billed).

## Test time

- `pytest --durations=50 --durations-min=0.5`: setup and teardown rows (`setup`, `teardown`) are as informative as `call` rows. Many fast tests each paying a long `setup` means a per-test fixture to widen in scope.
- Run the suite twice, cold and warm, on the same runner type before comparing a change. Report medians of at least 3 runs; one run is noise.
