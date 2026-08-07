---
name: open-design-archetype-authoring
description: Create an Open Design archetype baseline from a production route, populate it with representative static data, add companion frames, and hand it to the user for visual redesign.
argument-hint: "[production route]"
disable-model-invocation: true
---

# Open Design Archetype Authoring

Turn one existing production route into a complete Open Design archetype package.
The result is a design-ready baseline, not a production implementation and not a
final visual decision.

## Inputs

The user supplies a production route, for example `/dashboard/cases`. Resolve:

- The route's page source and nearest layout boundaries
- Its package in the living archetype registry
- The Open Design project and design-system source
- Imported components, tokens, fonts, assets, and current themes
- Representative data, actions, permissions, and visible states

Use the repository's registry and domain glossary. If the route is not classified,
classify it using the distinct-task-and-structure rule before authoring. If it is a
variant or companion extension, preserve that relationship in the artifact and
registry rather than silently creating a new top-level package.

## Source Retrieval

When an Open Design project, active file, or design system is involved, retrieve
source through Open Design MCP before reading local mirrors. Use explicit project
and path arguments when known. Prefer the complete artifact bundle for an existing
archetype and inspect its linked design-system resource.

Resolve the full source closure before writing:

- Imported components and variants
- Global and component CSS
- Every CSS custom property in both themes
- Fonts, weights, images, icons, and SVG behavior
- Breakpoints, container widths, and responsive branches
- Existing archetype package conventions

If no suitable Open Design project is active and no project is supplied, ask for
the project once. Do not invent a project identity.

## Baseline Workflow

1. **Inventory the route.** Read the production page, layouts, shared components,
   API calls, permission gates, localization, and representative states. Record the
   visible hierarchy and primary task.
2. **Choose the reference.** Confirm the route is a valid Reference Route for its
   package. Use the existing route as the baseline; do not create a synthetic
   production route.
3. **Prepare static data.** Replace live queries and mutations with deterministic,
   realistic fixture data that preserves the production content shape, bilingual
   density, status vocabulary, row/card counts, and important edge cases. Keep
   values obviously non-production and never copy secrets or personal data.
4. **Create or update the artifact.** In the selected Open Design project, create
   the archetype entry using the route's current visible structure, approved local
   tokens, and static data. Reuse existing Open Design primitives and styles where
   available. Keep the artifact self-contained enough to render in Open Design.
5. **Add companion frames.** Add frames in the same package for the relevant
   coverage matrix: desktop, mobile, light, dark, loading, empty, error,
   permission-gated, read-only, success, focus/selected, and localized content
   density. Include only states that the route actually supports or needs.
6. **Record the handoff.** Update the archetype registry with the artifact path,
   canonical route, mapped routes, companion frames, static-data notes, and status
   `baseline-ready-for-redesign`.
7. **Verify the baseline.** Confirm the artifact renders, every referenced token
   resolves, static data is deterministic, companion frames are labeled, and the
   baseline still represents the production route before redesign.

## Open Design Operations

Use the Open Design MCP for project/file operations:

- `get_active_context` for the current project/file pointer
- `get_project`, `list_files`, `get_file`, and `get_artifact` for source discovery
- `create_artifact` for a new archetype entry
- `write_file` for subsequent iteration of a created artifact

If the Open Design artifact format requires a project-specific structure, inspect a
neighboring archetype first and follow that project's conventions. Do not vendor
the full project into the production repository.

## Handoff Boundary

Stop after the baseline package is created and verified. Tell the user:

- Which production route was used
- Which Open Design project and artifact were created or updated
- Which static fixtures were used
- Which companion frames were added
- Which states were not applicable
- How to open and redesign the artifact
- That `/open-design-archetype-propagation` is the next command after approval

Do not propagate the baseline back into production. The user must redesign and
approve it first.

## Completion Criteria

- The canonical production route is recorded in the registry.
- The Open Design baseline exists and renders in its project.
- Static data is deterministic, realistic, bilingual-aware where applicable, and contains no secrets or personal data.
- The baseline preserves the production page hierarchy and visible interaction contract.
- Required companion frames are present and labeled.
- Light/dark tokens, fonts, assets, and responsive rules are resolved.
- Registry status and artifact path are updated.
- The user receives a clear redesign handoff and no production files were changed.

Use `references/static-fixture-rules.md` for fixture construction and
`references/authoring-handoff.md` for the final report shape.
