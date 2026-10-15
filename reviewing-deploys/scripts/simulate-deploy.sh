#!/usr/bin/env bash
# Run a deploy script against a scratch git repo with `docker`, `curl`, `sudo`, `nginx`
# and `systemctl` replaced by shims on PATH, and assert what it did.
#
#   simulate-deploy.sh /path/to/deploy.sh
#
# The script under test is expected to follow this contract (edit the CONTRACT block, or
# the scenario assertions, when yours differs):
#   - invoked as `DEPLOY_SHA=<full sha> bash deploy.sh <project dir>`
#   - reads the target release from DEPLOY_SHA, checks the project dir out at it
#   - pulls images tagged with the 7-character short SHA (`docker pull ...:<tag>`)
#   - exports IMAGE_TAG=<tag> to `docker compose ... up`
#   - records the last healthy release in <project dir>/.deployed-commit
#   - exits 0 on success, 1 on failure with a successful rollback, 2 when rollback fails
#
# Nothing here touches a real docker daemon, registry, or network.
set -euo pipefail

SCRIPT="$(cd "$(dirname "${1:?usage: simulate-deploy.sh /path/to/deploy.sh}")" && pwd)/$(basename "$1")"
ROOT="${SIM_ROOT:-$(mktemp -d)}"   # set SIM_ROOT to keep the scratch tree somewhere durable
if [ -e "$ROOT" ] && [ -n "$(ls -A "$ROOT" 2>/dev/null)" ] && [ ! -f "$ROOT/.simulate-deploy" ]; then
  echo "refusing to reuse non-empty $ROOT that this script did not create" >&2; exit 2
fi
rm -rf "$ROOT"; mkdir -p "$ROOT/bin" "$ROOT/work"; touch "$ROOT/.simulate-deploy"
export SIM_ALL_LOG="$ROOT/all-calls.log"; : > "$SIM_ALL_LOG"   # survives across scenarios

# ---------------------------------------------------------------- shims
cat > "$ROOT/bin/docker" <<'SHIM'
#!/usr/bin/env bash
# Logs every call with the IMAGE_TAG it saw. SIM_FAIL holds newline-separated bash globs,
# matched against "<args> [IMAGE_TAG=<tag>]"; a match exits 1.
line="$* [IMAGE_TAG=${IMAGE_TAG:-}]"
echo "docker $line" >> "$SIM_LOG"
while IFS= read -r pat; do
  [ -n "$pat" ] && [[ "$line" == $pat ]] && exit 1
done <<< "${SIM_FAIL:-}"
[ "$1" = images ] && printf '%s\n' ${SIM_IMAGE_TAGS:-}
exit 0
SHIM
cat > "$ROOT/bin/curl" <<'SHIM'
#!/usr/bin/env bash
echo "curl $*" >> "$SIM_LOG"
while IFS= read -r pat; do
  [ -n "$pat" ] && [[ "$*" == $pat ]] && exit 22
done <<< "${SIM_CURL_FAIL:-}"
exit 0
SHIM
cat > "$ROOT/bin/sudo" <<'SHIM'
#!/usr/bin/env bash
# A non-tty SSH session cannot answer a password prompt: without -n this would hang.
echo "sudo $*" | tee -a "$SIM_ALL_LOG" >> "$SIM_LOG"
if [ "$1" != "-n" ]; then echo "sudo: no tty present (would prompt)" >&2; exit 1; fi
shift; exec "$@"
SHIM
cat > "$ROOT/bin/nginx" <<'SHIM'
#!/usr/bin/env bash
echo "nginx $*" >> "$SIM_LOG"; exit 0
SHIM
cat > "$ROOT/bin/systemctl" <<'SHIM'
#!/usr/bin/env bash
echo "systemctl $*" >> "$SIM_LOG"; exit 0
SHIM
chmod +x "$ROOT"/bin/*

# ---------------------------------------------------------------- scratch repo
git init -q --bare "$ROOT/origin.git"
git init -q -b main "$ROOT/work/repo"
(
  cd "$ROOT/work/repo"
  git remote add origin "$ROOT/origin.git"
  # Plumbing commits: no identity guard, hook, or `git commit` wrapper in the way.
  parent=""
  for n in 1 2 3; do
    echo "release $n" > release.txt
    echo "services: {}" > docker-compose.prod.yml
    git add -A
    parent=$(git -c user.name=sim -c user.email=sim@example.invalid \
      commit-tree "$(git write-tree)" ${parent:+-p "$parent"} -m "c$n")
    git update-ref refs/heads/main "$parent"
  done
  git push -q origin main
)
C1=$(git -C "$ROOT/work/repo" rev-parse HEAD~2)
C2=$(git -C "$ROOT/work/repo" rev-parse HEAD~1)
C3=$(git -C "$ROOT/work/repo" rev-parse HEAD)
short() { echo "${1:0:7}"; }

# ---------------------------------------------------------------- scenario runner
FAILED=0
fresh_server() {            # a server checkout sitting on C2, last healthy release C2
  rm -rf "$ROOT/srv"; git clone -q "$ROOT/origin.git" "$ROOT/srv"
  git -C "$ROOT/srv" checkout -q --detach "$C2"
  echo "$C2" > "$ROOT/srv/.deployed-commit"
  : > "$ROOT/srv/.env.production"
  export SIM_LOG="$ROOT/calls.log"; : > "$SIM_LOG"
  export SIM_FAIL="" SIM_CURL_FAIL="" SIM_IMAGE_TAGS="old0000 $(short "$C1") $(short "$C2") $(short "$C3") latest"
}
deploy() {                  # runs the script; sets RC
  set +e
  ( cd "$ROOT/srv" && PATH="$ROOT/bin:$PATH" DEPLOY_SHA="$C3" bash "$SCRIPT" "$ROOT/srv" ) > "$ROOT/out.log" 2>&1
  RC=$?
  set -e
}
check() {                   # check "<description>" <command...>
  local d="$1"; shift
  if "$@"; then echo "  PASS  $d"; else echo "  FAIL  $d"; FAILED=1; fi
}
called()     { grep -qE -- "$1" "$SIM_LOG"; }
not_called() { ! grep -qE -- "$1" "$SIM_LOG"; }
head_is()    { [ "$(git -C "$ROOT/srv" rev-parse HEAD)" = "$1" ]; }
deployed_is(){ [ "$(cat "$ROOT/srv/.deployed-commit")" = "$1" ]; }
rc_is()      { [ "$RC" -eq "$1" ]; }

T3=$(short "$C3"); T2=$(short "$C2")

echo "1. happy path: C2 -> C3"
fresh_server; deploy
check "exit 0" rc_is 0
check "pulled the target tag $T3" called "docker pull .*:$T3"
check "compose up ran with IMAGE_TAG=$T3" called "up .*\[IMAGE_TAG=$T3\]"
check "server checkout is the target commit" head_is "$C3"
check ".deployed-commit records the target" deployed_is "$C3"
check "no build on the server" not_called "docker (compose .*)?build"
check "old image tags pruned" called "rmi .*old0000"
check "current and previous tags kept" not_called "rmi .*:($T3|$T2)\b"

echo "2. image pull fails: nothing may change"
fresh_server; export SIM_FAIL="pull*:$T3 *"; deploy
check "non-zero exit" bash -c "[ $RC -ne 0 ]"
check "no compose up" not_called "compose .* up "
check "checkout untouched" head_is "$C2"
check ".deployed-commit untouched" deployed_is "$C2"
check "no build fallback" not_called "build"

echo "3. migration fails: old release must keep serving"
fresh_server; export SIM_FAIL="*alembic upgrade*"; deploy
check "non-zero exit" bash -c "[ $RC -ne 0 ]"
check "no full compose up after the migration" not_called "up -d --remove-orphans"
check "checkout restored to the previous release" head_is "$C2"
check ".deployed-commit untouched" deployed_is "$C2"

echo "4. new release unhealthy: roll back to the previous release's own images"
fresh_server; export SIM_FAIL="*up -d --remove-orphans*[[]IMAGE_TAG=$T3[]]"; deploy
check "exit 1 (failed, rolled back)" rc_is 1
check "pulled the rollback tag $T2" called "docker pull .*:$T2"
check "compose up ran with IMAGE_TAG=$T2" called "up .*\[IMAGE_TAG=$T2\]"
check "checkout is the previous release" head_is "$C2"
check ".deployed-commit still the previous release" deployed_is "$C2"

echo "5. rollback images gone: must say so and exit 2"
fresh_server; export SIM_FAIL="*up -d --remove-orphans*[[]IMAGE_TAG=$T3[]]
pull*:$T2 *"; deploy
check "exit 2" rc_is 2

echo "6. sudo without -n would hang under non-tty SSH"
check "every sudo call used -n" bash -c "! grep -E '^sudo ' '$SIM_ALL_LOG' | grep -qvE '^sudo -n '"

echo
if [ "$FAILED" -eq 0 ]; then echo "All scenarios passed."; else echo "Some scenarios FAILED; see $ROOT/out.log and $ROOT/calls.log"; exit 1; fi
