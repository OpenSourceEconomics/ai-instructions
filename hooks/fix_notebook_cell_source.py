#!/usr/bin/env python3
"""Normalize notebook cell `source` and stream output `text` to arrays of lines.

Jupyter's schema allows either a single string or an array of lines, and editing
tools regularly emit the single-string form. It round-trips to an array as soon as
any standard tool touches the file, and until then the whole cell shows up as one
changed line in a diff — unreviewable. This rewrites the single-string form in
place and exits non-zero when it changed anything, the way a formatter hook does.
"""

import json
import sys
from pathlib import Path


def _to_lines(value: str | list[str]) -> list[str] | None:
    """Return `value` split into keepends lines, or None if already a list."""
    if isinstance(value, list):
        return None
    return value.splitlines(keepends=True)


def _normalize_notebook(notebook: dict) -> bool:
    """Rewrite single-string sources/texts in `notebook`. Return whether it changed."""
    changed = False
    for cell in notebook.get("cells", []):
        lines = _to_lines(cell.get("source", []))
        if lines is not None:
            cell["source"] = lines
            changed = True
        for output in cell.get("outputs", []):
            if "text" not in output:
                continue
            lines = _to_lines(output["text"])
            if lines is not None:
                output["text"] = lines
                changed = True
    return changed


def main(paths: list[str]) -> int:
    """Normalize every notebook in `paths`; return 1 if any file was rewritten."""
    failed = False
    for name in paths:
        path = Path(name)
        try:
            notebook = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            print(f"{path}: could not parse as JSON: {error}")
            failed = True
            continue
        if _normalize_notebook(notebook):
            path.write_text(
                json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"{path}: rewrote single-string cell source/text as line arrays")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
