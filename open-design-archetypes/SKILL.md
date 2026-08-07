---
name: open-design-archetypes
description: Plan and execute an archetype-driven design workflow between Open Design and a production codebase. Use when designing a reusable set of reference pages, mapping routes to archetypes, creating an Open Design registry, or propagating approved archetypes into production.
argument-hint: "[product, route family, Open Design project, or design goal]"
---

# Open Design Archetypes

Use Open Design to establish a small, reusable set of canonical reference pages,
then propagate those decisions through the production codebase without replacing
production behavior.

This is a planning-and-propagation workflow, not a request to redesign every
route independently.

## Core Model

Use these terms consistently:

- **Shell**: the shared page frame, such as navigation, header, sidebar, and content canvas.
- **Archetype page**: a complete canonical page used as the visual reference for a route family.
- **Pattern**: a reusable section inside a page, such as a filter bar, KPI row, table, tabs, timeline, or chat composer.
- **Variant**: a role, domain, scope, or state adaptation that preserves the archetype's hierarchy.
- **Archetype package**: one canonical reference route plus companion frames for variants, states, responsive layouts, and patterns.
- **Specialized archetype**: a repeated workflow with a materially different primary task and page hierarchy.
- **Companion extension**: a domain-specific frame set related to an archetype but not worth promoting to a top-level package.

An archetype is a page. A shell or pattern is not an archetype. Do not create a
new production route merely to hold a design reference.

## Source Boundaries

Keep authority explicit:

- Open Design owns approved visual structure, tokens, typography, responsive rules, visual states, and interaction presentation.
- Production code owns APIs, business behavior, permissions, routing, legal content, localization data, and persistence.
- The registry owns package boundaries, canonical routes, route mappings, variants, states, order, and approval status.
- Existing production routes are the source for what the product actually does; Open Design is not an API or domain-model source.

Never silently change production behavior to match demo content. Preserve live
data, authorization, error handling, legal disclaimers, and accessibility behavior.

## Phase 1: Establish Context

1. Inspect the repository's agent guidance, design docs, route structure, shared shell, and existing design registry.
2. Load `/domain-modeling` when terminology, package boundaries, or domain relationships are being established.
3. Load `/grilling` when product or architecture decisions are unresolved. Ask decisions with the question tool, not an unstructured list in chat.
4. Do not ask the user for route counts or codebase facts. Explore the repository or delegate factual inventory work.

If the user refers to an Open Design project, artifact, archetype, active file,
or design system, retrieve it through Open Design MCP before reading local
mirrors, opening a browser, or implementing anything. Prefer a complete artifact
bundle and trace its dependency closure. If active context is unavailable, use an
explicit project ID and entry path when known; do not treat an expired pointer as
a source failure.

## Phase 2: Inventory And Classify

Count and group production pages by primary task and structure, not by URL prefix
or domain name. Record:

- Route and dynamic-route inventory
- Existing shells and shared layout boundaries
- Repeated page structures and shared components
- Role and scope variants
- Loading, empty, error, permission, read-only, and success states
- Domain workflows that cross multiple page shapes

Start with candidate core families such as auth, public content, utility, dashboard,
collection, detail, form, chat, and settings. Add specialized candidates such as
research, document production, payment operations, legal knowledge, or operational
workspaces only when the evidence supports them.

Apply this promotion rule:

- Keep a route in an existing archetype when its primary task and hierarchy match.
- Make it a variant when only role, data scope, domain content, or state changes.
- Use a companion extension when the structure is related but needs domain-specific frames.
- Create a specialized archetype when the task and hierarchy are materially different and the workflow repeats.
- Do not create an archetype for a one-off page or a data-only difference.

Do not force a complex workbench into a generic list, detail, or form page merely
to keep the package count small.

## Phase 3: Create The Registry

Create or update a living registry at the project's established design-doc path,
preferably `docs/design/audit/ARCHETYPE-REGISTRY.md`. Use
`references/archetype-registry-template.md` when no registry exists.

For every package record:

- Package name and classification
- Canonical existing production route
- Open Design project and artifact path
- Mapped production routes or route families
- Companion frames and variants
- State coverage
- Shared patterns and dependencies
- Current status: proposed, mapped, in design, implemented, or approved
- Intentional deviations and their reasons

Keep historical audits labeled as historical when their counts or taxonomy are
superseded. Never leave two documents that both appear to be the current source
of truth.

## Phase 4: Design The Packages

Use the hybrid loop:

1. Rough-map all candidate packages so the whole system is coherent.
2. Fully design one package in Open Design.
3. Add companion frames using a coverage matrix rather than every possible combination.
4. Extract or correct shared production tokens and components.
5. Implement the canonical route and representative mapped routes.
6. Verify parity and feed valid shared discoveries back into Open Design.
7. Mark the package status in the registry before starting the next package.

Each package should cover representative combinations of:

- Desktop and narrow/mobile layouts
- Light and dark themes
- English and localized content density when applicable
- Loading, empty, error, permission-gated, read-only, and success states
- Keyboard focus, reduced motion, responsive overflow, and primary/destructive actions

Do not design every role x domain x state combination. Record the coverage matrix
and let production compose approved variants for combinations not shown as separate
frames.

When an Open Design package is approved, use `/open-design-implementation` for
the source-parity implementation loop rather than duplicating its dependency and
visual-verification instructions here.

## Phase 5: Implement Safely

Implement in dependency order:

1. Primitive and semantic tokens, including both themes
2. Shared shell and patterns
3. Canonical page structure and responsive behavior
4. Production data, APIs, permissions, routing, and localization
5. Accessibility semantics and keyboard behavior
6. Mapped routes and domain variants

Reuse established production components when they can express the source exactly.
If they cannot, correct the smallest shared token or component instead of adding
page-specific overrides.

Do not vendor the full Open Design project. Promote approved values into the
production token and component sources of truth.

## Approval Gate

Do not call a package approved until all of these are true:

- The canonical Open Design page and coverage frames are reviewed.
- The registry records the reference route, mapped routes, variants, states, and status.
- Production APIs, permissions, legal content, and behavior are preserved.
- Shared components are synchronized between Open Design and production.
- Relevant formatter, type, lint, build, and focused tests pass.
- Source and production are compared at the same viewport, state, and theme.
- Light and dark mode and at least one narrow viewport are verified when responsive.
- Computed colors, fonts, dimensions, spacing, borders, SVG styles, and overflow are checked.
- Every visible difference is fixed, explained, or recorded as an intentional deviation.

Use Browser Control only for browser-required checks and only after all code changes
are batched. Do not use a browser as an API test runner; use the project's HTTP or
unit/integration checks for APIs.

## Output

At the end of a planning pass, report:

- The selected package count and why it is not simply a target number
- Canonical routes and specialized candidates
- Variants and companion extensions
- Registry path and current status of each package
- The next package and implementation order
- Unresolved decisions, intentional deviations, and verification gaps

At the end of an implementation pass, also report the exact Open Design project
and artifact used, production adaptations, checks run, and any remaining parity
risks. Never claim exact or pixel-perfect parity while a dependency, theme,
viewport, state, token, or visible difference remains unverified.
