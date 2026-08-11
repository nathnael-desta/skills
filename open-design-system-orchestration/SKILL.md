---
name: open-design-system-orchestration
description: Plan a production-derived Open Design workflow from codebase inventory through design-system components, archetype reference pages, implementation, and propagation. Produce one canonical spec and dependency-aware tickets; do not author components or pages in this session.
argument-hint: "[scope, route family, or design milestone]"
disable-model-invocation: true
---

# Open Design System Orchestration

Turn a design-system or product-redesign request into a production-derived,
dependency-aware execution plan. This skill is the coordinator between the
repository, Open Design, the `to-spec` workflow, the `to-tickets` workflow, and
the individual Open Design execution skills.

This is a planning and routing skill. It does not commission long Open Design
authoring runs, implement production UI, or propagate designs into production.

## Project Model

Behigamlak uses two Open Design projects with different responsibilities:

- **Behigamlak Design System**: tokens, brand rules, component contracts,
  component previews, domain components, and reusable patterns.
- **Behigamlak Prototype**: archetype reference pages, companion frames, route
  variants, responsive states, and design handoffs.

Keep these project boundaries explicit in every spec and ticket. A component
belongs in the design-system project before an archetype depends on it. A
reference page belongs in the prototype project and must use approved design-system
components.

The repository also carries a checked-in design-system contract at
`docs/design/DESIGN-SYSTEM.md` and its machine-readable manifest at
`docs/design/design-system-manifest.json`. These are synchronized references for
agents and production developers, not a vendored copy of the Open Design project.
The repository's version-controlled token source and production components remain
the engineering source of truth. Open Design records approved visual intent and
provides the review surface; it is not an independent runtime source.

## Hard Rules

- Derive the plan from production code, routes, APIs, permissions, localization,
  real enums, existing component usage, and approved product requirements.
- Treat the application as the source of truth for feature scope and behavior.
- Treat the repository token source as the source of truth for shipped token values.
- Treat production components as the source of truth for component behavior and
  accessibility.
- Treat Open Design as the source of truth for approved visual intent until that
  decision is promoted into the repository and verified.
- Record a source for every proposed component, pattern, state, and page feature.
- Mark each item `implemented`, `approved-requested`, `not-applicable`, or
  `blocked`. Block design work when an item would require inventing production
  behavior.
- Prefer one canonical component with explicit variants over duplicated components.
- Do not make a separate archetype for a role, theme, viewport, or state when it
  can be a companion frame or component variant.
- Keep component authoring, archetype authoring, production implementation, and
  propagation in separate tickets and sessions.
- Preserve production APIs, auth, RBAC, permissions, navigation, notifications,
  localization, mutations, and error behavior.
- Do not make visual completeness a reason to add an unimplemented feature.
- Do not claim production parity before implementation and visual verification.

## Workflow

### 1. Establish Scope

Read the request, `CONTEXT.md`, `AGENTS.md`, the relevant design audit documents,
the archetype registry, and `docs/agents/issue-tracker.md`. Decide whether the scope
is:

- design-system foundations
- shared components
- domain components
- page patterns
- archetype reference pages
- production implementation
- propagation or migration

If the request mixes multiple scopes, retain the full destination but split it
into phases and tickets.

Completion criterion: the target scope, excluded scope, canonical Open Design
projects, and expected deliverables are written down.

### 2. Inspect Both Sources

Retrieve the live Open Design projects through Open Design MCP before using local
mirrors:

- `Behigamlak Design System`
- `Behigamlak Prototype`

For the design-system project, inventory `DESIGN.md`, tokens, components, patterns,
component previews, and design-system metadata. For the prototype project,
inventory archetypes, companion frames, artifact manifests, and existing handoffs.

Then inspect the repository:

- `docs/design/DESIGN-SYSTEM.md`
- `docs/design/design-system-manifest.json`
- the repository's canonical token source, if separate from the generated CSS

- route and page inventory
- shared UI and layout components
- API calls and response shapes
- permissions and role-driven navigation
- localization and Amharic content rules
- loading, empty, error, success, read-only, and permission states
- existing production usage of each candidate component

Compare all three surfaces and classify drift:

- `synchronized`: Open Design contract, repository contract, and production code
  agree
- `design-only`: approved in Open Design but not yet represented in production
- `code-only`: production behavior exists without an Open Design contract
- `stale`: the repository contract or implementation no longer matches Open Design
- `missing`: required by production or the approved scope but absent from one source
- `needs-variant`: the base component exists but required themes, states, roles, or
  responsive behavior are incomplete

If the repository contract is absent, create a prerequisite documentation and
manifest ticket before component or archetype authoring. If the repository has no
canonical, version-controlled token source separate from generated/runtime output,
create a `design-token-source` prerequisite ticket; a prose manifest is not a token
source. If the contract exists but is stale,
create a sync ticket and block dependent archetype tickets until the owner decides
whether Open Design or production is the intended source for the change.

When Open Design MCP is unavailable, report that as a verification limitation and
use local project mirrors only as a fallback. Never silently present a fallback
inventory as a live-project verification.

Completion criterion: both Open Design project inventories and the production
source closure are recorded with paths, repository sync status, and unresolved access
limitations.

Before creating tickets, resolve every referenced execution skill by checking the
available skill registry. If a required execution skill is absent, create a
`skill-prerequisite` ticket or report the blocker; do not publish tickets that point
to a nonexistent skill.

### 3. Build the Coverage Ledgers

Create four ledgers before proposing tickets.

**Component ledger**

| Field | Required content |
|---|---|
| id | Stable component identifier |
| name | Component or pattern name |
| level | foundation, core, form, composite, feedback, layout, overlay, chart, domain, pattern |
| production source | Code paths, usage count, API/schema, or approved requirement |
| design-system status | present, partial, missing, needs-variant, needs-review |
| required variants | themes, sizes, roles, responsive and semantic variants |
| required states | loading, empty, error, disabled, selected, permission, read-only, success |
| dependents | Archetypes and route families that require it |

**Archetype ledger**

Record each canonical route, page family, primary task, page structure, production
source, required components, variants, and states. Companion frames must not become
new production routes.

**Feature and behavior ledger**

Record every user-visible action, metric, permission boundary, navigation path,
notification trigger, API behavior, mutation, and legal or domain claim. Each row
needs a production source or an approved product specification.

**Dependency ledger**

Represent edges such as:

```text
semantic tokens -> Badge -> CaseStatusBadge -> collection archetype -> route sweep
AppShell + navigation -> every authenticated archetype
DataTable + FilterBar + Pagination -> list archetype -> collection route family
```

Completion criterion: every proposed ticket can point to ledger rows, and every
ledger row is either covered, explicitly not applicable, or blocked.

### 4. Decide What Comes First

Use this sequencing rule:

1. Foundations and semantic tokens
2. AppShell, navigation, and global interaction rules
3. High-frequency shared components
4. Feedback, accessibility, responsive, and permission variants
5. Domain components required by multiple route families
6. Archetype reference pages
7. Production implementation of approved components and archetypes
8. Route-family migration and propagation

Do not wait for every conceivable component. Select the smallest component set that
unblocks the next archetype and record the remaining components as later work.

Use reference pages as integration tests for the system. When a page exposes a
missing component variant, create a component ticket before continuing the page
ticket.

Completion criterion: the dependency graph has no circular blocking edge and each
phase has a clear entry and exit condition.

### 5. Produce the Canonical Spec

Use the Matt Pocock `to-spec` workflow once scope and sequencing decisions are
settled. The spec must include:

- problem and desired outcome
- production scope and excluded scope
- both Open Design project responsibilities
- component and archetype ledgers
- dependency graph and sequencing
- feature and behavior boundary
- required themes, viewports, languages, and states
- approval checkpoints
- implementation and propagation boundaries
- explicit non-goals and unresolved questions

Do not create implementation tickets until the scope and sequencing decisions are
settled. Legal and regulatory questions go to the legal register rather than being
settled in the design spec.

Completion criterion: one canonical spec exists, is published, or is explicitly
blocked on an owner decision; no unresolved scope decision is hidden inside a ticket.

### 6. Create Tracer-Bullet Tickets

Use the Matt Pocock `to-tickets` workflow after the canonical spec is settled. Create
small tickets that can run in independent sessions where dependencies allow.

Recommended ticket types:

- `design-system-foundation`: tokens, typography, spacing, themes, motion, icons
- `component-authoring`: one component or one tightly coupled component family in
  Behigamlak Design System
- `component-production-sync`: promote an approved component into production
- `archetype-authoring`: one canonical route and its companion frames in Behigamlak
  Prototype
- `archetype-production-implementation`: implement an approved reference route
- `archetype-propagation`: apply an approved archetype to mapped production routes
- `verification`: metadata, accessibility, responsive, behavior, and visual checks
- `design-system-sync`: reconcile Open Design, repository contract, tokens, and
  production components; update the manifest and record the source decision
- `design-token-source`: establish or reconcile version-controlled primitive,
  semantic, and component token data and its generated production outputs

Every ticket must contain:

- the exact Open Design project
- the execution skill to use
- production source paths
- prerequisite ticket IDs
- ledger row IDs covered
- behavior and feature boundaries
- required variants and states
- acceptance criteria
- verification commands or checks
- explicit non-goals

Every component or archetype ticket must also name its design-system sync status and
the manifest entries it is allowed to change. A ticket that changes a visual token,
component contract, or reusable pattern must update the repository contract and
manifest in the same unit of work, or explicitly create a blocking sync ticket.

Token changes must identify the canonical token input, generated outputs, validation
step, and owner of the sync. Component changes must identify matching Open Design
component names, code component names, variants, and states; visual documentation
alone does not satisfy implementation coverage.

Use these execution-skill references:

- Components: `/open-design-component-authoring` when installed; otherwise create a
  `skill-prerequisite` ticket before creating component-authoring tickets
- Archetypes: `/open-design-archetype-authoring`
- Production UI: `/open-design-implementation`
- Approved redesign propagation: `/open-design-archetype-propagation`
- Final validation: `/finish-ticket` or the repository's verification workflow

The orchestration skill may recommend or prepare these tickets, but the tickets are
the handoff boundary. Do not start the long-running execution work here.

Completion criterion: every ticket is independently understandable, dependency
ordered, linked to an installed execution skill, and published through the configured
issue tracker or explicitly reported as blocked.

### 7. Define the Approval Gates

Use these gates:

- **System gate**: visual intent is approved in the design-system project, and the
  repository token source, runtime components, and manifest are synchronized.
- **Archetype gate**: the reference page uses approved components and covers its
  production feature ledger.
- **Implementation gate**: production behavior remains intact and uses the approved
  tokens/components.
- **Propagation gate**: mapped routes are visually and behaviorally verified before
  claiming completion.

The owner may approve a phase while later phases remain open. Never treat a design
system as permanently finished; record additions discovered by archetype work as
new component tickets.

## Output Format

Return a concise orchestration report containing:

1. Scope and recommendation
2. Live Open Design inventory
3. Production inventory
4. Component, archetype, feature, and dependency gaps
5. Recommended phase order
6. Canonical spec status and `to-spec` handoff
7. Ticket set and blocking edges for `to-tickets`
8. Approval gates
9. Unresolved questions and verification limitations

The output is successful only when it gives the next agent a ticket-sized unit of
work rather than a request to "design the whole application."
