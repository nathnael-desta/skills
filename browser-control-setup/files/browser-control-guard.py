#!/usr/bin/env python3
"""PreToolUse guard for Browser Control calls (Bash CLI/bcx and the MCP execute tool).

Blocks patterns the usage audit (2026-10-20) found costly or disruptive:
bringToFront / CDP recording (steal desktop focus), long waitForTimeout sleeps
(~45 min of pure sleep in a month), and waiting for downloads (crashes the relay).
Exit 2 + stderr tells the agent why, so it can rewrite the call.
"""
import json
import re
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = data.get("tool_name", "")
inp = data.get("tool_input") or {}

if tool == "Bash":
    text = inp.get("command", "")
    # Only actual invocations, not greps or notes that mention the tool.
    if not re.search(r"(?:^|[\s;&|(`])(?:browser-control\s+(?:execute|recording)|bcx)\s", text):
        sys.exit(0)
elif tool.startswith("mcp__browser-control__"):
    text = " ".join(f"{k}: {v}" for k, v in inp.items() if isinstance(v, (str, int, float)))
else:
    sys.exit(0)

problems = []
if re.search(r"bringToFront", text):
    problems.append("bringToFront raises Chrome and steals the user's focus; screenshots and clicks work without it")
if re.search(r"--mode\s+cdp|\bmode[\"']?\s*[:=]\s*[\"']?cdp\b", text):
    problems.append("CDP recording calls Page.bringToFront and steals focus; record another way or skip it")
for ms in re.findall(r"waitForTimeout\(\s*(\d[\d_]*)", text):
    if int(ms.replace("_", "")) > 1000:
        problems.append(f"waitForTimeout({ms}) is a blind sleep; wait for a condition (waitFor, waitForURL, waitForResponse) instead. Settles up to 1000 ms are allowed")
        break
if re.search(r"waitForEvent\(\s*[\"']download", text):
    problems.append("downloads are unsupported through the extension and this crashes the relay; fetch the bytes in page.evaluate and write them with fs")

if problems:
    print("Browser Control guard blocked this call:\n- " + "\n- ".join(problems), file=sys.stderr)
    sys.exit(2)
sys.exit(0)
