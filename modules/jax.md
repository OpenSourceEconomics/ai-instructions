# JAX

When a project uses JAX, prefer JAX on production hot paths, but establish mathematical
correctness in a transparent reference before JIT/vectorization. Include
`@.ai-instructions/modules/math.md` for any equation-bearing JAX kernel.

## Shapes and types

Annotate arrays with shape and dtype using `jax.Array` and `jaxtyping` where the project
uses it. State semantic axis names in the function contract; shape compatibility alone
does not detect a swapped state/action/shock axis.

```python
from jax import Array
from jaxtyping import Float, Int


def process(
    states: Float[Array, "n_periods n_states"],
    indices: Int[Array, "n_samples"],
) -> Float[Array, "n_samples"]: ...
```

The shape-string syntax may require the project's configured ruff exception such as
`F722`. Do not introduce a lint exception without checking the current configuration.

## Mandatory reference-to-transform ladder

For mathematical kernels compare the same deterministic cases under:

1. independent Python/NumPy/exact/high-precision reference;
1. JAX eager production;
1. `jax.jit` production;
1. relevant `jax.vmap`, `lax.scan`, `lax.map`, sharded, or parallel path;
1. supported float32/float64 policy and device(s);
1. primal plus derivative path when derivatives are consumed.

Test values, policies/indices, masks/validity, and marginals separately. Compilation
equality on one input is not enough; use boundaries and a generated mutation class.

## Precision policy

- Follow the repository's explicit x64 policy. Do not silently enable/disable x64 inside
  a library function.
- Make dtype promotion intentional; Python literals and NumPy arrays can change tracing
  and precision.
- Accumulate sums/products/log-likelihoods in an appropriate dtype and test tail/scale
  behavior.
- For floating-point predicates, never treat a tolerance as an equality/sign
  certificate. Use exact provenance, directed bounds, adjacent floats, or a fail-loud
  result.
- Record device/backend when discrepancies may be backend-specific.

## Control flow and masking

- Use `lax.cond`/`switch` when only one branch may be semantically evaluated.
  `jnp.where` evaluates both branch expressions and can create NaNs/infs or invalid
  derivatives.
- Do not mask invalid rows to finite zeros before the validity/poison decision.
- Keep static versus dynamic arguments explicit. Do not close over mutable globals or
  silently recompile on value-dependent Python objects.
- Check empty/singleton/padded rows and capacity overflow under JIT, not only eager
  mode.

## Automatic differentiation

- Differentiate the same mathematical representation used for the primal value.
- Validate gradients/Jacobians/Hessians with analytic/SymPy results and directional
  finite differences or complex-step where valid.
- At kinks, maxima, clipping, interpolation nodes, and terminal boundaries, state the
  chosen left/right/subgradient convention and test it.
- For `custom_jvp`/`custom_vjp`, test primal equivalence, tangent/cotangent linearity,
  zero tangents, batching, JIT, and higher-order differentiation if promised.
- Avoid `stop_gradient` unless the mathematical model explicitly requires it; document
  its effect on estimation or Euler conditions.

## Randomness

- Pass keys explicitly and split once per independent random object.
- Never reuse a key, infer independence from differing array positions, or let batching
  change the stochastic experiment unintentionally.
- Test deterministic reproducibility and, where relevant, empirical moments/cross-stream
  dependence under fixed seeds.
- Common random numbers must be deliberate and documented.

## Pytrees and immutable mappings

Register custom containers and immutable mappings as pytrees only when flatten/unflatten
is lossless and key order is deterministic. Test a round trip and JIT use.

```python
from types import MappingProxyType

import jax

jax.tree_util.register_pytree_node(
    MappingProxyType,
    lambda mp: (tuple(mp.values()), tuple(mp.keys())),
    lambda keys, values: MappingProxyType(dict(zip(keys, values, strict=True))),
)
```

## Sharding and collectives

- Specify which axis is sharded and whether it transitions or couples across devices.
- Prove whether a collective is mathematically required; do not add communication merely
  because an array is sharded.
- Check global versus per-shard reductions, padding, replicated constants, and
  deterministic output ordering.
- Benchmark only after reference/eager/JIT/sharded results agree.

## Debugging and evidence

Use `jax.disable_jit`, `jax.debug.print`, `checkify`, smaller examples, and jaxprs to
isolate semantics. Preserve the minimal reproducer, exact command,
backend/version/dtype, and observed output. After two failed local fixes to one
numerical class, build a literal reference/replacement rather than adding another JAX
branch.
