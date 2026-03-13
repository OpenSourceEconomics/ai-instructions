---
description: Audit project code for coding standard compliance
allowed-tools: Read, Grep, Glob
---

# Verify Standards

Audit this project's Python code for compliance with the coding standards defined in
AGENTS.md and its modules. Produce a deviation report.

## Steps

1. **Load the applicable standards.** Read:
   - If `.ai-instructions/` exists: read AGENTS.md and all modules referenced in this
     project's CLAUDE.md `@` includes
   - Otherwise: ask the user for the path to the standards

2. **Scan the project's Python source files.** Focus on `src/` and `tests/` directories.
   Skip vendored code, generated files, and `bld/`.

3. **Check each standard category below.** For each violation found, record the file path,
   line number, and which standard is violated.

## Checks

### Critical Rules

- **Type hints**: All function signatures must have type annotations (args and return).
  Flag any `def` without annotations.
- **Pathlib**: Flag `os.path` usage, string concatenation for paths, hardcoded absolute
  paths outside the project.
- **Float comparisons**: Flag `== float_value` or `!= float_value` comparisons. Should
  use `np.isclose`, `math.isclose`, or tolerance-based checks.
- **Immutability**: Flag `@dataclass` without `frozen=True` for config/state classes.
  Flag mutable default arguments (`list`, `dict`, `set` defaults in signatures).

### Python Environment

- **Pixi**: Flag any `pip install`, `conda install`, `pip3 install` in scripts,
  Makefiles, or CI configs. Flag bare `python` or `python3` invocations (should be
  `pixi run python`).
- **src layout**: Flag if installable package code is not under `src/`.

### Code Quality

- **Naming**: Flag single-letter variable names (`n`, `c`, `s`, `u`, `x`, `y` outside
  list comprehensions and lambdas). Flag function names not starting with a verb.
  Flag `CamelCase` for non-classes.
- **Pure functions**: Flag functions that mix I/O with computation (reading files AND
  processing data in the same function body, outside task functions).
- **Error messages**: Flag bare `raise ValueError` or `raise TypeError` without a
  descriptive message string.

### Pandas (if applicable)

- **inplace**: Flag any `inplace=True` usage.
- **iterrows**: Flag `iterrows()`, `itertuples()`, row-wise `apply()`.
- **Legacy pd.options**: Flag any `pd.options.mode.copy_on_write` or
  `pd.options.future.infer_string` usage — these are unnecessary with pandas >= 3.0
  (CoW is always on, string inference is the default).

### NumPy (if applicable)

- **Legacy random**: Flag `np.random.seed()`, `np.random.rand()`, `np.random.randn()`,
  `np.random.random()`. Should use `np.random.default_rng()`.

### Type Checking

- **type: ignore**: Flag `# type: ignore` comments. Should use `# ty: ignore[rule-name]`.

## Output

Produce a summary table:

```
| Category | Violations | Files affected |
|----------|-----------|----------------|
| ...      | ...       | ...            |
```

Then list each violation with:
- `file_path:line_number` — description of violation
- Which standard it violates
- Suggested fix (brief)

Sort by severity: Critical Rules first, then Code Quality, then library-specific.
