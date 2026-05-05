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
- `pixi run ty` — type checking

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
`{py3XX, numpy, jax, cpu, cuda, cuda12, cuda13, tests, docs, type-checking}`

Can be combined like: `py314-jax`, `tests-cuda13`

### Tasks

Tasks should be from the set:
`{tests, tests-with-cov, tests-jax, ty, build-docs, view-docs, view-paper, view-pres, ...}`

- `ty` task should run `ty check`
- For projects with a single test environment, include `ty` in `feature.tests` (not as a
  separate environment and not in the general pypi dependencies)
- For projects with multiple test environments (e.g. `tests-cpu`, `tests-cuda`), move
  `ty` to a separate `feature.type-checking` and add a dedicated `type-checking`
  environment that includes only that feature, so `pixi run ty` resolves unambiguously

### CI / ReadTheDocs references

When renaming tasks or environments, also update references in:

- `.github/workflows/*.yml` — `pixi run -e <env> <task>` commands and `environments:` in
  `setup-pixi`
- `.readthedocs.yaml` — `pixi run -e docs <task>` in build jobs

To find the latest versions for GitHub Actions:

1. Run `pixi self-update` and note the version
1. Check https://github.com/prefix-dev/setup-pixi/tags for the latest setup-pixi version
1. Update `pixi-version:` and `uses: prefix-dev/setup-pixi@` accordingly

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
  "EM101",   # Exception must not use a string literal
  "EM102",   # Exception must not use an f-string literal
  "FIX002",  # Line contains TODO
  "ISC001",  # Conflicts with ruff-format
  "PLR0913", # Too many arguments in function definition
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
ty = "*"

[tool.pixi.feature.tests.tasks]
tests = "pytest"
tests-with-cov = "pytest --cov-report=xml --cov=./"
ty = "ty check"

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
    rev: v2.21.1
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
    rev: 0.37.2
    hooks:
      - id: check-github-workflows
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.12
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
ci:
  autoupdate_schedule: monthly
```

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
    rev: v0.15.12
    hooks:
      - id: ruff-check
        args:
          - --fix
      - id: ruff-format
ci:
  autoupdate_schedule: monthly
```

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
