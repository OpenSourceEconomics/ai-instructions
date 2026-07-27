---
description: Generate a pytask task file from a description
argument-hint: <description of what the task should do>
allowed-tools: Read, Grep, Glob, Write, Edit
---

# New Task

Generate a pytask task file based on the user's description: **$ARGUMENTS**

## Steps

1. **Understand the project layout.** Read the project's `config.py` to find:
   - `SRC` and `BLD` path constants
   - Whether a `DataCatalog` is used (and its variable name)
   - Existing task files for naming/numbering conventions

   If `.ai-instructions/modules/pytask.md` exists in this project, read it too — it is
   the canonical source for the conventions below.

2. **Determine inputs and outputs** from the user's description.

3. **Generate the task file** following these patterns:

### Task file template

```python
from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from <package>.config import BLD, SRC


def task_<name>(
    input_file: Path = SRC / "original_data" / "<input>.arrow",
    output_file: Annotated[Path, Product] = BLD / "<output>.pkl",
) -> None:
    """<Brief description>."""
    raw = pd.read_feather(input_file)
    result = _<helper_name>(raw)
    result.to_pickle(output_file)


def _<helper_name>(data: pd.DataFrame) -> pd.DataFrame:
    """<Pure function that does the actual work>."""
    ...
```

### With DataCatalog

If the project uses a `DataCatalog`, use catalog references instead of raw paths:

```python
from <package>.config import DATA_CATALOG


def task_<name>(
    input_file: Path = DATA_CATALOG["<input>"],
    output_file: Annotated[Path, Product] = DATA_CATALOG["<output>"],
) -> None: ...
```

## Rules

- **File naming**: `task_<descriptive_name>.py`
- **Function naming**: `task_<descriptive_name>` matching the file
- **Separation of concerns**: Task function handles I/O only (read input, call helper,
  write output). Helper function contains all logic and is pure.
- **Type hints**: All function signatures must have full type annotations
- **Annotated[Path, Product]**: Always use this for output parameters
- **No manual `.mkdir()`**: pytask creates a `Product` output's parent directory
  automatically — never create or check for it yourself inside the task
- **Helper functions**: Prefix with `_`, make them pure (no I/O), make them testable
- **One task per file** unless tasks are closely related
- **Imports**: Use project's config module for paths, not hardcoded strings

## After generating

- Place the file in the appropriate directory (e.g., `data_management/`, `analysis/`,
  `final/`)
- If using DataCatalog, add new entries to `config.py`
- Remind the user to run `pixi run pytask --collect-only` to verify the task is
  discovered
