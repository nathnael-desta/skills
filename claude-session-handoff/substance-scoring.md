# Substance Scoring Heuristic

Heuristic ranking -- prioritizes sessions with objective, tool calls, and discussion.

## Score formula

Each record scored from safe metadata (no raw tool payloads):

- User message (>= 5 words): **+1**
- Long user prompt (>= 50 words): **+2** (bonus)
- Assistant text (>20 chars): **+1**
- Engineering tool call (Bash, Write, Edit, Read, Grep, Glob, Task): **+2**

## Grades

- **0**: empty (not viable)
- **1-2**: probe
- **3-6**: light
- **7-15**: moderate
- **16+**: substantive

## Viability gate

Session is viable when: score > 0 AND user_messages > 0 AND has_concrete_prompt AND (tool_calls > 0 OR messages >= 3).

The last clause requires evidence of work: either actual tool calls or at least 3 messages of discussion.

## Field relationships

- `tool_calls`: total count of engineering tool uses (Bash, Write, Edit, Read, Grep, Glob, Task)
- `commands`: count of Bash/run_shell/run_terminal tool uses specifically
- `test_commands`: subset of `commands` where the command string matched a test runner pattern (pytest/npm test/cargo test/go test/ctest/tox/unittest)
- `file_references`: subset of `tool_calls` using Write, Edit, Read, Grep, or Glob

## Recency ordering

Sessions are sorted by parsed ISO timestamp from the JSONL. File mtime is used only as a fallback when no timestamp is present. The `_sort_key` function selects parsed timestamp over mtime, never the max of both.

## Groups output fields

| Field | Meaning |
|-------|---------|
| `latest_id` | Newest session by timestamp |
| `latest_viable` | Whether that newest session is viable |
| `newest_viable_id` | First viable session in timestamp order (the recommended continuation); null if same as latest |
| `highest_score_id` | Session with the highest raw score (diagnostics only; never recommended); null if same as latest or newest viable |

## Evidence extraction

Bounded sanitized evidence collected: tool names (first 30, no raw payloads), commands (first 20), modified file paths (first 30), read files/patterns (first 20), test commands (first 20), commit IDs (first 10), plans/specs (first 10), extraction limitations (first 10). All evidence lists are capped at collection time after deduplication. All evidence strings are redacted before writing to the handoff file.

## Conversation bounding

Conversation turns are bounded by default: the first substantive user objective (>= 50 chars) is always retained; newest turns fill the remaining budget (default 32 000 characters) working backward from the most recent. Individual turns exceeding 4 000 characters are truncated with a `[truncated...]` marker. Omitted turns are recorded in the extraction metadata as `N turns omitted (budget)`. Override the budget with `--max-chars`.

## Post-extraction completion gate

After extraction and bounding, the tool verifies three critical elements are recoverable before writing a standard handoff:

1. **Objective/investigation**: at least one substantive user turn (>= 50 chars).
2. **Work/current-state evidence**: tool calls, modified files, read files, test runs, or commits present.
3. **Concrete next action**: last assistant turn contains recoverable content.

If any element is missing, the tool exits with code 2 — no standard handoff is written. The agent must return to session selection. Diagnostic extractions (non-viable, `--allow-nonviable`) skip this gate.

## Escalation

When Claude JSONL tool schemas vary across versions, fall back to metadata-only summaries and document the limitation.
