---
description: Prepare and enforce closure for an external Pro audit
allowed-tools: Read, Bash
---

# Close Pro Audit

Prepare and enforce closure for an external Pro audit, using whichever `pro-*-audit`
skill produced the original bundle — `pro-comp-method-audit`, `pro-econ-paper-audit`,
`pro-math-code-review`, or `pro-pylcm-scope-feasibility-audit`. That skill's own
`SKILL.md` is the source of truth for its exact script names and flags (most use
`scripts/prepare_prompt.py`; `pro-math-code-review` uses `scripts/prepare_bundle.py`) —
this command sequences them for closure and enforces the gate. Do not hardcode a script
path from memory; read the relevant skill's `SKILL.md` first if unsure which one produced
the audit at hand.

## Steps

1. Confirm every blocking root-cause class has completion evidence — historical witness,
   independent oracle, boundary/generated mutation suite, transformed paths, and project
   integration — per `modules/math.md`'s required completion record.
2. Fill the skill's `claude-completion-record.md` template with exact commands and
   observed outputs.
3. Build a fresh closure bundle from the original inputs, using `--mode closure`,
   `--prior <AUDIT-STATE.json>` from the ingested audit result, the completion record as
   `--evidence`, and the same `--workflow-class`/`--output-detail compact` as the
   original round.
4. Run the skill's `verify_bundle.py` before upload. Inspect `BUNDLE-MANIFEST.json`.
5. Open a **fresh** Pro chat, upload the bundle, paste the generated prompt, and save the
   complete reply.
6. Ingest the fresh closure reply with `ingest_report.py --merge <AUDIT-STATE.json>`, then
   run `audit_gate.py` on the merged state.

## Gate

- **Exit 0** — closed. Stop.
- **Exit 1** — a class is still valid but open. Act only on that named class/artifact.
- **Exit 2** — the protocol state is malformed/inconsistent. Repair the state, not the
  science.

A further round requires a new supported blocking class, a changed target, or one exact
missing artifact. Nonblocking hardening and imaginable hostile-input checks do not prevent
closure. A repeated supported numerical class triggers strategy escalation
(reference/architecture replacement per `modules/math.md`), not a third micro-patch.
