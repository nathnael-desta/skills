# Speeding up Vitest and Jest suites

## Measure the split

Vitest prints a duration breakdown (`transform`, `setup`, `import`, `tests`, `environment`). On CI runners with 2 vCPUs, `environment` and `import` often outweigh `tests`. In one publicly reported case the same suite took about 3 minutes under Jest and 651 s under Vitest defaults, with 184 s in `environment` alone.

## Changes, in order

1. **Default environment `node`, DOM per file.** A global `environment: 'jsdom'` pays jsdom setup for every file, including pure-function tests. Set `node` in the config and annotate only the files that render:

   ```ts
   // @vitest-environment jsdom
   ```

   In one project: 24.4 s to 18.5 s on the same suite, tests unchanged. Files that touch `document` or `window` fail loudly under `node`, which is how you find them.
2. **Pool and worker count.** Cap workers to the runner's cores. In the public report above, `pool: 'forks'` with `maxWorkers: 2` was about 25% faster than defaults on a 2-vCPU runner.
3. **Barrel imports and heavy setup files.** Import from the module, not an index that pulls half the app; keep per-file setup minimal. Measure with the `import` and `setup` numbers.
4. **Coverage off in the main CI job** when nothing gates on it; run it in a separate job.

## Tried and rejected in one project

- `isolate: false`: faster, but tests leaked module state into each other and failed. Reported speedups for it are real and so are the failures; only use it on a suite that is isolation-clean, and run it twice with shuffled order to prove that.
- `pool: 'threads'`: slower than the default forks pool.
- Swapping jsdom for a lighter DOM: reported 20 to 40% gains in vendor blogs without datasets, and at least one reported crash class. Test on your suite before adopting.

## Version traps

- A Vitest major bump can raise the minimum Node version, and newer Node is sometimes needed for globals the tests use (`File`, `fetch`). Check the package's `engines` and the CI Node version before bumping.
- Cache `~/.npm` and the framework's build cache (`.next/cache`) keyed on the lockfile hash plus source hash, with `restore-keys` on the lockfile hash alone.
