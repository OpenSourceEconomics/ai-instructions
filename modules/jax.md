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

## Ruff Configuration for jaxtyping

If the project uses `jaxtyping`, add `F722` to `extend-ignore` in the ruff config:

```toml
extend-ignore = [
  "F722",  # https://docs.kidger.site/jaxtyping/faq/#flake8-or-ruff-are-throwing-an-error
]
```

The `Float[Array, "n_periods n_states"]` syntax triggers F722 (syntax error in forward
annotation). This is a known jaxtyping/ruff incompatibility.
