---
description: Repair a math/numerics root-cause defect class as one batch
argument-hint: <description of the failing witness or bug, or a path to a report>
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Repair Math Root Cause

Repair a root-cause defect class using the `modules/math.md` discipline, whatever its
source — a failing test, a bug report, or an external audit finding: **$ARGUMENTS**

## Steps

1. Reproduce the original witness before editing anything.
2. Identify the counterexample class the witness belongs to, not just the pinned case.
3. Verify (or build) an independent oracle/reference and confirm it does not share the
   production failure mode.
4. State the invariant that closes the class and a mechanical acceptance criterion.
5. Implement the fix. Batch all compatible root causes together rather than patching one
   symptom at a time.
6. Run the historical witness, boundary cases, the generated mutation suite, transformed
   paths (eager/compiled/vectorized as applicable), and the relevant project test suite.
7. Record the completion evidence `modules/math.md` requires: oracle and independence
   basis, mutation suite, exact commands/outputs, production diff, and the level and
   decision/estimand effect.

If this is local repair attempt 2 or later for the same class and it still survives, stop
micro-patching. Replace the kernel with the simplest independently testable reference, or
change the representation/architecture, before recovering performance.

If the root-cause class came from a `pro-*-audit` skill finding (`pro-comp-method-audit`,
`pro-econ-paper-audit`, `pro-math-code-review`, `pro-pylcm-scope-feasibility-audit`),
preserve its finding/artifact IDs in the completion record and run `/close-pro-audit`
afterward to prepare the closure bundle.
