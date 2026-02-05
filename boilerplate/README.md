# Boilerplate Rules

Common boilerplate configurations for project/repository setup.

- Apply these rules to a project configuration. Ask about which project tier the project
  belongs to, do not try to determine it yourself.
- Do NOT overwrite exclusions of `ruff` tools / `ty` configuration / etc. unless
  explicitly asked to do this.
- In case there is a pre-existing `uv` setup, do NOT add `pixi`.
- If a GitHub Actions workflow exists, update that if necessary.

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
`{tests, tests-with-cov, tests-jax, ty, docs, view-docs, view-paper, view-pres, ...}`

- `ty` task should run `ty check`
- Include `ty` in the tests feature (not as a separate environment and not in the
  general pypi dependencies)

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

[tool.hatch.build.hooks.vcs]
version-file = "src/project_name/_version.py"

[tool.hatch.build.targets.sdist]
exclude = [ "tests" ]
only-packages = true

[tool.hatch.build.targets.wheel]
only-include = [ "src" ]
sources = [ "src" ]

[tool.hatch.metadata]
allow-direct-references = true

[tool.hatch.version]
source = "vcs"

[tool.pixi.workspace]
channels = [ "conda-forge" ]
platforms = [ "linux-64", "osx-64", "osx-arm64", "win-64" ]

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

[tool.ruff]
fix = true
target-version = "py314"
unsafe-fixes = false

lint.select = [ "ALL" ]
lint.extend-ignore = [
  "COM812", # Conflicts with ruff-format
  "EM101",  # Exception must not use a string literal
  "EM102",  # Exception must not use an f-string literal
  "FIX002", # Line contains TODO
  "ISC001", # Conflicts with ruff-format
  "TC001",  # Move application import into a type-checking block
  "TC002",  # Move third-party import into a type-checking block
  "TC003",  # Move standard library import into a type-checking block
  "TRY003", # Long messages outside exception class
]
lint.per-file-ignores."tests/*" = [
  "INP001", # Implicit namespace packages
  "S101",   # Use of assert
]
lint.pydocstyle.convention = "google"

[tool.ty.rules]
ambiguous-protocol-member = "error"
deprecated = "error"
division-by-zero = "error"
ignore-comment-unknown-rule = "error"
invalid-argument-type = "error"
invalid-ignore-comment = "error"
invalid-return-type = "error"
possibly-missing-attribute = "error"
possibly-missing-implicit-call = "error"
possibly-missing-import = "error"
possibly-unresolved-reference = "error"
redundant-cast = "error"
undefined-reveal = "error"
unresolved-global = "error"
unsupported-base = "error"
unused-ignore-comment = "error"
useless-overload-body = "error"

[tool.pytest.ini_options]
addopts = [ "--pdbcls=pdbp:Pdb" ]
filterwarnings = [ ]
norecursedirs = [ "docs" ]

[tool.pytask.ini_options]
paths = [ "./src/project_name" ]
pdbcls = "pdbp:Pdb"

[tool.yamlfix]
line_length = 88
none_representation = "null"
sequence_style = "block_style"
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
target-version = "py313"

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
    rev: v2.12.1
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
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.11
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
    rev: 0.8.2
    hooks:
      - id: nbstripout
        args:
          - --extra-keys
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
        files: (CLAUDE\.md|README\.md)
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
    rev: v0.14.11
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

# Documentation
docs/_build/

# IDE
.idea/
.vscode/

# Jupyter
.ipynb_checkpoints/

# macOS
.DS_Store

# pixi
.pixi/

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

# Documentation
docs/_build/

# IDE
.idea/
.vscode/

# Jupyter
.ipynb_checkpoints/

# LaTeX
*-blx.bib
*.aux
*.bbl
*.bcf
*.blg
*.fls
*.log
*.out
*.run.xml
*.synctex.gz
*.toc

# macOS
.DS_Store

# pixi
.pixi/

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

# Python
__pycache__/
*.py[cod]

# Ruff
.ruff_cache/
```
