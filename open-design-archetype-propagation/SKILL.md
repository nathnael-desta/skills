---
name: open-design-archetype-propagation
description: Propagate an approved redesigned Open Design archetype artifact into the production route and its mapped variants while preserving production behavior and verifying visual parity.
argument-hint: "[approved Open Design artifact or production route]"
disable-model-invocation: true
---

# Open Design Archetype Propagation

Use an explicitly approved Open Design archetype package as the visual source for
production. This skill begins after the user has redesigned the baseline in Open
Design and says it is ready.

## Approval Gate

Require a clear approval signal and identify the exact Open Design project and
artifact. If approval or the artifact is ambiguous, stop and ask for the missing
reference. Do not propagate an unapproved baseline.

Read the living archetype registry and the production route mapping before editing.
Confirm the artifact's package, Reference Route, companion frames, and mapped route
families. If the artifact belongs to a different package than the user says, report
the mismatch before changing code.

## Retrieve And Trace

Retrieve the approved source through Open Design MCP before inspecting local copies.
Prefer `get_artifact` with the explicit project and entry path. Read the linked
design-system resource when present.

Trace the complete dependency closure:

- Imported components and variants
- Global and component CSS
- Every custom property in light and dark themes
- Fonts, weights, images, icons, and SVG behavior
- Breakpoints, container widths, overflow, and responsive branches
- Companion-frame states and interaction presentation

An unresolved token, missing font, asset, or responsive rule blocks parity.

## Production Mapping

Before editing, map source elements to production elements. Label each difference:

- **Exact port**: structure and visual values transfer directly.
- **Production adaptation**: demo data becomes live data, real permissions,
  localization, routes, accessibility, or actions while presentation stays aligned.
- **Intentional deviation**: required by approved product behavior and recorded in
  the registry.
- **Missing dependency**: must be resolved before claiming completion.

Preserve production authority over:

- APIs, schemas, persistence, and error handling
- Authorization, role scope, and permission gates
- Routing, redirects, deep links, and notifications
- Legal content, disclaimers, citations, and verification obligations
- Localization behavior and real data shape

## Implement In Dependency Order

1. Promote or correct primitive and semantic tokens for both themes.
2. Correct shared Shell and Pattern components.
3. Port the Reference Route structure and responsive rules.
4. Connect real data, API calls, permissions, routes, localization, and actions.
5. Propagate only the approved patterns to representative mapped variants.
6. Preserve loading, empty, error, permission, read-only, and success behavior.
7. Update the registry with mapped routes, deviations, and implementation status.

Prefer the smallest shared component or token correction. Do not create page-local
overrides when the approved decision belongs in a shared Pattern or Shell.

## Verification

Batch all code changes before browser verification. Use the cheapest checks first:

- Formatter, typecheck, lint, focused tests, and build
- Existing API and service tests for behavior and permissions
- Browser Control for rendered visual and interactive verification

Compare Open Design and production at the same viewport, theme, state, and fixture
content. Verify desktop, narrow/mobile when responsive, light, dark, and relevant
companion states.

Check computed values, not class names:

- Colors, opacity, gradients, shadows, and borders
- Fonts, weights, line heights, and letter spacing
- Widths, heights, gaps, padding, alignment, and overflow
- Radius and SVG stroke/fill behavior
- Focus, hover, selected, disabled, loading, empty, and error states
- Bilingual content wrapping and responsive density

Use `references/propagation-checklist.md` as the completion gate. An unexplained
visible difference, fallback token, missing dependency, or unverified state means
the package is not approved.

## Completion Criteria

- The approved artifact and design-system source were retrieved through MCP.
- The Reference Route and representative mapped routes use the approved visual contract.
- Production APIs, permissions, routing, legal content, localization, and business behavior are preserved.
- Shared tokens, Shell, and Patterns are updated at the correct source of truth.
- Companion states and responsive behavior are implemented or explicitly marked as intentional deviations.
- Relevant static, behavioral, and visual checks pass.
- The registry records the package as `implemented` or `approved`, never `approved` while parity gaps remain.
- The final report names the artifact, adaptations, checks, deviations, and remaining risks.

Use `/open-design-implementation` for detailed source-parity mechanics when the
propagation task needs the full artifact implementation checklist.
