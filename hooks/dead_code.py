#!/usr/bin/env python3
"""Refuse code that nothing outside the test suite calls.

Configured in the project's `pyproject.toml`:

```toml
[tool.dead-code]
consumers = ["src", "docs"]  # code whose uses count, besides the tests
internal = ["src/_project/"]  # report every unused definition here
public = ["src/project/"]  # report only `_`-private unused definitions here
tests = "tests"  # optional; the default is "tests"
registering-decorators = ["@rule", "@app.*"]  # optional; globs

[[tool.dead-code.allow]]
path = "src/_project/visitors.py"  # glob
name = "visit_*"  # glob
reason = "ast.NodeVisitor dispatches visit_<NodeClass> by name."
```

Two vulture runs over the repository:

- Without the tests: a function, method, property or class under `internal`, or a
  `_`-private one under `public`, that no consumer uses is orphaned. Code whose only
  callers are tests counts as orphaned too: either it moves into the test suite or it
  goes.
- With the tests: an unused function, method, property or class in the tests is
  orphaned.

Public names under `public` are the API and are not reported. Variables and attributes
are not reported (dataclass and record fields are read by name at runtime), nor are
imports (ruff's F401 covers them). vulture reads `.py` files only, so a use that exists
only in a notebook is invisible.

A function that a decorator hands to a registry, a loader or a DAG is used through that
decorator and never by name. Name such decorators in `registering-decorators`, as
vulture writes them (`@` plus the dotted name, globs allowed); whatever carries one
counts as used.

A definition inside a `with pytest.raises(...)` or `with pytest.warns(...)` block is
not reported: defining it is the test, since the decorator or class body is what raises.

Any other use that vulture cannot see, such as a protocol method called through an
instance it cannot type or a pytest hook, is declared as an `allow` entry with its
reason. An entry that no longer matches anything is itself a violation,
so the allowlist cannot outlive the code it excuses.
"""

import ast
import fnmatch
import functools
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import vulture

PYPROJECT = Path("pyproject.toml")
KINDS = frozenset({"function", "method", "property", "class"})


@dataclass(frozen=True, kw_only=True)
class Config:
    """The `[tool.dead-code]` table of a project."""

    consumers: tuple[str, ...]
    """Paths whose uses count, besides the tests."""
    internal: tuple[str, ...]
    """Path prefixes under which every unused definition is reported."""
    public: tuple[str, ...]
    """Path prefixes under which only `_`-private unused definitions are reported."""
    tests: str
    """The test directory."""
    registering_decorators: tuple[str, ...]
    """Globs of decorators whose targets count as used."""
    allow: tuple["AllowEntry", ...]
    """Uses vulture cannot see."""


@dataclass(frozen=True, kw_only=True)
class Orphan:
    """One unused definition, located by repository-relative path."""

    path: str
    """Repository-relative POSIX path of the defining file."""
    line: int
    """Line of the definition."""
    kind: str
    """vulture's kind: function, method, property or class."""
    name: str
    """Name of the definition."""
    test_only: bool
    """Whether only the tests use it."""


@dataclass(frozen=True, kw_only=True)
class AllowEntry:
    """An allowlisted use vulture cannot see; `path` and `name` are globs."""

    path: str
    """Glob matched against the repository-relative path."""
    name: str
    """Glob matched against the definition's name."""
    reason: str
    """Why the use is invisible to vulture."""

    def matches(self, orphan: Orphan) -> bool:
        """Return whether this entry excuses `orphan`."""
        return fnmatch.fnmatchcase(orphan.name, self.name) and fnmatch.fnmatch(
            orphan.path, self.path
        )


def main() -> int:
    """Print every violation and return a non-zero status if there is one."""
    root = Path.cwd()
    config = load_config(path=root / PYPROJECT)
    messages = check(root=root, config=config)
    for message in messages:
        print(message)
    if messages:
        print(
            f"\n{len(messages)} dead-code violation(s). Delete the code, move code "
            "used only by tests into the test suite, or declare a use vulture "
            "cannot see as a `[[tool.dead-code.allow]]` entry with its reason."
        )
    return 1 if messages else 0


def load_config(*, path: Path) -> Config:
    """Read `[tool.dead-code]`; every allow entry must name a path, name and reason."""
    table = tomllib.loads(path.read_text(encoding="utf-8")).get("tool", {})
    if "dead-code" not in table:
        msg = f"{path} has no [tool.dead-code] table; see this hook's docstring."
        raise SystemExit(msg)
    table = table["dead-code"]
    _fail_if_nothing_in_scope(table=table, path=path)
    return Config(
        consumers=tuple(table.get("consumers", ["src"])),
        internal=tuple(table.get("internal", [])),
        public=tuple(table.get("public", [])),
        tests=table.get("tests", "tests"),
        registering_decorators=tuple(table.get("registering-decorators", [])),
        allow=tuple(_allow_entry(entry) for entry in table.get("allow", [])),
    )


def check(*, root: Path, config: Config) -> list[str]:
    """Return one message per unexcused orphan and per stale allowlist entry."""
    orphans = find_orphans(root=root, config=config)
    messages = [
        f"{o.path}:{o.line}: unused {o.kind} {o.name!r}"
        + (" (used only by tests)" if o.test_only else "")
        for o in orphans
        if not any(entry.matches(o) for entry in config.allow)
    ]
    messages.extend(
        f"dead-code allow entry {entry.path}::{entry.name} matches nothing; remove it."
        for entry in config.allow
        if not any(entry.matches(o) for o in orphans)
    )
    return messages


def find_orphans(*, root: Path, config: Config) -> list[Orphan]:
    """Return every orphaned definition under `root`, test-only ones marked."""
    without_tests = _unused(root=root, paths=config.consumers, config=config)
    with_tests = set(
        _unused(root=root, paths=(*config.consumers, config.tests), config=config)
    )
    orphans = [
        Orphan(
            path=path,
            line=line,
            kind=kind,
            name=name,
            test_only=(path, line, kind, name) not in with_tests,
        )
        for path, line, kind, name in without_tests
        if _in_scope(path=path, name=name, config=config)
    ]
    orphans.extend(
        Orphan(path=path, line=line, kind=kind, name=name, test_only=False)
        for path, line, kind, name in with_tests
        if path.startswith(f"{config.tests}/")
    )
    return sorted(orphans, key=lambda o: (o.path, o.line))


def _unused(
    *, root: Path, paths: tuple[str, ...], config: Config
) -> list[tuple[str, int, str, str]]:
    """Return `(path, line, kind, name)` for vulture's unused definitions."""
    # pytest resolves fixtures by parameter name or `name=` alias, or applies them
    # with `autouse=True`; vulture sees none of these.
    scanner = vulture.Vulture(
        ignore_decorators=["@pytest.fixture", *config.registering_decorators]
    )
    scanner.scavenge([str(root / p) for p in paths if (root / p).exists()])
    if scanner.exit_code != vulture.core.ExitCode.NoDeadCode:
        # A file vulture cannot parse is skipped, and every use inside it is lost.
        msg = "vulture could not read every file; see its message above."
        raise SystemExit(msg)
    return [
        (
            Path(item.filename).resolve().relative_to(root.resolve()).as_posix(),
            item.first_lineno,
            item.typ,
            item.name,
        )
        for item in scanner.get_unused_code(min_confidence=0)
        # A dunder is called by the data model, never by name.
        if item.typ in KINDS
        and not (item.name.startswith("__") and item.name.endswith("__"))
        and not any(
            first <= item.first_lineno <= last
            for first, last in _expected_failure_blocks(str(item.filename))
        )
    ]


@functools.cache
def _expected_failure_blocks(filename: str) -> tuple[tuple[int, int], ...]:
    """Return the line spans of `with pytest.raises/warns(...)` blocks in a file."""
    tree = ast.parse(Path(filename).read_text(encoding="utf-8"))
    return tuple(
        (node.lineno, node.end_lineno or node.lineno)
        for node in ast.walk(tree)
        if isinstance(node, ast.With)
        and any(
            isinstance(item.context_expr, ast.Call)
            and ast.unparse(item.context_expr.func) in {"pytest.raises", "pytest.warns"}
            for item in node.items
        )
    )


def _in_scope(*, path: str, name: str, config: Config) -> bool:
    """Return whether a definition unused outside the tests is reported."""
    if path.startswith(config.internal):
        return True
    return path.startswith(config.public) and name.startswith("_")


def _allow_entry(entry: dict[str, str]) -> AllowEntry:
    """Build an allow entry, refusing one without a reason."""
    if not entry.get("reason", "").strip():
        msg = f"[[tool.dead-code.allow]] entry {entry} has no reason."
        raise SystemExit(msg)
    return AllowEntry(path=entry["path"], name=entry["name"], reason=entry["reason"])


def _fail_if_nothing_in_scope(*, table: dict, path: Path) -> None:
    """Refuse a configuration under which no source definition can be reported."""
    if not table.get("internal") and not table.get("public"):
        msg = (
            f"[tool.dead-code] in {path} sets neither `internal` nor `public`, so "
            "no source definition would ever be reported."
        )
        raise SystemExit(msg)


if __name__ == "__main__":
    sys.exit(main())
