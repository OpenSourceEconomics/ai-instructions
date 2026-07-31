# Numerical Optimization

Use optimagic for project optimization when it is already the repository standard.
Inspect the installed version/signature and lockfile before choosing `params=` versus
`x0=` or an algorithm name; do not code from remembered API examples.

```python
import optimagic as om

result = om.minimize(
    fun=objective,
    params=start_params,  # verify against the installed signature
    algorithm="scipy_lbfgsb",
)
```

## The optimizer is not the mathematical oracle

`result.success` is necessary evidence, never sufficient evidence — it reports that a
stopping criterion fired, not that the objective was right. Check `result.message` for
the criterion that actually fired, and treat identification failure as distinct from
optimizer failure: a flat or weakly identified direction produces a "converged" result
at an arbitrary point along it.

Include `@.ai-instructions/modules/math.md`, whose §8 governs objective/parameter-map
verification, derivative checks, and multi-start/profile evidence for load-bearing
estimates.

## Algorithm selection

Choose after inspecting smoothness, constraints, dimension, noise, and derivative
quality. Typical candidates, subject to the installed optimagic version:

- smooth bound-constrained: L-BFGS-B;
- smooth nonlinear constraints: IPOPT or another constrained derivative method;
- least squares: a dedicated least-squares method;
- derivative-free, few parameters: BOBYQA or another bounded method;
- nonconvex/global: a documented global/exhaustive stage followed by local refinement.

Never use Nelder–Mead as an unexamined default. Comparing algorithms is useful only when
all receive the same objective, parameter transformation, constraints, and stopping
scale.

## Objective structure

State whether the objective is a total, a mean, or a weighted mean — a silent switch
between them rescales gradients and every tolerance calibrated against them.

For likelihood/GMM/minimum-distance work, expose per-observation or per-cluster
contributions rather than only the scalar total. Robust covariance, clustering, and
resampling all need them, and retrofitting the decomposition later is far more fragile
than returning it from the start. Bootstrap the unit the theory requires — individual,
cluster, time block, market, or simulation draw — and preserve dependence across jointly
estimated periods or equations.

## Completion evidence

Record the exact optimagic version and algorithm alongside the usual `math.md`
completion record — the API and defaults move between releases, so a result is not
reproducible without it. Keep a deterministic small optimization test in the suite.
After two failed local repairs to the objective or parameter map, rebuild the literal
objective rather than switching algorithms blindly.
