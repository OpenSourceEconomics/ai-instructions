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
