# Boilerplate Rules

Common boilerplate configurations for project/repository setup.

- Apply these rules to a project configuration. Ask about which project tier the project
  belongs to, do not try to determine it yourself.
- Do NOT overwrite exclusions of `ruff` tools / `ty` configuration / etc. unless
  explicitly asked to do this.
- In case there is a pre-existing `uv` setup, do NOT add `pixi`.
- If a GitHub Actions workflow exists, update that if necessary.

## AI Tool Configuration

All project-specific agent instructions live in `AGENTS.md` at the project root. This
single file serves all AI coding tools.

| Tool           | Reads `AGENTS.md`? | Resolves `@` includes? | Extra file needed?                       |
| -------------- | ------------------ | ---------------------- | ---------------------------------------- |
| Claude Code    | Via `@AGENTS.md`   | Yes (nested, max 5)    | `CLAUDE.md` containing just `@AGENTS.md` |
| Gemini CLI     | Yes (auto)         | Yes                    | `GEMINI.md` containing just `@AGENTS.md` |
| OpenAI Codex   | Yes (primary)      | No                     | None                                     |
| GitHub Copilot | Yes (auto)         | No                     | None                                     |
| Cursor         | Yes (auto)         | No                     | None                                     |

### AGENTS.md (project root)

Put `@`-includes for shared standards at the top, then project-specific content below.
Claude and Gemini resolve the includes; other tools ignore them as plain text but still
read the project-specific sections.

```markdown
@.ai-instructions/profiles/tier-b-research.md
@.ai-instructions/modules/jax.md

# Project Name

## Overview

Brief project description.

## Build & Test

- `pixi run pytest` — run tests
- `pixi run pytask` — run task pipeline
- `prek run --all-files` — lint, format, and type-check (ty runs as a pre-commit hook)

## Architecture

Project-specific structure and conventions.
```

### CLAUDE.md (project root)

Only needed for Claude Code. Contains a single line:

```
@AGENTS.md
```

### GEMINI.md (project root)

Ensures the Gemini CLI (and roborev reviews) picks up the shared coding standards.
Contains a single line:

```
@AGENTS.md
```

### .ai-instructions submodule

Add this repo as a git submodule. **Always use HTTPS** (not SSH) — SSH URLs fail on CI
runners and ReadTheDocs.

```bash
git submodule add https://github.com/OpenSourceEconomics/ai-instructions .ai-instructions
```

## Project Tiers

Project tiers are based on **content complexity**, not project type. Choose the tier
based on what the project actually contains.

| Tier            | Description                                  | Indicators                                      |
| --------------- | -------------------------------------------- | ----------------------------------------------- |
| **A: Full**     | Installable packages, complex research       | Has `src/` layout, tests, multiple dependencies |
| **B: Standard** | Research with pytask, courses with notebooks | Uses pytask, has data processing                |
| **C: Minimal**  | Documentation, simple LaTeX projects, notes  | No Python code or very minimal                  |

## Key Conventions

| Aspect               | Convention                   |
| -------------------- | ---------------------------- |
| **Build backend**    | hatchling + hatch-vcs        |
| **Docstring style**  | Google                       |
| **Line length**      | 88                           |
| **Linter/formatter** | ruff with `select = ["ALL"]` |
| **TOML formatter**   | pyproject-fmt                |
| **Package manager**  | pixi only (no venv/env)      |
| **pytest markers**   | Only add when actually used  |
| **Type checker**     | ty (not mypy)                |

## Pixi Environment and Task Naming

### Environments

Environments should be from the set:
`{py3XX, numpy, jax, cpu, cuda, cuda12, cuda13, tests, docs}`

Can be combined like: `py314-jax`, `tests-cuda13`

### Tasks

Tasks should be from the set:
`{tests, tests-with-cov, tests-jax, build-docs, view-docs, view-paper, view-pres, ...}`

Type checking is **not** a pixi task — ty runs as a pre-commit hook (see
`.pre-commit-config.yaml`). It resolves third-party imports from the pixi environment
named in `[tool.ty] environment.python`, so run `pixi install` once.

### CI / ReadTheDocs references

When renaming tasks or environments, also update references in:

- `.github/workflows/*.yml` — `pixi run -e <env> <task>` commands and `environments:` in
  `setup-pixi`
- `.readthedocs.yaml` — `pixi run -e docs <task>` in build jobs

To find the latest versions for GitHub Actions:

1. Run `pixi self-update`, then `pixi --version`
1. Resolve the latest action versions from the releases API:
   ```bash
   gh api repos/prefix-dev/setup-pixi/releases --jq '.[0].tag_name'
   gh api repos/actions/checkout/releases --jq '.[0].tag_name'
   ```
1. Update `pixi-version:` and `uses: prefix-dev/setup-pixi@` accordingly

**`pixi-version:` must match the local pixi from step 1, not merely be recent.**
`pixi.lock` is written by whatever pixi a developer runs; CI then validates it with the
pinned binary. If local pixi is *newer* than the pin, CI is asking an older pixi to read
a newer lock — and because pixi is largely forward-tolerant that usually works, so the
mismatch goes unnoticed until a lock feature it cannot read appears. The reverse (CI
newer than local) is safe, as pixi reads older lock formats. Keeping both at latest
satisfies currency and compatibility at once.

**The version numbers in the workflow blocks below are illustrative, not canonical.**
They are refreshed by different commits than the pre-commit hook versions, so this file
can be at `origin/main` while its CI block is weeks old, and a project is often *ahead*
of it. Always resolve latest as above; never copy a version out of this README into a
project, which can silently downgrade it.

______________________________________________________________________

## pyproject.toml

### Tier A/B: Full Configuration

```toml
[build-system]
build-backend = "hatchling.build"
requires = [ "hatch-vcs", "hatchling" ]

[project]
name = "project-name"
description = "Short description"
readme = { file = "README.md", content-type = "text/markdown" }
keywords = [ ]
license = { file = "LICENSE" }
authors = [ { name = "Author Name", email = "email@example.com" } ]
maintainers = [ { name = "Maintainer Name", email = "email@example.com" } ]
requires-python = ">=3.11"
classifiers = [
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: MIT License",
  "Operating System :: MacOS :: MacOS X",
  "Operating System :: Microsoft :: Windows",
  "Operating System :: POSIX",
  "Programming Language :: Python :: 3 :: Only",
]
dynamic = [ "version" ]
dependencies = [ ]

[project.urls]
Github = "https://github.com/org/project-name"
Repository = "https://github.com/org/project-name"
Tracker = "https://github.com/org/project-name/issues"

[tool.hatch]
build.hooks.vcs.version-file = "src/project_name/_version.py"
build.targets.sdist.exclude = [ "tests" ]
build.targets.sdist.only-packages = true
build.targets.wheel.only-include = [ "src" ]
build.targets.wheel.sources = [ "src" ]
metadata.allow-direct-references = true
version.source = "vcs"

[tool.ruff]
fix = true
unsafe-fixes = false
lint.select = [ "ALL" ]
lint.extend-ignore = [
  "COM812",  # Conflicts with ruff-format
  "CPY001",  # Copyright notice at top of file
  "EM101",   # Exception must not use a string literal
  "EM102",   # Exception must not use an f-string literal
  "FIX002",  # Line contains TODO
  "ISC001",  # Conflicts with ruff-format
  "PLR0913", # Too many arguments in function definition
  "PLR0917", # Too many positional arguments
  "S301",    # pickle module (standard intermediate format)
  # TC001-TC003: TYPE_CHECKING guards. Always ignore for Python 3.14+ projects
  # (PEP 649 deferred evaluation makes them unnecessary).
  "TC001",   # Move application import into a type-checking block
  "TC002",   # Move third-party import into a type-checking block
  "TC003",   # Move standard library import into a type-checking block
  "TRY003",  # Long messages outside exception class
]
lint.per-file-ignores."task_*.py" = [
  "ARG001",  # Unused function argument (pytask signatures)
]
lint.per-file-ignores."tests/*" = [
  "D",       # Docstrings
  "INP001",  # Implicit namespace packages
  "PLR2004", # Magic value used in comparison
  "S101",    # Use of assert
]
lint.pydocstyle.convention = "google"

[tool.ty]
# ty resolves third-party imports from this pixi env (the official ty-pre-commit hook
# runs `uv check --no-project`, so uv neither creates a `.venv` nor resolves deps). Run
# `pixi install` once.
environment.python = ".pixi/envs/py314"
# Promote all warn/ignore-default rules to error.
# Rules that default to error are omitted (already enforced).
rules.ambiguous-protocol-member = "error"
rules.deprecated = "error"
rules.division-by-zero = "error"
rules.ignore-comment-unknown-rule = "error"
rules.ineffective-final = "error"
rules.invalid-enum-member-annotation = "error"
rules.invalid-ignore-comment = "error"
rules.invalid-legacy-positional-parameter = "error"

[tool.pytest]
ini_options.addopts = [ "--pdbcls=pdbp:Pdb" ]
ini_options.filterwarnings = [ ]
ini_options.norecursedirs = [ "docs" ]

[tool.pytask]
ini_options.paths = [ "./src/project_name" ]
ini_options.pdbcls = "pdbp:Pdb"

# codespell does NOT flag standard econ/numerics jargon (crra, egm, endog, exog,
# gmm, hessian, jacobian, heteroskedasticity, ...) — verified, so no entry is
# needed for those. What it does trip on is short abbreviations that collide with
# real words, and German text, where `ist`/`nd` and friends fire constantly.
# Extend per project rather than dropping the hook.
[tool.codespell]
ignore-words-list = "fpr,ist,mape,nd,nin"
skip = "*.lock,*.svg,*.bib,*.ipynb"

[tool.pyproject-fmt]
column_width = 88
max_supported_python = "3.14"
table_format = "long"
collapse_tables = [ "tool.hatch", "tool.pytest", "tool.pytask", "tool.ty" ]
expand_tables = [
  "tool.pixi.dependencies",
  "tool.pixi.environments",
  "tool.pixi.feature.tests.pypi-dependencies",
  "tool.pixi.feature.tests.tasks",
  "tool.pixi.pypi-dependencies",
  "tool.pixi.tasks",
  "tool.pixi.workspace",
]

[tool.yamlfix]
line_length = 88
none_representation = "null"
sequence_style = "block_style"

[tool.pixi.dependencies]
jupyterlab = "*"
prek = "*"
python = "~=3.14.0"

[tool.pixi.pypi-dependencies]
pdbp = "*"
project-name = { path = ".", editable = true }

[tool.pixi.feature.tests.pypi-dependencies]
pytest = "*"
pytest-cov = "*"
pytest-xdist = "*"

[tool.pixi.feature.tests.tasks]
tests = "pytest"
tests-with-cov = "pytest --cov-report=xml --cov=./"

[tool.pixi.environments]
py314 = [ "tests" ]

[tool.pixi.workspace]
channels = [ "conda-forge" ]
platforms = [ "linux-64", "osx-64", "osx-arm64", "win-64" ]
```

### Tier C: Minimal Configuration

```toml
[build-system]
build-backend = "hatchling.build"
requires = [ "hatchling" ]

[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.13"

[tool.ruff]
fix = true

lint.select = [ "ALL" ]
lint.extend-ignore = [
  "ANN",    # Type annotations
  "COM812", # Conflicts with ruff-format
  "CPY001", # Copyright notice at top of file
  "D",      # Docstrings
  "EM101",  # Exception must not use a string literal
  "EM102",  # Exception must not use an f-string literal
  "ISC001", # Conflicts with ruff-format
  "S101",   # Use of assert
  "TC001",  # Move application import into a type-checking block
  "TC002",  # Move third-party import into a type-checking block
  "TC003",  # Move standard library import into a type-checking block
  "TRY003", # Long messages outside exception class
]
lint.pydocstyle.convention = "google"

[tool.pyproject-fmt]
column_width = 88
max_supported_python = "3.14"
table_format = "long"
collapse_tables = [ "tool.hatch", "tool.pytest", "tool.pytask", "tool.ty" ]
```

______________________________________________________________________

## .pre-commit-config.yaml

**Note:** Do NOT alphabetize the outermost level (`ci`, `repos`). Keep logical order.

### Tier A/B: Full Configuration

```yaml
---
repos:
  - repo: meta
    hooks:
      - id: check-hooks-apply
      - id: check-useless-excludes
  - repo: https://github.com/tox-dev/pyproject-fmt
    rev: v2.27.1
    hooks:
      - id: pyproject-fmt
  - repo: https://github.com/lyz-code/yamlfix
    rev: 1.19.1
    hooks:
      - id: yamlfix
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-added-large-files
        args:
          - --maxkb=10000
      - id: check-ast
      - id: check-case-conflict
      - id: check-docstring-first
      - id: check-merge-conflict
      - id: check-toml
      - id: check-vcs-permalinks
      - id: check-yaml
      - id: debug-statements
      - id: end-of-file-fixer
      - id: fix-byte-order-marker
        types:
          - text
      - id: mixed-line-ending
        args:
          - --fix=lf
        description: Forces to replace line ending by the UNIX 'lf' character.
      - id: name-tests-test
        args:
          - --pytest-test-first
      - id: no-commit-to-branch
        args:
          - --branch
          - main
      - id: trailing-whitespace
  - repo: https://github.com/adrienverge/yamllint.git
    rev: v1.38.0
    hooks:
      - id: yamllint
  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.38.0
    hooks:
      - id: check-github-workflows
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.2
    hooks:
      - id: ruff-check
        args:
          - --fix
        types_or:
          - jupyter
          - pyi
          - python
      - id: ruff-format
        types_or:
          - jupyter
          - pyi
          - python
  - repo: https://github.com/astral-sh/ty-pre-commit
    rev: v0.0.71
    hooks:
      - id: ty
        # `--no-project` stops uv from creating a `.venv`/`uv.lock` in this
        # pixi-managed repo; ty resolves third-party imports from the env named
        # in `[tool.ty] environment.python` (run `pixi install` once).
        args:
          - --no-project
  - repo: https://github.com/kynan/nbstripout
    rev: 0.9.1
    hooks:
      - id: nbstripout
        args:
          - --extra-keys
          # Remove metadata.kernelspec from this line if using Jupyter Book 2
          # (mystmd), which needs kernelspec to select the execution kernel.
          - metadata.kernelspec metadata.language_info.version metadata.vscode
  - repo: https://github.com/executablebooks/mdformat
    rev: 1.0.0
    hooks:
      - id: mdformat
        additional_dependencies:
          - mdformat-gfm
          - mdformat-gfm-alerts
          - mdformat-ruff
        args:
          - --wrap
          - "88"
        files: (AGENTS\.md|CLAUDE\.md|README\.md|modules/.*\.md|profiles/.*\.md)
  - repo: https://github.com/codespell-project/codespell
    rev: v2.4.3
    hooks:
      - id: codespell
        additional_dependencies:
          - tomli
  - repo: local
    hooks:
      # Runs at pre-commit stage and fails if the config declares pre-push hooks
      # that this clone never installed — otherwise they look active and silently
      # never fire.
      - id: pre-push-hooks-installed
        name: pre-push hooks are installed in this clone
        entry: .ai-instructions/hooks/check_pre_push_installed.py
        language: script
        pass_filenames: false
        always_run: true
      # `--check` re-solves and compares without writing, so it cannot dirty the
      # worktree. pre-push, not pre-commit: a mid-branch commit may legitimately
      # lag the lock, but a push with a stale lock burns a CI cycle.
      - id: pixi-lock-check
        name: pixi.lock is in sync with the manifest
        entry: pixi lock --check
        language: system
        pass_filenames: false
        files: ^(pyproject\.toml|pixi\.toml|pixi\.lock)$
        stages:
          - pre-push
      - id: notebook-cell-source-format
        name: notebook cell source is a JSON array of lines
        entry: .ai-instructions/hooks/fix_notebook_cell_source.py
        language: script
        types:
          - jupyter
      - id: no-hardcoded-user-paths
        name: no hardcoded user-specific absolute paths
        language: pygrep
        entry: (/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/|[A-Za-z]:\\Users\\)
        types_or:
          - python
          - toml
      - id: no-section-separator-comments
        name: no decorative section-separator comments
        language: pygrep
        entry: ^\s*#\s*[-=#_*]{10,}\s*$
        types:
          - python
      # Catches the labelled forms only — PR/issue numbers, `E<n>`/`F<n>`
      # finding labels, `round-<n>`, `pre-fix`. Prose that rehearses history
      # without a label stays a review responsibility.
      - id: no-internal-references
        name: no references a reader cannot reach from the checkout
        language: pygrep
        entry: '(?:^|[\s(\[])\#[0-9]{2,5}\b(?!\.[0-9])|(?i:\b(?:round|wave)-[0-9]+\b)|(?i:\b(?:audit|review|finding|witness|defect|bug|fix|guard)\s+)(?:finding\s+)?[EF][0-9]{1,2}\b|\b[EF][0-9]{1,2}(?i:\s+(?:fix|guard|bug|defect|witness|signature|regression|finding|audit)\b)|(?:^|\s)\((?:the\s+)?(?!(?:F8|F16|F32|F64)\b)[EF][0-9]{1,2}[''’]?(?:\s*[,/]\s*[EF][0-9]{1,2}[''’]?)*(?:[,)\s])|(?i:\b(?:pre|post)-fix\b)'
        types:
          - python
ci:
  autoupdate_schedule: monthly
  # pre-commit.ci has no pixi environments and blocks network at hook runtime;
  # the GitHub Actions `run-ty` job covers type checking, and pixi-lock-check
  # needs a pixi binary that pre-commit.ci does not provide.
  skip:
    - ty
    - pixi-lock-check
```

The `pre-push` stage needs installing once per clone — `prek install -t pre-push`
alongside the usual `prek install`. The `pre-push-hooks-installed` hook above exists so
that omission fails loudly on the next commit instead of going unnoticed.

`no-hardcoded-user-paths`, `no-section-separator-comments` and `no-internal-references`
mechanize rules `AGENTS.md` already states in prose. They are near-free on actively
developed projects but can fire heavily on older code; add `exclude:` for legacy
directories rather than dropping the hook.

`no-internal-references` is deliberately calibrated for a low false-positive rate rather
than for coverage, since a hook that cries wolf gets excluded wholesale. It matches a
finding label only next to the vocabulary that makes it a reference (`audit F2`,
`the F1 bug`, `(E4, F7 guard)`), never a bare `F7`; a parenthesised label list only
after a delimiter, so a call's argument list (`floordiv(E1, E2)`) and a dtype tuple
(`(F32, BF16)`) stay clean; and an issue number only at two-to-five digits without a
decimal tail, so a CSS hex colour (`#000000`), an ordinal (`case #2`) and a citation
(`AMS55 #15.3.10`) stay clean. Measured against the installed `jax` source — 618 files,
no relation to any project's audit vocabulary — it produces six hits, all six genuine
PR/issue references in comments, and no false positives. Projects that legitimately use
`E<n>`/`F<n>` as mathematical notation should `exclude:` those modules.

It is scoped to `python` to match its siblings. Widening it to `markdown` catches design
notes too, at the cost of tripping on any document that quotes the banned forms as
examples — this file, for one.

### Tier C: Minimal Configuration

```yaml
---
repos:
  - repo: meta
    hooks:
      - id: check-useless-excludes
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-toml
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.2
    hooks:
      - id: ruff-check
        args:
          - --fix
      - id: ruff-format
ci:
  autoupdate_schedule: monthly
```

______________________________________________________________________

## .github/workflows/main.yml

Runs tests and type checking on every push to `main` and every pull request. Use the
`.yml` extension (not `.yaml`), matching GitHub's own convention. Pin every action and
the `pixi-version`, and refresh them with the steps under *CI / ReadTheDocs references*
above.

### Tier A/B: Full Configuration

The matrix below targets a single Python version (3.14). Libraries that support older
versions add `py311`, `py312`, `py313` to the `environment` list.

```yaml
---
name: main
# Automatically cancel a previous run.
concurrency:
  group: ${{ github.head_ref || github.run_id }}
  cancel-in-progress: true
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - '*'
jobs:
  run-tests:
    name: Run tests for ${{ matrix.os }} on ${{ matrix.environment }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os:
          - ubuntu-latest
          - macos-latest
          - windows-latest
        environment:
          - py314
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: prefix-dev/setup-pixi@v0.10.1
        with:
          pixi-version: v0.76.2
          cache: true
          cache-write: ${{ github.event_name == 'push' && github.ref_name == 'main' }}
          frozen: true
          environments: ${{ matrix.environment }}
      - name: Run tests without coverage
        if: ${{ !(runner.os == 'Linux' && matrix.environment == 'py314') }}
        run: pixi run --locked -e ${{ matrix.environment }} tests
        shell: bash -el {0}
      - name: Run tests with coverage
        if: runner.os == 'Linux' && matrix.environment == 'py314'
        run: pixi run --locked tests-with-cov
        shell: bash -el {0}
      - name: Upload coverage reports
        if: runner.os == 'Linux' && matrix.environment == 'py314'
        uses: codecov/codecov-action@v7.0.0
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
  run-ty:
    name: Run ty
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: prefix-dev/setup-pixi@v0.10.1
        with:
          pixi-version: v0.76.2
          cache: true
          cache-write: ${{ github.event_name == 'push' && github.ref_name == 'main' }}
          frozen: true
          environments: py314
      - name: Run ty
        run: pixi run --locked -e py314 prek run ty --all-files
        shell: bash -el {0}
```

### Tier C: Minimal

Minimal projects (documentation, LaTeX, notes) have no test suite and need no workflow —
pre-commit.ci handles linting and formatting.

______________________________________________________________________

## .github/workflows/bibliography.yml

For any repository containing `.bib` files, regardless of tier. Verifies that every DOI
resolves and that the work it points to actually matches the entry's title, year, and
first author — the failure mode that survives every formatter and every proofread,
because the citation *looks* authoritative and the next author inherits it unchecked.

This belongs in CI rather than pre-commit for two reasons: it needs network access, so a
flaky connection must not be able to block a commit; and correctness here decays after
merge, as DOIs are withdrawn, reassigned, or corrected. The monthly schedule catches
that drift, which a commit-time check never would.

`verify_bibliography.py` is standard-library only, so this job needs no pixi
environment.

```yaml
---
name: bibliography
concurrency:
  group: ${{ github.head_ref || github.run_id }}
  cancel-in-progress: true
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    # A DOI can be withdrawn or corrected long after the PR that added it merged.
    - cron: 0 6 1 * *
jobs:
  verify-citations:
    name: Verify citations against CrossRef
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          # `.ai-instructions` carries the verification script.
          submodules: true
      - uses: actions/setup-python@v7
        with:
          python-version: '3.14'
      - name: Verify bibliography
        env:
          # CrossRef's polite pool: identified callers get better rate limits.
          MAILTO: ${{ vars.CROSSREF_MAILTO }}
        run: |
          set -euo pipefail
          mapfile -t BIB < <(git ls-files '*.bib')
          if [ ${#BIB[@]} -eq 0 ]; then
            echo "No .bib files tracked; nothing to verify."
            exit 0
          fi
          python .ai-instructions/hooks/verify_bibliography.py \
            --online --mailto "${MAILTO}" "${BIB[@]}"
```

Set the `CROSSREF_MAILTO` repository variable to a contact address. Without it CrossRef
still answers, but from the throttled anonymous pool.

Severity is deliberately asymmetric, so that only a definite contradiction can fail a
build:

- **Error** — a DOI that CrossRef does not know; a DOI whose title denotes a different
  work; a year contradicting the registry by more than one; a duplicate citation key; an
  entry with no title, year, author, or editor.
- **Warning** — no DOI at all (the common case: DOI coverage in an economics
  bibliography is routinely under 5%, so requiring one would make the check unusable), a
  first author that disagrees, a missing venue field, or any network failure.

Pass `--require-doi` for a curated bibliography where every entry should be resolvable,
and `--warnings-as-errors` to tighten the gate once a repository is clean. Add
`--cache .doi-cache.json` (with `actions/cache`) to avoid re-querying unchanged DOIs.

Titles are compared after stripping LaTeX; a title that contains the other counts as
agreement, since registries frequently store `Main Title` where the bibliography has
`Main Title: Subtitle`.

______________________________________________________________________

## .yamllint.yml

Use with all tiers that have prek.

```yaml
---
rules:
  braces: enable
  brackets: enable
  colons: enable
  commas: enable
  comments:
    level: warning
  comments-indentation:
    level: warning
  document-end: disable
  document-start:
    level: warning
  empty-lines: enable
  empty-values: disable
  float-values: disable
  hyphens: enable
  indentation: { spaces: 2 }
  key-duplicates: enable
  key-ordering: disable
  line-length:
    allow-non-breakable-inline-mappings: true
    allow-non-breakable-words: true
    max: 88
  new-line-at-end-of-file: enable
  new-lines:
    type: unix
  octal-values: disable
  quoted-strings: disable
  trailing-spaces: enable
  truthy:
    level: warning
yaml-files:
  - "*.yaml"
  - "*.yml"
  - .yamllint
```

______________________________________________________________________

## .gitignore

All entries are alphabetically ordered within sections. Only pixi is used (no venv/env).

### Tier A: Libraries

```gitignore
# Claude Code
.claude/

# Distribution / packaging
*.egg
*.egg-info/
*.manifest
*.spec
.eggs/
.installed.cfg
build/
dist/
MANIFEST
sdist/
wheels/

# IDE
.idea/
.vscode/

# Jupyter / Jupyter Book
.ipynb_checkpoints/
_build

# macOS
.DS_Store

# pixi
.pixi/
node_modules/

# Python
__pycache__/
*.py[cod]
*.so
*$py.class

# Ruff
.ruff_cache/

# Testing
.cache/
.coverage
.coverage.*
.hypothesis/
.pytest_cache/
coverage.xml
htmlcov/

# Version file (generated by hatch-vcs)
src/*/_version.py
```

### Tier B: Research Projects

```gitignore
# Claude Code
.claude/

# Data files
*.parquet
*.pkl

# Distribution / packaging
*.egg
*.egg-info/
*.manifest
*.spec
.eggs/
.installed.cfg
build/
dist/
MANIFEST
sdist/
wheels/

# IDE
.idea/
.vscode/

# Jupyter / Jupyter Book
.ipynb_checkpoints/
_build

# LaTeX
*-blx.bib
*.aux
*.bbl
*.bcf
*.blg
*.fdb_latexmk
*.fls
*.lof
*.log
*.lot
*.nav
*.out
*.run.xml
*.snm
*.synctex.gz
*.toc
*.vrb
*.xdv

# macOS
.DS_Store

# pixi
.pixi/
node_modules/

# Python
__pycache__/
*.py[cod]
*.so
*$py.class

# pytask
.pytask/
.pytask.sqlite3
bld/
out/
pytask.lock
pytask.lock.journal

# Ruff
.ruff_cache/

# Testing
.cache/
.coverage
.coverage.*
.hypothesis/
.pytest_cache/
coverage.xml
htmlcov/

# Version file (generated by hatch-vcs)
src/*/_version.py
```

### Tier C: Minimal

```gitignore
# Claude Code
.claude/

# IDE
.idea/
.vscode/

# macOS
.DS_Store

# pixi
.pixi/
node_modules/

# Python
__pycache__/
*.py[cod]

# Ruff
.ruff_cache/
```
