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
