#!/usr/bin/env bash
# Read-only health check of the Browser Control agent setup. Prints one line per
# check with the fix next to each problem. Exits 1 when anything fails.
set -uo pipefail

AGENT_PORT=19990
USER_PORT=19989
BCDIR="$HOME/.local/share/bc-agent-browser"
fails=0
ok()   { printf '[ok]   %s\n' "$*"; }
warn() { printf '[warn] %s\n' "$*"; }
fail() { printf '[FAIL] %s\n' "$*"; fails=$((fails + 1)); }

if ! command -v browser-control >/dev/null; then fail "browser-control CLI not on PATH -> npm i -g @opencode-ai/browser-control"; exit 1; fi
PKG=$(dirname "$(dirname "$(readlink -f "$(command -v browser-control)")")")
cli=$(jq -r .version "$PKG/package.json")
bundled_ext=$(jq -r .version "$PKG/extension/dist/manifest.json")
latest=$(timeout 15 npm view @opencode-ai/browser-control version 2>/dev/null || true)
if [ -z "$latest" ]; then warn "CLI $cli (npm unreachable, latest unknown)"
elif [ "$latest" = "$cli" ]; then ok "CLI $cli is the latest"
else warn "CLI $cli, npm has $latest -> see Upgrade in SKILL.md"; fi

for unit in browser-control-relay bc-agent-relay bc-agent-browser; do
  state=$(systemctl --user is-active "$unit" 2>/dev/null)
  if [ "$state" = active ]; then ok "$unit active"
  else fail "$unit $state -> systemctl --user restart $unit; journalctl --user -u $unit -n 30"; fi
  exe=$(systemctl --user show -p ExecStart --value "$unit" 2>/dev/null | grep -o 'path=[^ ;]*' | head -1 | cut -d= -f2)
  [ -n "$exe" ] && [ ! -x "$exe" ] && fail "$unit runs missing binary $exe (node or package moved) -> re-run scripts/install.sh"
done

st=$(BROWSER_CONTROL_PORT=$AGENT_PORT browser-control status --json 2>/dev/null)
if [ "$(jq -r .extension.connected <<<"$st")" = true ]; then
  v=$(jq -r .extension.version <<<"$st")
  [ "$v" = "$bundled_ext" ] && ok "agent browser connected, extension $v" \
    || fail "agent browser extension $v != bundled $bundled_ext -> systemctl --user restart bc-agent-browser"
else
  fail "agent browser not connected -> systemctl --user restart bc-agent-relay bc-agent-browser"
fi

st=$(BROWSER_CONTROL_PORT=$USER_PORT browser-control status --json 2>/dev/null)
if [ "$(jq -r .extension.connected <<<"$st")" = true ]; then
  v=$(jq -r .extension.version <<<"$st")
  [ "$v" = "$bundled_ext" ] && ok "user Chrome connected, extension $v" \
    || warn "user Chrome runs extension $v, bundled is $bundled_ext -> user reloads it at chrome://extensions"
else
  warn "user Chrome not connected (only needed for its logged-in tabs) -> user reloads Browser Control at chrome://extensions, then clicks its toolbar button on a tab"
fi

for port in $USER_PORT $AGENT_PORT; do
  # Capture first: upstream doctor exits non-zero whenever the extension is disconnected.
  report=$(BROWSER_CONTROL_PORT=$port browser-control doctor 2>&1)
  grep -q '\[ok\] relay build: matches' <<<"$report" \
    || warn "relay $port build differs from the CLI -> systemctl --user restart the relay units (check status for connected sessions first)"
done

# Relays outside the units live inside an agent's session and die with it.
for pid in $(pgrep -f 'browser-control/dist/cli.js serve'); do
  grep -qE 'browser-control-relay|bc-agent-relay' "/proc/$pid/cgroup" 2>/dev/null \
    || fail "unsupervised relay pid $pid -> kill $pid (the systemd unit takes over)"
done

[ -x "$BCDIR/chrome/chrome" ] && ok "agent Chrome: $("$BCDIR/chrome/chrome" --version 2>/dev/null)" || fail "agent Chrome missing -> scripts/install.sh"

env_line=$(env -i HOME="$HOME" PATH=/usr/bin:/bin bash -lc 'echo "$BROWSER_CONTROL_PORT $BROWSER_CONTROL_AUTOSTART"' 2>/dev/null | tail -1)
[ "$env_line" = "$AGENT_PORT false" ] && ok "login shells default to $AGENT_PORT, autostart off" || fail "login shell env is '$env_line' -> scripts/install.sh"

if [ -f "$HOME/.claude.json" ]; then
  bad=$(jq -r '[.mcpServers["browser-control"]?, (.projects // {} | .[] | .mcpServers["browser-control"]?)] | map(select(. != null and .env.BROWSER_CONTROL_PORT != "19990")) | length' "$HOME/.claude.json")
  [ "$bad" = 0 ] && ok "Claude MCP entries use $AGENT_PORT" || fail "$bad Claude MCP entries lack BROWSER_CONTROL_PORT -> scripts/install.sh"
fi
f="$HOME/.gemini/config/mcp_config.json"
if [ -f "$f" ] && jq -e '.mcpServers["browser-control"]' "$f" >/dev/null 2>&1; then
  [ "$(jq -r '.mcpServers["browser-control"].env.BROWSER_CONTROL_PORT' "$f")" = "$AGENT_PORT" ] && ok "Antigravity MCP uses $AGENT_PORT" || fail "Antigravity MCP lacks the port -> scripts/install.sh"
fi
if [ -f "$HOME/.claude/settings.json" ]; then
  grep -q browser-control-guard "$HOME/.claude/settings.json" && ok "Claude guard hook registered" || warn "guard hook not registered -> scripts/install.sh"
fi
command -v bcx >/dev/null && ok "bcx on PATH" || fail "bcx missing -> scripts/install.sh"

# The upstream skill (from anomalyco/browser-control main) can drift ahead of the installed CLI.
[ -e "$HOME/.agents/skills/browser-control" ] && warn "upstream browser-control skill installed; it may describe unreleased features -> npx skills remove browser-control -g (full text: browser-control skill)"

cut=$(date -u -d '7 days ago' +%FT%TZ)
for port in $USER_PORT $AGENT_PORT; do
  n=$(BROWSER_CONTROL_PORT=$port browser-control session list --json 2>/dev/null | jq --arg c "$cut" '[(.sessions // .)[] | select(.updatedAt < $c)] | length' 2>/dev/null)
  [ "${n:-0}" -gt 0 ] && warn "$n sessions older than 7 days on $port -> delete them (see SKILL.md, Repair)"
done

mem=$(systemctl --user show -p MemoryCurrent --value bc-agent-browser 2>/dev/null)
[[ "$mem" =~ ^[0-9]+$ ]] && ok "agent browser memory $((mem / 1048576)) MB (cap 3 GB)"

[ "$fails" -eq 0 ] && echo "doctor: healthy" || echo "doctor: $fails problem(s)"
[ "$fails" -eq 0 ]
