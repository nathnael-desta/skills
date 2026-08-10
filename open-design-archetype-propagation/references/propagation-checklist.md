# Propagation Checklist

## Source

- [ ] User explicitly approved the artifact
- [ ] Explicit Open Design project and artifact retrieved through MCP
- [ ] Linked design-system resource read
- [ ] Components, CSS, fonts, assets, tokens, themes, and responsive rules traced

## Mapping

- [ ] Reference Route confirmed
- [ ] Mapped production routes identified
- [ ] Exact ports, production adaptations, and intentional deviations labeled
- [ ] APIs, permissions, routing, legal content, localization, and behavior preserved

## Implementation

- [ ] Shared tokens corrected first
- [ ] Every visual value resolves through a primitive or semantic token
- [ ] Shared Shell and Patterns corrected before page-local markup
- [ ] Repeated or reusable structure extracted into a shared component or Pattern
- [ ] Shared component APIs are data/domain agnostic and preserve production behavior at the route boundary
- [ ] Canonical route implemented
- [ ] Representative variants implemented
- [ ] Loading, empty, error, permission, read-only, and success states covered
- [ ] Registry status and deviations updated

## Upward Synchronization

- [ ] New or corrected tokens, components, and Patterns classified as upstream candidates
- [ ] Each candidate passes the reuse/system-level, state, token, accessibility, and localization gate
- [ ] Upstream contribution created or updated in the Open Design design-system project
- [ ] Every candidate has a manifest/registry status: proposed, accepted, implemented, or rejected
- [ ] Accepted candidates name their source artifact and production consumer routes
- [ ] Unapproved candidates are reported as blockers or documented intentional deviations

## Verification

- [ ] Formatter, typecheck, lint, focused tests, and build pass
- [ ] Same viewport compared in Open Design and production
- [ ] Light and dark themes compared
- [ ] Narrow/mobile viewport compared when responsive
- [ ] Computed colors, typography, spacing, dimensions, borders, SVG, and overflow checked
- [ ] Focus, hover, selected, disabled, and primary interactions checked
- [ ] Bilingual density checked when applicable
- [ ] Every visible difference fixed or explained
- [ ] Final propagation report states what propagated upward, what propagated downward, and what remains pending
