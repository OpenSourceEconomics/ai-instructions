#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook: Enforce pixi-wrapped commands.

Rejects bare python/python3/pytest/ruff commands and suggests pixi alternatives.
"""

import json
import re
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_name = data.get("tool_name")
tool_input = data.get("tool_input", {})

if tool_name != "Bash":
    sys.exit(0)

cmd = tool_input.get("command", "").strip()


def deny(reason):
    """Output denial JSON and exit."""
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(result))
    sys.exit(0)


# Check for bare python/python3
if re.match(r"^python3?\s", cmd):
    deny("Use `pixi run python` instead of bare `python` or `python3`")

# Check for bare pytest (not already wrapped in pixi run)
if re.match(r"^pytest\s", cmd) or cmd == "pytest":
    deny("Use `pixi run tests` or `pixi run -e test-cpu pytest ...`")

# Check for bare ruff
if re.match(r"^ruff\s", cmd) or cmd == "ruff":
    deny("Use `prek run --all-files` instead of bare `ruff`")

# Check for bare ty/mypy/pyright
if re.match(r"^(ty|mypy|pyright)\s", cmd) or cmd in ("ty", "mypy", "pyright"):
    deny("Use `pixi run ty` instead of bare type checker commands")

# No issues found, let it through (other hooks will handle approval)
sys.exit(0)
