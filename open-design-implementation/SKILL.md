---
name: open-design-implementation
description: Implement or refine production UI from an Open Design artifact with exact source parity. Use when a request mentions an Open Design project, artifact, archetype, design, active file, or asks to copy or match a design in another codebase.
---

# Open Design implementation

Treat the Open Design artifact as executable design source, not a screenshot to
approximate. Preserve production data and behavior while porting its structure,
tokens, typography, components, and responsive rules exactly.

## Retrieve source first

1. When the user refers to the open design or active file, query active context
   through the Open Design MCP before reading local mirrors or opening a browser.
2. Prefer one artifact-bundle retrieval. It should include the entry file and
   its referenced CSS, JavaScript or JSX, assets, and token files.
3. If the artifact has a linked design system, read its design-system resource.
4. Use targeted file search or single-file reads only to close gaps left by the
   bundle. If active context has expired, use a known project and path; otherwise
   ask the user to reopen the design.
5. Fall back to a CLI or local mirror only after the MCP request actually fails,
   and state that failure.

Do not start implementation before tracing the full dependency closure:

- Imported components and their variants
- Global and component CSS
- Fonts and font weights
- Images, icons, and SVG behavior
- Every referenced CSS custom property
- Light and dark definitions for every token
- Breakpoints, container widths, and responsive branches

An unresolved custom property is a blocking source-parity defect. Do not assume
a similarly named production token has the same value.

## Map source to production

Before editing, make a compact mapping from source elements to production
components, tokens, routes, and data. Label each difference as one of:

- Exact port: use the source structure and values.
- Production adaptation: preserve source styling while replacing demo data,
  routes, permissions, localization, accessibility, or real interactions.
- Intentional deviation: retain only when required by product behavior or
  explicitly approved by the user.
- Missing dependency: resolve before claiming parity.

Reuse established production components when they can express the source
exactly. If they cannot, make the smallest shared token or component correction
instead of layering page-specific overrides.

Do not vendor the full Open Design project. Port the requested artifact and
promote approved shared values into the production token and component sources
of truth.

## Implement in dependency order

1. Add or correct primitive and semantic tokens, including both themes.
2. Correct shared shell and component behavior.
3. Port page structure and responsive layout.
4. Connect production APIs, permissions, routing, localization, and actions.
5. Preserve accessibility semantics and keyboard behavior.
6. Format and run the cheapest static checks that catch the changed code.

Batch implementation before visual verification. Do not use compilation as
evidence of visual parity; CSS custom properties can remain unresolved while
the build passes.

## Verify exact parity

Use Browser Control only after source retrieval and implementation. Compare the
source and production at the same viewport, state, and theme. Verify both light
and dark mode and at least one narrow viewport when the artifact is responsive.

Check computed values, not class names:

- Colors, opacity, gradients, shadows, and borders
- Font family, size, weight, line height, and letter spacing
- Widths, heights, gaps, padding, alignment, and overflow
- Border radius and stroke width
- SVG fill, stroke, and inherited color
- Breakpoint behavior and content wrapping
- Hover, focus, selected, loading, empty, and disabled states when present

Use a focused screenshot only when rendered appearance cannot be established
economically from DOM geometry and computed styles. Explain every visible
difference. A browser fallback value, transparent custom property, unresolved
token, or unexplained screenshot difference means parity has not been reached.

Use [the parity checklist](references/parity-checklist.md) before reporting
completion.

## Report completion

State which source artifact and design-system resources were used, what was
adapted for production behavior, which checks ran, and any intentional
deviations. Never call the result exact or pixel-perfect while a dependency,
theme, viewport, interaction state, or visible difference remains unverified.
