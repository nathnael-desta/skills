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

## Token And Component Contract

Treat every archetype as a reusable system specimen, not a page to repaint in
isolation. Before writing page-local markup:

1. Match each visual value to an existing primitive or semantic token. Promote a
   missing token at the design-system source of truth before adding a one-off
   value. Components consume semantic tokens; they do not introduce raw colors,
   arbitrary spacing, or page-specific typography.
2. Match repeated structure to an existing shared component or Pattern. If the
   artifact introduces a structure that another route could reasonably reuse,
   extract it into the smallest useful shared component before implementing the
   page. Tables, filters, headers, badges, tabs, pagination, stat groups, and
   loading/empty/error states are Patterns, not page-local markup.
3. Keep the component API separate from the page data contract. Shared
   components receive typed content, state, slots, and callbacks; they do not
   know the route's API, permissions, legal content, or domain-specific query.
4. Implement the component's supported states and responsive behavior at the
   shared source of truth so mapped archetype routes inherit the decision rather
   than copying it.

A page-local implementation is acceptable only when the structure is genuinely
one-off or when a documented missing dependency blocks extraction. Record that
exception as an intentional deviation and name the future component candidate.

## Upward Design-System Synchronization

Propagation is bidirectional. After mapping the approved artifact, identify
reusable discoveries that should be promoted into the attached Behigamlak design
system. Upward promotion includes new or corrected tokens, shared component
contracts, Patterns, variants, and their state/responsive specifications. It
does not include production data, API behavior, permissions, legal copy, or
domain-specific business rules.

Use this gate for every candidate:

- It has at least two credible consumers, or a clear system-level reason to
  exist before a second consumer is available.
- Its light/dark, responsive, focus, disabled, loading, empty, and error
  behavior is specified where applicable.
- Its typography, spacing, color, border, elevation, and motion values resolve
  through semantic tokens.
- Its API is reusable and data/domain agnostic.
- Its accessibility and localization behavior are explicit, including Amharic
  wrapping and density when text is present.
- It has at least one production consumer after implementation.

Create or update the upstream design-system contribution through Open Design,
then record the result in a propagation manifest or registry entry containing:

- Promoted token, component, Pattern, or variant
- Source artifact and design-system project
- Production consumer routes
- Covered themes, breakpoints, and states
- Validation evidence and any intentional deviations
- Status: `proposed`, `accepted`, `implemented`, or `rejected`

Do not silently mark an upstream candidate accepted. If the design-system
workflow requires a human approval step, leave it `proposed`, report the exact
Open Design file and candidate, and do not claim complete system propagation
until the decision is recorded. The downward production implementation may use
an already-approved shared contract; a new unapproved contract is a completion
blocker unless the user explicitly accepts the documented deviation.

Preserve production authority over:

- APIs, schemas, persistence, and error handling
- Authorization, role scope, and permission gates
- Routing, redirects, deep links, and notifications
- Legal content, disclaimers, citations, and verification obligations
- Localization behavior and real data shape

## Implement In Dependency Order

1. Promote or correct primitive and semantic tokens for both themes.
2. Promote or correct shared Shell and Pattern components, including reusable
   states and responsive rules.
3. Record upward candidates and their gate status in the design-system
   contribution or propagation manifest.
4. Port the Reference Route using the shared tokens and components; extract any
   newly repeated structure before continuing page implementation.
5. Connect real data, API calls, permissions, routes, localization, and actions.
6. Propagate only the approved patterns to representative mapped variants.
7. Preserve loading, empty, error, permission, read-only, and success behavior.
8. Update the registry with mapped routes, deviations, upstream contribution
   statuses, and implementation status.

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
- The route uses shared semantic tokens and reusable components; repeated
  structure is not copied into page-local markup.
- Upward design-system candidates have a recorded status and evidence, and every
  accepted candidate has a queryable propagation manifest entry.
- Companion states and responsive behavior are implemented or explicitly marked as intentional deviations.
- Relevant static, behavioral, and visual checks pass.
- The registry records the package as `implemented` or `approved`, never `approved` while parity gaps remain.
- The final report names the artifact, adaptations, checks, deviations, and remaining risks.

Use `/open-design-implementation` for detailed source-parity mechanics when the
propagation task needs the full artifact implementation checklist.
