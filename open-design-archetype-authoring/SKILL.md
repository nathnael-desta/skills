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

The artifact is production-derived, not a feature ideation surface. Build a feature
ledger before authoring with one row for every user-visible feature, action, metric,
permission boundary, and state that the reference route is expected to show. Each
row must identify its production source (route, component, API, permission, or
approved product specification), the behavior boundary, and the companion frames
where it appears.

- **Implemented**: present in production and eligible for the baseline.
- **Requested**: explicitly approved for this package but not yet implemented;
  stop and ask before showing it, rather than inventing behavior.
- **Not applicable**: intentionally absent for this route or variant, with a reason
  recorded in the handoff.

Never add a feature, action, metric, workflow, legal claim, or domain concept just
to make a frame look complete. Never omit an implemented or explicitly approved
user-facing feature from the frame matrix without recording the reason. Fixture data
may simulate existing production shapes and states, but it must not create new
product capabilities.

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
the project once. Do not invent a project identity or silently create a replacement
project.

## Execution Gate

This is an Open Design generation workflow. The repository agent prepares the
brief; Open Design creates the visual artifact.

Before authoring, confirm that all of these are available:

- A suitable existing Open Design project
- A usable Open Design generation path: Open Design Cloud, Local Codex, or Secure BYOK
- A generation-capable agent/runtime for the selected path

If any prerequisite is missing, stop and tell the user exactly which prerequisite
is blocked and what they need to do. The skill is fail-closed: it does not switch
to manual artifact authoring, local HTML/CSS, a local mirror, or browser automation
as a substitute for Open Design generation.

`create_artifact` and `write_file` are not fallback authoring tools in this skill.
Use them only when the user has explicitly supplied complete artifact content and
asked for file persistence, not when generation is unavailable.

## Baseline Workflow

1. **Inventory the route.** Read the production page, layouts, shared components,
   API calls, permission gates, localization, and representative states. Record the
   visible hierarchy, primary task, and feature ledger. Reconcile the ledger against
   the originating issue/spec or approved user requirements. Resolve every row as
   implemented, requested-and-blocked, or not applicable before generation.
2. **Choose the reference.** Confirm the route is a valid Reference Route for its
   package. Use the existing route as the baseline; do not create a synthetic
   production route.
3. **Create the authoring handoff manifest.** Populate
     `references/authoring-brief-template.json` with the route inventory, source
     closure, feature ledger, behavior contract, deterministic fixtures, variant
     matrix, state coverage, frame matrix, and intentional deviations. This is the
     canonical handoff to Open Design, not a planning note. Every feature row must
     have a source and every frame must name the feature rows it demonstrates.
     Keep values obviously non-production and never copy secrets or personal data.
     Validate that there are no unresolved requested features before continuing.
4. **Prepare the generation brief.** Serialize the completed handoff manifest into
     the prompt passed to Open Design. The prompt must identify the requested artifact
     path, canonical route, design-system source, static fixture rules, production
     behavior boundary, feature-to-frame matrix, and intentional deviations. It must
     explicitly say which production feature each frame demonstrates and which controls
     are authoring-only. If a requested feature has no production source or approved
     specification, stop before commissioning and ask for clarification.
5. **Commission Open Design.** Use the selected Open Design project and generation
     path to create or refine the artifact. The prompt must identify the requested
     artifact path, canonical route, design-system source, static fixture rules,
     and companion-frame coverage. Reuse existing Open Design primitives and styles
     where available.
6. **Wait for the generation run.** Poll the same generation run until it succeeds
     or reaches a terminal failure. If it fails, stop and report the failure,
     recharge/login requirement, or unavailable runtime. Never substitute manual
     HTML/CSS or a browser-built approximation.
7. **Confirm generated companion frames.** The generation brief must request frames
    in the same package for the relevant coverage matrix: desktop, mobile, light,
    dark, loading, empty, error, permission-gated, read-only, success,
    focus/selected, and localized content density. Confirm that Open Design produced
    the applicable frames; do not add them manually. Check every feature-ledger row:
    implemented and approved features must have a mapped frame or an explicit
    not-applicable reason, and no frame may contain an unmapped feature.
8. **Record the handoff.** Update the archetype registry with the artifact path,
   canonical route, mapped routes, companion frames, static-data notes, and status
   `baseline-ready-for-redesign`.
9. **Verify the generation output.** Confirm through Open Design metadata and source
    retrieval that the run produced the requested artifact, companion frames are
    labeled, the artifact metadata matches the handoff manifest, and the registry
    path matches. The Open Design preview and the human designer are the visual
    verification boundary for this authoring skill.

## Open Design Operations

Use the Open Design MCP for project discovery and generation:

- `get_active_context` for the current project/file pointer
- `get_project`, `list_files`, `get_file`, and `get_artifact` for source discovery
- `list_agents` and `list_byok_profiles` when selecting a generation path
- `start_run` to commission Open Design generation
- `get_run` to poll the commissioned run to a terminal state

The handoff manifest is the required bridge between repository evidence and Open
Design generation. Read the template at
`references/authoring-brief-template.json`, populate it before `start_run`, and
include the complete serialized manifest in the prompt. Do not rely on Open Design
to infer production features, routes, permissions, or requested scope from a short
natural-language request.

If the Open Design artifact format requires a project-specific structure, include
that convention in the generation brief and let Open Design produce the artifact.
Do not vendor the full Open Design project into the production repository.

Browser automation is not part of the baseline authoring loop. Do not open a
browser to inspect or validate the preview unless the user explicitly requests
automated browser verification. The user reviews the Open Design preview manually.

## Handoff Boundary

Stop after the Open Design generation run succeeds and the package metadata is
recorded. Tell the user:

- Which production route was used
- Which Open Design project and artifact were created or updated
- Which static fixtures were used
- Which companion frames were added
- Which states were not applicable
- How to open and redesign the artifact
- That `/open-design-archetype-propagation` is the next command after approval

If generation is unavailable or fails, stop at that point and tell the user the
exact blocker using this shape:

- `Blocked`: Open Design generation is unavailable or failed.
- `Missing`: the project, runtime, login, quota, or generation error.
- `Next action`: what the user must fix or choose.
- `Artifact`: none created or changed by this skill.

Do not report a partial manually authored artifact as completion.

Do not propagate the baseline back into production. The user must redesign and
approve it first.

## Completion Criteria

- The canonical production route is recorded in the registry.
- A completed authoring handoff manifest exists and was included verbatim in the
  Open Design generation prompt.
- The Open Design generation run succeeded and its baseline exists in the project.
- Static data is deterministic, realistic, bilingual-aware where applicable, and contains no secrets or personal data.
- The baseline preserves the production page hierarchy and visible interaction contract.
- The feature ledger is complete: every shown feature has a production or approved
  specification source, and every implemented or explicitly approved user-facing
  feature is represented or documented as not applicable.
- Required companion frames are present and labeled.
- Artifact metadata and companion frames reconcile with the handoff manifest.
- Open Design reports the required light/dark tokens, fonts, assets, and responsive
  rules in the generated artifact.
- Registry status and artifact path are updated.
- The user receives a clear redesign handoff, no production files were changed, and
  no browser automation was needed for baseline completion.

Use `references/static-fixture-rules.md` for fixture construction and
`references/authoring-handoff.md` for the final report shape.
