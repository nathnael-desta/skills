---
name: browser-control-operations
description: Drive a browser through Browser Control economically and reliably. Use when a task needs browser interaction, localhost UI verification, an authenticated tab in the user's own Chrome (2FA, passkeys, CAPTCHAs, payments via handoff), stateful web debugging, or visual verification of rendered output.
---

# Browser Control operations

Operating policy for Browser Control (`@opencode-ai/browser-control`, tested on
0.8.4). It assumes the `browser-control-setup` skill's install: if `bcx` or the
agent browser is missing, or calls fail to connect, use that skill.

Full upstream reference for the installed version: `browser-control skill`. Read
only the section you need, e.g. `browser-control skill | sed -n '/## Recording/,/^## /p'`.

## Browser Control or T3 preview?

Pick per task. In T3 Code, the `preview_*` tools fit when the user is involved:

- they watch it inline and can take over or check things off themselves
- screenshots meant for them (`preview_snapshot` with `save: true`)
- theme or viewport checks, devices, recordings, drag/hover/upload/dialogs

Browser Control fits agent-side verification:

- It is usually cheaper. A flow runs as one Playwright script in one call, with compact output.
  Measured: a 50-row page cost ~8.5 KB via `preview_snapshot`, ~3 KB via `snapshot()` and 64 B
  via `snapshot({ find })`. A form fill+submit+verify was 1 call and 56 B, against ~6 preview calls.
- It runs invisibly from any agent or terminal and supports parallel sessions.
- It can use the user's logged-in Chrome, with `handoff()` for 2FA.

## Which browser

| Target | How | Use for |
|---|---|---|
| Headless agent Chrome (default) | `BROWSER_CONTROL_PORT=19990` is already set | Anything you can log into yourself: localhost apps, staging. No window, never touches the user's screen. Logins persist (cookies flush ~30 s after login). |
| The user's real Chrome | prefix `BROWSER_CONTROL_PORT=19989` | Their logged-in third-party accounts. Ask them to click the Browser Control toolbar button on the tab, then `session adopt`. |

Never run `browser-control serve` or `relay restart`; the relays are systemd
services and `BROWSER_CONTROL_AUTOSTART=false`. If connection errors repeat (not
connected, relay unavailable), don't loop: check the setup with `browser-control-setup`
or report it.

## Calling it

```bash
bcx 'await page.goto("http://localhost:3000/login"); return await snapshot()'   # prints "session: <id>"
bcx --session <id> 'await ref("e3").click(); await page.waitForURL("**/dashboard"); return page.url()'
bcx --session <id> --file ./flow.js
browser-control session delete <id>       # when done
```

`bcx` is `browser-control execute --json` with compact output: the value, plus an
error, URL change and page console errors only when present. Without `bcx`, pipe
`--json` to `jq .value`.

- Code runs in Node with `page`, `context`, `state` (persists per session), `fs`, `path`.
  DOM access needs `page.evaluate(() => …)`; bare `document` throws.
- Single expressions auto-return; multi-statement scripts need `return`.
- Use real `http://` URLs (`data:` URLs abort) or `page.setContent(html)`.
- Batch code changes first, then verify in one session. Fewer, bigger scripts cost less than many small calls.

## Inspect, act, verify

- `snapshot()` gives a compact semantic tree with refs `e1..eN`; act with `ref("e12").click()`.
- Cheaper reads:
  - `snapshot({ find: /checkout/i, context: 2 })`
  - `snapshot({ diff: true })` after an action, with the same options as the previous snapshot
  - `snapshot({ within: "form", maxItems: 40 })`, where `within` must match exactly one element
  - a targeted `page.evaluate`
- `ariaSnapshot()` is about 6x larger. Use it only when the compact snapshot lacks structure.
- Keep dependent steps (open menu → click item) in one call. Return evidence (URL,
  text, counts), not `"ok"`. A click returning is not proof; wait for the destination or receipt.
- Waits: prefer conditions (`locator.waitFor()`, `page.waitForURL()`, `page.waitForResponse()`)
  over sleeps. A sleep that never fails can pass a broken page.
- Short action timeouts make failures surface fast. Don't re-run a failing call unchanged;
  inspect with `snapshot()` first.
- Forms: `getByLabel(...).fill()`, `selectOption`, `check`. If `fill` hangs, use `fillInput(locator, value)`.

## Screenshots: visual checkpoints only

Image reads are the largest token cost in practice. Take one for:

- the initial bug
- a material visual change
- a DOM-versus-rendered ambiguity
- final confirmation

```js
await page.screenshot({ path: "/home/<user>/temp/<task>/after.png", style: "[id^=__browser_control]{display:none!important}" })
```

- `style` hides the agent cursor and session pill.
- The agent browser renders at 1440 px.
- The CLI returns only image metadata, so save with `path:` and read the file.
- Compare with `screenshotDiff({ baseline: "/abs/before.png" })`.
- Confirm any visual finding through the DOM, computed styles or bounding boxes before editing.

## Never

- `page.bringToFront()` or `recording --mode cdp` in the user's Chrome (19989): they raise the window
  and steal the user's focus. They are harmless in the agent browser.
- `page.waitForEvent("download")`: it is unsupported through the extension in 0.8.4 and crashes the relay.
  Fetch the bytes in `page.evaluate` and write them with `fs`.
- Using the browser as an API test runner: use `curl`.
- Working around CDP guardrails, protection tokens or CAPTCHAs.
- Handing live browser control to a worker or reviewer subagent. Inspect, act and verify stay with the orchestrator.

## The user's Chrome: adopt and hand off

```bash
BROWSER_CONTROL_PORT=19989 browser-control session adopt --target-url github.com --session gh
BROWSER_CONTROL_PORT=19989 bcx --session gh 'return await snapshot()'
```

For 2FA, passkeys, CAPTCHA or payment, hand the step to the user, then verify:

```js
await handoff("Complete the security-key prompt, then continue", {
  timeoutMs: 600_000,
  start: () => page.getByRole("button", { name: /sign in/i }).click({ timeout: 600_000 }),
})
await page.waitForURL((u) => !u.pathname.startsWith("/login"))
return page.url()
```

Destructive or account-changing actions:

1. Read the candidates.
2. Get the user's approval for the exact items.
3. Re-select only those items.
4. Assert the confirmation dialog's text.
5. Confirm, then verify.

Never auto-accept dialogs globally. For inspect-only work, use `browser-control session new <name> --read-only`.

## More (in `browser-control skill`)

- Network capture and secrets: `network start/stop`, `secrets run`
- Recording and the flight recorder
- `demonstrate()`
- WebMCP
- Password-manager prompts
- The TypeScript client
- The journal: `browser-control journal --session <id>`
