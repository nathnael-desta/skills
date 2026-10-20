#!/usr/bin/env python3
"""PreToolUse guard for Browser Control calls (Bash CLI/bcx and the MCP execute tool).

Blocks only what breaks things, not style choices:
- bringToFront / CDP recording aimed at the user's own Chrome (port 19989): they
  raise the window and steal desktop focus. Harmless in the headless agent browser.
- waiting for downloads on any relay: unsupported through the extension in 0.8.4
  and crashes the relay.
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
users_chrome = re.search(r"BROWSER_CONTROL_PORT=[\"']?19989\b", text) is not None
if users_chrome and re.search(r"bringToFront", text):
    problems.append("bringToFront raises the user's Chrome and steals their focus; screenshots and clicks work without it")
if users_chrome and re.search(r"--mode\s+cdp|\bmode[\"']?\s*[:=]\s*[\"']?cdp\b", text):
    problems.append("CDP recording calls Page.bringToFront and steals the user's focus; record in the agent browser (port 19990) instead")
if re.search(r"waitForEvent\(\s*[\"']download", text):
    problems.append("downloads are unsupported through the extension and this crashes the relay; fetch the bytes in page.evaluate and write them with fs")

if problems:
    print("Browser Control guard blocked this call:\n- " + "\n- ".join(problems), file=sys.stderr)
    sys.exit(2)
sys.exit(0)
