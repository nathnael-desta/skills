# Archetype Registry

**Status:** Proposed
**Updated:** YYYY-MM-DD

This registry maps production route families to Open Design archetype packages.

## Model

- **Archetype package:** one canonical existing route plus companion frames.
- **Variant:** role, domain, scope, or state adaptation preserving the page hierarchy.
- **Companion extension:** related domain frames that do not justify a new package.
- **Specialized archetype:** repeated workflow with a materially different task and hierarchy.

## Inventory

- Tracked page routes: `<count>`
- Dynamic routes: `<count>`
- Existing shells: `<list>`
- Open Design project: `<project id or path>`

## Packages

| # | Package | Class | Canonical route | Open Design artifact | Mapped routes/families | Status |
|---:|---|---|---|---|---|---|
| 1 | `<name>` | Core / specialized | `<route>` | `<artifact>` | `<routes>` | Proposed |

## Companion Extensions And Variants

| Area | Classification | Parent package | Reference frames | Notes |
|---|---|---|---|---|
| `<area>` | Variant / extension | `<package>` | `<frames>` | `<scope>` |

## Coverage Matrix

| Package | Desktop | Mobile | Light | Dark | Loading | Empty | Error | Permission | Read-only | Success | Localization |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `<package>` | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

## Build Order

1. `<package>`
2. `<package>`

## Approval Gate

- [ ] Canonical page and companion frames approved
- [ ] Route mapping recorded
- [ ] Shared patterns and tokens synchronized
- [ ] Production behavior and permissions preserved
- [ ] Relevant checks pass
- [ ] Source and production verified at matching viewport, theme, and state
- [ ] Intentional deviations recorded
