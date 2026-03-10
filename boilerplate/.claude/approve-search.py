#!/usr/bin/env python3
"""Claude Code PreToolUse Hook: Auto-approve Search in current directory tree.

Approves the Search tool when operating within the current working directory.
"""

import json
import os
import sys
from pathlib import Path

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    sys.exit(0)

tool_name = data.get("tool_name")
tool_input = data.get("tool_input", {})

if tool_name != "Search":
    sys.exit(0)

# Check if the search path is within the current directory tree
cwd = os.path.realpath(Path.cwd())
search_path = tool_input.get("path", cwd)
search_path = os.path.realpath(search_path)

if not search_path.startswith(cwd):
    sys.exit(0)  # Outside current directory tree, don't auto-approve

result = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": f"Search within current directory tree: {cwd}",
    }
}
print(json.dumps(result))
