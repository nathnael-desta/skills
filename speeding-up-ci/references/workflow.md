# Workflow YAML for the waste items

## One run per change

```yaml
on:
  push:
    branches: [main]            # default and release branches only
  pull_request:
    branches: [dev, main]
  merge_group:                   # only if a merge queue is enabled

concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.event_name != 'merge_group' }}
```

- Concurrency cancels superseded runs. It does not merge a `push` run and a `pull_request` run for the same commit, because their refs differ (`refs/heads/x` against `refs/pull/N/merge`). Limiting the triggers is what removes the duplicate.
- Branches with no open PR get no CI under this scheme. Say so; it is the accepted trade.
- A `pull_request` run tests a synthetic merge of head into base at that moment, not the commit that later lands. Require branches to be up to date, or use a merge queue, when that matters.
- A merge queue needs a plan that supports it for the repository type, and adds one `merge_group` run per PR. It buys "the checked commit is the one that lands".

## Required checks and the aggregator

```yaml
  ci-ok:
    if: always()
    needs: [lint, backend, frontend]       # every job; a forgotten one is silently non-required
    runs-on: ubuntu-latest
    steps:
      - uses: re-actors/alls-green@release/v1
        with:
          jobs: ${{ toJSON(needs) }}
          allowed-skips: heavy-tier        # jobs that legitimately skip on some events
```

- Only `ci-ok` goes in branch protection.
- Without `if: always()` the aggregator is skipped when a dependency fails, and a skipped required check counts as success.
- The workflow containing it must not have a workflow-level `paths:` filter, or it never reports.

## Timeouts

```yaml
jobs:
  backend:
    timeout-minutes: 20      # measured p90 plus margin
```

## Fast gates

```yaml
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff black isort     # only the linters, pinned
      - run: ruff check . && black --check . && isort --check-only .
```

## Docker layer cache with one scope per image

```yaml
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name == 'push' }}
          cache-from: type=gha,scope=backend
          cache-to: ${{ github.event_name == 'push' && 'type=gha,scope=backend,mode=max' || '' }}
```

- Default scope is `buildkit`: building several images without distinct scopes overwrites each cache with the next.
- Only the current branch, the base branch, and the default branch caches are readable. Populate from pushes to the target branch; PR builds read only.
- All caches in a repository share one pool (10 GB by default; unused entries expire after 7 days; oldest-accessed evicted first). `mode=max` with several images plus language caches fills it quickly.
