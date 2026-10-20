#!/bin/sh
# Copy the installed Browser Control extension and point it at the agent relay
# port, so the headless agent browser and the user's own Chrome (19989) can be
# connected at the same time. Re-run on every start, so npm upgrades carry over.
set -eu
src="$BC_PKG/extension/dist"
dst="$HOME/.local/share/bc-agent-browser/extension"
rm -rf "$dst.tmp" && cp -r "$src" "$dst.tmp"
sed -i "s/^var relayPort = 19989;/var relayPort = ${BROWSER_CONTROL_PORT};/" "$dst.tmp/background.js"
grep -q "^var relayPort = ${BROWSER_CONTROL_PORT};" "$dst.tmp/background.js"
rm -rf "$dst" && mv "$dst.tmp" "$dst"
