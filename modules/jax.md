# JAX

When a project uses JAX, prefer it over NumPy for performance-critical code. Standard
idioms are assumed known: `jnp` in place of `np`, `@jit` on hot paths, `vmap` instead of
loops, `jnp.where` for conditionals, immutable arrays, and `jax.random` keys instead of
global state. The notes below are the ecosystem-specific deltas.

## jaxtyping

Annotate arrays with shape and dtype:

```python
from jax import Array
from jaxtyping import Float, Int


def process(
    states: Float[Array, "n_periods n_states"],
    indices: Int[Array, "n_samples"],
) -> Float[Array, "n_samples"]: ...
```

The shape-string syntax trips ruff's forward-annotation check, so add `F722` to
`extend-ignore`
([jaxtyping FAQ](https://docs.kidger.site/jaxtyping/faq/#flake8-or-ruff-are-throwing-an-error)).

## Immutable mappings as pytrees

Register `MappingProxyType` so JIT can flatten it:

```python
import jax

jax.tree_util.register_pytree_node(
    MappingProxyType,
    lambda mp: (tuple(mp.values()), tuple(mp.keys())),
    lambda keys, values: MappingProxyType(dict(zip(keys, values, strict=True))),
)
```
