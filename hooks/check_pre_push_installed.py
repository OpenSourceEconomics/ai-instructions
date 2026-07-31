#!/usr/bin/env python3
"""Fail if the config declares pre-push hooks but none are installed in this clone.

`prek install` only wires up the pre-commit stage. Any hook declared with
`stages: [pre-push]` stays dormant until someone additionally runs
`prek install -t pre-push`, and a dormant hook is worse than no hook: the config
looks like the check is running when it never fires. This runs at pre-commit
stage, so the omission surfaces on the first commit rather than after a bad push.
"""

import subprocess
import sys
from pathlib import Path

CONFIG = Path(".pre-commit-config.yaml")
MARKERS = ("prek", "pre-commit")


def _hooks_dir() -> Path | None:
    """Return the directory git reads hooks from, honoring `core.hooksPath`."""
    configured = _git("config", "--get", "core.hooksPath")
    if configured:
        return Path(configured)
    common = _git("rev-parse", "--git-common-dir")
    return Path(common) / "hooks" if common else None


def _git(*args: str) -> str:
    """Run a git command, returning stripped stdout or "" if it fails."""
    try:
        # S603/S607: the executable is the literal "git", resolved from PATH so
        # the hook works wherever git is installed, and every argument is a
        # constant from this module; nothing here comes from user input.
        result = subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def main() -> int:
    """Check that a managed pre-push hook exists when the config needs one."""
    if not CONFIG.is_file() or "pre-push" not in CONFIG.read_text(encoding="utf-8"):
        return 0

    hooks_dir = _hooks_dir()
    if hooks_dir is None:
        return 0

    hook = hooks_dir / "pre-push"
    if hook.is_file() and any(
        marker in hook.read_text(encoding="utf-8", errors="replace")
        for marker in MARKERS
    ):
        return 0

    print(
        f"{CONFIG} declares pre-push hooks, but {hook} is missing or not managed.\n"
        "Those hooks are silently not running. Install them once per clone:\n\n"
        "    prek install -t pre-push\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
