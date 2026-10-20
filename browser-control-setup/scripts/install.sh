#!/usr/bin/env bash
# Install or refresh the Browser Control agent setup (Linux, systemd --user).
# Idempotent: re-run after upgrading @opencode-ai/browser-control or node.
#
#   - relay for the user's Chrome on 19989      (browser-control-relay.service)
#   - relay for the agent browser on 19990       (bc-agent-relay.service)
#   - headless Chrome for Testing + extension    (bc-agent-browser.service)
#   - BROWSER_CONTROL_PORT=19990 / AUTOSTART=false for shells, desktop apps, MCP configs
#   - bcx wrapper, Claude Code guard hook
#
# Every file it changes is backed up to ~/temp/browser-control-setup-backup-<time>/.
set -euo pipefail

SKILL_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
FILES="$SKILL_DIR/files"
BCDIR="$HOME/.local/share/bc-agent-browser"
UNITS="$HOME/.config/systemd/user"
BACKUP="$HOME/temp/browser-control-setup-backup-$(date +%Y%m%d-%H%M%S)"
AGENT_PORT=19990
USER_PORT=19989

say() { printf '==> %s\n' "$*"; }
backup() { [ -e "$1" ] || return 0; mkdir -p "$BACKUP"; cp -a "$1" "$BACKUP/$(echo "$1" | sed "s#^$HOME/##; s#/#__#g")"; }
# Overwrite in place (keeps permissions and symlinks) via a temp file.
write_json() { local f="$1" filter="$2" tmp; tmp=$(mktemp); jq "$filter" "$f" >"$tmp" && cat "$tmp" >"$f"; rm -f "$tmp"; }

for cmd in jq systemctl node browser-control; do
  command -v "$cmd" >/dev/null || { echo "missing: $cmd (install @opencode-ai/browser-control with npm -g first)" >&2; exit 1; }
done

NODE=$(node -p 'process.execPath')
PKG=$(dirname "$(dirname "$(readlink -f "$(command -v browser-control)")")")
[ -f "$PKG/package.json" ] && [ -d "$PKG/extension/dist" ] || { echo "cannot locate the browser-control package (got $PKG)" >&2; exit 1; }
say "browser-control $(jq -r .version "$PKG/package.json") at $PKG (node $NODE)"

# 1. Chrome for Testing. Branded Google Chrome 137+ ignores --load-extension.
mkdir -p "$BCDIR"
if [ ! -x "$BCDIR/chrome/chrome" ]; then
  cached=$(ls -d "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux64 2>/dev/null | sort -V | tail -1 || true)
  if [ -n "$cached" ] && [ -x "$cached/chrome" ]; then
    say "copying Chrome for Testing from $cached"
    cp -a "$cached" "$BCDIR/chrome"
  else
    say "downloading Chrome for Testing (stable)"
    npx -y @puppeteer/browsers@latest install chrome@stable --path "$BCDIR/cft" >/dev/null
    ln -sfn "$(dirname "$(ls -d "$BCDIR"/cft/chrome/linux-*/chrome-linux64/chrome | sort -V | tail -1)")" "$BCDIR/chrome"
  fi
fi
say "agent browser: $("$BCDIR/chrome/chrome" --version)"

# 2. Helper files.
install -m 755 "$FILES/prepare-extension.sh" "$BCDIR/prepare-extension.sh"
mkdir -p "$HOME/.local/bin"
install -m 755 "$FILES/bcx" "$HOME/.local/bin/bcx"
if [ -d "$HOME/.claude" ]; then
  mkdir -p "$HOME/.claude/hooks"
  install -m 755 "$FILES/browser-control-guard.py" "$HOME/.claude/hooks/browser-control-guard.py"
fi

# 3. systemd units, with this machine's node and package paths.
mkdir -p "$UNITS"
for unit in browser-control-relay bc-agent-relay bc-agent-browser; do
  backup "$UNITS/$unit.service"
  sed -e "s#@NODE@#$NODE#g" -e "s#@PKG@#$PKG#g" "$FILES/$unit.service" >"$UNITS/$unit.service"
done
systemctl --user daemon-reload

# A relay auto-spawned by an agent holds the port inside that agent's session; replace it.
for port in $USER_PORT $AGENT_PORT; do
  pid=$(ss -ltnpH "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2 || true)
  [ -n "$pid" ] || continue
  if ! grep -qE 'browser-control-relay|bc-agent-relay' "/proc/$pid/cgroup" 2>/dev/null; then
    say "stopping unsupervised relay pid $pid on $port"
    kill -TERM "$pid" 2>/dev/null || true
    for _ in $(seq 1 30); do kill -0 "$pid" 2>/dev/null || break; sleep 0.5; done
  fi
done

systemctl --user enable browser-control-relay bc-agent-relay bc-agent-browser >/dev/null 2>&1
systemctl --user restart browser-control-relay bc-agent-relay bc-agent-browser
loginctl enable-linger "$USER" 2>/dev/null || say "could not enable linger; services start at login instead of boot"

# 4. Environment: login shells, desktop apps (next login), MCP servers.
mkdir -p "$HOME/.config/environment.d"
printf 'BROWSER_CONTROL_PORT=%s\nBROWSER_CONTROL_AUTOSTART=false\n' $AGENT_PORT >"$HOME/.config/environment.d/browser-control.conf"

BEGIN='# >>> browser-control-setup >>>'
END='# <<< browser-control-setup <<<'
if [ -f "$HOME/.bashrc" ]; then
  backup "$HOME/.bashrc"
  # Drop a previous managed block, and the older hand-written one, before appending.
  python3 -I - "$HOME/.bashrc" "$BEGIN" "$END" <<'EOF'
import re, sys
path, begin, end = sys.argv[1:]
s = open(path).read()
s = re.sub(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", "", s, flags=re.S)
s = re.sub(r"\n# Browser Control: agents default to the headless agent browser.*?export BROWSER_CONTROL_AUTOSTART=false\n", "\n", s, flags=re.S)
open(path, "w").write(s.rstrip("\n") + "\n")
EOF
  cat >>"$HOME/.bashrc" <<EOF

$BEGIN
# Agents default to the headless agent browser (relay $AGENT_PORT); the user's
# Chrome is on $USER_PORT. Relays run under systemd, so CLIs must not spawn their own.
export BROWSER_CONTROL_PORT=$AGENT_PORT
export BROWSER_CONTROL_AUTOSTART=false
$END
EOF
fi

MCP_ENV="{\"BROWSER_CONTROL_PORT\":\"$AGENT_PORT\",\"BROWSER_CONTROL_AUTOSTART\":\"false\"}"
if [ -f "$HOME/.claude.json" ]; then
  backup "$HOME/.claude.json"
  write_json "$HOME/.claude.json" "
    (if .mcpServers[\"browser-control\"] then .mcpServers[\"browser-control\"].env += $MCP_ENV else . end)
    | (.projects // {}) as \$p
    | .projects = (\$p | map_values(if .mcpServers[\"browser-control\"] then .mcpServers[\"browser-control\"].env += $MCP_ENV else . end))"
fi
for f in "$HOME/.gemini/config/mcp_config.json" "$HOME/.gemini/antigravity/mcp_config.json"; do
  [ -f "$f" ] && jq -e '.mcpServers["browser-control"]' "$f" >/dev/null 2>&1 || continue
  backup "$f"
  write_json "$f" ".mcpServers[\"browser-control\"].env += $MCP_ENV"
done
if grep -q '^\[mcp_servers\.browser-control\]' "$HOME/.codex/config.toml" 2>/dev/null; then
  say "Codex has a browser-control MCP server: add env BROWSER_CONTROL_PORT=$AGENT_PORT by hand in ~/.codex/config.toml"
fi

# 5. Claude Code guard hook.
if [ -f "$HOME/.claude/settings.json" ] && ! grep -q browser-control-guard "$HOME/.claude/settings.json"; then
  backup "$HOME/.claude/settings.json"
  write_json "$HOME/.claude/settings.json" '.hooks.PreToolUse = ((.hooks.PreToolUse // []) + [{
    "matcher": "Bash|mcp__browser-control__execute|mcp__browser-control__recording_start",
    "hooks": [{"type": "command", "command": "python3 -I ~/.claude/hooks/browser-control-guard.py", "timeout": 5}]}])'
fi

# 6. Wait for the agent browser's extension.
for _ in $(seq 1 30); do
  [ "$(BROWSER_CONTROL_PORT=$AGENT_PORT browser-control status --json 2>/dev/null | jq -r .extension.connected)" = true ] && break
  sleep 1
done
say "agent browser (19990): $(BROWSER_CONTROL_PORT=$AGENT_PORT browser-control status --json 2>/dev/null | jq -c '.extension | {connected, version}')"
say "user Chrome  (19989): $(BROWSER_CONTROL_PORT=$USER_PORT browser-control status --json 2>/dev/null | jq -c '.extension | {connected, version}')"
[ -d "$BACKUP" ] && say "backups: $BACKUP"
say "done. Next: scripts/doctor.sh, then scripts/smoke-test.sh"
