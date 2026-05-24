# beartype + jaxtyping

Runtime type checking with **beartype**, combined with shape-tagged array types from
**jaxtyping**, gives a project a single source of truth: the annotations on a function
are also its runtime contract. The patterns below describe the OSE-ecosystem rollout —
package-wide claw, per-component exception hierarchy, wide/narrow type split at user
boundaries — as deployed in `ttsim`, `gettsim`, `gettsim-personas`, and `pylcm`.

## When to use beartype

Use beartype in projects that meet at least one of:

- **JAX or jaxtyping** is used and the codebase relies on shape/dtype invariants
  (`Float[Array, " n_obs"]`, `Int[Array, "n_periods n_states"]`). Stringified shapes rot
  silently without a runtime checker.
- **Multi-package codebase** with stable internal interfaces between packages —
  ttsim/gettsim/personas, or any other split where module A's annotations form a
  contract with module B.
- **User-facing constructors and entry points** that should reject malformed input
  loudly, with a typed error vocabulary the user (not the maintainer) sees first.

Skip beartype for:

- Pure pytask data-pipeline projects where the only runtime values are `pd.DataFrame` /
  `pd.Series` and the schema is enforced by other means.
- One-off scripts and notebooks where the cost of wrong types is a stack trace, not a
  silent bug.
- Library code that has to interop with arbitrary user types — beartype's claw becomes
  more friction than signal.

## The package-wide claw

`beartype.claw.beartype_package(<pkg>, conf=INTERNAL_CONF)` registers an import hook
that runs `@beartype` on every function defined in the package. Register it from the
package's `__init__.py`, **before** any submodule of the package loads.

```python
# src/project/__init__.py
import os

if os.environ.get("PROJECT_BEARTYPE_CLAW", "0") != "0":
    from beartype.claw import beartype_package

    from project._beartype_conf import INTERNAL_CONF

    beartype_package("project", conf=INTERNAL_CONF)

# ...then the package's regular imports
```

The env-var gate (`TTSIM_BEARTYPE_CLAW`, `GETTSIM_BEARTYPE_CLAW`,
`GETTSIM_PERSONAS_BEARTYPE_CLAW`, `LCM_BEARTYPE_CLAW`, …) is for the rollout PR only:
collaborators can run the test suite with the claw off while the new violations get
triaged. After the rollout PR merges, drop the gate and call `beartype_package`
unconditionally.

For projects with a split public/private layout (`gettsim_personas` +
`_gettsim_personas`), register a claw on each package and gate both behind the same env
var.

## `INTERNAL_CONF` and per-component `BeartypeConf`

The claw's `INTERNAL_CONF` configures runtime checks across the whole package; its
violations surface as beartype's own `BeartypeCallHintViolation`, signalling an internal
bug. User-facing constructors layer an explicit `@beartype(conf=<COMPONENT_CONF>)` on
top that maps violations to a project-defined exception class.

```python
# src/project/_beartype_conf.py
from beartype import BeartypeConf, BeartypeStrategy

from project.exceptions import (
    EntryPointError,
    InputDataError,
    ProjectError,
)


def project_conf(error_class: type[ProjectError]) -> BeartypeConf:
    """Build a `BeartypeConf` that re-raises violations as `error_class`."""
    return BeartypeConf(
        is_color=False,
        is_pep484_tower=True,
        strategy=BeartypeStrategy.On,
        violation_door_type=error_class,
        violation_param_type=error_class,
        violation_return_type=error_class,
    )


INTERNAL_CONF = BeartypeConf(
    is_color=False,
    is_pep484_tower=True,
    strategy=BeartypeStrategy.On,
)

ENTRY_POINT_CONF = project_conf(EntryPointError)
INPUT_DATA_CONF = project_conf(InputDataError)
# ...one per user-facing component
```

`strategy=BeartypeStrategy.On` enables O(n) container validation (every entry in a
mapping/sequence is checked, not just one sampled element). User-facing constructors are
called rarely, so per-call cost is invisible. `is_pep484_tower=True` honours PEP 484's
numeric tower so an `int` value satisfies a `float`-typed parameter.

Set `violation_door_type`, `violation_param_type`, and `violation_return_type` all to
the project class so the same exception surfaces regardless of where the violation
originated. Requires `beartype >= 0.18`.

## Project exception hierarchy

Define a single base exception and one subclass per user-facing component:

```python
# src/project/exceptions.py
class ProjectError(Exception):
    """Base class for all project-defined exceptions."""


class EntryPointError(ProjectError):
    """Raised when a call to `main()` has invalid arguments."""


class InputDataError(ProjectError):
    """Raised when an `InputData.*` factory receives invalid arguments."""


class PolicyFunctionDefinitionError(ProjectError):
    """Raised when an `@policy_function` declaration is invalid."""


# ...one per @beartype-decorated user boundary
```

Each subclass corresponds to a `@beartype(conf=<COMPONENT_CONF>)` decoration site. Users
catch the base class; library code dispatches on subclasses. Pre-existing exceptions can
be hoisted into the hierarchy by changing their base class to `ProjectError` without
moving their definition site.

Downstream packages re-use the upstream hierarchy: `gettsim` imports `TTSIMError` from
`ttsim.exceptions` and adds no `GettsimError` of its own. Packages with a single extra
boundary add one class (`PersonaDefinitionError(TTSIMError)`).

## The wide / narrow type split: `UserX` vs `X`

User-facing boundaries accept a wider set of inputs than internal code wants to deal
with. Encode that explicitly:

```python
# src/project/typing.py
import numpy as np
import pandas as pd
from jaxtyping import Float, Int, Bool
from jax import Array

# Canonical (narrow) — internal use.
FloatColumn: TypeAlias = Float[Array | np.ndarray, " n_obs"]
IntColumn: TypeAlias = Int[Array | np.ndarray, " n_obs"]
BoolColumn: TypeAlias = Bool[Array | np.ndarray, " n_obs"]

ScalarFloat: TypeAlias = float | np.floating
ScalarInt: TypeAlias = int | np.integer
ScalarBool: TypeAlias = bool | np.bool_

# Wide — user boundary only.
UserScalarFloat: TypeAlias = float | int | np.floating | np.integer
UserFloatColumn: TypeAlias = FloatColumn | pd.Series
UserIntColumn: TypeAlias = IntColumn | pd.Series
UserBoolColumn: TypeAlias = BoolColumn | pd.Series
```

Use `User*` on `@beartype`-decorated entry points. Convert to the narrow alias
immediately via an explicit `_canonicalize_*` boundary function:

```python
def _canonicalize_float_column(col: UserFloatColumn) -> FloatColumn:
    if isinstance(col, pd.Series):
        return col.to_numpy()
    return col
```

One `_canonicalize_*` per user-facing boundary keeps the conversion site discoverable
and testable. Internal call sites then accept only the narrow alias, so type drift
cannot leak inward.

## Backend-agnostic union types

In projects that support both NumPy and JAX backends, jaxtyping's `Float[Array, ...]`
matches only the JAX type. NumPy arrays under the same claw get rejected. Union `Array`
with `np.ndarray` in every column alias:

```python
FloatColumn: TypeAlias = Float[Array | np.ndarray, " n_obs"]
```

When `jax` is an optional runtime dependency, fall back to `np.ndarray` if the import
fails, so the alias stays runtime-resolvable in NumPy-only environments:

```python
try:
    from jax import Array
except ImportError:
    Array = np.ndarray
```

This keeps one vocabulary across backends — call sites never have to mention which
backend they are running under.

## Two-definition pattern for recursive aliases

beartype's runtime forward-ref machinery cannot resolve recursive `TypeAlias` whose
inner stringified name is itself the alias. The pattern below keeps the precise type for
**ty** and a wider runtime form for beartype:

```python
if TYPE_CHECKING:
    NestedData: TypeAlias = Mapping[
        str, "FloatColumn | IntColumn | BoolColumn | NestedData"
    ]
else:
    # Wider runtime form — beartype only needs a Mapping subtype here.
    NestedData = Mapping[str, FloatColumn | IntColumn | BoolColumn | Mapping]
```

The runtime check on the recursive types becomes weaker — beartype validates the outer
`Mapping` and the first level of values, but a malformed deeper level slips through.
Static checking via ty is still precise. Reserve this pattern for the handful of aliases
that truly need it (recursive trees, lookup dicts); flag each occurrence in the alias's
surrounding comment.

## PEP 649 and `from __future__ import annotations`

beartype reads annotations at decoration time. Under
`from __future__ import annotations` (PEP 563), annotations are strings that beartype
resolves by walking the defining module's globals. Names hidden inside
`if TYPE_CHECKING:` are invisible at that point and cause forward-ref errors.

Strategy depends on `requires-python`:

- **`requires-python >= 3.14`**: drop `from __future__ import annotations`. PEP 649
  evaluates annotations lazily without stringifying them, so beartype gets real objects.
- **`requires-python < 3.14`**: keep the future-import. Hoist every name beartype needs
  to see (column aliases, scalar aliases, `Callable`, `Any`, `ModuleType`, `datetime`,
  recursive aliases via the two-definition pattern) **out** of `TYPE_CHECKING` blocks
  and into module scope. Leave only forward types that would create import cycles inside
  `TYPE_CHECKING`.

PEP 612 `ParamSpec` annotations (`*args: P.args, **kwargs: P.kwargs`) do not resolve
under stringified annotations plus beartype. Apply `@no_type_check` to the affected
method (typically `__call__` of a generic protocol class) as an acceptable shim. A
future migration to PEP 695 generic syntax removes the workaround.

## `functools.wraps` strips wrapper annotations

When a decorator wraps a function whose signature is *different* from the wrapper's (for
example, a scalar-to-column auto-vectorizer wrapping a scalar policy function),
`functools.wraps` copies the wrapped function's `__annotations__` and `__annotate__`
onto the wrapper. The package claw then checks the wrapper's call against scalar
annotations, even though it is being called with columns, and every invocation raises.

The fix: drop annotations from the assignment list.

```python
import functools

_WRAPPER_ASSIGNMENTS_NO_ANNOTATIONS = tuple(
    a
    for a in functools.WRAPPER_ASSIGNMENTS
    if a not in ("__annotations__", "__annotate__")
)


def vectorize_scalar(scalar_func):
    @functools.wraps(scalar_func, assigned=_WRAPPER_ASSIGNMENTS_NO_ANNOTATIONS)
    def wrapper(*args, **kwargs):
        return _column_impl(scalar_func, *args, **kwargs)

    return wrapper
```

`__annotate__` is PEP 649's deferred-eval alias; strip it as well for 3.14+.

## The claw binds decorator-produced callable instances

A decorator that returns a **callable class instance** rather than a function — a frozen
dataclass with a `__call__` that wraps the real function is the common case — trips the
claw. The claw appends `@beartype` to the decorated `def`, and with the default
(outermost) placement that becomes `beartype(Wrapper(raw_func))`. Given a
pseudo-callable object, `beartype()` returns a *bound method* of its `__call__`, so the
module-level name is no longer the `Wrapper` instance:

```python
@interface_function()  # returns an `InterfaceFunction` instance
def num_segments(processed_data): ...


# under the claw, `num_segments` is now
# <bound method InterfaceFunction.__call__ of InterfaceFunction(...)>
```

`isinstance(num_segments, InterfaceFunction)` and every attribute access (`.leaf_name`,
`.dependencies`) then fail. A *non-callable* wrapper — a pure metadata dataclass — is
instead skipped with a `BeartypeClawDecorWarning`, leaving the instance intact; only
callable wrappers are silently bound.

`claw_decor_place_func=BeartypeDecorPlace.FIRST` runs `@beartype` on the raw function
*before* the decorator wraps it, which avoids the binding — but beartype must then
resolve the raw function's annotations, reintroducing every forward-ref /
`from __future__ import annotations` problem, and if the wrappers feed a DAG library
that compares annotations it can desync that comparison. Treat `FIRST` as a last resort.

The remedy depends on how the wrapped objects are consumed:

- **Consumed only via a claw-free loader** (e.g.
  `importlib.util.spec_from_file_location`, which bypasses `sys.meta_path` and so the
  claw) — the binding is harmless in production; it bites only code that imports the
  module *normally*. Point such code (typically tests) at the claw-free loader too, so
  it sees the same pristine instances the loader produces.
- **Consumed via normal import in production** — exclude the offending modules from the
  claw with `BeartypeConf(claw_skip_package_names=("pkg.subpkg",))` (skips that package
  and all submodules transitively), or make the wrapper non-callable and hand the
  consumer its `.function` attribute.

## CI integration

Run the test suite with the claw on. Set the env var unconditionally on every test
environment so the claw stays on even when the user types `pixi run tests` locally:

```toml
# pyproject.toml
[tool.pixi.feature.tests.activation.env]
TTSIM_BEARTYPE_CLAW = "1"
```

For the rollout PR, also surface the env var in CI matrix entries; run one matrix job
with the claw off as a baseline. After the rollout PR merges, remove the env-var gate
from `__init__.py` and the claw is on for everyone, always.

## jaxtyping sentinel-cloudpickle fix (upstream)

jaxtyping's three module-level `object()` sentinels (`_any_dtype`, `_anonymous_dim`,
`_anonymous_variadic_dim`) do not survive a `cloudpickle` round-trip — the receiving
side gets fresh `object()` instances that no longer match the live module-global, so
identity-based shape checks on cloudpickled jaxtyping types fail. Projects that pickle
DAG-built functions (ttsim does, gettsim and pylcm inherit) hit this whenever the DAG's
annotations reference a jaxtyping type.

Resolved upstream in `jaxtyping >= 0.3.10`
([patrick-kidger/jaxtyping#390](https://github.com/patrick-kidger/jaxtyping/pull/390))
by replacing all three sentinels with `__reduce__`-backed singleton classes. Until the
release is on PyPI, depend on the fork via a pixi pypi-dependency override:

```toml
[tool.pixi.pypi-dependencies]
jaxtyping = { git = "https://github.com/hmgaudecker/jaxtyping", branch = "fix/sentinel-cloudpickle" }
```

Pair the override with `jaxtyping>=0.3.10` in `[project].dependencies` so consumers
installing the released wheel get the same floor. Drop the override once the release
lands.

## jaxtyping `Ellipsis` shim (under `from __future__ import annotations`)

Projects supporting Python < 3.14 keep `from __future__ import annotations` (PEP 563).
Under that import, an annotation like `Int[Array, ...]` is stored as the source string
`"Int[Array, ...]"`; runtime consumers (beartype, jaxtyping) `eval` it back, producing
`Int[Array, Ellipsis]`. jaxtyping's subscript handler then calls `dim_str.strip()` and
dies with `AttributeError` because `Ellipsis` is not a string. The shim coerces a bare
`Ellipsis` to `"..."` inside `_MetaAbstractDtype.__getitem__`; see
[`ttsim/_jaxtyping_patch.py`](../../src/ttsim/_jaxtyping_patch.py). Import it before any
jaxtyping-subscripted type is created. Projects on `requires-python >= 3.14` that have
dropped `from __future__ import annotations` (and so receive real `Ellipsis` only via
inline annotations they control) do not need this shim — pylcm is in that bucket.

## Ruff configuration

If the project uses jaxtyping, add `F722` to `extend-ignore` in `pyproject.toml` (see
also `modules/jax.md`). The shape-string syntax otherwise trips ruff's
forward-annotation syntax check.
