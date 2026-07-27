# Mathematical Implementation

Use this module whenever code implements equations, estimators, dynamic programs,
probability laws, numerical algorithms, or scientific decision rules. Correctness is not
established by plausible code, optimizer success, one regression, or agreement with a
second implementation that shares the same logic.

## Governing principle

Implement and verify this sequence:

```text
executable contract
→ literal independent reference
→ smallest red witness
→ counterexample-class generator
→ production implementation
→ transformed-path agreement
→ performance work
```

Do not optimize, vectorize, JIT-compile, parallelize, or generalize before a transparent
reference agrees on small cases. A passing historical witness is not proof that the
defect class is closed.

## 1. Write the executable contract first

Before editing production code, record:

- symbols, domains, parameter restrictions, and special/limiting cases;
- input/output shapes, axis meanings, broadcasting, ordering, and flattening convention;
- units, levels/logs, normalization, scaling, and transformation direction;
- timing and information set: what is known, chosen, realized, and conditioned on;
- sign, ordering, tie, inequality, and boundary conventions;
- support, feasibility, terminal, missing, invalid, and fail-loud semantics;
- exact versus approximate operations and the expected tolerance/error notion;
- parameter, state, action, shock, seed, dtype, and device dependence;
- the downstream object consuming the output: value, policy, argmax, probability,
  likelihood, score, estimate, SE, welfare, equilibrium, or reported result.

Turn the contract into assertions or tests. Resolve notation-to-code naming and axis
mapping explicitly. Do not silently choose a branch, terminal convention, extrapolation
rule, or normalization that the source leaves ambiguous.

## 2. Build an independent reference

The reference must minimize shared failure modes with production code. Prefer one of:

- direct scalar loops following the equation literally;
- exhaustive enumeration on a tiny finite problem;
- a second algorithm with different control flow;
- analytical closed forms or special cases;
- exact `fractions.Fraction` or `decimal.Decimal` arithmetic;
- high-precision `mpmath` evaluation;
- symbolic derivation with SymPy plus numerical substitution;
- brute-force grids/profiles for optimizers;
- synthetic DGPs with known estimands for estimators;
- finite-state backward induction for a DP kernel.

A NumPy translation of the same JAX branches is not automatically independent. Explain
the independence basis. Keep the reference slow and legible; do not contaminate it with
production performance tricks.

## 3. Use symbolic tools carefully

SymPy is encouraged for algebra, derivatives, roots, limits, identities, and exact
special cases. It is a tool, not an oracle without conditions.

- Declare assumptions (`positive`, `real`, `integer`, nonzero) matching the model
  domain.
- Track branches for `log`, powers, roots, `Abs`, `Piecewise`, inverse functions, and
  complex continuation.
- `simplify(expr) == 0` is useful evidence, not a universal proof. Use `equals`,
  factorized differences, assumptions, and domain-specific reasoning.
- Solve both transformed and original equations. Substitute candidate solutions into the
  **original** equation and reject extraneous roots.
- Check limiting parameter cases separately; symbolic formulas often divide by a
  parameter whose zero case has a valid limit.
- Compare symbolic/high-precision results with production using `lambdify` only after
  controlling modules/dtypes and branch conventions.
- For derivatives, compare symbolic/analytic expressions to automatic differentiation
  and step-swept finite differences or complex-step where valid.

Record the exact tool command/script and output worth preserving as a regression
fixture.

## 4. Define the counterexample class

For every mathematical defect, identify the structural family rather than only the point
that exposed it. Examples:

- all equality/tie cases under scaling and adjacent representable perturbations;
- every axis permutation or flattening order for a tensor contraction;
- all zero-probability, zero-variance, singular, terminal, empty-feasible-set cases;
- a class of resampling structures with nonzero cross-step derivatives;
- interpolation crossings with different slopes/curvatures and endpoint positions;
- all signs and limiting values of a parameter;
- alternative seeds, shapes, dtypes, and compiled/vectorized paths.

State the production invariant that closes the class and a mechanical acceptance
criterion. If the class cannot be certified safely, fail loudly on it rather than
publishing a plausible finite answer.

## 5. Testing ladder

Use the smallest relevant layers; do not substitute only end-to-end tests for local
mathematical evidence.

1. **Historical witness.** Fails before, passes after.
1. **Analytical/degenerate cases.** Zero, identity, deterministic, one-state,
   one-action, linear/quadratic, no-shock, no-transition, or other closed forms.
1. **Boundary cases.** Equality, terminal node, empty/singleton, singular covariance,
   zero probability/variance, binding constraints, support endpoints.
1. **Tiny exhaustive cases.** Enumerate all states/actions/labels/permutations when
   small.
1. **Oracle differential.** Production agrees with independent reference.
1. **Generated class.** Deterministic seeds and a parameterized mutation neighborhood.
1. **Metamorphic properties.** Symmetry, equivariance, monotonicity, conservation,
   probability sums, scale/translation behavior, envelope domination, permutation
   invariance, relabeling invariance.
1. **Transformed paths.** Eager/compiled/vectorized/parallel/dtype variants as
   supported.
1. **Integration.** Relevant project tests, examples, docs, and reported outputs.
1. **Performance.** Only after correctness, compare time/memory/compilation without
   changing the acceptance semantics.

Use deterministic generators and print/store the seed and minimal shrunk witness.
Property libraries are welcome, but a transparent explicit generator is often easier to
preserve in scientific repositories.

## 6. Floating-point decisions

Distinguish approximation error in a reported level from uncertainty in a structural
predicate. Never use an arbitrary tolerance as a proof of equality, ordering, ownership,
feasibility, or branch dominance.

For structural decisions use, as appropriate:

- exact input provenance or integer/rational arithmetic;
- error-free transforms/compensated expansions;
- directed rounding or interval bounds;
- higher precision solely as an independent certificate;
- `numpy.nextafter` / adjacent representable checks;
- explicit left/right germs at discontinuities;
- separate value, policy, derivative, and ownership publication;
- a conservative unresolved/overflow/fail-loud state.

Check rescaling, translation, subnormal/large-normal regimes, signed zero, duplicate
nodes, finite-versus-infinite sentinels, and interpolation exactly at nodes. Do not let
masks such as `where(is_valid, value, 0)` launder NaNs or invalid branches before the
validity decision.

## 7. Derivatives

Derivatives are part of the mathematical object, not incidental AD output.

- Specify derivative with respect to which scalar/vector and what other values are held
  fixed.
- State left/right/subgradient conventions at kinks, maxima, clipping, interpolation
  nodes, and terminal boundaries.
- Differentiate the exact production value representation; do not combine a value from
  one interpolant with a marginal from another unless the contract explicitly defines
  two objects.
- Compare AD to analytic/SymPy derivatives and finite-difference step sweeps. Use
  complex-step only for holomorphic paths without clipping, `abs`, comparisons, or
  branch changes.
- For custom JVP/VJP rules, test primal equality, tangent/cotangent linearity, zero
  tangents, batched transforms, and higher-order differentiation if supported.

## 8. Optimization and estimation

An optimizer is a search mechanism, not a proof of the objective or solution.

- Verify objective sign, parameter ordering/tree, transformations, constraints, fixed
  parameters, weights, and per-observation aggregation.
- Evaluate the objective at the start, candidate, known benchmark, boundaries, and local
  profiles; use multiple starts when nonconvex.
- Check gradients/Hessians against independent derivatives and directional derivatives.
- Inspect feasibility, active constraints, KKT/residual conditions, and whether a
  reported `success` corresponds to the intended stopping criterion.
- Compare algorithms only after confirming they solve the same transformed problem.
- For sequential/two-step estimators, propagate generated-regressor/earlier-step
  uncertainty, use the correct resampling unit, preserve cross-period dependence, and
  test with an analytical toy estimator or synthetic DGP.
- Separate identification failure from numerical optimization failure.

## 9. Dynamic programming and EGM-like methods

Write the timing table before coding. Verify:

- state versus action versus realized next state;
- current utility, continuation law, discounting/CE, and terminal payoff;
- feasible sets and borrowing/resource constraints;
- perceived solution law versus objective realization law;
- interpolation/extrapolation and off-grid semantics;
- envelope/candidate ownership, ties, discontinuities, and one-sided policies;
- consistency of value, policy, and marginal channels;
- stochastic integration order relative to nonlinear aggregators;
- exact node and terminal behavior;
- fail-loud handling when capacity or certification is insufficient.

Always retain a tiny brute-force solver as an oracle for a simplified instance. Compare
policies and values, not merely aggregate moments.

## 10. Repair strategy and stopping

Group symptoms under a stable root-cause class. Implement all compatible changes
together. One local repair and one local retry are reasonable. If the same class
survives two local attempts, stop adding tolerances, branches, or special cases. Replace
the kernel with the simplest independently testable correct reference or change the
representation/architecture. Recover performance only after class-level agreement.

A repair is complete only when the historical witness, boundary cases, generated
mutation suite, oracle differential, supported transformed paths, and relevant project
tests pass, and when the decision/estimand/result effect is explicitly resolved.
Imagining additional defensive validation outside the supported contract is not a reason
to keep a scientific repair open.

## Required completion record

For nontrivial mathematical work, leave a compact record containing:

- equation/source locator and executable contract;
- root-cause/counterexample class and implemented invariant;
- reference/oracle file and independence basis;
- historical witness and mutation suite;
- exact commands, environment/dtype/device/seed, and observed outputs;
- production diff and affected call paths;
- level effect and decision/estimand/result effect;
- performance result after correctness;
- any exact unresolved artifact or author decision.
