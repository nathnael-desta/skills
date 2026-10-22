---
name: codex-code-review
description: Review local repository changes with OpenAI Codex CLI. Use when the user asks for a local code review, branch diff review, staged/uncommitted review, security review, performance review, or a pre-merge sanity pass. Prefer Codex's native `codex review` command, and fall back to static diff review only when Codex cannot execute shell commands in its sandbox.
---

# Codex Code Review

Use this skill to run a focused local code review with Codex CLI and turn findings into actionable engineering work.

## Current CLI Assumptions

This skill is written for Codex CLI `0.130.x`.

Prefer these commands:

```bash
codex review --uncommitted
codex review --base main
codex review --commit <sha>
codex exec --sandbox read-only --cd /path/to/repo "Review this provided diff..."
```

Do not use these older patterns:

```bash
codex --full-auto exec "..."
codex exec --full-auto "..."
```

`--full-auto` is deprecated in Codex CLI `0.130.x`. Use `--sandbox read-only` for review-only work and `--sandbox workspace-write` only when you want Codex to edit files.

## Prerequisites

Check the CLI and auth before a review:

```bash
codex --version
codex login status
```

If `codex login status` is not available in your installed CLI, run `codex` once interactively and complete sign-in.

## Review Scope

Use native review when possible:

```bash
# Review staged, unstaged, and untracked local changes
codex review --uncommitted

# Review current branch against a base branch
codex review --base main

# Review a single commit
codex review --commit <sha>
```

Use `codex exec` for custom review prompts:

```bash
codex exec --sandbox read-only --cd /path/to/repo "Review changes between main and current branch. Focus on breaking changes, API compatibility, test coverage gaps, and documentation needs."
```

## Helper Script

Use the bundled script when you want a repeatable command:

```bash
~/.claude/skills/codex-code-review/scripts/review.sh --branch main
~/.claude/skills/codex-code-review/scripts/review.sh --uncommitted
~/.claude/skills/codex-code-review/scripts/review.sh --files src/api/v1/cases.py,src/schemas/case.py
```

For machines where Codex cannot run shell commands inside its sandbox, use static diff mode:

```bash
~/.claude/skills/codex-code-review/scripts/review.sh --branch main --static
```

Static mode generates the git diff outside Codex and pipes it in. If the diff is too large, narrow the scope:

```bash
~/.claude/skills/codex-code-review/scripts/review.sh --branch main --static --files src/api/v1/cases.py,src/schemas/case.py
```

## Sandbox Failure Fallback

If Codex prints errors like:

```text
Shell snapshot validation failed
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

then Codex may be unable to inspect files by running shell commands. Switch to static diff review:

```bash
git diff --stat main...HEAD
git diff --no-ext-diff --unified=80 main...HEAD -- <file-or-dir> \
  | codex exec --sandbox read-only --cd /path/to/repo \
    "Review the git diff provided on stdin. Focus on concrete findings with file references."
```

If the diff exceeds the model input limit, review smaller slices by file or directory. Do not paste multi-megabyte diffs into Codex.

## Prompt Guidance

For ordinary branch review:

```text
Review changes between main and the current branch. Focus on concrete findings only:
1. Breaking changes
2. API compatibility
3. Test coverage gaps
4. Documentation needs

Report findings first, ordered by severity. Include file and line references when available. If there are no findings, say that directly.
```

For security review:

```text
Review the selected diff for security issues. Focus on auth, authorization, input validation, injection risks, sensitive data exposure, CORS, rate limiting, and unsafe file or command handling. Report only concrete risks.
```

For performance review:

```text
Review the selected diff for performance issues. Focus on N+1 queries, blocking I/O, unnecessary re-render loops, expensive algorithms, excessive payloads, missing indexes, and resource leaks. Report only concrete risks.
```

## Web Verification Rule

If a finding depends on current external facts, verify it before claiming it.

Examples:

- latest package versions
- security advisories or CVEs
- current framework deprecations
- current best practices that may have changed recently

Do not guess version status from memory.

## Review Output Standard

Good review output starts with findings:

```text
Findings
- High: file/path.ts:42 - Concrete issue and why it can fail.
- Medium: file/path.py:88 - Coverage gap or compatibility risk.

Open Questions
- Any assumptions that affect the review.

Checks
- What command or scope was reviewed.
```

If there are no findings:

```text
No actionable findings found in the reviewed scope.

Residual risk: <what was not checked, such as browser-only behavior or oversized diff sections>.
```

## Limits

- Native `codex review` is best for normal local repo reviews.
- Static diff review is best when Codex sandbox command execution fails.
- Static diff review is limited by prompt size, so split large branches by file or subsystem.
- For GitHub PR review comments, use the GitHub PR comment workflow/skill instead of this local diff skill.

## Reference Files

- [Codex CLI Reference](./references/codex_cli.md)
- [Review Prompts Library](./references/review_prompts.md)
- [Helper Script](./scripts/review.sh)
