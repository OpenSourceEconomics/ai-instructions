---
description: Implement a mathematical/statistical feature reference-first
argument-hint: <equation, estimator, or claim to implement>
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Implement Math

Implement the requested mathematical/statistical feature using `modules/math.md`:
**$ARGUMENTS**

## Steps

1. Read the source equation/claim and all current call paths/tests.
2. Write the executable contract: domains, shapes/axes, units/transforms, timing,
   boundaries/ties, approximation semantics, and downstream decision/estimand.
3. Build a literal independent reference (scalar/brute-force/SymPy/exact/high precision or
   synthetic DGP as appropriate).
4. Add a failing historical/analytical witness and a deterministic counterexample-class
   mutation suite.
5. Implement production code; compare reference/eager/compiled/vectorized/derivative paths.
6. Run targeted and project tests; only then optimize.
7. Return a completion record with commands, outputs, diff, invariant, level effect, and
   decision/estimand effect.

Do not stop when one witness passes. If the same class already had two failed local fixes,
replace the kernel/architecture instead of adding another branch or tolerance.
