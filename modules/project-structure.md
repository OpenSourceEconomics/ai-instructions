# Project Structure

## Directory Layout

```
my_project/
├── src/my_project/
│   ├── config.py
│   ├── original_data/
│   ├── data_management/
│   ├── analysis/
│   └── final/
├── bld/           # Generated outputs (gitignored)
├── tests/
└── pyproject.toml
```

## Config File

```python
# src/my_project/config.py
from pathlib import Path

SRC = Path(__file__).parent.resolve()
BLD = SRC.joinpath("..", "..", "bld").resolve()
```

## AI Agent Instructions

Every project should have a `GEMINI.md` file at the repo root that references
`AGENTS.md` using the `@` include syntax, mirroring what `CLAUDE.md` does. This ensures
the Gemini CLI (used by roborev for code reviews) picks up the same coding standards.

```
# GEMINI.md
@AGENTS.md
```

If `AGENTS.md` is not at the repo root (e.g., in a parent directory or submodule),
adjust the path accordingly:

```
# GEMINI.md — when AGENTS.md is in a parent directory
@../AGENTS.md

# GEMINI.md — when using submodule @-references directly
@.ai-instructions/profiles/tier-a.md @.ai-instructions/modules/jax.md
```

## Reproducibility

- Include all source data and code
- Keep raw data and code in version control
- Put generated files in `bld/` (gitignored)
- Never rely on manual execution order
