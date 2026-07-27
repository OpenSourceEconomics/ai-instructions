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

`result.success` is necessary evidence, never sufficient evidence. Before trusting an
estimate or solution:

- confirm minimization/maximization sign and objective normalization;
- verify parameter names/order/tree, fixed values, transformations, scales, bounds, and
  nonlinear constraints;
- evaluate objective and constraints at start, candidate, known benchmark, and
  boundaries;
- compare multiple starts and, for low dimensions, grids/profiles/contours;
- compare gradients/Hessians to independent analytic/SymPy/directional derivatives;
- inspect feasibility, residuals, active constraints, KKT/projected-gradient conditions,
  and the actual stopping reason;
- rerun with stricter tolerances and at least one appropriate alternative algorithm
  where the solution is scientifically load-bearing;
- distinguish flat/weakly identified directions from optimizer failure.

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

## Objective and derivative contract

Record:

- whether objective is total, mean, or weighted mean;
- observation/cluster/time aggregation and missing-data masks;
- penalties versus true constraints;
- transformations and Jacobian adjustments;
- simulation/quadrature seeds and common random numbers;
- expected differentiability and kink conventions;
- parameter units and scaling.

For likelihood/GMM/minimum-distance work, expose per-observation or per-cluster
contributions for inference tests. A scalar total alone makes resampling and robust
covariance auditing unnecessarily fragile.

## Estimation and inference

- Identification is separate from numerical convergence. Use profiles, rank/eigenvalue
  diagnostics, synthetic DGPs, and known analytical cases.
- For sequential/two-step estimators, include earlier-step uncertainty and
  cross-derivative propagation; use a common resampling unit when the theory requires
  it.
- Bootstrap the correct unit—individual, cluster, time block, market, or simulation
  draw—and preserve dependence across jointly estimated periods/equations.
- Check Hessian/sandwich/cluster/finite-sample conventions against the stated estimator.
- Compare reported SEs to simulation or an analytical toy problem when feasible.

## Completion evidence

Record the exact optimagic version, algorithm, starts, constraints, tolerances,
objective values, termination message, derivative checks, profile/boundary results, and
final parameter map. Keep a deterministic small optimization test in the suite. After
two failed local repairs to the objective/parameter map, rebuild the literal
objective/reference rather than switching algorithms blindly.
