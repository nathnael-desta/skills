---
name: browser-control-operations
description: Drive a browser through Browser Control MCP economically and reliably. Use when a task needs browser interaction, localhost UI iteration, an authenticated or attached tab, stateful web debugging, or visual verification of rendered output.
---

# Browser Control operations

Browser Control MCP is the default browser transport. This skill is the
operating policy for using it without burning context or producing false
passes.

## Why this transport

Measured on identical operations:

| Operation    | playwright-cli | Browser Control | Browser Control + filtered JSON |
| ------------ | -------------- | --------------- | ------------------------------- |
| Trivial eval | 124 B          | 3 B             | 3 B                             |
| Navigate     | 419 B          | 642 B           | **39 B**                        |

Roughly ten times cheaper on the calls that matter — **but only with filtered
JSON**. The playwright-cli skill additionally echoes the whole script back in a
"Ran Playwright code" block on every run and writes snapshot files you then pay
to read.

## Non-negotiables

1. **Always request JSON output and filter it to the fields you need.** Plain
   output emits every console and network event. One noisy page — a failing auth
   script, a WebSocket retry loop — floods a single call.
2. **Code executes Node-side.** Anything touching the document must run inside
   `page.evaluate`. Reaching for `document` at the top level fails.
3. **Assert, do not sleep.** Use real Playwright locators — `getByRole`, `fill`,
   `waitForSelector`. Sleeping and re-polling makes a component that never
   mounts pass silently; a locator fails immediately and tells you why.
4. **One session.** Prefer a single named or adopted session, especially the
   user's attached authenticated tab. Sessions persist across calls, so do not
   re-login each time.

## Keeping context small

- Start with **one bounded snapshot** of the relevant region, not the page.
- Combine dependent interactions and focused DOM assertions into **one execute
  call**, and return only acceptance-specific structured evidence.
- Use snapshot diff only for compatible same-page changes — never across
  navigation or reload.
- Preserve the session through localhost/HMR cycles. Request a fresh bounded
  snapshot only when state is surprising or refs are stale.
- Avoid repeated full snapshots, raw HTML, full accessibility trees,
  console/network dumps, and screenshots on every turn.

## Visual checkpoints

Capture a screenshot only for: the initial bug, a material visual change, an
ambiguous DOM-versus-rendered result, and final confirmation.

Save screenshots to temporary absolute paths. If a visual analyst is available
(see `antigravity-delegation`), route them there rather than to the primary
model. Maintain a compact UI intent/state summary across checkpoints.

Verify any actionable visual finding through DOM, ARIA, computed styles, or
bounding boxes before editing. A visual analyst is advisory: it must never
click, type, authenticate, approve, or control the browser.

## Human handoff

Use Browser Control handoff for CAPTCHA, 2FA, passkeys, payment confirmation, or
any other human-only step, then independently verify the expected URL or a
stable element before continuing.

Browser Control can **adopt the user's real authenticated tab**. That is what
makes logged-in work possible, and it is also why destructive or
account-changing actions require explicit user confirmation first.

## When it is unavailable

Use its status and doctor diagnostics and ask the user to attach or reconnect.
Do not silently fall back to an isolated browser — an isolated browser is not
logged in, so results will not reflect the user's actual session.

## Ownership

Keep inspect, act, and verify under the orchestrator's own control. Do not
delegate live browser interaction to a worker or reviewer.
