---
name: browser-control-setup
description: Install, check, repair, upgrade and smoke-test the local Browser Control setup (headless agent Chrome plus the user's own Chrome, systemd relays, bcx, guard hook). Use when the user asks to check, fix, update, test or set up Browser Control, when it reports "not connected" or "relay unavailable", or on a new machine. For using the browser, see browser-control-operations.
---

# Browser Control setup

Linux with systemd user services. Scripts live next to this file. Run them by
absolute path, e.g. `bash ~/.agents/skills/browser-control-setup/scripts/doctor.sh`.

## What the setup is, and why

| Piece | Port | Why |
|---|---|---|
| `bc-agent-browser`: headless Chrome for Testing with the extension | 19990 | Agents never touch the user's screen and need no open Chrome. Branded Chrome 137+ ignores `--load-extension`, hence Chrome for Testing. |
| `bc-agent-relay` | 19990 | One relay serves one browser, so the agent browser needs its own. |
| `browser-control-relay` | 19989 | The relay for the user's real Chrome (unpacked extension, hardcoded to 19989). |
| `prepare-extension.sh` | | Re-copies the npm extension at every start and patches its port to 19990, so upgrades carry over. |
| `BROWSER_CONTROL_PORT=19990`, `BROWSER_CONTROL_AUTOSTART=false` | | Set in `~/.bashrc`, `~/.config/environment.d/` and the Claude/Antigravity MCP `env`. Agents default to the agent browser and never spawn relays. |
| `bcx` (`~/.local/bin`) | | Compact `execute --json` output, about 8x smaller. |
| `~/.claude/hooks/browser-control-guard.py` | | Blocks `bringToFront` and CDP recording aimed at the user's Chrome (they steal focus), and download waits (they crash the relay). Nothing else is capped. |

Lessons this design encodes (2026-10-20):

- **Relays dying:** relays auto-spawned by an agent live in that agent's T3 session cgroup and die when it ends. That was the "not connected" cause.
- **Hung screenshots:** agent tabs open in the background, and Chrome throttles them, so screenshots hang on "waiting for fonts". That hang is why agents used to call `bringToFront`. The agent browser runs with `--disable-background-timer-throttling --disable-renderer-backgrounding --disable-backgrounding-occluded-windows`.
- **Every unit needs an explicit port:** systemd re-reads `environment.d` on `daemon-reload`, so a unit without one inherits 19990.

## Check

```bash
bash <skill>/scripts/doctor.sh       # read-only, prints a fix next to each problem
bash <skill>/scripts/smoke-test.sh   # 9 end-to-end checks on the agent browser (~20 s)
```

Only pass `smoke-test.sh 19989` when the user asks. It opens background tabs in their Chrome.

## Repair

| Symptom | Fix |
|---|---|
| Agent browser not connected | `systemctl --user restart bc-agent-relay bc-agent-browser` |
| A unit is failed or restart-looping | `journalctl --user -u <unit> -n 30`. `EADDRINUSE` means another process holds the port: find it with `ss -ltnp \| grep 1999`. |
| Unsupervised relay (doctor FAIL) | `kill <pid>`; the unit takes over |
| Unit runs a missing binary (node or package moved) | re-run `scripts/install.sh` |
| User's Chrome not connected | **User step:** reload Browser Control at `chrome://extensions`, then click its toolbar button on a tab. Never open Chrome or URLs on the user's desktop yourself; it steals their focus. |
| Stale sessions | `BROWSER_CONTROL_PORT=<port> browser-control session list --json`, then `session delete <id>` for old ones |

Before restarting a relay, run `browser-control status --json` on that port. If
any session shows `connected: true`, another agent is mid-task: ask first.

## Upgrade

1. `npm view @opencode-ai/browser-control version`, and read the changelog at
   https://github.com/anomalyco/browser-control (releases / `CHANGELOG.md`).
2. Check for connected sessions on both ports (see above).
3. `npm i -g @opencode-ai/browser-control@latest`
4. `bash <skill>/scripts/install.sh`. It rewrites the units with the new paths and restarts them.
5. User step: reload the extension in their Chrome (`chrome://extensions`). The agent browser reloads by itself.
6. `doctor.sh`, then `smoke-test.sh`.
7. If the release changes behaviour this setup relies on (relay port, `execute --json` shape, the
   download or focus behaviour), update `files/`, `scripts/` and `browser-control-operations` to match.

## Install on a new machine

Needs node, `jq`, systemd user services, and `npm i -g @opencode-ai/browser-control`. Then:

- Run `scripts/install.sh`. It copies Chrome for Testing from the Playwright cache, or downloads it with `@puppeteer/browsers`.
- It backs up every file it changes to `~/temp/browser-control-setup-backup-<time>/`.
- It is idempotent.

For the user's own Chrome: they load `<package>/extension/dist` as an unpacked extension (Developer mode on `chrome://extensions`).

## Uninstall

```bash
systemctl --user disable --now bc-agent-browser bc-agent-relay browser-control-relay
rm ~/.config/systemd/user/{bc-agent-browser,bc-agent-relay,browser-control-relay}.service ~/.config/environment.d/browser-control.conf
```

Then remove:

- the `browser-control-setup` block from `~/.bashrc`
- the hook entry from `~/.claude/settings.json`
- the MCP `env` keys

`~/.local/share/bc-agent-browser` holds the agent browser's profile, including its logins.
