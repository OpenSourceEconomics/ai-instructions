---
description: Generate a pytask task file from a description
argument-hint: <description of what the task should do>
allowed-tools: Read, Grep, Glob, Write, Edit
---

# New Task

Generate a pytask task file based on the user's description: **$ARGUMENTS**

## Steps

1. **Read the conventions.** `.ai-instructions/modules/pytask.md` is canonical for task
   structure, `Product` annotations, and the DataCatalog pattern — follow it rather than
   any remembered pytask API.

2. **Read the project's layout.** From `config.py`: the `SRC`/`BLD` constants, whether a
   `DataCatalog` is in use and under what name, and the numbering/naming convention of
   existing task files. Match what the project already does.

3. **Determine inputs and outputs** from the description, then write the task into the
   stage directory it belongs to (`data_management/`, `analysis/`, `final/`).

4. **If using a DataCatalog**, add the new entries to `config.py`.

5. **Tell the user to run `pixi run pytask --collect-only`** to confirm the task is
   discovered.

The failure mode specific to generating tasks: putting computation in the `task_*`
function. It does I/O only — read, call a pure `_`-prefixed helper, write — because the
helper is the part that can be unit-tested without touching the filesystem.
