# AI Coding Standards

Guidelines for AI agents, derived from
[Effective Programming Practices for Economists](https://effective-programming-practices.vercel.app/).

______________________________________________________________________

# Critical Rules

## Type Hints

**Always use type hints in all function signatures.** This is mandatory for this
codebase.

```python
# REQUIRED pattern
def calculate_utility(consumption: float, gamma: float = 1.5) -> float:
    return consumption ** (1 - gamma) / (1 - gamma)


def clean_data(raw: pd.DataFrame) -> pd.DataFrame: ...


def load_config(path: Path) -> dict[str, Any]: ...
```

- Use `from __future__ import annotations` for forward references
- Use `typing` module types: `Optional`, `Union`, `Callable`, `Any`
- Use `collections.abc` for abstract types: `Sequence`, `Mapping`, `Iterable`
- Prefer `X | None` over `Optional[X]` in Python 3.10+

## File Paths

**Always use `pathlib.Path`** - never string paths.

```python
from pathlib import Path

# In .py files
root = Path(__file__).parent.parent
data_path = root / "datasets" / "data.csv"

# In notebooks
root = Path(".").resolve().parent
```

Three rules:

1. Always use `pathlib.Path` objects instead of strings
1. Never hardcode absolute paths outside the project directory
1. Concatenate paths with `/` operator

## Cross-Platform Compatibility

- Use forward slashes `/` (works everywhere)
- Use `pathlib.Path` for all path operations
- Be consistent with file naming (Unix is case-sensitive, Windows is not)
- Never hardcode paths like `C:\Users\...` or `/home/...`

## Floating Point Comparisons

Never use `==` for floats. Use tolerance-based comparison:

```python
import math

if math.isclose(result, 0.3, rel_tol=1e-9):
    ...

# Or with NumPy
import numpy as np

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

- Include `__init__.py` in all package directories
- Use `pip install -e .` for development
- Never commit `__pycache__`

______________________________________________________________________

# Code Quality

## Naming Conventions

- `lowercase_with_underscores` - functions, methods, variables
- `UPPERCASE_WITH_UNDERSCORES` - constants
- `CamelCase` - classes
- Function names start with verb: `create_`, `calculate_`, `convert_`, `get_`
- Private functions: `_underscore` prefix
- Avoid: abbreviations, misspellings, single letters (`n`, `c`, `s`, `u` conflict with
  debugger), built-in names (`list`, `dict`, `type`)

## Pure Functions

Write pure functions whenever possible:

1. Same inputs → same outputs
1. No side effects

```python
# Good: Separate I/O from logic
def task_clean_data(
    data: Path = SRC / "original_data" / "data.csv",
    produces: Path = BLD / "data.pkl",
) -> None:
    df = pd.read_csv(data)  # I/O at boundary
    clean = clean_data(df)  # Pure logic
    clean.to_pickle(produces)  # I/O at boundary


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pure function - all logic here."""
    ...
```

## Error Handling

- Raise errors early with descriptive messages
- `TypeError` for wrong types, `ValueError` for wrong values
- Use `_fail_if_...` helper functions for validation

```python
def process_data(data: list[dict]) -> dict:
    _fail_if_not_list(data)
    _fail_if_wrong_element_types(data)
    ...


def _fail_if_not_list(data: Any) -> None:
    if not isinstance(data, list):
        msg = f"data must be a list, not {type(data).__name__}"
        raise TypeError(msg)
```

## Testing

- Test files: `test_<module>.py`
- Test functions: `test_<function>_<behavior>`
- One assertion per test
- Test edge cases and expected exceptions
- Use `@pytest.mark.parametrize` for multiple inputs

```python
@pytest.mark.parametrize("invalid_input", [-77, "typo"])
def test_clean_scale_raises_on_invalid(invalid_input: Any) -> None:
    with pytest.raises(ValueError):
        clean_scale(pd.Series([invalid_input]))
```

## Immutability

Prefer immutable structures:

- `NamedTuple` over `dataclass` when possible
- `@dataclass(frozen=True)` when dataclass features needed
- Copy before modifying: `result = some_list.copy()`

______________________________________________________________________

# Git

## Commits

- Descriptive messages explaining "why" not "what"
- Imperative mood: "Add feature" not "Added feature"
- Stage specific files, not `git add .`

## Pre-commit Hooks

- Run `pre-commit install` after cloning
- If commit fails, try again (hooks may auto-fix)
- If second commit fails, read error and fix manually

## Safety

- Never use `--force` on shared branches
- Never use `git reset --hard` without understanding consequences
- Don't modify history after pushing

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
- Loop over columns is fine

## File Formats

- `.pkl` for intermediate files (not shared)
- `.arrow` for files to share
- Avoid `.dta` unless sharing with Stata

## Functional Data Cleaning

```python
def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(index=raw.index)
    df["var1"] = clean_var1(raw["Q001"])
    df["var2"] = clean_var2(raw["Q002"])
    return df
```

Three rules:

1. Start with empty DataFrame
1. Touch each variable once
1. Use pure functions for each transformation

## Merging

- Always specify keys: `pd.merge(left, right, on=["key1", "key2"])`
- Explicitly choose join type: `how="left"`
- Verify observation counts before and after

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

**Never use:**

- `np.random.seed()` (deprecated global state)
- `np.random.rand()`, `np.random.randn()` (legacy)
- `np.random.default_rng()` without seed (not reproducible)

## Performance

1. Get it working first
1. Add tests
1. Profile to find bottleneck
1. Vectorize the bottleneck
1. Consider Numba for loops that can't be vectorized

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

## Task Structure

```python
from pathlib import Path
import pandas as pd

BLD = Path(__file__).parent / "bld"


def task_clean_data(
    raw_file: Path = Path("data.arrow"),
    produces: Path = BLD / "clean.pkl",
) -> None:
    raw = pd.read_feather(raw_file)
    clean = _clean_data(raw)
    clean.to_pickle(produces)


def _clean_data(raw: pd.DataFrame) -> pd.DataFrame: ...
```

- Task files: `task_*.py`
- Task functions: `task_*`
- Use `Path` objects for dependencies
- Use `produces` keyword for outputs
- Keep tasks focused: read → compute → write

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

**Econometrics** (statsmodels): causal inference, hypothesis testing **ML**
(scikit-learn): prediction

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
