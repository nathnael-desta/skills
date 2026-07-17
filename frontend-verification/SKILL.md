---
name: frontend-verification
description: "Verify frontend work in the browser before claiming a task is done. Use whenever building new UI components or pages, fixing visual or interaction bugs, confirming responsive behavior, checking accessibility, or validating that a user flow works end-to-end. Triggers on tasks involving React, Vue, Svelte, Next.js, Nuxt, SvelteKit, Astro, plain HTML/CSS, Tailwind, or any change that affects what a user sees or does. Defines build, fix, and user-flow verification workflows plus stop conditions that prevent premature \"done\" claims. Pairs with the agent-browser skill for the underlying browser automation."
---

# Frontend verification

Use **agent-browser** to verify UI work before claiming a task is done. The agent-browser skill covers *how* to drive the tool — this skill covers *when* to use it and what "done" means.

## Dev server

make your own port to test the frontend and backend for the project using this command, these should be the ports that agent-browser uses

```bash
make dev-auto
```

## Viewports

Verify at three sizes before claiming done. Defaults if the project doesn't specify:
- mobile `390 844`
- tablet `768 1024`
- desktop `1440 900`

If the project has its own breakpoints (Tailwind config, CSS media queries), pick one viewport per breakpoint instead.

## Workflow A — Building UI

1. Open the new route, snapshot, screenshot.
2. Iterate: edit → reload → snapshot → screenshot → check console.
3. Verify at all three viewports.
4. Confirm interactive elements have accessible names in the snapshot (button "Submit", not button "").
5. Run Workflow C against the new feature's user flow.

## Workflow B — Fixing UI bugs

1. Open the affected route, capture `before.png` + console baseline.
2. Edit smallest relevant file → reload → snapshot → `after.png`.
3. Diff the screenshots to confirm the fix changed what was intended.
4. Repeat at all three viewports — fixing one often breaks another.
5. Run Workflow C against any flow that touches the affected UI.

## Workflow C — User flow verification (required after A or B)

Walk the actual path a user takes to reach and use the feature. Don't jump to the target route — start where a real user starts.

1. Write the steps down first (e.g. land on `/` → click nav link → fill form → submit → see success).
2. For each step: snapshot → act with `@eN` ref → snapshot → check console.
3. Verify the final success state via snapshot, not assumption.
4. Run the full flow at all three viewports.
5. Test at least one failure path (invalid input, missing field, network error) and confirm the error surfaces on the correct element.

## Stop conditions (all must hold)

- Visual matches intent at mobile, tablet, and desktop
- No new console errors compared to baseline
- Relevant user flow passes end-to-end
- At least one failure path tested and handled correctly

## Artifacts

Save screenshots to `.agent-browser/screenshots/<task>/`. Ensure `.agent-browser/` is gitignored — add it if missing.

## Project overrides

If the project's `CLAUDE.md` or `AGENTS.md` specifies a different port, viewport set, dev command, or stop conditions, those take precedence over this skill's defaults.