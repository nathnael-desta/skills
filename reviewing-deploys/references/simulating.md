# Simulating the deploy script locally

Goal: exercise the script's branches (pull fails, migration fails, health fails, rollback fails) without a server, a registry, or a docker daemon.

## How it works

`scripts/simulate-deploy.sh <deploy.sh>` builds, under `$SIM_ROOT` (default: a fresh `mktemp -d`; set it to keep the tree, and the script refuses to wipe a non-empty directory it did not create):

- a bare `origin.git` with three plumbing-made commits `c1..c3` on `main`;
- a server checkout `srv/` cloned from it, sitting on `c2`, with `.deployed-commit` = `c2` and an empty `.env.production`;
- a `bin/` directory of shims placed first on `PATH`: `docker`, `curl`, `sudo`, `nginx`, `systemctl`.

Then it runs the script as `DEPLOY_SHA=<c3> bash deploy.sh srv` for each scenario and asserts on the shims' call log (`calls.log`), the script's exit code, the checkout's HEAD, and `.deployed-commit`.

## The shims

- `docker` appends `docker <args> [IMAGE_TAG=<value>]` to the log, so you can assert which image tag each `compose up` ran with. `SIM_FAIL` holds newline-separated bash globs matched against that line; a match exits 1. `docker images` prints `SIM_IMAGE_TAGS`, which drives the prune logic.
- `curl` logs and exits 0, or exits 22 on a match in `SIM_CURL_FAIL`.
- `sudo` fails unless the first argument is `-n`: an un-flagged call is what would hang under non-tty SSH.
- `nginx` and `systemctl` log and succeed, so the reload path runs.

## Scenarios and what each proves

| # | Injected failure | Must hold |
|---|---|---|
| 1 | none | exit 0; target tag pulled and used by `up`; checkout and `.deployed-commit` at target; no build; old tags pruned, current and previous kept |
| 2 | `docker pull` of the target tag fails | non-zero; no `compose up`; checkout and `.deployed-commit` untouched; no build fallback |
| 3 | migration command fails | non-zero; no full `up`; checkout restored to previous; `.deployed-commit` untouched |
| 4 | `up` for the target tag fails (unhealthy) | exit 1; previous tag pulled and used by `up`; checkout and `.deployed-commit` at previous |
| 5 | as 4, and the previous tag's pull fails | exit 2 |
| 6 | (all scenarios, `all-calls.log`) | every `sudo` call used `-n` |

## Adapting it

- The CONTRACT block at the top of the script lists what it assumes: the `DEPLOY_SHA` variable, the 7-character tag, `IMAGE_TAG` exported to `compose up`, `.deployed-commit`, the 0/1/2 exit codes. Change the variable names and the glob patterns to match your script, not the other way round.
- Match shim patterns on the specific compose subcommand your script calls (`alembic upgrade`, `up -d`). If the script wraps compose in a function, the pattern still sees the final `docker compose ...` line.
- Add scenarios for your own gates: a failing identity-table check, a failing public smoke test, a missing `.env` file.

## Reading the result

- Run it on the old script first. Expect FAILs on the classes in the checklist (in the measured case: no tagged pull, rollback to the wrong tag, checkout not restored, no pruning). A harness that cannot fail the old script proves nothing.
- Some assertions pass vacuously on a script that never reaches that code path (for example "no build fallback" passes if the script built nothing because it exited earlier). Read the pairs together: scenario 2's exit code and `up` assertions tell you whether the early exit happened for the right reason.
- It does not cover: real registry auth, real healthcheck timing, Docker's recreate-only-changed behaviour, the SSH action's timeout. Say so in the report.
