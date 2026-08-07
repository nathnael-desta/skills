# Archetype Coverage Matrix

Use a representative matrix. Do not multiply every role, domain, and state into
separate design pages.

## Dimensions

| Dimension | Required coverage |
|---|---|
| Viewport | Desktop and narrow/mobile when responsive |
| Theme | Light and dark |
| Content | Primary language and localized density when applicable |
| Data | Populated, empty, loading, and error |
| Access | Full access, read-only, and permission-gated |
| Interaction | Focus, hover/selected, disabled, validation, destructive confirmation |
| Workflow | Primary success, retry/failure, and cancellation where relevant |

## Matrix

| Package | Canonical populated | Mobile | Dark | Empty | Loading | Error | Restricted | Read-only | Success/retry | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `<package>` | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | `<notes>` |

## Rules

- A companion frame is justified by a different task, hierarchy, or state behavior, not merely different copy.
- A role variant may change modules and data scope while preserving the page's visual zones.
- State frames should expose the component contract needed by production; they do not automatically become new archetypes.
- If a family requires a fundamentally different workbench, promote it to a specialized archetype and explain the evidence in the registry.
