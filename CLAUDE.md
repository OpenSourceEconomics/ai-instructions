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

______________________________________________________________________

# Pandas

## Configuration

Always enable at script/notebook start:

```python
import pandas as pd

pd.options.mode.copy_on_write = True
pd.options.future.infer_string = True
```

## Key Practices

- Use `engine="pyarrow"` when reading CSV
- Never use `inplace` argument (deprecated)
- Use `.loc` for label-based selection, avoid `.iloc`
- Use `.query()` for readable filtering
- Never loop over rows (`iterrows`, row-wise `apply`)

## File Formats

- `.pkl` for intermediate files (not shared)
- `.arrow` for files to share
- Avoid `.dta` unless sharing with Stata

## Functional Data Cleaning

Always follow these rules:

1. Start with empty DataFrame
1. Touch each variable once
1. Use pure functions for each transformation

```python
def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(index=raw.index)
    df["var1"] = clean_var1(raw["Q001"])
    df["var2"] = clean_var2(raw["Q002"])
    return df
```

Do all data management in a collection of tables satisfying these rules (normal forms):

- Values have no internal structure
- Tables do not contain redundant information
- Variable names have no structure (long format, NOT wide format)

## Merging

- At the very end, merge / reshaping tables as needed for analysis
- Always specify keys: `pd.merge(left, right, on=["key1", "key2"])` or index
- Explicitly choose join type: `how="left"`

______________________________________________________________________

# NumPy

## Core Practices

- Vectorize: use array operations, not Python loops
- Use `axis` argument for reductions
- `*` for elementwise, `@` for matrix multiplication
- Use broadcasting instead of `np.repeat`/`np.tile`

## Random Numbers

**Use modern API only:**

```python
rng = np.random.default_rng(seed=5471)  # Always provide seed
rng.uniform(0, 1, size=3)
rng.normal(0, 1, size=(2, 3))
```

**Never use:** `np.random.seed()`, `np.random.rand()`, `np.random.randn()`

______________________________________________________________________

# JAX

**When a project uses JAX, prefer it over NumPy for performance-critical code.**

## Core Patterns

```python
import jax.numpy as jnp
from jax import jit, vmap


# Use jnp instead of np
def utility(consumption: Array, gamma: float) -> Array:
    return jnp.where(
        gamma == 1.0,
        jnp.log(consumption),
        consumption ** (1 - gamma) / (1 - gamma),
    )


# JIT compile hot paths
@jit
def solve_model(params: Array, states: Array) -> Array: ...


# Vectorize with vmap instead of loops
batched_fn = vmap(single_fn, in_axes=(0, None))
```

## Key Differences from NumPy

- Use `jnp.where()` for conditionals (not Python `if`)
- Arrays are immutable - operations return new arrays
- Use `jax.random` with explicit keys (not global state)

```python
import jax.random as jr

key = jr.key(42)
key, subkey = jr.split(key)
samples = jr.normal(subkey, shape=(100,))
```

## Type Hints with jaxtyping

Use `jaxtyping` for shape-annotated array types:

```python
from jax import Array
from jaxtyping import Float, Int


def process(
    states: Float[Array, "n_periods n_states"],
    indices: Int[Array, "n_samples"],
) -> Float[Array, "n_samples"]: ...
```

## Immutable Mappings in JAX

Register `MappingProxyType` as a pytree for JIT compatibility:

```python
import jax

jax.tree_util.register_pytree_node(
    MappingProxyType,
    lambda mp: (tuple(mp.values()), tuple(mp.keys())),
    lambda keys, values: MappingProxyType(dict(zip(keys, values, strict=True))),
)
```

______________________________________________________________________

# Numerical Optimization

Use **optimagic** for all optimization:

```python
import optimagic as om

res = om.minimize(
    fun=objective,
    params=start_params,
    algorithm="scipy_lbfgsb",  # Always specify explicitly
)
```

## Algorithm Selection

| Problem Type           | Algorithm                        |
| ---------------------- | -------------------------------- |
| Smooth, unconstrained  | `scipy_lbfgsb`                   |
| Smooth, constrained    | `ipopt`                          |
| Least-squares          | `scipy_ls_lm`                    |
| Non-smooth, few params | `nlopt_bobyqa`                   |
| Global search          | `scipy_brute` + local refinement |

- Always compare multiple algorithms with `om.criterion_plot()`
- Check `res.success` before trusting results
- Never use Nelder-Mead as default

______________________________________________________________________

# Project Structure

## Directory Layout

```
my_project/
├── src/my_project/
│   ├── config.py
│   ├── original_data/
│   ├── data_management/
│   ├── analysis/
│   └── final/
├── bld/           # Generated outputs (gitignored)
├── tests/
└── pyproject.toml
```

## Config File

```python
# src/my_project/config.py
from pathlib import Path

SRC = Path(__file__).parent.resolve()
BLD = SRC.joinpath("..", "..", "bld").resolve()
```

## Reproducibility

- Include all source data and code
- Keep raw data and code in version control
- Put generated files in `bld/` (gitignored)
- Never rely on manual execution order

______________________________________________________________________

# Pytask

Use modern pytask syntax with `Annotated` and `Product` markers.

## Basic Task with Product Annotation

```python
from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from my_project.config import BLD, SRC


def task_clean_data(
    raw_file: Path = SRC / "original_data" / "data.arrow",
    output_file: Annotated[Path, Product] = BLD / "clean_data.pkl",
) -> None:
    raw = pd.read_feather(raw_file)
    clean = _clean_data(raw)
    clean.to_pickle(output_file)


def _clean_data(raw: pd.DataFrame) -> pd.DataFrame: ...
```

## Return Annotation for Simple Outputs

When the task's primary purpose is producing a single file:

```python
def task_create_summary() -> Annotated[str, Path("summary.txt")]:
    return "Summary content here"
```

## Data Catalog Pattern

For projects with many data files, use a `DataCatalog`:

```python
# src/my_project/config.py
from pytask import DataCatalog

DATA_CATALOG = DataCatalog()
DATA_CATALOG["raw_data"] = SRC / "original_data" / "data.arrow"
DATA_CATALOG["clean_data"] = BLD / "clean_data.pkl"
DATA_CATALOG["results"] = BLD / "results.pkl"
```

```python
# src/my_project/data_management/task_clean.py
from my_project.config import DATA_CATALOG


def task_clean_data(
    raw_file: Path = DATA_CATALOG["raw_data"],
    output_file: Annotated[Path, Product] = DATA_CATALOG["clean_data"],
) -> None: ...
```

## Task Conventions

- Task files: `task_*.py`
- Task functions: `task_*`
- Use `Annotated[Path, Product]` for outputs
- Keep tasks focused: read → compute (via helper) → write
- Helper functions do the actual work (testable, pure)

______________________________________________________________________

# Plotting (Plotly)

```python
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_dark"
pd.options.plotting.backend = "plotly"
```

Key principles:

1. Show the data clearly
1. Remove clutter (unnecessary gridlines, borders)
1. Use facets to avoid spaghetti charts
1. Use grey as default, accent colors for emphasis
1. Label directly on plot when possible

______________________________________________________________________

# ML vs Econometrics

**Econometrics** (statsmodels): causal inference, hypothesis testing

**ML** (scikit-learn): prediction

Critical rules:

- Never interpret ML parameters causally
- Never skip train/test split for prediction tasks
- Never evaluate on training data
- Use cross-validation for hyperparameter tuning
- Reserve test set for final evaluation only

```python
# Statsmodels
import statsmodels.formula.api as smf

results = smf.ols("y ~ x1 + x2", data=df).fit(cov_type="HC1")

# Scikit-learn
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)
```
