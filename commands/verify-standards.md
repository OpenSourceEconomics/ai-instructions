---
description: Audit project code for coding standard compliance
allowed-tools: Read, Grep, Glob
---

# Verify Standards

Audit this project's Python code against the coding standards it actually includes, and
produce a deviation report.

## Steps

1. **Load the applicable standards.** Read `AGENTS.md` and every module it pulls in via
   `@.ai-instructions/` includes (directly, or through a `profiles/` include). Those
   files — not this command — are the definition of a violation. If `.ai-instructions/`
   is absent, ask the user for the path to the standards.

2. **Scan `src/` and `tests/`.** Skip vendored code, generated files, and `bld/`.

3. **Check every rule in the loaded standards**, including ones this command does not
   enumerate. Rules stated as preferences ("prefer", "whenever possible") are reported at
   lower severity than rules stated as absolutes ("mandatory", "never", "always").

Two checks worth calling out, because they need whole-file reading rather than grep:

- **Deep modules**: in each `src/` file, public functions must precede private `_`
  helpers. Flag files where helpers are interleaved with or precede the public API.
- **Docstrings/comments describing history**: flag "previously", "now", "formerly", "the
  old", "before the fix", PR numbers, and hardware- or model-size-specific magic numbers
  — in source *and* tests.

## Output

Produce a summary table:

```
| Category | Violations | Files affected |
|----------|-----------|----------------|
| ...      | ...       | ...            |
```

Then list each violation with:

- `file_path:line_number` — description of violation
- Which standard it violates, quoted from the file it came from
- Suggested fix (brief)

Sort by severity: Critical Rules first, then Code Quality, then library-specific.
