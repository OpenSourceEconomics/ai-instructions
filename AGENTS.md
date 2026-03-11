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

- Use `from __future__ import annotations` for forward references
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
    n_states: int
    discount_factor: float = 0.95

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
- Avoid: abbreviations, single letters (`n`, `c`, `s`, `u` conflict with debugger),
  built-in names (`list`, `dict`, `type`)

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
