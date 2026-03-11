# Pytask

Use modern pytask syntax with `Annotated` and `Product` markers.

## Basic Task with Product Annotation

```python
from pathlib import Path
from typing import Annotated

import pandas as pd
from pytask import Product

from my_project.config import BLD, SRC


def task_clean_data(
    raw_file: Path = SRC / "original_data" / "data.arrow",
    output_file: Annotated[Path, Product] = BLD / "clean_data.pkl",
) -> None:
    raw = pd.read_feather(raw_file)
    clean = _clean_data(raw)
    clean.to_pickle(output_file)


def _clean_data(raw: pd.DataFrame) -> pd.DataFrame: ...
```

## Return Annotation for Simple Outputs

When the task's primary purpose is producing a single file:

```python
def task_create_summary() -> Annotated[str, Path("summary.txt")]:
    return "Summary content here"
```

## Data Catalog Pattern

For projects with many data files, use a `DataCatalog`:

```python
# src/my_project/config.py
from pytask import DataCatalog

DATA_CATALOG = DataCatalog()
DATA_CATALOG["raw_data"] = SRC / "original_data" / "data.arrow"
DATA_CATALOG["clean_data"] = BLD / "clean_data.pkl"
DATA_CATALOG["results"] = BLD / "results.pkl"
```

```python
# src/my_project/data_management/task_clean.py
from my_project.config import DATA_CATALOG


def task_clean_data(
    raw_file: Path = DATA_CATALOG["raw_data"],
    output_file: Annotated[Path, Product] = DATA_CATALOG["clean_data"],
) -> None: ...
```

## Task Conventions

- Task files: `task_*.py`
- Task functions: `task_*`
- Use `Annotated[Path, Product]` for outputs
- Keep tasks focused: read → compute (via helper) → write
- Helper functions do the actual work (testable, pure)
