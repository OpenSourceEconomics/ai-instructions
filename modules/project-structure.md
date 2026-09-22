# Project Structure

Research projects follow the EPP layout:

```
src/<project>/
├── config.py           # defines SRC / BLD paths
├── original_data/
├── data_management/
├── analysis/
└── final/
bld/                     # generated outputs, gitignored
tests/
pyproject.toml
```

`config.py` derives paths from `__file__`:

```python
from pathlib import Path

SRC = Path(__file__).parent.resolve()
BLD = SRC.joinpath("..", "..", "bld").resolve()
```

Keep raw data and code in version control, put every generated file in `bld/`, and never
rely on manual execution order — let pytask resolve dependencies.

## AI agent instruction files

Each project root has a single `AGENTS.md`; there are no `CLAUDE.md` or `GEMINI.md`
wrappers. Claude Code reads `AGENTS.md` only when no `CLAUDE.md` exists in the project
or any directory above it, so a leftover wrapper — including one in a parent workspace
directory — stops the project's `AGENTS.md` from loading.
