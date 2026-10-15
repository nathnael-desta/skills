"""Unit and CLI integration tests for claude_sessions.

Covers: substance scoring, viability, nonviable rejection/override,
timestamp-vs-mtime ordering, newest viable recommendation,
evidence redaction, grade thresholds, malformed JSONL,
deduplication, backward compatibility,
bounded conversation extraction, first-objective retention,
newest-turns budget, truncation, omission markers,
evidence caps with overflow tracking, diagnostic extraction,
completion gate, --max-chars override.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import claude_sessions as cs


def _jl(obj):
    fp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    fp.write(chr(10).join(json.dumps(o) for o in obj) + chr(10))
    fp.close()
    return Path(fp.name)


_SCRIPT = str(_SCRIPTS / "claude_sessions.py")


def _run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, _SCRIPT, *args],
        capture_output=True, text=True,
    )


# ===================== SubstanceScore =====================

def test_empty():
    j = _jl([{"type": "system", "isSidechain": False, "cwd": "/tmp/t",
              "gitBranch": "main", "timestamp": "2026-01-01T00:00:00Z"}])
    _, ss = cs.summarize_full(j)
    assert ss.value == 0
    assert cs._score_summary(ss) == "empty"
    assert not cs._is_viable(ss)


def test_short_not_viable():
    j = _jl([{"type": "user", "isSidechain": False,
              "message": {"content": [{"type": "text", "text": "hello world"}],
                          "role": "user"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    _, ss = cs.summarize_full(j)
    assert ss.value == 0
    assert not cs._is_viable(ss)


def test_viable_min():
    j = _jl([{"type": "user", "isSidechain": False,
              "message": {"content": [{"type": "text",
                          "text": "Please help fix this bug in the code"}],
                          "role": "user"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"},
             {"type": "assistant", "isSidechain": False,
              "message": {"content": [
                  {"type": "text", "text": "Let me help with that bug."},
                  {"type": "tool_use", "name": "Read", "id": "t1",
                   "input": {"filePath": "/tmp/t/bug.py"}},
              ], "role": "assistant"},
              "timestamp": "2026-01-01T00:00:01Z",
              "cwd": "/tmp/t", "gitBranch": "main"},
    ])
    _, ss = cs.summarize_full(j)
    assert cs._is_viable(ss)
    assert ss.tool_calls == 1


def test_no_tool_no_discussion_not_viable():
    """No tool calls and < 3 messages -> not viable even with prompt."""
    j = _jl([{"type": "user", "isSidechain": False,
              "message": {"content": [{"type": "text",
                          "text": "Please help fix this bug in the code"}],
                          "role": "user"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    _, ss = cs.summarize_full(j)
    # user_messages=1, score=1, tool_calls=0, messages=1 (< 3)
    assert not cs._is_viable(ss)


def test_with_tools():
    t = ("Can you refactor the database layer? "
         "It needs to handle connection handling properly. "
         "We also need to add retry logic and better error messages "
         "for timeout scenarios across the entire module. "
         "Please update all related tests as well.")
    j = _jl([
        {"type": "user", "isSidechain": False,
         "message": {"content": [{"type": "text", "text": t}], "role": "user"},
         "timestamp": "2026-01-01T00:00:00Z",
         "cwd": "/tmp/t", "gitBranch": "main"},
        {"type": "assistant", "isSidechain": False,
         "message": {"content": [
             {"type": "text", "text": "I will refactor now."},
             {"type": "tool_use", "name": "Edit", "id": "t1",
              "input": {"filePath": "/tmp/t/db.py"}},
             {"type": "tool_use", "name": "Bash", "id": "t2",
              "input": {"command": "pytest tests/"}},
         ], "role": "assistant"},
         "timestamp": "2026-01-01T00:00:01Z",
         "cwd": "/tmp/t", "gitBranch": "main"},
    ])
    _, ss = cs.summarize_full(j)
    assert ss.value >= 5
    assert cs._is_viable(ss)
    assert ss.file_references == 1
    assert ss.test_commands == 1
    assert ss.tool_calls == 2


def test_long_prompt_bonus():
    w = "design architecture implement feature " * 15
    j = _jl([{"type": "user", "isSidechain": False,
              "message": {"content": [{"type": "text", "text": w}],
                          "role": "user"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    _, ss = cs.summarize_full(j)
    assert ss.value == 3


# ===================== Grades =====================

def test_grades():
    assert cs._score_summary(cs.SubstanceScore(0, 0, 0, 0, 0, 0, "", False)) == "empty"
    assert cs._score_summary(cs.SubstanceScore(2, 1, 1, 0, 0, 0, "", True)) == "probe"
    assert cs._score_summary(cs.SubstanceScore(6, 3, 2, 1, 0, 0, "", True)) == "light"
    assert cs._score_summary(cs.SubstanceScore(15, 5, 3, 3, 2, 1, "", True)) == "moderate"
    assert cs._score_summary(cs.SubstanceScore(20, 8, 4, 5, 3, 2, "", True)) == "substantive"


# ===================== Viability gates =====================

def test_viability_zero_score():
    ss = cs.SubstanceScore(0, 0, 0, 0, 0, 0, "", False)
    assert not cs._is_viable(ss)


def test_viability_no_user_messages():
    ss = cs.SubstanceScore(5, 2, 0, 2, 1, 0, "", True)
    assert not cs._is_viable(ss)


def test_viability_no_concrete_prompt():
    ss = cs.SubstanceScore(3, 2, 1, 1, 0, 0, "", False)
    assert not cs._is_viable(ss)


def test_viability_no_work_evidence():
    """Tool calls=0 and messages<3: no evidence of work done."""
    ss = cs.SubstanceScore(2, 2, 1, 0, 0, 0, "", True)
    assert not cs._is_viable(ss)


def test_viability_happy_path():
    ss = cs.SubstanceScore(8, 3, 2, 3, 1, 1, "", True)
    assert cs._is_viable(ss)


# ===================== Timestamp ordering =====================

def test_sort_key_parsed_timestamp():
    """Parsed ISO timestamp should drive sort, not mtime."""
    s1 = cs.SessionSummary(Path("a.jsonl"), "id1", "/tmp", "main",
                           "2026-06-15T10:00:00Z", "", "", 5, 999999999.0)
    s2 = cs.SessionSummary(Path("b.jsonl"), "id2", "/tmp", "main",
                           "2026-07-01T10:00:00Z", "", "", 5, 1.0)
    assert cs._sort_key(s2) > cs._sort_key(s1)


def test_sort_key_mtime_fallback():
    s = cs.SessionSummary(Path("a.jsonl"), "id1", "/tmp", "main",
                          "", "", "", 5, 1750000000.0)
    assert cs._sort_key(s) == 1750000000.0


# ===================== Evidence extraction =====================

def test_evidence_basic():
    j = _jl([{"type": "assistant", "isSidechain": False,
              "message": {"content": [
                  {"type": "tool_use", "name": "Write", "id": "t1",
                   "input": {"filePath": "/tmp/t/foo.py"}},
                  {"type": "tool_use", "name": "Read", "id": "t2",
                   "input": {"filePath": "/tmp/t/bar.py"}},
                  {"type": "tool_use", "name": "Bash", "id": "t3",
                   "input": {"command": "echo done"}},
              ], "role": "assistant"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    ev = cs._extract_evidence(cs._records(j))
    assert set(ev["tool_calls"]) == {"Write", "Read", "Bash"}
    assert "/tmp/t/foo.py" in ev["files_modified"]
    assert ev["tests_run"] == []


def test_test_detection():
    j = _jl([{"type": "assistant", "isSidechain": False,
              "message": {"content": [
                  {"type": "tool_use", "name": "Bash", "id": "t1",
                   "input": {"command": "npm run test -- --coverage"}},
                  {"type": "tool_use", "name": "Bash", "id": "t2",
                   "input": {"command": "cargo test --all"}},
              ], "role": "assistant"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    ev = cs._extract_evidence(cs._records(j))
    assert len(ev["tests_run"]) == 2


def test_plan_detection():
    j = _jl([{"type": "assistant", "isSidechain": False,
              "message": {"content": [
                  {"type": "tool_use", "name": "Write", "id": "t1",
                   "input": {"filePath": "/tmp/t/docs/architecture/SYSTEM.md"}},
                  {"type": "tool_use", "name": "Read", "id": "t2",
                   "input": {"filePath": "/tmp/t/cool_plan_v3.md"}},
              ], "role": "assistant"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    ev = cs._extract_evidence(cs._records(j))
    assert len(ev["plans_or_specs"]) == 2


def test_skip_sidechain():
    j = _jl([{"type": "assistant", "isSidechain": True,
              "message": {"content": [
                  {"type": "tool_use", "name": "Bash", "id": "t1",
                   "input": {"command": "bad"}},
              ], "role": "assistant"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    ev = cs._extract_evidence(cs._records(j))
    assert ev["commands"] == []


# ===================== Redaction =====================

def test_redact_key_value():
    t = "ApiKey=abc123"
    r = cs._redact(t)
    assert "ApiKey=[REDACTED]" in r
    assert "abc123" not in r


def test_redact_env():
    t = "export API_KEY=sk-abc123xyz456"
    r = cs._redact(t)
    assert "sk-abc123" not in r
    assert "API_KEY=[REDACTED]" in r


def test_redact_token_value():
    r = cs._redact("ghp_abc123def456ghi789jkl012")
    assert "ghp_abc123" not in r
    assert "[REDACTED_TOKEN]" in r


def test_redact_pkey():
    t = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQE...\n-----END RSA PRIVATE KEY-----"
    r = cs._redact(t)
    assert "MIIEpA" not in r
    assert "[REDACTED_PRIVATE_KEY]" in r


# ===================== Malformed JSONL =====================

def test_malformed_jsonl():
    j = _jl([{"type": "user", "isSidechain": False,
              "message": {"content": [{"type": "text",
                          "text": "fix this please and thank you very much"}],
                          "role": "user"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    with open(j, "a") as f:
        f.write("NOT VALID JSON {{{{\n")
        f.write(json.dumps({"type": "assistant", "isSidechain": False,
                "message": {"content": [{"type": "text", "text": "ok"}],
                            "role": "assistant"},
                "timestamp": "2026-01-01T00:00:02Z",
                "cwd": "/tmp/t", "gitBranch": "main"}) + "\n")
    s, ss = cs.summarize_full(j)
    assert s is not None
    assert s.messages >= 1


# ===================== Backward compat =====================

def test_backward_compat():
    j = _jl([{"type": "user", "isSidechain": False,
              "message": {"content": [{"type": "text",
                          "text": "Refactor the storage layer to use adapter"}],
                          "role": "user"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "my-branch"}])
    o = cs.summarize(j)
    n, _ = cs.summarize_full(j)
    for f in ("session_id", "cwd", "branch", "timestamp", "title",
              "first_prompt", "messages"):
        assert getattr(o, f) == getattr(n, f), f"Mismatch on {f}"


def test_ai_title():
    j = _jl([{"type": "ai-title", "aiTitle": "Deploy R2",
              "isSidechain": False,
              "cwd": "/tmp/t", "gitBranch": "main",
              "timestamp": "2026-01-01T00:00:00Z"},
             {"type": "user", "isSidechain": False,
              "message": {"content": [{"type": "text",
                          "text": "deploy right now please"}],
                          "role": "user"},
              "timestamp": "2026-01-01T00:00:01Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    s, _ = cs.summarize_full(j)
    assert s.title == "Deploy R2"


def test_dedup():
    j = _jl([{"type": "assistant", "isSidechain": False,
              "message": {"content": [
                  {"type": "tool_use", "name": "Read", "id": "t1",
                   "input": {"filePath": "/tmp/t/foo.py"}},
                  {"type": "tool_use", "name": "Read", "id": "t2",
                   "input": {"filePath": "/tmp/t/foo.py"}},
              ], "role": "assistant"},
              "timestamp": "2026-01-01T00:00:00Z",
              "cwd": "/tmp/t", "gitBranch": "main"}])
    ev = cs._extract_evidence(cs._records(j))
    assert ev["files_read"] == ["/tmp/t/foo.py"]


# ===================== CLI integration =====================

def test_list_json_output():
    r = _run("list", str(Path.home()), "--branch", "HEAD", "--json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert len(data) >= 2
    assert all("substance" in s for s in data)


def test_groups_includes_newest_viable():
    r = _run("groups", "--json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert all("newest_viable_id" in g for g in data)
    assert all("newest_viable_score" in g for g in data)
    assert all("highest_score_id" in g for g in data)


def test_groups_skip_empty():
    r = _run("groups", "--skip-empty", "--json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert all(g["latest_viable"] for g in data)


def test_extract_nonviable_rejected():
    # HEAD group's latest is a probe
    r = _run("extract", "latest", "--worktree", str(Path.home()))
    assert r.returncode == 2
    assert "not viable" in r.stderr


def test_extract_nonviable_override():
    r = _run("extract", "latest", "--worktree", str(Path.home()),
             "--allow-nonviable")
    assert r.returncode == 0
    assert r.stdout.strip().endswith(".md")


def test_extract_exact_id_viable():
    r = _run("extract", "465cbbf7", "--worktree", str(Path.home()))
    assert r.returncode == 0
    fpath = r.stdout.strip()
    assert fpath.endswith(".md")
    content = Path(fpath).read_text()
    assert "Implementation Evidence" in content or "Conversation" in content


# ============ Bounded conversation extraction ============

def test_bounded_turns_empty():
    turns, omissions = cs._bounded_turns([], 10000)
    assert turns == []
    assert omissions == []


def test_bounded_turns_first_objective_always_retained():
    """First substantive user turn of >=50 chars is always retained."""
    turns_list = [
        ("user", "t1", "A" * 55),
        ("assistant", "t2", "short"),
        ("user", "t3", "more text"),
    ]
    selected, _ = cs._bounded_turns(turns_list, 500)
    assert any(r == "user" and "A" * 55 in txt for r, _, txt in selected)


def test_bounded_turns_newest_fill_budget():
    """After first objective, newest turns fill the remaining char budget."""
    objective = "X" * 60
    turns_list = [
        ("user", "t1", objective),
        ("assistant", "t2", "Y" * 100),
        ("user", "t3", "Z" * 100),
        ("assistant", "t4", "W" * 100),
    ]
    selected, omissions = cs._bounded_turns(turns_list, 300)
    assert any(r == "user" and ts == "t1" for r, ts, _ in selected)
    assert any(r == "assistant" and ts == "t4" for r, ts, _ in selected)
    assert any(r == "user" and ts == "t3" for r, ts, _ in selected)
    assert any("omitted" in o for o in omissions)


def test_bounded_turns_truncation_marker():
    """Turns exceeding MAX_TURN_CHARS get truncated with [truncated...]."""
    big = "L" * 5000
    selected, omissions = cs._bounded_turns(
        [("user", "t1", big)], 8000
    )
    assert "[truncated...]" in selected[0][2]
    assert any("truncated" in o for o in omissions)


def test_bounded_turns_omission_count():
    """Omitted turns produce N turns omitted (budget) marker."""
    obj = "Need design help with a complex multi-system integration feature"
    others = [
        ("assistant", "t{}".format(i), "reply") for i in range(20)
    ]
    turns_list = [("user", "t0", obj)] + others
    _, omissions = cs._bounded_turns(turns_list, 500)
    assert any("omitted" in o.lower() for o in omissions)


# ============ Evidence caps with overflow tracking ============

def test_evidence_tool_calls_bounded():
    """Tool calls capped at _MAX_EVIDENCE_TOOLS with overflow tracked."""
    records = [
        {
            "type": "assistant", "isSidechain": False,
            "message": {
                "content": [
                    {"type": "tool_use", "name": "T{}".format(i),
                     "id": "x{}".format(i), "input": {}}
                ], "role": "assistant"
            },
            "timestamp": "2026-01-01T00:00:00Z",
            "cwd": "/tmp/t", "gitBranch": "main",
        }
        for i in range(50)
    ]
    ev = cs._extract_evidence(records)
    assert len(ev["tool_calls"]) == cs._MAX_EVIDENCE_TOOLS
    assert ev.get("_tool_calls_capped", 0) > 0


def test_evidence_commands_bounded():
    records = [
        {
            "type": "assistant", "isSidechain": False,
            "message": {
                "content": [
                    {"type": "tool_use", "name": "Bash", "id": "x{}".format(i),
                     "input": {"command": "echo {}".format(i)}}
                ], "role": "assistant"
            },
            "timestamp": "2026-01-01T00:00:00Z",
            "cwd": "/tmp/t", "gitBranch": "main",
        }
        for i in range(30)
    ]
    ev = cs._extract_evidence(records)
    assert len(ev["commands"]) <= cs._MAX_EVIDENCE_COMMANDS


def test_evidence_files_read_bounded():
    records = [
        {
            "type": "assistant", "isSidechain": False,
            "message": {
                "content": [
                    {"type": "tool_use", "name": "Read", "id": "x{}".format(i),
                     "input": {"filePath": "/tmp/f{}.py".format(i)}}
                ], "role": "assistant"
            },
            "timestamp": "2026-01-01T00:00:00Z",
            "cwd": "/tmp/t", "gitBranch": "main",
        }
        for i in range(30)
    ]
    ev = cs._extract_evidence(records)
    assert len(ev["files_read"]) <= cs._MAX_EVIDENCE_FILES_READ


def test_evidence_files_modified_bounded():
    records = [
        {
            "type": "assistant", "isSidechain": False,
            "message": {
                "content": [
                    {"type": "tool_use", "name": "Write", "id": "x{}".format(i),
                     "input": {"filePath": "/tmp/f{}.ts".format(i)}}
                ], "role": "assistant"
            },
            "timestamp": "2026-01-01T00:00:00Z",
            "cwd": "/tmp/t", "gitBranch": "main",
        }
        for i in range(40)
    ]
    ev = cs._extract_evidence(records)
    assert len(ev["files_modified"]) <= cs._MAX_EVIDENCE_FILES_MOD


# ============ Completion gate ============

def test_completion_gate_passes_when_all_present():
    turns = [
        ("user", "t1", "Write comprehensive test suite for the API layer covering edge"),
        ("assistant", "t2", "Done, tests at expected location."),
    ]
    evidence = {"tool_calls": ["Write"], "files_modified": ["/tmp/x.py"]}
    ok, missing = cs._completion_gate(turns, evidence)
    assert ok
    assert missing == []


def test_completion_gate_no_objective():
    turns = [("user", "t1", "ok"), ("assistant", "t2", "done")]
    evidence = {"tool_calls": ["Write"]}
    ok, missing = cs._completion_gate(turns, evidence)
    assert not ok
    assert any("objective" in m.lower() for m in missing)


def test_completion_gate_no_work_evidence():
    turns = [
        ("user", "t1", "Write comprehensive test suite for API layer"),
        ("assistant", "t2", "ok."),
    ]
    evidence = {}
    ok, missing = cs._completion_gate(turns, evidence)
    assert not ok
    assert any("work" in m.lower() for m in missing)


def test_completion_gate_no_next_action():
    turns = [
        ("user", "t1", "Write comprehensive test suite for the API layer"),
    ]
    evidence = {"tool_calls": ["Read"]}
    ok, missing = cs._completion_gate(turns, evidence)
    assert not ok
    assert any("next action" in m.lower() for m in missing)


# ============ Diagnostic extraction ============

def test_nonviable_diagnostic_label_in_file():
    """Nonviable --allow-nonviable produces Diagnostic Extraction header."""
    j = _jl([
        {
            "type": "user", "isSidechain": False,
            "message": {
                "content": [
                    {"type": "text",
                     "text": "Write comprehensive test suite for the API layer"}
                ], "role": "user"
            },
            "timestamp": "2026-01-01T00:00:00Z",
            "cwd": "/tmp/t", "gitBranch": "main",
        }
    ])
    r = _run("extract", str(j), "--allow-nonviable")
    assert r.returncode == 0
    assert "diagnostic" in r.stderr.lower() or "nonviable" in r.stderr.lower()
    fpath = r.stdout.strip()
    content = Path(fpath).read_text()
    assert "Diagnostic Extraction" in content or "NOT a standard handoff" in content


# ============ --max-chars ============

def test_max_chars_flag_accepted():
    r = _run("extract", "465cbbf7", "--worktree", str(Path.home()),
             "--max-chars", "10000")
    assert r.returncode == 0
    assert r.stdout.strip().endswith(".md")


# ============ Nonviable wording ============

def test_nonviable_message_includes_diagnostic():
    """Rejection stderr mentions diagnostic nature, not just bypass."""
    r = _run("extract", "latest", "--worktree", str(Path.home()))
    assert r.returncode == 2
    assert "not viable" in r.stderr.lower()
    assert "diagnostic" in r.stderr.lower()


if __name__ == "__main__":
    import traceback
    funcs = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    passed = 0
    failed = 0
    for f in funcs:
        try:
            f()
            passed += 1
            print(f"  PASS {f.__name__}")
        except Exception:
            failed += 1
            tb = traceback.format_exc()
            print(f"  FAIL {f.__name__}: {tb.split(chr(10))[-3:-1]}")
    print(f"\n{passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
