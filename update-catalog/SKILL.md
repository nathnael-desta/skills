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

Whenever a user asks what has changed, what features were merged, or asks for release notes, do not output a generic unformatted bullet list or raw git logs. Instead, use this structured catalog format with PR/commit references, bold sub-topics, and explicit `What it does:` breakdowns with square bullet points.

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

## Source Gathering Process

1. **Identify the Range**:
   - Determine the start point (last checked date, previous release tag, base branch, or commit SHA) and the end point (current release, latest nightly, or HEAD).
   - If git history is available locally or via CLI (`gh`, `git log`), query the commits and merged PRs across that specific window.

2. **Extract High-Signal Changes**:
   - Filter for user-facing features (`feat`), notable enhancements, significant performance wins (`perf`), major architectural milestones (`chore(release)`, `refactor`), and critical bug fixes.
   - Ignore trivial dependency bumps, typo fixes, or internal housekeeping unless they impact user workflows or build performance.

3. **Synthesize & Group**:
   - Group related commits/PRs into cohesive themes or numbered sections (e.g., Major Milestone Releases, Core Features, UI/UX Enhancements, Performance & Reliability, Tooling & Infrastructure).

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
🚀 <Project/Product Name> Update Catalog (<Version/Commit Range>)
```

### 3. Numbered Feature / Milestone Sections
Format each major feature or group as a numbered section:

```markdown
### <N>. <Feature Group or Milestone Title>

* <Sub-Topic / Functional Area>:

  * PR: 🐙#<PR_NUMBER> — `<commit_type>(<scope>): <short description>`
  * What it does:
    ▪ <Core user-facing behavior, problem solved, or what changed in the product experience.>
    ▪ <Technical detail, architecture, safeguards, or under-the-hood implementation highlight.>
```

If multiple PRs contribute to the same section, nest them under their respective `* <Sub-Topic>:` blocks.

### Rules & Formatting Standards:
- **Header Emoji**: Always start the main catalog title with `🚀`.
- **PR / Commit Link**: Prefix GitHub PRs with `🐙#<PR_NUMBER>` (linked if URL available) followed by an em-dash `—` and the exact commit header in inline code format: `` `feat(scope): title` ``. For non-GitHub repos or raw git commits, format as `* Commit: 🐙`<commit_hash>` — `...``.
- **What it does block**: Use `* What it does:` followed by indented square black bullets (`▪`) for the explanation items.
- **Two-part explanation**:
  1. First `▪` bullet: User-facing benefit, workflow change, or UI capability.
  2. Second `▪` bullet: Architectural upgrade, technical performance win, or edge-case safeguard.

---

## Example Reference

```markdown
Here is the feature breakdown and changelog of everything merged into `main` since `v0.1.1-nightly.20261018.3285` through `v0.1.2-nightly.20261021.3457` (October 18 – October 21, 2026):

🚀 Project Update Catalog (Nightlies `.3285` → `.3457` & v0.1.1 Release)

### 1. Milestone Release: Version 0.1.1 ( `v0.1.1` )

* Official Stable Rollout:

  * PR: 🐙#22608 — `chore(release): prepare v0.1.1`
  * What it does:
    ▪ Official production release consolidating over 200 stability fixes and performance optimizations across web, mobile, and server.
    ▪ Introduces verified React Compiler compatibility across all views and solidifies Database V2 migration paths.

### 2. Real-Time Command & Terminal Streaming

* Live Output Execution:

  * PR: 🐙#15094 — `fix: command output streams live while it runs`
  * What it does:
    ▪ Long-running commands, tests, and builds run by the agent now stream standard output and standard error live in the thread timeline.
    ▪ Replaces the previous behavior where terminal output blocks were buffered until the process exited, eliminating blank loading periods during builds and test suites.
```
