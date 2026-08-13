# AI Coding Standards

Guidelines for AI agents, mostly derived from
[Effective Programming Practices for Economists](https://effective-programming-practices.vercel.app/).
These capture *deltas from a capable agent's defaults* — ecosystem-specific tool choices
and opinionated rules. Generic best practice a strong model already follows is omitted.

______________________________________________________________________

# Critical Rules

## Type Hints

Type hints are **mandatory** in every function signature.

- Do NOT use `from __future__ import annotations` in Python 3.14+ projects — PEP 649
  deferred evaluation makes it unnecessary and changes runtime annotation semantics. For
  projects supporting < 3.14, use it for forward references.

## Immutability

Prefer immutable data structures throughout.

- `@dataclass(frozen=True)` for all config/state objects, with PEP 257 inline field
  docstrings (an `attr: int` line followed by its own `"""..."""` line).
- `tuple` / `MappingProxyType` / `frozenset` over `list` / `dict` / `set`.
- Create modified copies via `dataclasses.replace()` or `with_*` methods — never mutate.
- `NewType` to distinguish same-typed domain values (`Period`, `Age`); `Enum` for
  categorical values instead of string-literal or boolean flags.

## File Paths & Numerics

- **Paths:** always `pathlib.Path`, never strings; join with the `/` operator; no
  hardcoded absolute paths outside the project.
- **Float comparison:** never `==`; use `np.isclose` / `math.isclose` with an explicit
  tolerance.
- **Random numbers:** `np.random.default_rng(seed=...)`; never the legacy
  `np.random.seed` / `np.random.rand` / `np.random.randn`.

______________________________________________________________________

# Evidence and Claims

**A claim ships with its evidence or with its limit — never bare.** Drop it, make the
observation, or state it with what was measured and what was inferred marked, so a
reader can see the edge of the evidence. A bounded claim is a claim; an unmarked one is
a guess. This binds on numbers, counts, mechanisms, negative results, and "that can't
happen" alike.

The third branch is not a concession. "Eight call expressions; reachability per-mode not
traced", "900 binades short, derived from the grid definition rather than from
instrumented geometries", "single-route, unconfirmed" — each is decision-relevant, none
is fully measured, and withholding any of them would be the wrong call. What is
forbidden is stating one of them *unqualified*.

## The instrument lied to you

These fire many times a day and produce no symptom. Each yields evidence that looks
exactly like the real thing, which is why care alone prevents none of them.

### Measure something complete by construction

A count, a summary line, an exit code, a checksum. Never a truncated view of a listing:
`head`, `tail`, and `grep -m` return output indistinguishable from the full thing.

```bash
# Bad — shows 5 lines and looks complete; the file has 8, and nothing says so
grep -n "envelope_at_query(" step.py | head -5

# Good — every number is complete by construction; the listing is separate and whole.
#        `grep -c` counts matching *lines*, so count occurrences instead whenever
#        two calls can share one line.
grep -c "envelope_at_query(" step.py           # matching lines
grep -o "envelope_at_query(" step.py | wc -l   # call sites
grep -n "envelope_at_query(" step.py
```

**You cannot know in advance which output becomes a claim**, so make every listing
complete at the point you run it. Truncation cannot be repaired afterwards: a truncated
result and a complete one are indistinguishable, and by the time the number matters the
short view is all you have.

Nobody reads a 2000-test run unabridged, and this does not ask you to. It asks that the
*number you quote* come from something that cannot be short — the summary line, not the
tail of the log.

### Prove the instrument can fire, and that the specimen survived construction

"No NaNs", "no regressions", "no callers" are claims about a detector, not about the
world. A probe that reports a negative must be shown capable of producing a positive
**in the same run** — a deliberately failing case, a known-bad input, a seeded defect.
Otherwise a disabled check, a skipped validation, or a probe that silently did nothing
reports clean.

The same applies to the specimen. Assert — as a line of code in the run, not as a
reading of the output — that your inputs survived construction **in the format that will
actually be used**: `assert jnp.isfinite(rival).all()`, `assert x0 > 0 and x1 != x0`. An
operand that leaves the representable range on the way in — underflowing to zero,
overflowing to infinity, collapsing to equal endpoints, silently cast — answers an
easier question truthfully, and the run continues.

Two things that are not this check. A library diagnostic is not: depending on one to
notice makes luck the last line of defence, and the quiet case is the one that reaches
the record. Agreement with an independent report is not either: two parties can
construct the same degenerate witness, and a confirming wrong answer is where checking
stops.

### Check the population, not the verdict

Zero collected is not zero failures. A filter that selects nothing, a glob that matches
nothing, and a query that returns nothing all exit successfully.

```bash
# Bad — the pipe hands you tail's status, so a run that collected nothing
#       and a run that was killed both read as success
pytest -m "not slow" tests/ | tail -1

# Good — exit 5 is "nothing collected"; turn it into a real failure and pass
#        every other status through unchanged
pytest -m "not slow" tests/
status=$?
if [ "$status" -eq 5 ]; then
  echo "NOTHING COLLECTED"
  exit 1
fi
exit "$status"
```

Capture the status before you branch on it, and exit on it explicitly. A trailing
`[ $? -eq 5 ] && echo ...` inverts the very signal it is meant to guard: the test is
false on a healthy run, so the line — and with it the script or CI step that ends on it
— reports failure, while the nothing-collected case it was written to catch reports
success.

That one character in the Bad case defeats both rules in this group at once: the status
you read belongs to `tail`, and the output you read is truncated. It is the only place
two of these fail on a single keystroke.

A marker or filter that selects nothing is the common cause: on the command line `-m`
*replaces* the configured expression rather than intersecting with it, so a directory
marked wholesale can deselect its entire contents and still exit successfully.

### Pin a comparison to an immutable id, and assert the relationship

State what a measurement was taken against by commit hash, not by branch or tag name,
and check that the baseline really stands in the relation you assume — an ancestor is an
ancestor only if `git merge-base --is-ancestor` says so. A ref name is not a pin, and
"latest upstream" is not a baseline: comparing against a tip that has diverged reports
the other side's progress as your own deletions.

The same applies to the environment: assert inside the run which installation you
actually imported (`print(module.__file__)`), because a sibling checkout's editable
install resolves silently and a console script's shebang can point outside the
environment you believe you are in.

## The claim outran its support

These fire on conclusions rather than on commands. They are what turns a defensible
result into an overstated one.

### Treat an inherited claim as carrying a timestamp

A figure or mechanism you got from another agent, an earlier round, or your own summary
is a citation. Attribution is not freshness: **a correctly attributed superseded claim
is still a wrong claim**, and re-attributing it launders it into the record as jointly
held.

Name the round, message, or commit the figure came from, and confirm that source is
still its latest form. If you cannot, mark it inherited-unverified and let the reader
weigh it.

The same applies to stored artefacts. A frozen baseline, table, or calibration constant
needs the commit **and** the numerical precision it was produced under recorded with it,
or it cannot be compared to anything generated later.

### Say what a sweep holds fixed

Varying one input usually moves several quantities at once. Before naming a cause, write
down what the varied input does **not** change; if you cannot, the sweep cannot separate
them and is evidence for none of them.

Two results agreeing corroborate only if they differ in what they hold fixed — otherwise
it is one measurement reported twice, and calling it "two independent routes" is worse
than reporting one, because it manufactures confidence that was never there. Two
*recollections* of the same run are not two runs: if neither party can produce the
invocation, the agreement is a shared memory, not evidence.

If the result is invariant by construction, say so and label the sweep as a check on the
edges — subnormals, overflow, empty inputs — rather than offering it as the argument.

### Name the second route, or declare the claim single-route

Re-checking your own number re-runs the same route and therefore separates nothing, by
construction; no amount of attention fixes that. Before calling a result confirmed, name
the second route — a derivation of what you measured, a measurement of what you derived,
a different instrument, or a different agent. If you cannot name one, say the claim is
single-route.

### When you revise a claim, purge the old framing from the whole document

A retraction that lands in one section leaves every other section asserting the
retracted thing, because each editing pass only looks at the part it is editing. Before
shipping a revised document, grep it for the old framing and name the search string you
used, then resolve every cross-reference written as a placeholder — "see below", "TBD",
a table cell pointing at a section that was never written.

### When you contradict someone who read the same code, produce the distinguishing observation

Being able to construct a counter-story is not evidence. Identify the observation on
which the two accounts differ, make it, and report it — or concede.

______________________________________________________________________

# Python Environment

## Python Version

Minimum Python version is **3.14** unless a project specifies otherwise. Use 3.14+
features freely, including:

- `except ValueError, TypeError:` without parentheses (PEP 758) — this is **not** Python
  2 syntax. It is valid when there is no `as` clause.

## Pixi Package Manager

Pixi is the required package and environment manager.

- Run everything through it: `pixi run python`, `pixi run pytest`, `pixi run pytask`.
- Add deps with `pixi add` (conda-forge) or `pixi add --pypi` (PyPI-only); commit
  `pixi.lock` for reproducibility.
- Never use `pip`, `conda`, or `uv` directly, never run bare `python script.py`, never
  use the `defaults` conda channel.

### Always re-lock before committing — and especially before pushing

**Whenever `pyproject.toml` changes in any way — a dependency added, removed, or
version-bumped, a git/URL pin updated, an environment or feature edited — run
`pixi lock` and commit the regenerated `pixi.lock` in the same commit.**

A stale `pixi.lock` passes locally but breaks CI, and the failure surfaces *only* after
you push:

- `pixi install --frozen` / `pixi list --frozen` (the locked CI jobs) fail outright.
- `pixi install` silently regenerates the lock and dirties the worktree, which blocks
  any task that refuses to run on a dirty tree (e.g. benchmarks).

So treat `pixi lock` as mandatory before `git commit`, and double-check it before
`git push` — pushing a stale lock burns a full CI cycle to discover a one-line fix.

### Migrate feature `system-requirements` (cuda) via named platform variants

pixi deprecates feature-level `system-requirements = { cuda = "12" }` and its warning
tells you to put the constraint on the platform as a **feature-level** inline table,
`platforms = [{ platform = "linux-64", cuda = "12" }]`. **That feature-level form does
not parse** — `pixi lock` fails with `× expected a string, found table` (and `pixi info`
will *not* catch it: it only echoes the host's own virtual packages, so the edit looks
fine until you lock). The migration guide's example is a workspace-level one; the
per-feature translation the warning implies is what's unsupported. Still true as of pixi
0.76 — re-test before assuming it has been fixed.

The form that **does** work: declare **named platform variants** at the workspace level
and point each cuda feature at its variant by bare string.

```toml
[tool.pixi.workspace]
platforms = [
  "linux-64",
  { name = "linux-64-cuda12", platform = "linux-64", cuda = "12" },
  { name = "linux-64-cuda13", platform = "linux-64", cuda = "13" },
]

[tool.pixi.feature.cuda12]
platforms = [ "linux-64-cuda12" ]              # bare string ref — parses
# target selectors still key on the BASE platform, not the variant name:
[tool.pixi.feature.cuda12.target.linux-64.pypi-dependencies]
jax = { version = ">=0.9", extras = [ "cuda12" ] }
```

Verified properties (pixi 0.76): locks with **no warnings**; `target.linux-64` applies
to the `linux-64-cuda12` variant; and because a variant shares the base conda subdir,
the lock is **not** bloated — CPU/`tests` envs may *list* the variant platforms but
resolve to the same `linux-64` packages (only the cuda features add the GPU wheels).
Always confirm with `pixi lock`, never `pixi info`.

A *separate*, real warning — "target selector `osx-arm64` does not match any of the
platforms supported by the workspace" — means a feature references a platform not in
`[tool.pixi.workspace].platforms`. That one is genuine: either add the platform to the
workspace or drop the orphaned feature.

## Package Structure

Use `src` layout — package code under `src/<package>/`, tests in a top-level `tests/`.

______________________________________________________________________

# Code Quality

## Naming Conventions

Standard PEP 8 casing is assumed. Beyond it:

- Function names start with verb: `create_`, `calculate_`, `convert_`, `get_`
- Private functions: `_underscore` prefix
- Use `func`, not `fn`, when abbreviating "function" (e.g., `apply_func`)
- Avoid: abbreviations, single letters (`n`, `c`, `s`, `u` conflict with debugger),
  built-in names (`list`, `dict`, `type`)
- Avoid vague action nouns like "sweep", "pass", "handler" in identifiers, comments, and
  docstrings unless paired with a concrete qualifier (e.g., "annotation-stripping
  pass"). Prefer the verb form (`resolve_*`) or a specific noun (`resolver`,
  `validator`) that says what the thing actually does.

## Module Layout

Write "deep" modules: important public function(s) at the top, private helpers below.
Readers should see the API first without scrolling past implementation details.

Never add decorative section-separator comments like:

```python
# ---------------------------------------------------------------------------
# Section name
# ---------------------------------------------------------------------------
```

Code structure should be self-evident from function names and ordering.

## Docstrings

Use **Google convention** (`pydocstyle.convention = "google"`). Use **MyST** syntax (not
reStructuredText) for markup inside docstrings: `` `code` ``, `$math$`, markdown links.

- Imperative mood in summary lines ("Calculate utility", not "Calculates utility")
- Use inline field docstrings (PEP 257) for dataclass attributes (see Frozen Dataclasses
  example above)

```python
def calculate_utility(consumption: float, gamma: float = 1.5) -> float:
    """Calculate CRRA utility.

    Args:
        consumption: Consumption level (must be positive).
        gamma: Coefficient of relative risk aversion.

    Returns:
        Utility value.

    """
    ...
```

## Docstring Style

Docstrings and inline comments describe the code's *current* state in user-facing terms.
The 9-month-without-PR-context reader is the audience: a docstring that survives that
test stays useful; one that rehearses the diff or the prior implementation rots
immediately.

This applies to **all** docstrings and comments — source and tests. For tests
specifically, see also the "Test docstrings — describe behavior, not history" subsection
in the Testing section.

### Describe state, not history

State what is true now. Don't reference prior designs, removed code, or what was
changed. Words like "earlier", "previously", "now", "formerly", "the old", "before the
fix" are red flags.

```python
# Good — forward-looking constraint
class _DiagnosticRow:
    """Metadata captured during the backward-induction loop.

    Holds only Python-scalar metadata — no device-array references —
    so every (regime, period) row stays at a few bytes regardless of
    grid size.
    """


# Bad — rehearses prior design
class _DiagnosticRow:
    """Metadata captured during the backward-induction loop.

    Holds only Python-scalar metadata. The earlier design captured
    state_action_space and a closure directly on each row, which
    pinned every period's V template in device memory until the
    post-loop flush.
    """
```

### No PR numbers, no model-specific magic numbers

PR references (`#334 removed the host stalls`, `the bug was fixed in #42`) rot as the
codebase evolves and provide no useful signal to a reader who isn't already in context.
Magic numbers tied to a specific model size or hardware
(`~2 MB at production grid sizes`, `fits on a 16 GB device`) imply a fixed scale that's
only true on whichever model/box the comment was written against. State the qualitative
dependency instead.

```python
# Good — qualitative dependency
# Frees per-period intermediate buffers (V_arr-shaped, so
# model-dependent) so they don't stack up across the loop.

# Bad — PR reference + magic number
# Frees per-period intermediate buffers (~2 MB each at production
# grid sizes) so we don't re-introduce the host stalls that #334
# removed.
```

### Bulleted lists for enumerated cases

When describing a fixed set of cases (log levels, regime kinds, parameter types,
dispatch strategies), use one bullet per case rather than running prose. Bullets scan;
prose hides cases.

```python
# Good — scannable
# Gate falls out of the public log level:
# - `"off"` ⇒ nothing (skips even the NaN fail-fast)
# - `"warning"` / `"progress"` ⇒ NaN/Inf only
# - `"debug"` ⇒ adds the min/max/mean trio


# Bad — buried in prose
# Gate falls out of the public log level: `"off"` ⇒ nothing,
# `"warning"` / `"progress"` ⇒ NaN/Inf only, `"debug"` ⇒ adds the
# min/max/mean trio. `"off"` skips even the NaN fail-fast.
```

## Pure Functions

Write pure functions whenever possible:

1. Same inputs → same outputs
1. No side effects

```python
# Good: Separate I/O from logic
def task_example(path_in: Path, path_out: Path) -> None:
    data = pd.read_csv(path_in)  # I/O at boundary
    result = process_data(data)  # Pure logic
    result.to_pickle(path_out)  # I/O at boundary


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pure function - all logic here."""
    ...
```

## Error Handling

Raise early, with a message naming the offending value. Factor validation into
`_fail_if_...` helpers:

```python
def _fail_if_not_list(data: Any) -> None:
    if not isinstance(data, list):
        msg = f"data must be a list, not {type(data).__name__}"
        raise TypeError(msg)
```

## Testing

### Test-Driven Development — always

**Always write the test first, watch it fail, then implement.** No exceptions for new
behavior or bug fixes. Tests are not an afterthought, they are the spec.

The cycle:

1. **Red.** Write a failing test that asserts the desired behavior in user-facing terms.
   Run it. Confirm it fails for the *right* reason (the missing behavior — not a typo,
   not an import error).
1. **Green.** Write the smallest amount of code that makes the test pass.
1. **Refactor.** Clean up while keeping the test green.

Apply per case:

- **New feature** → red-green-refactor.
- **Bug fix** → reproduce as a failing test before writing the fix. The test then
  prevents regression.
- **Refactor (no behavior change)** → existing tests are the spec. Keep them green
  before, during, and after. No new test needed if behavior is unchanged; if you find a
  behavior gap, fill it with a new test *before* refactoring.

### Test docstrings — describe behavior, not history

Test docstrings state what *should* be true, in user-facing terms. Pretend the reader
has never seen the PR. They should not need to.

```python
# Good — behavior, in plain language
def test_simulate_with_chained_transitions_yields_expected_next_wealth():
    """`next_wealth_t = wealth_t - c_t + 0.1 * next_aime_t` holds in simulation."""


# Bad — rehearses the prior bug or implementation history
def test_solve_resolves_chain_via_dags():
    """Before the fix, `_resolve_fixed_params` raised
    `InvalidParamsError: Missing required parameter: ...` because
    `create_regime_params_template` classified ..."""
```

Rule of thumb: **would the docstring still make sense in 9 months without the PR
context?** If not, rewrite it.

### Concrete-value assertions

Assert *what* the result is, not just that it didn't crash.

```python
# Good — analytical value with explicit tolerance
np.testing.assert_allclose(curr["wealth"], expected_next_wealth, atol=1e-6)

# Bad — passes whether the math is right or not
assert not jnp.any(jnp.isnan(V_arr))
assert df["wealth"].notna().all()
```

`not isnan` and `no exception raised` belong in CI smoke tests, not in the unit tests
for the feature itself.

### Mechanics

Name tests `test_<function>_<behavior>` in `test_<module>.py`, and keep **one assertion
per test** — parametrize rather than stacking assertions in one body.

## Type Checking

Use **ty** (not mypy, not pyright). ty runs as a pre-commit hook
([`astral-sh/ty-pre-commit`](https://github.com/astral-sh/ty-pre-commit)) — part of
`prek run --all-files` — resolving third-party imports from the pixi environment named
in `[tool.ty] environment.python`. Run `pixi install` once so that environment exists.

- Suppress with `# ty: ignore[rule-name]` (never `# type: ignore`); always name the
  rule.

## Verification After Changes

Run these checks after making code changes. Skip any that don't apply to the project.

1. **Lockfile**: If `pyproject.toml` changed, run `pixi lock` and stage the updated
   `pixi.lock`. Never commit or push a `pyproject.toml` change without re-locking — a
   stale lock breaks CI (see "Always re-lock before committing").
1. **Pre-commit (incl. type checking)**: Stage new files, then `prek run --all-files`
   (or `pixi run prek run --all-files`). This runs ruff, formatting, and the `ty` hook.
   Fix any failures.
1. **Tests**: `pixi run tests` (or the project's test task).
1. **Notebook diffs**: If `.ipynb` files changed
   1. verify the diff looks like clean cell-content changes, not JSON noise (cell
      metadata, execution counts, output blobs). If the diff is bloated, the notebook
      was not properly stripped — run nbstripout before committing
   1. Make sure notebook cells are properly formatted (each line in a cell is a new json
      line, not one cell=one line).
   1. Use actual UTF-8 characters everywhere — in markdown cells, Python strings, and
      f-strings. Never write unicode escape sequences; write the actual characters (`—`,
      `μ`) directly.
