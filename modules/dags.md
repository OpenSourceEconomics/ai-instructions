# dags

**dags combines interrelated functions into a single function.** Dependency order is
inferred from signatures: if function `g` has a parameter named `f`, it depends on the
output of function `f`. Only functions needed to reach the target(s) are included
(automatic pruning).

## Basic Usage

```python
from dags import concatenate_functions


def f(x, y):
    return x + y


def g(f, z):
    return f * z


functions = {"f": f, "g": g}
combined = concatenate_functions(functions, targets="g")
# combined(x, y, z) computes f first, then g
combined(1, 2, 3)  # (1 + 2) * 3 = 9
```

## The Key Insight: Removing Functions Changes the Interface

**If you remove a function from the DAG, its output becomes an external input
(parameter).** You can then fix that parameter to a constant via `functools.partial`.
This is how regime-specific simplification works: remove irrelevant functions, fix their
former outputs to constants.

```python
from functools import partial

from dags import concatenate_functions

# Full DAG: labor_income is computed from wages, hours
functions = {
    "labor_income": lambda wages, hours: wages * hours,
    "gross_income": lambda labor_income, transfers: labor_income + transfers,
}
full = concatenate_functions(functions, targets="gross_income")
# full(wages, hours, transfers) -> gross_income

# Simplified DAG for retirees: remove labor_income, fix it to 0
retired_functions = {
    "gross_income": lambda labor_income, transfers: labor_income + transfers,
}
retired = concatenate_functions(retired_functions, targets="gross_income")
# retired(labor_income, transfers) -> gross_income
retired_fixed = partial(retired, labor_income=0.0)
# retired_fixed(transfers) -> gross_income
```

Never work around a missing function by setting its inputs to zero or manually dropping
states. Remove the function and fix its output directly.

## Multi-Target and Return Types

Different targets produce different pruned DAGs. Use `return_type` to control the output
format:

```python
combined = concatenate_functions(
    functions,
    targets=["gross_income", "labor_income"],
    return_type="dict",  # or "tuple"
)
```

## Signature Tools

Use `rename_arguments` to adapt third-party functions whose parameter names do not match
your DAG's naming convention:

```python
from dags import rename_arguments

adapted = rename_arguments(
    func=third_party_fn,
    rename={"x": "consumption", "y": "leisure"},
)
```

Use `with_signature` to set signatures programmatically on functions that lack them
(e.g., lambdas wrapped in closures). Passing the dict form of `args`/`kwargs` plus a
`return_annotation` also stamps parameter and return *type annotations* onto the
function—not just argument names—so a dynamically built DAG wrapper gets a fully typed,
runtime-checkable signature:

```python
from dags import with_signature


@with_signature(
    args={"wages": "float", "hours": "float"},
    return_annotation="float",
)
def labor_income(*args, **kwargs):
    return args[0] * args[1]
```

## JAX Compatibility

If all individual functions are JAX-compatible, the combined function is too. It can be
JIT-compiled, vmapped, and differentiated:

```python
from jax import jit, vmap

combined = concatenate_functions(functions, targets="value")
fast = jit(combined)
batched = vmap(fast, in_axes=(0, None))
```
