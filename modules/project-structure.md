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

Each project root has `AGENTS.md` (the content) plus thin `CLAUDE.md` and `GEMINI.md`
wrappers, each containing only `@AGENTS.md`. The `GEMINI.md` is what lets the Gemini CLI
— and roborev code reviews — pick up the shared standards. When `AGENTS.md` lives in a
parent directory or submodule, adjust the include path accordingly (e.g.
`@../AGENTS.md`).
