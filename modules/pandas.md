# Pandas

## Configuration

Always enable at script/notebook start:

```python
import pandas as pd

pd.options.mode.copy_on_write = True
pd.options.future.infer_string = True
```

## Key Practices

- Use `engine="pyarrow"` when reading CSV
- Never use `inplace` argument (deprecated)
- Use `.loc` for label-based selection, avoid `.iloc`
- Use `.query()` for readable filtering
- Never loop over rows (`iterrows`, row-wise `apply`)

## File Formats

- `.pkl` for intermediate files (not shared)
- `.arrow` for files to share
- Avoid `.dta` unless sharing with Stata

## Functional Data Cleaning

Always follow these rules:

1. Start with empty DataFrame
1. Touch each variable once
1. Use pure functions for each transformation

```python
def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(index=raw.index)
    df["var1"] = clean_var1(raw["Q001"])
    df["var2"] = clean_var2(raw["Q002"])
    return df
```

Do all data management in a collection of tables satisfying these rules (normal forms):

- Values have no internal structure
- Tables do not contain redundant information
- Variable names have no structure (long format, NOT wide format)

## Merging

- At the very end, merge / reshaping tables as needed for analysis
- Always specify keys: `pd.merge(left, right, on=["key1", "key2"])` or index
- Explicitly choose join type: `how="left"`
