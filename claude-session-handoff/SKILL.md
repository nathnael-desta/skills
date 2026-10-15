---
name: claude-session-handoff
description: Imports a Claude Code session from a repository or worktree and turns it into a redacted Markdown handoff for a fresh agent. Use when the user points to a Claude Code worktree/project, asks to recover the latest Claude session, choose an earlier session, find a session by Git branch, or continue Claude work in another provider.
argument-hint: "[worktree path | branch:<name>] [latest|session id] [next-session focus]"
---

# Claude Session Handoff

Create a handoff from Claude Code local session history without modifying the source worktree.

## Workflow

Discovery is a two-level hierarchy: **(worktree, branch) group -> session**. Every path converges on the same two-step UI, with bypasses when the input makes a level unambiguous.

### Intents the workflow recognizes

- **Literal latest** -- user said "latest" and all selectors agree (worktree, branch, recency). Identity is preserved (the selection is the newest session). If nonviable, extraction requires `--allow-nonviable` and produces only a diagnostic extraction, never a standard handoff.
- **Latest substantive** -- user said "latest" but did **not** name a branch. After group selection, show list with substance labels. Recommend the **newest viable** (first viable in timestamp order), not the highest-scored.
- **Continue on branch** -- user named a branch. `find` collects across worktrees; select group from narrowed results, then session.
- **Exact ID** -- user gave a session id or JSONL path. Extract directly; preserve identity (literal match). Viability is surfaced; nonviable exact ID still requires `--allow-nonviable` flag and produces only a diagnostic extraction, never a standard handoff.

### Fast paths

- **Exact session ID**: `python scripts/claude_sessions.py extract "<id>" --worktree "<worktree>"`
- **Worktree + branch + "latest"** (all three agree): `python scripts/claude_sessions.py list "<worktree>" --branch "<branch>" --json` -- take first entry.

### Step 1 -- Pick a worktree/branch group

```bash
python scripts/claude_sessions.py groups [--worktree ...] [--branch ...] [--skip-empty] --json
```

Groups show: `latest_viable`, `latest_substance_grade`, `latest_substance_score`. When the latest is nonviable: `newest_viable_id`/`newest_viable_score` holds the recommended continuation. `highest_score_id`/`highest_score_value` holds the raw-top-scoring session as **diagnostics only** (never recommended).

**Rules**:

- No groups -> say so. Do not search parent repos or sibling worktrees unless asked.
- One group -> proceed to Step 2. Show metadata and viability.
- Multiple groups -> use `question`. Groups newest-first. Recommend the first **viable** group. Show viability labels and the recommended newest-viable candidate when latest is nonviable.
- **Branch continuation** favors exact group match > recency. When `--branch` matches exactly one group, select it.

### Step 2 -- Pick a session within the chosen group

```bash
python scripts/claude_sessions.py list "<worktree>" --branch "<branch>" --json
```

Each session has `substance` (`score`, `grade`, `viable`, `tool_calls`, `file_references`, `test_commands`).

**Rules**:

- One session -> proceed. Show metadata and viability.
- Multiple sessions -> use `question`. Sorted newest-first (parsed timestamp, mtime fallback). Label newest as **"Latest"**. Label first viable in order as **"Recommended (Newest Viable)"**. Raw-highest-scored session may differ -- show its score as diagnostic, never as recommended.

#### Viability gate

A session is viable when: score > 0, user messages > 0, has a concrete prompt, **and** either tool calls > 0 or >= 3 messages (evidence of work done). See [`substance-scoring.md`](substance-scoring.md).

When the selected session is **not viable**:

- Show the viability warning with grade and score.
- Use `question` to offer: pick the newest viable alternative, or proceed anyway. Do not silently continue.
- If the user opts to proceed: use `extract --allow-nonviable`. This produces a **diagnostic extraction only** — raw session data for inspection, explicitly labeled as non-viable. It must never be treated as a standard handoff.

### Step 3 -- Extract

```bash
python scripts/claude_sessions.py extract "<session-id>" --worktree "<session-cwd>" [--allow-nonviable] [--max-chars N]
```

`extract` rejects nonviable sessions with exit code 2 and prints the newest viable candidate. Add `--allow-nonviable` to produce a diagnostic extraction (non-viable sessions never produce a standard handoff).

Conversation extraction is **bounded by default**. Only the first substantive user objective plus the newest turns that fit within a deterministic character budget (default 32 000 characters) are included. Oversized individual turns are truncated with a `[truncated...]` marker. Omitted turns are noted in the extraction metadata. Override the budget with `--max-chars`.

The extract writes a temp Markdown file containing:

- Header metadata (session ID, worktree, branch, timestamp, title, omissions, viability status).
- **Implementation Evidence** section: redacted tool names, command texts, file paths, test commands, commits, plans/specs. All evidence lists are bounded at collection time (capped counts, truncated command strings). All evidence strings are redacted before writing.
- **Conversation** section: user/assistant turns, redacted, bounded to the character budget.

#### Post-extraction completion gate

After extraction and bounding, the tool verifies three critical elements are recoverable:

1. **Objective/investigation**: at least one substantive user turn (>= 50 chars).
2. **Work/current-state evidence**: tool calls, modified files, read files, test runs, or commits present.
3. **Concrete next action**: last assistant turn contains recoverable content.

If any element is missing, the tool exits with code 2 and prints the missing reasons. A standard handoff is **not written**. The agent must return to session selection. Diagnostic extractions (non-viable) skip this gate entirely — they are inspection-only.

### Writing the handoff

Inspect `git status --short --branch` and recent `git log --oneline` for current state. Repository commit history is included only when linked by transcript/session time; otherwise note only that HEAD differs.

Write the handoff to the OS temp directory with a descriptive filename and mode `0600`. Include: objective, important decisions, completed work, current state, remaining work, blockers/open questions, verification evidence, next recommended action, relevant artifact paths/URLs, and `Suggested skills`.

Treat extra user arguments as the next session focus. Reference existing plans/specs/commits/diffs rather than copying them.

## Output

Return the final handoff path, selected session id, session timestamp, and any extraction limitations.

## Safety

- Redact credentials, tokens, passwords, and personal data. The extractor applies pattern redaction; review the output.
- Do not alter, resume, delete, or rewrite JSONL session files.
- If no exact-worktree session exists, report it clearly and ask before searching parent repos or sibling worktrees.
- Do not reproduce raw terminal/tool output or hidden provider metadata.
- Do not claim a task is complete solely because the old assistant said so; distinguish reported state from verified repository state.
- Never include `subagents/*.jsonl` as standalone sessions.
