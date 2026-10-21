---
name: update-catalog
description: Generate structured feature breakdowns, release changelogs, and "what's new" update catalogs for any project, repository, or tool using the standardized Update Catalog format. Use whenever the user asks "what's new", "any new features", "what changed since X", "changelog", "release notes", "summarize updates", or asks for a breakdown of recent commits/PRs.
triggers:
  - "what's new"
  - "any new features"
  - "what changed since"
  - "changelog"
  - "feature breakdown"
  - "release catalog"
  - "update catalog"
  - "summarize updates"
  - "what was merged"
  - "new features since"
---

# Update Catalog

Generate structured, high-signal feature breakdowns, release changelogs, and "what's new" catalogs for any software project, library, CLI, or product.

Whenever a user asks what has changed, what features were merged, or asks for release notes, do not output a generic unformatted bullet list or raw git logs. Instead, use this structured catalog format with embedded PR/commit links, bold sub-topics, prioritized user-facing capabilities, and explicit `What it does:` breakdowns with square bullet points.

---

## When To Use

Use this skill when the user asks:
- "What's new since the last time we checked?"
- "Any new features since version X?"
- "Give me a feature breakdown of recent changes"
- "Summarize the changelog / release notes"
- "What was merged into main this week?"
- Any general request to summarize product/repo additions across a timeframe or commit range.

Applicable to **any** codebase, repository, or product (not limited to any single tool).

---

## Core Principles

1. **Prioritize User-Facing Features**:
   - Give top prominence to changes the user will directly see, touch, or experience in their daily workflow: UI updates, composer interactions, keyboard shortcuts, new settings, visual badges, mobile screens, and CLI additions.
   - Group internal refactors or build tooling toward the end or omit them if user-facing changes dominate the release.

2. **Always Embed Real Clickable Markdown Links**:
   - Every PR or commit mention MUST be an active clickable markdown link, e.g. `[🐙#22732](https://github.com/org/repo/pull/22732)`. Never output unlinked plain text like `#22732` or `🐙#22732`.

3. **Exhaustive Legwork**:
   - Don't settle for only 3–5 items if 15–20 user-facing features or polish fixes were merged. Gather the full picture across web, desktop, mobile, and CLI.

---

## Standard Output Format Specification

Every catalog must strictly adhere to the following layout:

### 1. Scope Intro Header
State the branch, start commit/version, end commit/version, and readable date range:
```markdown
Here is the feature breakdown and changelog of everything merged into `main` since `<start-tag-or-commit>` through `<end-tag-or-commit>` (<Start Month Day> – <End Month Day, Year>):
```

### 2. Main Title Banner
```markdown
# 🚀 <Project/Product Name> Update Catalog (<Version/Commit Range>)
```

### 3. Numbered User-Facing Feature Sections
Format each major user-visible feature or capability as a numbered section:

```markdown
### <N>. <Feature or Capability Title>

* <Sub-Topic / Functional Area>:

  * PR: [🐙#<PR_NUMBER>](https://github.com/<owner>/<repo>/pull/<PR_NUMBER>) — `<commit_type>(<scope>): <short description>`
  * What it does:
    ▪ <Core user-facing behavior, problem solved, or what changed in the UI / product experience.>
    ▪ <Technical detail, architecture, safeguards, or under-the-hood implementation highlight.>
```

If multiple related PRs contribute to the same area, nest them under their respective `* <Sub-Topic>:` blocks.

### Rules & Formatting Standards:
- **Header Emoji**: Always start the main catalog title with `# 🚀`.
- **Embedded PR / Commit Links**: PR numbers MUST be formatted as `[🐙#<PR_NUMBER>](<FULL_PR_URL>)` followed by an em-dash `—` and the exact commit header in inline code format: `` `feat(scope): title` ``. For commit SHAs, format as `[🐙`<short_sha>`](<FULL_COMMIT_URL>)`.
- **What it does block**: Use `* What it does:` followed by indented square black bullets (`▪`) for the explanation items.
- **Two-part explanation**:
  1. First `▪` bullet: User-facing benefit, workflow change, keyboard shortcut, or UI visual capability.
  2. Second `▪` bullet: Technical mechanics, error handling, performance win, or edge-case behavior.
