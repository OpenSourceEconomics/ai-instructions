---
description: Repair a math/numerics root-cause defect class as one batch
argument-hint: <description of the failing witness or bug, or a path to a report>
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Repair Math Root Cause

Repair this as a root-cause *class*, not a pinned case, under the `modules/math.md`
discipline — whatever its source, a failing test, a bug report, or an external audit
finding: **$ARGUMENTS**

Read `.ai-instructions/modules/math.md` now if it is not already in context. Reproduce
the witness before editing anything, identify the counterexample class it belongs to
(§4), confirm the oracle does not share the production failure mode (§2), then batch all
compatible root causes into one change rather than patching symptoms serially. Close with
the required completion record.

§10's stopping rule is the one to actually honor: if this is local repair attempt 2 or
later for the same class and it still survives, stop micro-patching — replace the kernel
with the simplest independently testable reference, or change the representation, and
recover performance afterward.

If the class came from a `pro-*-audit` skill finding, preserve its finding/artifact IDs
in the completion record and run `/close-pro-audit` afterward.
