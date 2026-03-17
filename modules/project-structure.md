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

## Reproducibility

- Include all source data and code
- Keep raw data and code in version control
- Put generated files in `bld/` (gitignored)
- Never rely on manual execution order
