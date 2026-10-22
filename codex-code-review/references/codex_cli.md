# Codex CLI Reference

Reference for Codex CLI usage relevant to local code review.

## Version Checked

This reference was updated against Codex CLI `0.130.0`.

```bash
codex --version
```

## Review Command

Use `codex review` for normal code reviews.

```bash
codex review --uncommitted
codex review --base main
codex review --commit <sha>
codex review --base main --title "Branch review"
```

Options:

| Option | Purpose |
| --- | --- |
| `--uncommitted` | Review staged, unstaged, and untracked changes |
| `--base <branch>` | Review current branch against a base branch |
| `--commit <sha>` | Review one commit |
| `--title <title>` | Display a review title |
| `[PROMPT]` | Optional custom instructions, when supported by the selected flags |

Note: in Codex CLI `0.130.0`, `--uncommitted` rejects a custom prompt in some invocation forms. If that happens, run `codex review --uncommitted` without the prompt or use static diff mode with `codex exec`.

## Exec Command

Use `codex exec` when you need custom instructions or want to feed a static diff on stdin.

```bash
codex exec --sandbox read-only --cd /path/to/repo "Review this repository."
codex exec --sandbox workspace-write --cd /path/to/repo "Fix the issue found by review."
git diff main...HEAD -- src/api | codex exec --sandbox read-only --cd /path/to/repo "Review the diff provided on stdin."
```

Useful options:

| Option | Purpose |
| --- | --- |
| `--sandbox read-only` | Review-only mode |
| `--sandbox workspace-write` | Allow Codex to edit files in the workspace |
| `--cd <dir>` | Set the repository root |
| `--model <model>` | Choose a model |
| `-o, --output-last-message <file>` | Save final response |
| `--json` | Stream JSONL events |
| `--ignore-user-config` | Skip user config if config causes problems |
| `--skip-git-repo-check` | Allow running outside a git repo |

## Deprecated Or Wrong Patterns

Do not put `--full-auto` before the subcommand:

```bash
codex --full-auto exec "..."
```

That fails with:

```text
error: unexpected argument '--full-auto' found
tip: 'exec --full-auto' exists
```

Also avoid new usage of:

```bash
codex exec --full-auto "..."
```

It is deprecated. Prefer:

```bash
codex exec --sandbox workspace-write "..."
```

For reviews, prefer:

```bash
codex review --base main
codex exec --sandbox read-only "..."
```

## Static Diff Review

Use static diff review when Codex cannot execute shell commands in its sandbox.

```bash
git diff --stat main...HEAD
git diff --no-ext-diff --unified=80 main...HEAD -- src/api \
  | codex exec --sandbox read-only --cd /path/to/repo \
    "Review the git diff provided on stdin. Focus on concrete findings."
```

Keep static diffs under the input limit. If the diff is too large, narrow by path:

```bash
git diff main...HEAD -- frontend/src/components
git diff main...HEAD -- src/api src/schemas
```

## Troubleshooting

Authentication:

```bash
codex
```

Sandbox command execution failure:

```text
Shell snapshot validation failed
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

Use static diff mode because Codex may not be able to run `git diff` itself.

Input too large:

```text
Input exceeds the maximum length
```

Review smaller paths or commits. Do not pipe the full branch diff when it is multiple megabytes.
