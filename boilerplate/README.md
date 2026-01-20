# Boilerplate Rules

Common boilerplate configurations for project/repository setup.

## Project Tiers

Project tiers are based on **content complexity**, not project type. Choose the tier based on
what the project actually contains.

| Tier | Description | Indicators |
|------|-------------|------------|
| **A: Full** | Installable packages, complex research | Has `src/` layout, tests, multiple dependencies |
| **B: Standard** | Research with pytask, courses with notebooks | Uses pytask, has data processing |
| **C: Minimal** | Documentation, simple LaTeX projects, notes | No Python code or very minimal |

## Key Conventions

| Aspect | Convention |
|--------|------------|
| **Build backend** | hatchling + hatch-vcs |
| **Docstring style** | Google |
| **Line length** | 88 |
| **Linter/formatter** | ruff with `select = ["ALL"]` |
| **Ordering** | Alphabetical within all blocks |
| **Package manager** | pixi only (no venv/env) |
| **pytest markers** | Only add when actually used |
| **Type checker** | ty (not mypy) |

---

## pyproject.toml

### Tier A/B: Full Configuration

```toml
# ======================================================================================
# Build system configuration
# ======================================================================================

[build-system]
build-backend = "hatchling.build"
requires = ["hatchling", "hatch-vcs"]

[tool.hatch.build.hooks.vcs]
version-file = "src/project_name/_version.py"

[tool.hatch.build.targets.sdist]
exclude = ["tests"]
only-packages = true

[tool.hatch.build.targets.wheel]
only-include = ["src"]
sources = ["src"]

[tool.hatch.metadata]
allow-direct-references = true

[tool.hatch.version]
source = "vcs"


# ======================================================================================
# Pixi configuration
# ======================================================================================

[tool.pixi.dependencies]
jupyterlab = "*"
pre-commit = "*"
pytest = "*"
pytest-cov = "*"
pytest-xdist = "*"

[tool.pixi.environments]
py311 = ["py311", "test"]
py312 = ["py312", "test"]
py313 = ["py313", "test"]
py314 = ["py314", "test"]
ty = ["ty"]

[tool.pixi.feature.py311.dependencies]
python = "~=3.11.0"

[tool.pixi.feature.py312.dependencies]
python = "~=3.12.0"

[tool.pixi.feature.py313.dependencies]
python = "~=3.13.0"

[tool.pixi.feature.py314.dependencies]
python = "~=3.14.0"

[tool.pixi.feature.test.tasks]
tests = "pytest tests"

[tool.pixi.feature.ty.pypi-dependencies]
ty = ">=0.0.9"

[tool.pixi.feature.ty.tasks]
ty = "ty check"

[tool.pixi.pypi-dependencies]
pdbp = "*"
project-name = { path = ".", editable = true }

[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "osx-arm64", "win-64"]


# ======================================================================================
# Project metadata
# ======================================================================================

[project]
authors = [
    { name = "Author Name", email = "email@example.com" },
]
classifiers = [
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
]
dependencies = []
description = "Short description"
dynamic = ["version"]
keywords = []
license = { file = "LICENSE" }
maintainers = [
    { name = "Maintainer Name", email = "email@example.com" },
]
name = "project-name"
readme = { file = "README.md", content-type = "text/markdown" }
requires-python = ">=3.11"

[project.urls]
Github = "https://github.com/org/project-name"
Repository = "https://github.com/org/project-name"
Tracker = "https://github.com/org/project-name/issues"


# ======================================================================================
# pytest configuration
# ======================================================================================

[tool.pytest.ini_options]
addopts = ["--pdbcls=pdbp:Pdb"]
filterwarnings = []
norecursedirs = ["docs"]


# ======================================================================================
# pytask configuration
# ======================================================================================

[tool.pytask.ini_options]
paths = ["./src/project_name"]
pdbcls = "pdbp:Pdb"


# ======================================================================================
# Ruff configuration
# ======================================================================================

[tool.ruff]
fix = true
target-version = "py311"
unsafe-fixes = false

[tool.ruff.lint]
extend-ignore = [
    "ANN",      # Type annotations (use ty instead)
    "COM812",   # Conflicts with ruff-format
    "D",        # Docstrings (enable selectively when ready)
    "EM101",    # Exception must not use a string literal
    "EM102",    # Exception must not use an f-string literal
    "FBT001",   # Boolean-typed positional argument
    "FBT002",   # Boolean default positional argument
    "FIX002",   # Line contains TODO
    "ISC001",   # Conflicts with ruff-format
    "PLR0913",  # Too many arguments
    "PLR2004",  # Magic value used in comparison
    "S101",     # Use of assert
    "TC002",    # Move third-party import into a type-checking block
    "TC003",    # Move standard library import into a type-checking block
    "TRY003",   # Long messages outside exception class
]
select = ["ALL"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["INP001"]

[tool.ruff.lint.pydocstyle]
convention = "google"


# ======================================================================================
# ty configuration
# ======================================================================================

[tool.ty.rules]
ambiguous-protocol-member = "error"
deprecated = "error"
division-by-zero = "error"
ignore-comment-unknown-rule = "error"
invalid-argument-type = "error"
invalid-ignore-comment = "error"
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


# ======================================================================================
# yamlfix configuration
# ======================================================================================

[tool.yamlfix]
line_length = 88
none_representation = "null"
sequence_style = "block_style"
```

### Tier C: Minimal Configuration

```toml
# ======================================================================================
# Build system configuration
# ======================================================================================

[build-system]
build-backend = "hatchling.build"
requires = ["hatchling"]


# ======================================================================================
# Project metadata
# ======================================================================================

[project]
name = "project-name"
requires-python = ">=3.13"
version = "0.1.0"


# ======================================================================================
# Ruff configuration
# ======================================================================================

[tool.ruff]
fix = true
target-version = "py313"

[tool.ruff.lint]
extend-ignore = [
    "ANN",      # Type annotations
    "COM812",   # Conflicts with ruff-format
    "D",        # Docstrings
    "EM101",    # Exception must not use a string literal
    "EM102",    # Exception must not use an f-string literal
    "FBT001",   # Boolean-typed positional argument
    "FBT002",   # Boolean default positional argument
    "FIX002",   # Line contains TODO
    "ISC001",   # Conflicts with ruff-format
    "PLR0913",  # Too many arguments
    "PLR2004",  # Magic value used in comparison
    "S101",     # Use of assert
    "TC002",    # Move third-party import into a type-checking block
    "TC003",    # Move standard library import into a type-checking block
    "TRY003",   # Long messages outside exception class
]
select = ["ALL"]

[tool.ruff.lint.pydocstyle]
convention = "google"
```

---

## .pre-commit-config.yaml

### Tier A/B: Full Configuration

```yaml
---
ci:
  autoupdate_schedule: monthly
repos:
  - repo: meta
    hooks:
      - id: check-hooks-apply
      - id: check-useless-excludes
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
          - mdformat-ruff
        args:
          - --wrap
          - '88'
        files: (CLAUDE\.md|README\.md)
```

### Tier C: Minimal Configuration

```yaml
---
ci:
  autoupdate_schedule: monthly
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
```

---

## .yamllint.yml

Use with all tiers that have pre-commit.

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
  indentation: {spaces: 2}
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
  - '*.yaml'
  - '*.yml'
  - .yamllint
```

---

## .gitignore

All entries are alphabetically ordered. Only pixi is used (no venv/env).

### Tier A: Libraries

```gitignore
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
