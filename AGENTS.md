@modules/pandas.md @modules/numpy.md @modules/jax.md @modules/optimagic.md
@modules/project-structure.md @modules/pytask.md @modules/plotting.md
@modules/ml-econometrics.md @modules/dags.md

# AI Coding Standards

Guidelines for AI agents, mostly derived from
[Effective Programming Practices for Economists](https://effective-programming-practices.vercel.app/).

______________________________________________________________________

# Critical Rules

## Type Hints

**Always use type hints in all function signatures.** This is mandatory.

```python
def calculate_utility(consumption: float, gamma: float = 1.5) -> float:
    return consumption ** (1 - gamma) / (1 - gamma)


def clean_data(raw: pd.DataFrame) -> pd.DataFrame: ...


def load_config(path: Path) -> dict[str, Any]: ...
```

- Do NOT use `from __future__ import annotations` in Python 3.14+ projects — PEP 649
  deferred evaluation makes it unnecessary and it changes runtime annotation semantics.
  For projects supporting < 3.14, use it for forward references.
- Prefer `X | None` over `Optional[X]` in Python 3.10+
- Use `collections.abc` for abstract types: `Sequence`, `Mapping`, `Iterable`

## Immutability

**Prefer immutable data structures throughout.** This prevents bugs and enables safer
concurrent code.

### Frozen Dataclasses

Use `@dataclass(frozen=True)` for all configuration and state objects:

```python
from dataclasses import dataclass, field
from types import MappingProxyType


@dataclass(frozen=True)
class ModelConfig:
    n_periods: int
    """Number of time periods."""
    n_states: int
    """Number of discrete states per period."""
    discount_factor: float = 0.95
    """Subjective discount factor."""

    @property
    def n_total(self) -> int:
        return self.n_periods * self.n_states
```

### Immutable Collections

- Use `tuple` instead of `list` for sequences
- Use `MappingProxyType` instead of `dict`
- Use `frozenset` instead of `set`

```python
from types import MappingProxyType


@dataclass(frozen=True)
class Labels:
    factors: tuple[str, ...]  # Not list[str]
    mappings: MappingProxyType[str, int]  # Not dict[str, int]


# For read-only dict views
def ensure_immutable[K, V](d: dict[K, V]) -> MappingProxyType[K, V]:
    return MappingProxyType(d)
```

### Immutable Update Pattern

Use `with_*` methods or `dataclasses.replace()` to create modified copies:

```python
from dataclasses import replace


@dataclass(frozen=True)
class Config:
    alpha: float
    beta: float

    def with_alpha(self, alpha: float) -> Self:
        return replace(self, alpha=alpha)


# Usage
new_config = config.with_alpha(0.5)
```

### NewType for Domain Safety

Use `NewType` to distinguish semantically different values of the same type:

```python
from typing import NewType

Period = NewType("Period", int)
Age = NewType("Age", int)


def get_state(period: Period, age: Age) -> State: ...
```

### Enums for Categorical Values

Use `Enum` instead of string literals or boolean flags:

```python
from enum import Enum, auto


class FactorType(Enum):
    STATE = auto()
    ENDOGENOUS = auto()
    CONTROL = auto()
```

## File Paths

**Always use `pathlib.Path`** - never string paths.

```python
from pathlib import Path

root = Path(__file__).parent.parent
data_path = root / "datasets" / "data.csv"
```

Three rules:

1. Always use `pathlib.Path` objects instead of strings
1. Never hardcode absolute paths outside the project directory
1. Concatenate paths with `/` operator

## Floating Point Comparisons

Never use `==` for floats. Use tolerance-based comparison:

```python
# With NumPy/JAX
if np.isclose(result, 0.3):
    ...
```

______________________________________________________________________

# Python Environment

## Python Version

Minimum Python version is **3.14** unless a project specifies otherwise. Use 3.14+
features freely, including:

- `except ValueError, TypeError:` without parentheses (PEP 758) — this is **not** Python
  2 syntax. It is valid when there is no `as` clause.

## Pixi Package Manager

Pixi is the required package and environment manager.

**DO:**

- `pixi run python script.py` - execute Python scripts
- `pixi run pytest` - run tests
- `pixi run pytask` - run task pipeline
- `pixi add <package>` - add conda-forge dependencies
- `pixi add --pypi <package>` - add PyPI-only packages
- Commit `pixi.lock` for reproducibility

**DON'T:**

- Never use `pip install` or `conda install` directly
- Never run `python script.py` without `pixi run` prefix
- Never use the `defaults` conda channel

### Always re-lock before committing — and especially before pushing

**Whenever `pyproject.toml` changes in any way — a dependency added, removed, or
version-bumped, a git/URL pin updated, an environment or feature edited — run
`pixi lock` and commit the regenerated `pixi.lock` in the same commit.**

A stale `pixi.lock` passes locally but breaks CI, and the failure surfaces *only* after
you push:

- `pixi install --frozen` / `pixi list --frozen` (the locked CI jobs) fail outright.
- `pixi install` silently regenerates the lock and dirties the worktree, which blocks
  any task that refuses to run on a dirty tree (e.g. benchmarks).

So treat `pixi lock` as mandatory before `git commit`, and double-check it before
`git push` — pushing a stale lock burns a full CI cycle to discover a one-line fix.

## Package Structure

Use `src` layout:

```
project/
├── src/
│   └── package/
│       ├── __init__.py
│       └── module.py
├── tests/
└── pyproject.toml
```

______________________________________________________________________

# Code Quality

## Naming Conventions

- `lowercase_with_underscores` - functions, methods, variables
- `UPPERCASE_WITH_UNDERSCORES` - constants
- `CamelCase` - classes
- Function names start with verb: `create_`, `calculate_`, `convert_`, `get_`
- Private functions: `_underscore` prefix
- Use `func`, not `fn`, when abbreviating "function" (e.g., `apply_func`)
- Avoid: abbreviations, single letters (`n`, `c`, `s`, `u` conflict with debugger),
  built-in names (`list`, `dict`, `type`)
- Avoid vague action nouns like "sweep", "pass", "handler" in identifiers, comments, and
  docstrings unless paired with a concrete qualifier (e.g., "annotation-stripping
  pass"). Prefer the verb form (`resolve_*`) or a specific noun (`resolver`,
  `validator`) that says what the thing actually does.

## Module Layout

Write "deep" modules: important public function(s) at the top, private helpers below.
Readers should see the API first without scrolling past implementation details.

Never add decorative section-separator comments like:

```python
# ---------------------------------------------------------------------------
# Section name
# ---------------------------------------------------------------------------
```

Code structure should be self-evident from function names and ordering.

## Docstrings

Use **Google convention** (`pydocstyle.convention = "google"`). Use **MyST** syntax (not
reStructuredText) for markup inside docstrings: `` `code` ``, `$math$`, markdown links.

- Imperative mood in summary lines ("Calculate utility", not "Calculates utility")
- Use inline field docstrings (PEP 257) for dataclass attributes (see Frozen Dataclasses
  example above)

```python
def calculate_utility(consumption: float, gamma: float = 1.5) -> float:
    """Calculate CRRA utility.

    Args:
        consumption: Consumption level (must be positive).
        gamma: Coefficient of relative risk aversion.

    Returns:
        Utility value.

    """
    ...
```

## Docstring Style

Docstrings and inline comments describe the code's *current* state in user-facing terms.
The 9-month-without-PR-context reader is the audience: a docstring that survives that
test stays useful; one that rehearses the diff or the prior implementation rots
immediately.

This applies to **all** docstrings and comments — source and tests. For tests
specifically, see also the "Test docstrings — describe behavior, not history" subsection
in the Testing section.

### Describe state, not history

State what is true now. Don't reference prior designs, removed code, or what was
changed. Words like "earlier", "previously", "now", "formerly", "the old", "before the
fix" are red flags.

```python
# Good — forward-looking constraint
class _DiagnosticRow:
    """Metadata captured during the backward-induction loop.

    Holds only Python-scalar metadata — no device-array references —
    so every (regime, period) row stays at a few bytes regardless of
    grid size.
    """


# Bad — rehearses prior design
class _DiagnosticRow:
    """Metadata captured during the backward-induction loop.

    Holds only Python-scalar metadata. The earlier design captured
    state_action_space and a closure directly on each row, which
    pinned every period's V template in device memory until the
    post-loop flush.
    """
```

### No PR numbers, no model-specific magic numbers

PR references (`#334 removed the host stalls`, `the bug was fixed in #42`) rot as the
codebase evolves and provide no useful signal to a reader who isn't already in context.
Magic numbers tied to a specific model size or hardware
(`~2 MB at production grid sizes`, `fits on a 16 GB device`) imply a fixed scale that's
only true on whichever model/box the comment was written against. State the qualitative
dependency instead.

```python
# Good — qualitative dependency
# Frees per-period intermediate buffers (V_arr-shaped, so
# model-dependent) so they don't stack up across the loop.

# Bad — PR reference + magic number
# Frees per-period intermediate buffers (~2 MB each at production
# grid sizes) so we don't re-introduce the host stalls that #334
# removed.
```

### Bulleted lists for enumerated cases

When describing a fixed set of cases (log levels, regime kinds, parameter types,
dispatch strategies), use one bullet per case rather than running prose. Bullets scan;
prose hides cases.

```python
# Good — scannable
# Gate falls out of the public log level:
# - `"off"` ⇒ nothing (skips even the NaN fail-fast)
# - `"warning"` / `"progress"` ⇒ NaN/Inf only
# - `"debug"` ⇒ adds the min/max/mean trio


# Bad — buried in prose
# Gate falls out of the public log level: `"off"` ⇒ nothing,
# `"warning"` / `"progress"` ⇒ NaN/Inf only, `"debug"` ⇒ adds the
# min/max/mean trio. `"off"` skips even the NaN fail-fast.
```

## Pure Functions

Write pure functions whenever possible:

1. Same inputs → same outputs
1. No side effects

```python
# Good: Separate I/O from logic
def task_example(path_in: Path, path_out: Path) -> None:
    data = pd.read_csv(path_in)  # I/O at boundary
    result = process_data(data)  # Pure logic
    result.to_pickle(path_out)  # I/O at boundary


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pure function - all logic here."""
    ...
```

## Error Handling

- Raise errors early with descriptive messages
- `TypeError` for wrong types, `ValueError` for wrong values
- Use `_fail_if_...` helper functions for validation

```python
def _fail_if_not_list(data: Any) -> None:
    if not isinstance(data, list):
        msg = f"data must be a list, not {type(data).__name__}"
        raise TypeError(msg)
```

## Testing

### Test-Driven Development — always

**Always write the test first, watch it fail, then implement.** No exceptions for new
behavior or bug fixes. Tests are not an afterthought, they are the spec.

The cycle:

1. **Red.** Write a failing test that asserts the desired behavior in user-facing terms.
   Run it. Confirm it fails for the *right* reason (the missing behavior — not a typo,
   not an import error).
1. **Green.** Write the smallest amount of code that makes the test pass.
1. **Refactor.** Clean up while keeping the test green.

Apply per case:

- **New feature** → red-green-refactor.
- **Bug fix** → reproduce as a failing test before writing the fix. The test then
  prevents regression.
- **Refactor (no behavior change)** → existing tests are the spec. Keep them green
  before, during, and after. No new test needed if behavior is unchanged; if you find a
  behavior gap, fill it with a new test *before* refactoring.

### Test docstrings — describe behavior, not history

Test docstrings state what *should* be true, in user-facing terms. Pretend the reader
has never seen the PR. They should not need to.

```python
# Good — behavior, in plain language
def test_simulate_with_chained_transitions_yields_expected_next_wealth():
    """`next_wealth_t = wealth_t - c_t + 0.1 * next_aime_t` holds in simulation."""


# Bad — rehearses the prior bug or implementation history
def test_solve_resolves_chain_via_dags():
    """Before the fix, `_resolve_fixed_params` raised
    `InvalidParamsError: Missing required parameter: ...` because
    `create_regime_params_template` classified ..."""
```

Rule of thumb: **would the docstring still make sense in 9 months without the PR
context?** If not, rewrite it.

### Concrete-value assertions

Assert *what* the result is, not just that it didn't crash.

```python
# Good — analytical value with explicit tolerance
np.testing.assert_allclose(curr["wealth"], expected_next_wealth, atol=1e-6)

# Bad — passes whether the math is right or not
assert not jnp.any(jnp.isnan(V_arr))
assert df["wealth"].notna().all()
```

`not isnan` and `no exception raised` belong in CI smoke tests, not in the unit tests
for the feature itself.

### Mechanics

- Test files: `test_<module>.py`
- Test functions: `test_<function>_<behavior>`
- One assertion per test
- Use `@pytest.mark.parametrize` for multiple inputs

```python
@pytest.mark.parametrize("invalid_input", [-77, "typo"])
def test_clean_scale_raises_on_invalid(invalid_input: Any) -> None:
    with pytest.raises(ValueError):
        clean_scale(pd.Series([invalid_input]))
```

## Type Checking

Use **ty** (not mypy, not pyright) for type checking.

- Run via `pixi run ty`
- Suppress errors with `# ty: ignore[rule-name]` (not `# type: ignore`)
- Always specify the rule name in ignore comments

```python
# Good
x = some_call()  # ty: ignore[unresolved-reference]

# Bad - don't use type: ignore
x = some_call()  # type: ignore
```

## Verification After Changes

Run these checks after making code changes. Skip any that don't apply to the project.

1. **Lockfile**: If `pyproject.toml` changed, run `pixi lock` and stage the updated
   `pixi.lock`. Never commit or push a `pyproject.toml` change without re-locking — a
   stale lock breaks CI (see "Always re-lock before committing").
1. **Pre-commit**: Stage new files, then `pixi run prek run --all-files` (or
   `prek run --all-files` if globally installed). Fix any failures.
1. **Tests**: `pixi run tests` (or the project's test task).
1. **Type checking**: `pixi run ty`.
1. **Notebook diffs**: If `.ipynb` files changed
   1. verify the diff looks like clean cell-content changes, not JSON noise (cell
      metadata, execution counts, output blobs). If the diff is bloated, the notebook
      was not properly stripped — run nbstripout before committing
   1. Make sure notebook cells are properly formatted (each line in a cell is a new json
      line, not one cell=one line).
   1. Use actual UTF-8 characters everywhere — in markdown cells, Python strings, and
      f-strings. Never write unicode escapes like `\u2014` or `\u03bc`; write `—` and
      `μ` directly.
