#!/usr/bin/env python3
"""List, score, and safely extract top-level Claude Code sessions for a worktree."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"

_ENGINEERING_TOOLS = frozenset({
    "Bash", "Write", "Edit", "Read", "Grep", "Glob", "Task",
    "run_shell_command", "run_terminal_cmd",
})
_TEST_TOOLS = frozenset({"Bash", "run_shell_command", "run_terminal_cmd"})
_FILE_TOOLS = frozenset({"Write", "Edit", "Read", "Grep", "Glob"})
_SECURE_KEY_BLACKLIST = frozenset({
    "api_key", "apikey", "secret", "password", "token", "credential",
    "access_key", "private_key",
})

DEFAULT_MAX_CHARS = 32000
MAX_TURN_CHARS = 4000
_MAX_EVIDENCE_TOOLS = 30
_MAX_EVIDENCE_COMMANDS = 20
_MAX_EVIDENCE_FILES_MOD = 30
_MAX_EVIDENCE_FILES_READ = 20
_MAX_EVIDENCE_TESTS = 20
_MAX_EVIDENCE_COMMITS = 10
_MAX_EVIDENCE_PLANS = 10
_MAX_EVIDENCE_LIMITATIONS = 10

SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s]+"),
    re.compile(r"(?i)\b([A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|COOKIE))\s*=\s*([^\s]+)"),
    re.compile(r"\b(?:sk|pk|ghp|github_pat|xox[baprs])[-_][A-Za-z0-9_-]{12,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
)


@dataclass
class SessionSummary:
    path: Path
    session_id: str
    cwd: str
    branch: str
    timestamp: str
    title: str
    first_prompt: str
    messages: int
    mtime: float


@dataclass
class SubstanceScore:
    """Rough heuristic: higher -> more handoff-worthy content.
    Zero means empty/probe - session is not continuation-worthy.

    Field relationships:
    - test_commands counts Bash tool_use calls matching test runners;
      it is a subset of commands/tool_calls (each test command is both
      a command AND a Bash/run_shell tool_use).
    """

    value: int
    messages: int
    user_messages: int
    tool_calls: int
    file_references: int
    test_commands: int
    last_substantive_ts: str
    has_concrete_prompt: bool


def _top_level_sessions() -> Iterable[Path]:
    if not CLAUDE_PROJECTS.is_dir():
        return []
    return CLAUDE_PROJECTS.glob("*/*.jsonl")


def _text_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
    return "\n\n".join(parts)


def _redact(text: str) -> str:
    redacted = text
    redacted = SECRET_PATTERNS[0].sub(r"\1[REDACTED]", redacted)
    redacted = SECRET_PATTERNS[1].sub(r"\1=[REDACTED]", redacted)
    redacted = SECRET_PATTERNS[2].sub("[REDACTED_TOKEN]", redacted)
    redacted = SECRET_PATTERNS[3].sub("[REDACTED_PRIVATE_KEY]", redacted)
    return redacted


def _records(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                yield value


def _substance_score(records_iter: Iterable[dict[str, Any]]) -> SubstanceScore:
    """Score a session for continuation-worthiness without dumping raw payloads."""
    user_msgs = 0
    total_msgs = 0
    tool_calls = 0
    file_refs = 0
    test_cmds = 0
    has_prompt = False
    last_ts = ""
    score = 0

    for rec in records_iter:
        if rec.get("isSidechain") is True:
            continue
        t = rec.get("type")
        if t not in ("user", "assistant"):
            continue

        msg = rec.get("message") or {}
        content = msg.get("content")
        text = _text_content(content)
        ts = str(rec.get("timestamp", "") or "")

        if t == "user":
            if text and len(text.split()) >= 5:
                user_msgs += 1
                total_msgs += 1
                has_prompt = True
                last_ts = ts
                score += 1
                if len(text.split()) >= 50:
                    score += 2
        elif t == "assistant":
            if isinstance(content, list):
                blocks = [b for b in content if isinstance(b, dict)]
                text_blocks = [b for b in blocks if b.get("type") == "text"]
                tool_blocks = [b for b in blocks if b.get("type") == "tool_use"]

                meaningful_text = any(
                    len(str(b.get("text", ""))) > 20 for b in text_blocks
                )
                if meaningful_text or tool_blocks:
                    total_msgs += 1
                    last_ts = ts
                    if meaningful_text:
                        score += 1

                for tb in tool_blocks:
                    tool_name = str(tb.get("name", ""))
                    if tool_name in _ENGINEERING_TOOLS:
                        tool_calls += 1
                        score += 2
                        if tool_name in _TEST_TOOLS:
                            test_cmds += 1
                        if tool_name in _FILE_TOOLS:
                            file_refs += 1
            elif text:
                total_msgs += 1
                last_ts = ts
                score += 1

    return SubstanceScore(
        value=score,
        messages=total_msgs,
        user_messages=user_msgs,
        tool_calls=tool_calls,
        file_references=file_refs,
        test_commands=test_cmds,
        last_substantive_ts=last_ts,
        has_concrete_prompt=has_prompt,
    )


def _score_summary(ss: SubstanceScore) -> str:
    """Human-readable grade."""
    if ss.value == 0:
        return "empty"
    if ss.value <= 2:
        return "probe"
    if ss.value <= 6:
        return "light"
    if ss.value <= 15:
        return "moderate"
    return "substantive"


def _is_viable(ss: SubstanceScore) -> bool:
    """Viability gate: session must have objective, evidence of work, useful next action.

    Requires: user messages with concrete prompt, AND tool calls or substantial
    assistant discussion (evidence of work being done), AND score > 0.
    """
    if ss.value == 0:
        return False
    if ss.user_messages == 0:
        return False
    if not ss.has_concrete_prompt:
        return False
    # Evidence of work: tool calls OR substantial discussion (>= 3 messages)
    if ss.tool_calls == 0 and ss.messages < 3:
        return False
    return True


def summarize(path: Path) -> SessionSummary | None:
    cwd = branch = timestamp = title = first_prompt = ""
    messages = 0
    session_id = path.stem
    for record in _records(path):
        if record.get("isSidechain") is True:
            continue
        cwd = cwd or str(record.get("cwd") or "")
        branch = branch or str(record.get("gitBranch") or "")
        timestamp = timestamp or str(record.get("timestamp") or "")
        if record.get("type") == "ai-title":
            title = str(record.get("aiTitle") or "")
        if record.get("type") in {"user", "assistant"}:
            text = _text_content((record.get("message") or {}).get("content"))
            if text:
                messages += 1
                if record.get("type") == "user" and not first_prompt:
                    first_prompt = " ".join(text.split())[:180]
    if not cwd:
        return None
    return SessionSummary(
        path=path,
        session_id=session_id,
        cwd=cwd,
        branch=branch,
        timestamp=timestamp,
        title=title,
        first_prompt=first_prompt,
        messages=messages,
        mtime=path.stat().st_mtime,
    )


def summarize_full(path: Path) -> tuple[SessionSummary | None, SubstanceScore]:
    """Full summary with substance score (single pass through the file)."""
    records = list(_records(path))
    ss = _substance_score(records)

    cwd = branch = timestamp = title = first_prompt = ""
    messages = 0
    session_id = path.stem
    for record in records:
        if record.get("isSidechain") is True:
            continue
        cwd = cwd or str(record.get("cwd") or "")
        branch = branch or str(record.get("gitBranch") or "")
        timestamp = timestamp or str(record.get("timestamp") or "")
        if record.get("type") == "ai-title":
            title = str(record.get("aiTitle") or "")
        if record.get("type") in {"user", "assistant"}:
            text = _text_content((record.get("message") or {}).get("content"))
            if text:
                messages += 1
                if record.get("type") == "user" and not first_prompt:
                    first_prompt = " ".join(text.split())[:180]

    if not cwd:
        return None, ss

    summary = SessionSummary(
        path=path,
        session_id=session_id,
        cwd=cwd,
        branch=branch,
        timestamp=timestamp,
        title=title,
        first_prompt=first_prompt,
        messages=messages,
        mtime=path.stat().st_mtime,
    )
    return summary, ss


def _parse_ts(ts_str: str) -> float:
    """Parse ISO timestamp to unix float; return 0 on failure."""
    if not ts_str:
        return 0.0
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return 0.0


def _sort_key(summary: SessionSummary) -> float:
    """Recency: parsed timestamp first, mtime only as fallback."""
    parsed = _parse_ts(summary.timestamp)
    if parsed > 0:
        return parsed
    return summary.mtime


def sessions_for(worktree: Path) -> list[SessionSummary]:
    target = str(worktree.resolve())
    matches = []
    for path in _top_level_sessions():
        summary = summarize(path)
        if summary and str(Path(summary.cwd).resolve()) == target:
            matches.append(summary)
    return sorted(matches, key=_sort_key, reverse=True)


def _display_time(summary: SessionSummary) -> str:
    if summary.timestamp:
        return summary.timestamp
    return datetime.fromtimestamp(summary.mtime).astimezone().isoformat()


def _session_json(summary: SessionSummary, ss: SubstanceScore | None = None) -> dict[str, Any]:
    d: dict[str, Any] = (
        summary.__dict__
        | {"path": str(summary.path), "time": _display_time(summary)}
    )
    if ss is not None:
        d["substance"] = {
            "score": ss.value,
            "grade": _score_summary(ss),
            "viable": _is_viable(ss),
            "messages": ss.messages,
            "user_messages": ss.user_messages,
            "tool_calls": ss.tool_calls,
            "file_references": ss.file_references,
            "test_commands": ss.test_commands,
            "last_substantive_ts": ss.last_substantive_ts,
            "has_concrete_prompt": ss.has_concrete_prompt,
        }
    return d


def cmd_list(args: argparse.Namespace) -> int:
    worktree = Path(args.worktree).expanduser()
    if not worktree.is_dir():
        print(f"error: worktree does not exist: {worktree}", file=sys.stderr)
        return 2
    sessions = sessions_for(worktree)
    if args.branch:
        sessions = [s for s in sessions if s.branch.strip() == args.branch]

    scored: list[tuple[SessionSummary, SubstanceScore]] = []
    for s in sessions:
        _, ss = summarize_full(s.path)
        scored.append((s, ss))

    if args.skip_empty:
        scored = [(s, ss) for s, ss in scored if _is_viable(ss)]

    if args.json:
        print(json.dumps([_session_json(s, ss) for s, ss in scored]))
    else:
        if not scored:
            print(f"No exact Claude Code sessions found for {worktree.resolve()}")
            return 1
        for index, (item, ss) in enumerate(scored, 1):
            label = item.title or item.first_prompt or "Untitled session"
            grade = _score_summary(ss)
            viable = "yes" if _is_viable(ss) else "NO"
            print(
                f"{index}. {item.session_id} | {_display_time(item)} | "
                f"branch={item.branch or '-'} | msgs={item.messages} | "
                f"score={ss.value} | grade={grade} | viable={viable} | {label}"
            )
    return 0


def _select_session_full(
    selector: str, worktree: Path | None
) -> tuple[SessionSummary, SubstanceScore | None]:
    """Select session and return its substance score if available."""
    if Path(selector).expanduser().is_file():
        path = Path(selector).expanduser().resolve()
        summary, ss = summarize_full(path)
        if summary is None:
            raise ValueError(f"not a readable top-level Claude session: {path}")
        if "subagents" in path.parts:
            raise ValueError("subagent sessions cannot be selected directly")
        if worktree and str(Path(summary.cwd).resolve()) != str(worktree.resolve()):
            raise ValueError("session cwd does not match the requested worktree")
        return summary, ss
    if worktree is None:
        raise ValueError("--worktree is required when selecting by id")
    sessions = sessions_for(worktree)
    if selector == "latest":
        if not sessions:
            raise ValueError("no exact Claude sessions found")
        # Return newest with score
        summary = sessions[0]
        _, ss = summarize_full(summary.path)
        return summary, ss
    matches = [item for item in sessions if item.session_id.startswith(selector)]
    if len(matches) != 1:
        raise ValueError(f"session selector matched {len(matches)} sessions")
    summary = matches[0]
    _, ss = summarize_full(summary.path)
    return summary, ss


def _bounded_turns(
    turns: list[tuple[str, str, str]], budget: int
) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Select turns within char budget: first objective + newest fit.

    Always includes first substantive user turn (the objective).
    Fills from newest backward; truncates oversized turns.
    """
    omissions: list[str] = []
    if not turns:
        return [], omissions

    # Find first substantive user turn (>= 50 chars)
    first_obj_idx = None
    for i, (role, _, text) in enumerate(turns):
        if role == "user" and len(text) >= 50:
            first_obj_idx = i
            break

    selected: list[tuple[str, str, str]] = []
    selected_timestamps: set[str] = set()
    used = 0

    if first_obj_idx is not None:
        role, ts, text = turns[first_obj_idx]
        text, tr = _truncate_turn(text)
        if tr:
            omissions.append("first objective truncated")
        selected.append((role, ts, text))
        selected_timestamps.add(ts)
        used += len(text)

    # Fill from newest backward
    for i in range(len(turns) - 1, -1, -1):
        role, ts, text = turns[i]
        if ts in selected_timestamps:
            continue
        text, tr = _truncate_turn(text)
        overhead = len(text) + 5  # markdown heading overhead
        if used + overhead > budget:
            break
        selected.append((role, ts, text))
        selected_timestamps.add(ts)
        used += overhead
        if tr:
            omissions.append("turn {} truncated".format(i))

    unselected = len(turns) - len(selected)
    if unselected > 0:
        omissions.append("{} turns omitted (budget)".format(unselected))

    # Sort chronologically by original index
    selected.sort(key=lambda x: [i for i, t in enumerate(turns)
                                  if t[1] == x[1]][0])
    return selected, omissions


def _truncate_turn(text: str) -> tuple[str, bool]:
    """Truncate turn to MAX_TURN_CHARS, returning (text, was_truncated)."""
    if len(text) <= MAX_TURN_CHARS:
        return text, False
    return text[:MAX_TURN_CHARS] + "\n\n[truncated...]", True


def _newest_viable_for(worktree: Path) -> SessionSummary | None:
    sessions = sessions_for(worktree)
    for s in sessions:
        _, ss = summarize_full(s.path)
        if _is_viable(ss):
            return s
    return None


_EVIDENCE_CAPS = {
    "tool_calls": _MAX_EVIDENCE_TOOLS,
    "commands": _MAX_EVIDENCE_COMMANDS,
    "files_modified": _MAX_EVIDENCE_FILES_MOD,
    "files_read": _MAX_EVIDENCE_FILES_READ,
    "tests_run": _MAX_EVIDENCE_TESTS,
    "plans_or_specs": _MAX_EVIDENCE_PLANS,
    "commits": _MAX_EVIDENCE_COMMITS,
    "limitations": _MAX_EVIDENCE_LIMITATIONS,
}


def _extract_evidence(records_iter: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Collect sanitized structured evidence without raw tool payloads.

    Each evidence list is bounded at collection time (see _EVIDENCE_CAPS);
    the cap is enforced after deduplication.
    """
    risk_keys = _SECURE_KEY_BLACKLIST
    evidence: dict[str, Any] = {
        "tool_calls": [],
        "commands": [],
        "files_modified": [],
        "files_read": [],
        "tests_run": [],
        "plans_or_specs": [],
        "commits": [],
        "limitations": [],
    }

    for rec in records_iter:
        if rec.get("isSidechain") is True:
            continue
        if rec.get("type") != "assistant":
            continue

        msg = rec.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue

            name = str(block.get("name", "") or "")
            inp = block.get("input") or {}
            if not isinstance(inp, dict):
                continue

            evidence["tool_calls"].append(name)

            if name in ("Bash", "run_shell_command", "run_terminal_cmd"):
                cmd = str(inp.get("command", ""))
                if cmd and cmd.strip():
                    evidence["commands"].append(cmd)
                if re.search(r"\b(pytest|npm test|npm run test"
                              r"|yarn test|cargo test|go test"
                              r"|ctest|tox|unittest)\b", cmd):
                    evidence["tests_run"].append(cmd)

            if name in ("Write", "Edit"):
                fp = str(inp.get("filePath", ""))
                if fp:
                    evidence["files_modified"].append(fp)

            if name == "Read":
                fp = str(inp.get("filePath", ""))
                if fp:
                    evidence["files_read"].append(fp)

            if name == "Glob":
                pat = str(inp.get("pattern", ""))
                if pat:
                    evidence["files_read"].append(pat)

            if name == "Grep":
                pat = str(inp.get("pattern", ""))
                if pat:
                    evidence["files_read"].append("grep:" + pat)

            prompt = str(inp.get("prompt", "") or inp.get("description", "")
                          or inp.get("message", ""))
            if prompt:
                commit_match = re.search(r"[0-9a-f]{7,40}", prompt)
                if commit_match:
                    evidence["commits"].append(commit_match.group(0))

            for fp_key in ("filePath", "target_directory", "directory"):
                fp = str(inp.get(fp_key, ""))
                if fp and any(kw in fp.lower() for kw in
                              ("plan", "spec", "adr", "roadmap", "architecture")):
                    evidence["plans_or_specs"].append(fp)

            risky_keys = [k for k in inp if k.lower() in risk_keys]
            if risky_keys:
                evidence["limitations"].append(
                    f"redacted {len(risky_keys)} secret-bearing keys from {name} input"
                )

    for k in ("tool_calls", "commands", "files_modified", "files_read",
              "tests_run", "plans_or_specs", "commits", "limitations"):
        seen: set[str] = set()
        deduped = []
        for v in evidence[k]:
            if v not in seen:
                seen.add(v)
                deduped.append(v)
        cap = _EVIDENCE_CAPS.get(k, len(deduped))
        if len(deduped) > cap:
            evidence[f"_{k}_capped"] = len(deduped) - cap
        evidence[k] = deduped[:cap]

    return evidence


def _completion_gate(
    turns: list[tuple[str, str, str]], evidence: dict[str, Any]
) -> tuple[bool, list[str]]:
    """Post-extraction gate: verify objective, work evidence, and next action are recoverable.

    Returns (passes, missing_reasons). Only produce a standard handoff when all pass.
    """
    missing: list[str] = []

    # Objective / investigation: at least one user turn with >= 50 chars
    has_user = any(r == "user" and len(t) >= 50 for r, _, t in turns)
    if not has_user:
        missing.append("no substantive user objective/investigation found")

    # Work / current-state evidence: tool calls, files, test runs, or commits
    has_work = bool(
        evidence.get("tool_calls")
        or evidence.get("files_modified")
        or evidence.get("files_read")
        or evidence.get("tests_run")
        or evidence.get("commits")
    )
    if not has_work:
        missing.append("no work/current-state evidence (tools, files, tests, commits)")

    # Next action: last assistant turn with any content
    last_assistant_text = ""
    for r, _, t in reversed(turns):
        if r == "assistant":
            last_assistant_text = t
            break
    if not last_assistant_text:
        missing.append("no recovery of concrete next action from assistant turns")

    return len(missing) == 0, missing


def cmd_extract(args: argparse.Namespace) -> int:
    worktree = Path(args.worktree).expanduser() if args.worktree else None
    try:
        session, ss = _select_session_full(args.selector, worktree)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    max_chars = int(args.max_chars) if args.max_chars else DEFAULT_MAX_CHARS
    is_nonviable = ss is not None and not _is_viable(ss)
    diagnostic = False  # if True, only produce diagnostic extraction (never standard handoff)

    # Viability check: nonviable sessions require --allow-nonviable
    if is_nonviable and not args.allow_nonviable:
        candidate = None
        if session.cwd:
            candidate = _newest_viable_for(
                Path(session.cwd).expanduser().resolve()
            )
        msg = (
            f"session {session.session_id[:12]}... is not viable "
            f"(grade={_score_summary(ss)}, score={ss.value})"
        )
        if candidate and candidate.session_id != session.session_id:
            msg += (
                f"\nnewest viable: {candidate.session_id[:12]}... "
                f"| {_display_time(candidate)}"
            )
        print(msg, file=sys.stderr)
        print("use --allow-nonviable for a diagnostic extraction only (no standard handoff)", file=sys.stderr)
        return 2

    if is_nonviable:
        print(
            f"warning: nonviable session "
            f"(grade={_score_summary(ss)}, score={ss.value}) — diagnostic extraction only",
            file=sys.stderr,
        )
        diagnostic = True

    records = list(_records(session.path))
    turns: list[tuple[str, str, str]] = []
    for record in records:
        if record.get("isSidechain") is True or record.get("type") not in {"user", "assistant"}:
            continue
        message = record.get("message") or {}
        text = _text_content(message.get("content"))
        if not text:
            continue
        role = str(message.get("role") or record.get("type") or "unknown")
        turns.append((role, str(record.get("timestamp") or ""), _redact(text)))

    selected_turns, omissions = _bounded_turns(turns, max_chars)
    evidence = _extract_evidence(records)

    # Post-extraction completion gate
    gate_ok, gate_missing = _completion_gate(selected_turns, evidence)

    if not diagnostic and not gate_ok:
        msg = (
            f"extraction incomplete for session {session.session_id[:12]}... — "
            f"cannot produce a standard handoff"
        )
        print(f"error: {msg}", file=sys.stderr)
        for reason in gate_missing:
            print(f"  - {reason}", file=sys.stderr)
        print("return to session selection", file=sys.stderr)
        return 2

    fd, output_name = tempfile.mkstemp(
        prefix=f"claude-session-{session.session_id[:8]}-", suffix=".md"
    )
    os.close(fd)
    output = Path(output_name)
    output.chmod(stat.S_IRUSR | stat.S_IWUSR)
    with output.open("w", encoding="utf-8") as handle:
        if diagnostic:
            handle.write("# Diagnostic Extraction (Nonviable Session)\n\n")
            handle.write("**This is NOT a standard handoff.** "
                         "Below is a raw extraction for inspection only.\n\n")
        else:
            handle.write("# Extracted Claude Code Session\n\n")
        handle.write(f"- Session ID: `{session.session_id}`\n")
        handle.write(f"- Worktree: `{session.cwd}`\n")
        handle.write(f"- Branch: `{session.branch or 'unknown'}`\n")
        handle.write(f"- Started: `{_display_time(session)}`\n")
        handle.write(f"- Title: {session.title or 'Untitled'}\n")
        handle.write("- Extraction: conversational text only; "
                     "tool payloads and subagents excluded\n")
        if omissions:
            handle.write("- Omissions: {}\n".format("; ".join(omissions)))
        if diagnostic:
            handle.write(f"- Viability: NOT VIABLE (grade={_score_summary(ss)}, score={ss.value})\n")
        elif is_nonviable:
            handle.write(f"- Viability: NONVIABLE (diagnostic only)\n")
        handle.write("\n")

        if any(evidence.values()):
            handle.write("## Implementation Evidence\n\n")
            if evidence["tool_calls"]:
                capped = evidence["tool_calls"][:_MAX_EVIDENCE_TOOLS]
                handle.write(f"- **Tools used**: {', '.join(capped)}\n")
                if len(evidence["tool_calls"]) > _MAX_EVIDENCE_TOOLS:
                    handle.write(f"  - ... and {len(evidence['tool_calls']) - _MAX_EVIDENCE_TOOLS} more (capped)\n")
            if evidence["commands"]:
                handle.write("- **Commands executed**:\n")
                for c in evidence["commands"]:
                    handle.write(f"  - `{_redact(c[:200])}`\n")
                if evidence.get("_commands_capped"):
                    handle.write(f"  - ... and {evidence['_commands_capped']} more (capped)\n")
            if evidence["files_modified"]:
                handle.write("- **Files modified/created**:\n")
                for f in evidence["files_modified"]:
                    handle.write(f"  - `{_redact(f)}`\n")
                if evidence.get("_files_modified_capped"):
                    handle.write(f"  - ... and {evidence['_files_modified_capped']} more (capped)\n")
            if evidence["files_read"]:
                handle.write("- **Files/patterns read**:\n")
                for f in evidence["files_read"]:
                    handle.write(f"  - `{_redact(f)}`\n")
                if evidence.get("_files_read_capped"):
                    handle.write(f"  - ... and {evidence['_files_read_capped']} more (capped)\n")
            if evidence["tests_run"]:
                handle.write("- **Tests executed**:\n")
                for t in evidence["tests_run"]:
                    handle.write(f"  - `{_redact(t[:200])}`\n")
                if evidence.get("_tests_run_capped"):
                    handle.write(f"  - ... and {evidence['_tests_run_capped']} more (capped)\n")
            if evidence["commits"]:
                handle.write(f"- **Commit IDs referenced**: {', '.join(evidence['commits'])}\n")
                if evidence.get("_commits_capped"):
                    handle.write(f"  - ... and {evidence['_commits_capped']} more (capped)\n")
            if evidence["plans_or_specs"]:
                handle.write(f"- **Plans/specs referenced**: "
                             f"{', '.join(evidence['plans_or_specs'])}\n")
                if evidence.get("_plans_or_specs_capped"):
                    handle.write(f"  - ... and {evidence['_plans_or_specs_capped']} more (capped)\n")
            if evidence["limitations"]:
                handle.write("- **Extraction limitations**:\n")
                for lim in evidence["limitations"]:
                    handle.write(f"  - {lim}\n")
                if evidence.get("_limitations_capped"):
                    handle.write(f"  - ... and {evidence['_limitations_capped']} more (capped)\n")
            handle.write("\n")
        handle.write("## Conversation\n")
        for role, timestamp, text in selected_turns:
            handle.write(f"\n### {role.title()} ({timestamp or 'unknown time'})\n\n{text}\n")
    print(output)
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    branch = args.branch.strip()
    if not branch:
        print("error: --branch must not be empty", file=sys.stderr)
        return 2
    sessions: list[tuple[SessionSummary, SubstanceScore]] = []
    for path in _top_level_sessions():
        summary, ss = summarize_full(path)
        if summary is None:
            continue
        if summary.branch.strip() != branch:
            continue
        if args.worktree:
            target = str(Path(args.worktree).expanduser().resolve())
            if str(Path(summary.cwd).resolve()) != target:
                continue
        sessions.append((summary, ss))

    if args.skip_empty:
        sessions = [(s, ss) for s, ss in sessions if _is_viable(ss)]

    sessions.sort(key=lambda item: _sort_key(item[0]), reverse=True)
    if args.json:
        print(json.dumps([_session_json(s, ss) for s, ss in sessions]))
    else:
        if not sessions:
            worktree_hint = f" in worktree {args.worktree}" if args.worktree else ""
            print(f"No Claude Code sessions found for branch '{branch}'{worktree_hint}")
            return 1
        for index, (item, ss) in enumerate(sessions, 1):
            label = item.title or item.first_prompt or "Untitled session"
            grade = _score_summary(ss)
            viable = "yes" if _is_viable(ss) else "NO"
            print(
                f"{index}. {item.session_id} | {_display_time(item)} | "
                f"branch={item.branch} | cwd={item.cwd} | msgs={item.messages} | "
                f"score={ss.value} | grade={grade} | viable={viable} | {label}"
            )
    return 0


def cmd_groups(args: argparse.Namespace) -> int:
    """Enumerate unique (worktree, branch) groups with substance scores."""
    from collections import defaultdict

    branch_filter = args.branch.strip() if args.branch else None
    worktree_filter = str(Path(args.worktree).expanduser().resolve()) if args.worktree else None
    groups: dict[tuple[str, str], list[tuple[SessionSummary, SubstanceScore]]] = defaultdict(list)

    for path in _top_level_sessions():
        summary, ss = summarize_full(path)
        if summary is None:
            continue
        key = (str(Path(summary.cwd).resolve()), summary.branch.strip())
        groups[key].append((summary, ss))

    if worktree_filter:
        groups = {k: v for k, v in groups.items() if k[0] == worktree_filter}
    if branch_filter:
        groups = {k: v for k, v in groups.items() if k[1] == branch_filter}

    if args.skip_empty:
        groups = {
            k: [(s, ss) for s, ss in v if _is_viable(ss)]
            for k, v in groups.items()
        }
        groups = {k: v for k, v in groups.items() if v}

    result: list[dict[str, Any]] = []
    for (cwd, branch), sessions in groups.items():
        latest_summary, latest_ss = max(sessions, key=lambda x: _sort_key(x[0]))

        # "latest substantive" = newest viable by timestamp (not highest raw score)
        viable_sessions = [(s, ss) for s, ss in sessions if _is_viable(ss)]
        newest_viable = None
        if viable_sessions:
            newest_viable = max(viable_sessions, key=lambda x: _sort_key(x[0]))

        # diagnostics only: highest raw score (may be old)
        highest_score = max(sessions, key=lambda x: x[1].value)
        _, highest_ss = highest_score

        entry = {
            "worktree": cwd,
            "branch": branch,
            "session_count": len(sessions),
            "latest_id": latest_summary.session_id,
            "latest_time": _display_time(latest_summary),
            "latest_title": latest_summary.title or latest_summary.first_prompt or "Untitled",
            "latest_substance_grade": _score_summary(latest_ss),
            "latest_substance_score": latest_ss.value,
            "latest_viable": _is_viable(latest_ss),
            "newest_viable_id": (
                newest_viable[0].session_id
                if newest_viable and newest_viable[0].session_id != latest_summary.session_id
                else None
            ),
            "newest_viable_score": newest_viable[1].value if newest_viable else 0,
            "highest_score_id": (
                highest_score[0].session_id
                if highest_score[0].session_id != latest_summary.session_id
                and highest_score[0].session_id != (newest_viable[0].session_id if newest_viable else None)
                else None
            ),
            "highest_score_value": highest_ss.value,
        }
        result.append(entry)

    result.sort(key=lambda g: g["latest_time"], reverse=True)

    if args.json:
        print(json.dumps(result))
    else:
        if not result:
            branch_hint = f" for branch '{branch_filter}'" if branch_filter else ""
            print(f"No Claude Code session groups found{branch_hint}")
            return 1
        for i, g in enumerate(result, 1):
            viable_tag = "" if g["latest_viable"] else " [NOT VIABLE]"
            print(
                f"{i}. {g['worktree']} | branch={g['branch'] or '-'} | "
                f"{g['session_count']} sessions | latest={g['latest_id'][:12]}... | "
                f"score={g['latest_substance_score']} | "
                f"grade={g['latest_substance_grade']}{viable_tag} | "
                f"{g['latest_title']}"
            )
            if g["newest_viable_id"]:
                print(
                    f"   recommend (newest viable): {g['newest_viable_id'][:12]}..."
                    f" (score={g['newest_viable_score']})"
                )
            if g["highest_score_id"]:
                print(
                    f"   highest score: {g['highest_score_id'][:12]}..."
                    f" (score={g['highest_score_value']})"
                )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="list exact-worktree sessions with substance scores")
    listing.add_argument("worktree")
    listing.add_argument("--branch", default=None, help="optional: filter to a specific branch")
    listing.add_argument("--json", action="store_true")
    listing.add_argument("--skip-empty", action="store_true", help="hide non-viable sessions")
    listing.set_defaults(func=cmd_list)
    finder = commands.add_parser("find", help="find sessions by git branch with substance scores")
    finder.add_argument("--branch", required=True, help="exact git branch name")
    finder.add_argument("--worktree", default=None, help="optional: narrow to a specific worktree")
    finder.add_argument("--json", action="store_true")
    finder.add_argument("--skip-empty", action="store_true", help="hide non-viable sessions")
    finder.set_defaults(func=cmd_find)
    groups = commands.add_parser(
        "groups", help="enumerate unique worktree+branch groups with substance scores"
    )
    groups.add_argument("--worktree", default=None, help="optional: narrow to a specific worktree")
    groups.add_argument("--branch", default=None, help="optional: filter groups by branch name")
    groups.add_argument("--json", action="store_true")
    groups.add_argument("--skip-empty", action="store_true",
                        help="hide groups with no viable sessions")
    groups.set_defaults(func=cmd_groups)
    extract = commands.add_parser("extract", help="extract a selected session with evidence")
    extract.add_argument("selector", help="latest, session id/prefix, or JSONL path")
    extract.add_argument("--worktree")
    extract.add_argument("--allow-nonviable", action="store_true",
                         help="permit diagnostic extraction of non-viable sessions (no standard handoff)")
    extract.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS,
                         help="max conversation budget (chars; default 32000)")
    extract.set_defaults(func=cmd_extract)
    return root


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
