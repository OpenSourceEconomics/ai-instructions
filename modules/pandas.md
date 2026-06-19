# Pandas

Requires **pandas >= 3.0** — Copy-on-Write and string inference are always on, so no
`pd.options` setup is needed. Read CSVs with `engine="pyarrow"`. Never use the
deprecated `inplace` argument. (Routine practice — `.loc` over `.iloc`, `.query` for
filters, no `iterrows` / row-wise `apply` — is assumed.)

## File formats

- `.pkl` — intermediate files, not shared
- `.arrow` — files to share
- `.dta` — avoid unless sharing with Stata

## Functional data cleaning

Build the result column-by-column from an empty frame, touch each variable once, and use
one pure function per transformation:

```python
def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(index=raw.index)
    df["var1"] = clean_var1(raw["Q001"])
    df["var2"] = clean_var2(raw["Q002"])
    return df
```

Spell out every input column as a literal where its output is assigned — never an
f-string or loop, and never by handing a helper the whole frame to reach into; a helper
takes the specific Series it needs. This keeps provenance at the assignment site, and
grep-able: `out["y"] = f(df)` hides which columns feed `y`. A dynamic `df[f"x_{i}"]`
also silently skips a missing column, and any tool that selects inputs by scanning a
function for literal subscripts drops the reference entirely.

```python
# inputs visible at the assignment, not hidden behind _count_months(df)
df["n_months"] = df[["m_1", "m_2"]].astype("boolean").fillna(value=False).sum(axis=1)
```

Keep tables in normal form — atomic values, no redundancy, long not wide. Reshape and
merge only at the end, always with explicit keys and an explicit join type:

```python
pd.merge(left, right, on=["key1", "key2"], how="left")
```
