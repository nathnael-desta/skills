#!/usr/bin/env bash
# End-to-end check of a Browser Control relay against a throwaway local page.
# Usage: smoke-test.sh [port]   (default 19990, the agent browser; 19989 tests
# the user's Chrome and opens background tabs there). Exits 1 on any failure.
set -uo pipefail

PORT=${1:-19990}
export BROWSER_CONTROL_PORT=$PORT
SITE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/files/test-site"
OUT=$(mktemp -d)
WEB=$(python3 -I -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])')
python3 -I -m http.server "$WEB" --bind 127.0.0.1 --directory "$SITE" >/dev/null 2>&1 &
server=$!
sessions=()
cleanup() {
  kill "$server" 2>/dev/null
  for s in "${sessions[@]}"; do browser-control session delete "$s" >/dev/null 2>&1; done
  rm -rf "$OUT"
}
trap cleanup EXIT
URL="http://127.0.0.1:$WEB"
for _ in $(seq 1 20); do curl -s -o /dev/null "$URL/" && break; sleep 0.2; done

pass=0 failn=0
check() {
  local name=$1 expect=$2; shift 2
  local t0=$(date +%s%N) out
  out=$("$@" 2>&1)
  local ms=$(( ($(date +%s%N) - t0) / 1000000 ))
  if grep -qE -- "$expect" <<<"$out"; then printf 'PASS %-26s %5d ms\n' "$name" "$ms"; pass=$((pass + 1))
  else printf 'FAIL %-26s %5d ms  %s\n' "$name" "$ms" "$(head -c 300 <<<"$out" | tr '\n' ' ')"; failn=$((failn + 1)); fi
  LAST="$out"
}

st=$(browser-control status --json 2>/dev/null)
[ "$(jq -r .extension.connected <<<"$st")" = true ] || { echo "FAIL extension on $PORT not connected (run doctor.sh)"; exit 1; }

check "navigate + title"        'BC Test'          bcx "await page.goto('$URL/'); return await page.title()"
S=$(sed -n 's/^session: \([^ ]*\).*/\1/p' <<<"$LAST"); sessions+=("$S")
check "page errors surfaced"    'test-error-from-page' printf '%s' "$LAST"
check "snapshot find"           'Show result'      bcx --session "$S" "return await snapshot({ find: /show result/i, context: 0 })"
check "click + wait for status" 'Result shown'     bcx --session "$S" "await page.getByRole('button', { name: 'Show result' }).click(); await page.getByRole('status').waitFor({ timeout: 8000 }); return await page.getByRole('status').innerText()"
check "form fill + submit"      'Thanks Abebe true' bcx --session "$S" "await page.goto('$URL/form.html'); await page.getByLabel('Name').fill('Abebe'); await page.getByLabel('Plan').selectOption('Pro'); await page.getByLabel('Accept').check(); await page.getByRole('button', { name: 'Submit' }).click(); await page.getByText(/Thanks Abebe/).waitFor({ timeout: 8000 }); return await page.locator('#msg').innerText()"
check "screenshot (clean)"      '"ok":true'        bcx --session "$S" "await page.screenshot({ path: '$OUT/shot.png', timeout: 10000, style: '[id^=__browser_control]{display:none!important}' }); return { ok: true }"
w=$(python3 -I -c 'import struct,sys; d=open(sys.argv[1],"rb").read(24); print(struct.unpack(">I", d[16:20])[0])' "$OUT/shot.png" 2>/dev/null || echo 0)
check "screenshot >= 1280 px"   '^ok'              bash -c "[ ${w:-0} -ge 1280 ] && echo ok || echo width=$w"
check "errors reach the agent"  'ERROR: .*Timeout' bcx --session "$S" "await page.locator('#does-not-exist').click({ timeout: 1500 })"

par() { bcx "await page.goto('$URL/?p=$1'); return page.url()"; }
check "two sessions in parallel" 'p=1.*p=2|p=2.*p=1' bash -c "$(declare -f par); export URL='$URL'; par 1 > '$OUT/p1' & par 2 > '$OUT/p2' & wait; cat '$OUT/p1' '$OUT/p2' | tr '\n' ' '"
for f in "$OUT/p1" "$OUT/p2"; do s=$(sed -n 's/^session: \([^ ]*\).*/\1/p' "$f" 2>/dev/null); [ -n "$s" ] && sessions+=("$s"); done

echo "smoke-test on $PORT: $pass passed, $failn failed"
[ "$failn" -eq 0 ]
