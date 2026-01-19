# AI Coding Standards

This document provides coding guidelines for AI agents, derived from the
[Effective Programming Practices for Economists](https://effective-programming-practices.vercel.app/) course.

---

# Background

## Operating Systems

### Key Knowledge

- There are two broad lines of operating systems: Unix-based/inspired (Linux, MacOS)
  and Windows.
- Linux and MacOS share Unix heritage, which means they have similar behaviors for many
  programming tasks.
- Windows has a completely separate history from Unix (originating from MS-DOS).
- Code that works on one operating system may not work on another due to fundamental
  differences.
- There are signs of convergence: Windows Subsystem for Linux (WSL) allows running
  Linux on Windows.

### DO

- Write cross-platform code whenever possible.
- Test code on multiple operating systems if the project targets different platforms.
- Use platform-agnostic libraries (e.g., `pathlib` in Python) for file operations.
- Consider using WSL when developing on Windows for Unix-like behavior.

### DON'T

- Assume code working on Windows will automatically work on MacOS/Linux or vice versa.
- Hardcode platform-specific assumptions without proper conditionals.
- Ignore platform differences when writing installation or setup instructions.

---

## File Systems

### Key Knowledge

- Unix-based systems (Linux, MacOS) use forward slashes `/` as directory separators.
- Windows uses backslashes `\` as directory separators.
- Unix root directory is `/`; Windows uses drive letters like `C:\`.
- Unix has a single directory tree; Windows has separate trees for each drive.
- MacOS uses `/Users/username/` while Linux uses `/home/username/`.
- **Critical**: Unix-based file systems are case-sensitive (`Documents` and `documents`
  are different), while Windows is case-insensitive.
- Modern Windows can accept forward slashes in paths, but Unix cannot use backslashes.

### DO

- Use forward slashes `/` for cross-platform compatibility (works on all systems).
- Use absolute paths when clarity is needed.
- Use platform-agnostic path handling libraries:
  - Python: `pathlib.Path` or `os.path`
  - Other languages: equivalent cross-platform path utilities
- Be consistent with file naming conventions to avoid case-sensitivity issues.
- Know where files are stored for reproducibility purposes.

### DON'T

- Use backslashes `\` in paths intended for cross-platform use.
- Mix case variations of the same filename (e.g., `Data.csv` and `data.csv`).
- Assume cloud sync services handle case conflicts gracefully.
- Rely on "recent documents" or search functionality for reproducible workflows.
- Hardcode paths like `C:\Users\...` or `/home/...` without abstraction.

### Path Examples

```python
# GOOD: Cross-platform path handling
from pathlib import Path
data_path = Path("data") / "input" / "file.csv"

# BAD: Hardcoded Windows path
data_path = "C:\\Users\\user\\data\\file.csv"

# BAD: Hardcoded Unix path
data_path = "/home/user/data/file.csv"

# ACCEPTABLE: Forward slashes work everywhere
data_path = "data/input/file.csv"
```

---

## Floating Point Numbers

### Key Knowledge

- Floating point numbers cannot represent all real numbers exactly.
- Many decimal fractions (like 0.1) have no exact binary representation.
- Floating point arithmetic can produce unexpected results due to rounding errors.
- The IEEE 754 standard defines how floating point numbers are stored and computed.
- Accumulated rounding errors can cause significant issues in numerical computations.

### DO

- Use appropriate tolerance when comparing floating point numbers.
- Use dedicated libraries for precise decimal arithmetic when needed (e.g., Python's
  `decimal` module).
- Be aware of potential precision loss in financial or scientific calculations.
- Use `math.isclose()` or `numpy.isclose()` for float comparisons in Python.
- Consider the order of operations to minimize accumulated errors.

### DON'T

- Compare floating point numbers with exact equality (`==`).
- Assume `0.1 + 0.2 == 0.3` will evaluate to `True`.
- Use floating point for currency calculations without understanding the implications.
- Ignore potential precision issues in iterative numerical algorithms.

### Examples

```python
# BAD: Direct equality comparison
if result == 0.3:
    print("Equal")

# GOOD: Use tolerance-based comparison
import math
if math.isclose(result, 0.3, rel_tol=1e-9):
    print("Close enough")

# GOOD: NumPy equivalent
import numpy as np
if np.isclose(result, 0.3):
    print("Close enough")

# For financial calculations, consider:
from decimal import Decimal
price = Decimal("19.99")
```

---

## Graph Theory Basics

### Key Knowledge

- A graph G is a pair (N, E) where N is a set of nodes and E is a set of edges.
- **Undirected graphs**: Edges are sets of two nodes (order does not matter).
- **Directed graphs**: Edges are ordered pairs of nodes (direction matters).
- **Chain**: Nodes connected in sequence.
- **Tree**: A connected graph with no cycles; only one path between any two nodes.
- **Arborescence**: A directed tree where each node has exactly one parent (except
  root).
- **Directed Acyclic Graph (DAG)**: A directed graph with no cycles; cannot return to a
  node by following edges.

### Applications in Programming

- **File systems** are trees (directories and files form a hierarchy).
- **Git** uses DAGs to track commits and branches.
- **Reproducible research** pipelines are DAGs (tasks depend on other tasks).
- **Build systems** use DAGs to determine compilation order.

### DO

- Understand that file systems are tree structures rooted at `/` (Unix) or drive letters
  (Windows).
- Use DAG-based workflow tools (like `pytask`, `make`, `dvc`) for reproducible research.
- Recognize that Git history forms a DAG, which explains merge behavior.
- Use graph visualization to understand complex dependencies.

### DON'T

- Create circular dependencies in build systems or research workflows.
- Confuse directed and undirected relationships when modeling problems.
- Assume all graph structures allow cycles when they may require acyclicity.

### Graph Type Quick Reference

| Type | Directed | Cycles Allowed | Key Property |
|------|----------|----------------|--------------|
| Chain | Can be either | No | Linear sequence |
| Tree | Undirected | No | One path between nodes |
| Arborescence | Yes | No | Each node has one parent |
| DAG | Yes | No | No directed cycles |
| General Graph | Either | Yes | Most flexible |

---

# Tools

## When to Use Shell vs. GUI

### DO use the shell for:

- **Package installation and environment management** - No GUI alternative exists;
  shell is required
- **Version control with git** - Shell is the recommended approach over Git GUIs or
  VS Code integrations
- **Running tests** for Python projects
- **Running automated research pipelines**

### Either shell or GUI is acceptable for:

- Debugging Python code (VS Code debugger is a valid alternative)
- Creating, copying, and deleting files (File Explorer is acceptable)
- Trying out code in a Python REPL (Jupyter Notebook is acceptable)

### DON'T use the shell for:

- Editing files with vim when a modern editor is available - use a modern editor
  instead

---

## File System Navigation

### Core Concepts

- Every shell session has a **present working directory (pwd)**
- By default, this is the user's home directory
- Most operations should be performed with pwd set to the project folder

### Essential Navigation Commands

#### Unix/Linux/macOS Commands

| Command | Purpose |
|---------|---------|
| `pwd` | Print the current working directory |
| `cd <path>` | Change directory to the specified path |
| `cd ..` | Move to the parent directory |
| `cd ~` | Move to the home directory |
| `ls` | List contents of the current directory |

#### Windows PowerShell Commands

| Command | Purpose |
|---------|---------|
| `Get-Location` (or `pwd`) | Print the current working directory |
| `Set-Location <path>` (or `cd <path>`) | Change directory to the specified path |
| `cd ..` | Move to the parent directory |
| `Get-ChildItem` (or `ls`) | List contents of the current directory |

---

## Best Practices for Shell Usage

### DO

1. **Always verify the current working directory** before executing commands that
   depend on relative paths - use `pwd` (Unix) or `Get-Location` (Windows)

2. **Use absolute paths** when precision is critical to avoid ambiguity about file
   locations

3. **Store projects close to the home directory** to minimize typing and simplify
   navigation. Recommended structure:
   ```
   /home/username/projects/
       project_1/
       project_2/
       course_name/
           exercises/
           assignments/
           final_project/
   ```

4. **Verify navigation with pwd** after using `cd` to confirm you are in the expected
   directory

5. **Use ls/Get-ChildItem** to inspect directory contents before operating on files

### DON'T

1. **Don't assume the working directory** - always check with `pwd` when uncertain

2. **Don't mix path separators** - use `/` for Unix/macOS and `\` for Windows

3. **Don't forget that `cd ..`** moves to the parent directory, not a directory
   literally named `..`

---

# Git

## Repository Management

### Creating Repositories

**DO:**
- Use `git init` to convert a normal folder into a git repository
- This creates a `.git` folder that tracks your project

**DON'T:**
- Assume `git init` uploads anything to GitHub (it does not)
- Create nested git repositories (avoid `git init` inside an existing repo)

### Cloning Repositories

**DO:**
- Use `git clone <URL>` to download a repository from GitHub
- Clone creates a linked copy that can be synchronized with the remote

**DON'T:**
- Download repositories as zip files (this loses the git history and remote link)
- Confuse cloning with downloading

---

## Staging and Committing

### The Staging Area

**DO:**
- Use `git status` to check which files are untracked, modified, or staged
- Use `git add <file>` to stage specific files for the next commit
- Use `git add .` to stage all changes (use with caution)
- Use `git reset` to unstage all staged files if needed

**DON'T:**
- Commit without first staging the relevant files
- Assume all modified files are automatically included in commits

### Making Commits

**DO:**
- Write descriptive commit messages that explain the "why" not just the "what"
- Use `git commit -m "Your message"` for simple commits
- Use `git commit -am "Your message"` to stage and commit all modified files in one step
- Create commits after making changes that belong together logically
- Use `git log` to inspect commit history

**DON'T:**
- Use `git commit -am` for untracked files (it only works for already-tracked files)
- Write vague commit messages like "fixed stuff" or "updates"
- Create commits automatically without user intent

### Commit Message Best Practices

**DO:**
- Start with a short summary line (50 characters or less)
- Use imperative mood ("Add feature" not "Added feature")
- Explain what changed and why

**DON'T:**
- Write overly long single-line messages
- Omit context that future readers will need

---

## Branches

### Working with Branches

**DO:**
- Use branches to try out changes without affecting the stable main branch
- Use `git branch <name>` or `git checkout -b <name>` to create new branches
- Use `git branch` (no arguments) to see which branch you are on
- Use `git checkout <branch>` to switch between branches
- Use `git branch -d <name>` to delete branches after merging

**DON'T:**
- Make experimental changes directly on the main branch
- Forget which branch you are working on before making commits
- Delete branches that have unmerged changes without warning

### Creating Feature Branches (Recommended Workflow)

1. `git checkout main` - Switch to main branch
2. `git pull` - Get latest changes from remote
3. `git checkout -b feature_branch` - Create and switch to new branch

---

## Merging and Conflict Resolution

### Merging Branches

**DO:**
- To merge branch `a` into branch `b`:
  1. `git checkout b` - Switch to the target branch
  2. `git merge a` - Merge the source branch into current branch
- Understand the difference between fast-forward and recursive merge strategies

**DON'T:**
- Merge without being on the correct target branch
- Panic if merge conflicts occur

### Resolving Merge Conflicts

**DO:**
- Modify the conflicting files manually to resolve conflicts
- After resolving, use `git add <file>` to stage the resolved files
- Then use `git commit` to complete the merge
- Read conflict markers carefully (`<<<<<<<`, `=======`, `>>>>>>>`)

**DON'T:**
- Use `git reset` to "fix" merge conflicts
- Expect a `git resolve conflict` command (it does not exist)
- Leave conflict markers in committed files

---

## Undoing Things

### Safe Operations

**DO:**
- Use `git checkout <commit-hash>` to browse earlier versions (safe, non-destructive)
- Use `git checkout main` to return from detached HEAD state
- Use `git revert <commit>` to create a new commit that undoes a specific commit

**DON'T:**
- Panic when in detached HEAD mode
- Type random git commands hoping to fix things

### Destructive Operations (Use with Extreme Caution)

**DO:**
- Use `git reset --hard` only when you truly want to permanently delete commits
- Understand that `git reset --hard` deletes commits and resets local files

**DON'T:**
- Use `git reset --hard` without understanding the consequences
- Use destructive commands on shared branches
- Modify commit history after pushing to a shared remote

---

## Pre-commit Hooks

### Working with Pre-commit Hooks

**DO:**
- Run `pre-commit install` once after cloning a repository with hooks
- Use `git commit -am "message"` to stage and commit (important because hooks run on staged files)
- If the first commit fails, simply try again (hooks may have auto-fixed issues)
- If the second commit fails, carefully read error messages and fix manually
- Re-add files after hooks modify them

**DON'T:**
- Panic when pre-commit hooks fail
- Look for ways to disable pre-commit hooks
- Skip reading error messages when commits fail repeatedly

---

## Command Reference

### Essential Commands

| Command | Purpose |
|---------|---------|
| `git init` | Create a new repository |
| `git clone <url>` | Download a repository from GitHub |
| `git status` | Check repository state |
| `git add <file>` | Stage files for commit |
| `git commit -m "msg"` | Create a commit |
| `git commit -am "msg"` | Stage and commit modified files |
| `git log` | View commit history |
| `git branch` | List branches / see current branch |
| `git branch <name>` | Create a new branch |
| `git checkout <branch>` | Switch branches |
| `git checkout -b <name>` | Create and switch to new branch |
| `git merge <branch>` | Merge branch into current branch |
| `git pull` | Download changes from remote |
| `git push` | Upload changes to remote |
| `git revert <commit>` | Undo a commit (safely) |

### Commands to Use Carefully

| Command | Purpose | Warning |
|---------|---------|---------|
| `git reset --hard` | Discard all uncommitted changes | Destructive |
| `git reset --hard <commit>` | Delete commits after specified commit | Destructive |
| `git push --force` | Overwrite remote history | Very destructive |

---

# Python Installation and Execution

## Package Management with Pixi

Pixi is the recommended package and environment manager. It manages conda packages and
provides isolated, reproducible environments for each project.

### DO

- Use `pixi run <command>` to execute any command that requires the project environment
  - `pixi run python script.py` instead of `python script.py`
  - `pixi run pytest` instead of `pytest`
  - `pixi run pytask` instead of `pytask`
- Use `pixi add <package>` to add new conda-forge dependencies
- Use `pixi add --pypi <package>` for packages only available on PyPI
- Use `pyproject.toml` for pixi configuration (not `pixi.toml`)
- Commit the `pixi.lock` file to version control for reproducibility
- Use `pixi list` to see all packages in the current environment

### DON'T

- Do not use `pip install` directly - use `pixi add` or `pixi add --pypi` instead
- Do not use `conda install` - use `pixi add` instead
- Do not use the `defaults` conda channel - use `conda-forge` instead
- Do not forget to prefix commands with `pixi run`
- Do not manually edit `pixi.lock` - it is automatically managed

---

## Python Package Structure

### DO

- Use the `src` layout for Python packages:
  ```
  project/
  ├── src/
  │   └── package/
  │       ├── __init__.py
  │       └── module.py
  └── pyproject.toml
  ```
- Include `__init__.py` files in all package directories
- Use `pip install -e .` (editable install) during development
- Use `if __name__ == "__main__":` guard for code that should only run when executed directly

### DON'T

- Do not commit `__pycache__` directories to version control
- Do not forget the `__init__.py` files in package directories
- Do not use regular `pip install .` during development (changes require reinstallation)

---

## Executing Python Code

### From the Shell

```bash
# Correct way
pixi run python script.py

# Also correct (with relative paths)
pixi run python ../script.py
```

### DO

- Always run pixi commands from a directory containing (or with a parent containing)
  `pyproject.toml`
- Ensure VS Code has the correct Python interpreter selected (from the `.pixi`
  environment)

### DON'T

- Do not run `python script.py` without `pixi run` prefix
- Do not assume the system Python is the correct one

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Add conda package | `pixi add <package>` |
| Add PyPI package | `pixi add --pypi <package>` |
| Run Python script | `pixi run python script.py` |
| Run tests | `pixi run pytest` |
| Run tasks | `pixi run pytask` |
| List installed packages | `pixi list` |
| Initialize new project | `pixi init --format pyproject` |

---

# Python Basics

## Variables and Scalar Types

### DO

- Use `=` for assignment and `==` for comparison
- Use `int` for whole numbers, `float` for real numbers, `bool` for True/False
- Use `type()` to inspect variable types when debugging
- Remember that Booleans are case-sensitive: `True` and `False` (not `true`/`false`)
- Use `**` for exponentiation (not `^`)

### DON'T

- Don't compare floats for exact equality due to precision issues
  ```python
  # Bad - may fail due to floating point precision
  if 0.1 + 0.2 == 0.3:
      ...

  # Better - use approximate comparison
  import math
  if math.isclose(0.1 + 0.2, 0.3):
      ...
  ```

---

## Strings

### DO

- Use f-strings for string formatting (they are readable and powerful)
  ```python
  name = "Alice"
  age = 30
  message = f"{name} is {age} years old"
  ```
- Use single or double quotes consistently; use the other to embed quotes
- Use string methods like `.lower()`, `.upper()`, `.replace()`, `.startswith()`
- Remember that indexing starts at 0 and negative indices count from the end

### DON'T

- Don't assume strings containing numbers behave like numbers
  ```python
  # This concatenates, not adds!
  "123" * 2  # Returns '123123'
  ```

---

## Lists, Tuples, and Sets

### DO

- Use **lists** `[]` for mutable, ordered sequences
- Use **tuples** `()` for immutable, ordered sequences (safer, can be dict keys)
- Use **sets** `{}` for unique items and fast membership checking
- Use `len()` to get the number of elements in any collection
- Remember: single-element tuples need a trailing comma: `(1,)`

### DON'T

- Don't use sets when you need to preserve order or allow duplicates
- Don't try to index into sets (they are unordered)
- Don't create empty sets with `{}` (that creates an empty dict)
  ```python
  # Wrong - creates empty dict
  empty = {}

  # Correct - creates empty set
  empty = set()
  ```

### Choosing the Right Container

| Use Case | Container |
|----------|-----------|
| Need to modify elements | list |
| Need immutability/hashability | tuple |
| Need fast membership checks | set |
| Need unique elements | set |
| Need to preserve insertion order | list or tuple |

---

## Dictionaries

### DO

- Use dictionaries for label-based access (more readable than position-based)
- Use descriptive, meaningful keys
- Access nested dictionaries with chained square brackets: `d[key1][key2]`
- Use `.items()` when you need both keys and values

```python
# Good - descriptive variable name and keys
german_regions = {"North Rhine-Westphalia": 1, "Bavaria": 2}

# Accessing nested dictionaries
students = {
    "Alice": {"age": 25, "grade": "A"},
    "Bob": {"age": 23, "grade": "B"},
}
alice_age = students["Alice"]["age"]
```

### DON'T

- Don't use unhashable types (lists, sets, dicts) as dictionary keys
- Don't use generic variable names like `dictionary` or `dict1`
- Don't forget that modifying a nested dict modifies the original

---

## For Loops

### DO

- Use for loops to avoid code repetition (DRY: Don't Repeat Yourself)
- Choose descriptive names for loop variables
- Use `.items()` to loop over dictionary key-value pairs
- Indent loop body by 4 spaces

```python
# Good - descriptive loop variable
names = ["Alice", "Bob", "Carol"]
for name in names:
    print(name.lower())

# Good - looping over dict items
scores = {"Alice": 95, "Bob": 87}
for name, score in scores.items():
    print(f"{name}: {score}")
```

### DON'T

- Don't avoid loops just because "loops are slow" - premature optimization is bad
- Don't use loops when a simple built-in function exists (`sum()`, `len()`, etc.)

---

## Functions

### DO

- Name functions with `lowercase_with_underscores`
- Use keyword arguments for functions with more than one argument
- Set sensible default values for optional parameters
- Pass all variables the function needs as arguments
- Return values explicitly with `return`

```python
def utility_crra(consumption, gamma=1.5):
    """Calculate CRRA utility."""
    return consumption ** (1 - gamma) / (1 - gamma)

# Good - using keyword arguments
result = utility_crra(consumption=1.0, gamma=2.0)
```

### DON'T

- Don't rely on global variables inside functions
- Don't modify mutable arguments in place
  ```python
  # Bad - modifies the original list
  def append_4(some_list):
      some_list.append(4)
      return some_list

  # Good - create a copy first
  def append_4(some_list):
      result = some_list.copy()
      result.append(4)
      return result
  ```

---

## Importing

### DO

- Import specific items when you only need a few things
- Import entire libraries with conventional aliases
- Keep imports at the top of the file

```python
# Good - specific import
from pathlib import Path

# Good - conventional alias
import numpy as np
import pandas as pd
```

### DON'T

- **Never** use `from library import *` (pollutes namespace)
  ```python
  # NEVER do this
  from numpy import *
  ```

---

## File Paths with pathlib

### DO

- **Always** use `pathlib.Path` objects instead of strings
- Concatenate paths with `/` operator
- Start paths relative to the project root
- Use `.resolve()` for debugging to see full paths
- Use `.exists()` to verify paths

```python
from pathlib import Path

# In a .py file
root = Path(__file__).parent.parent
data_path = root / "datasets" / "data.csv"

# In a notebook
root = Path(".").resolve().parent
data_path = root / "datasets" / "data.csv"

# Debugging
print(data_path.resolve())
print(data_path.exists())
```

### DON'T

- **Never** hardcode absolute paths from your file explorer
- Don't use backslashes `\` in paths (Windows-only)
- Don't assume paths outside the project structure

### Three Rules for File Paths

1. Always use `pathlib.Path` objects instead of strings
2. Do not hardcode any parts of a path outside of the project's directory
3. Always concatenate paths with `/`

---

## Tracebacks and Error Handling

### DO

- Read tracebacks from bottom to top
- Look for three key pieces of information:
  1. What type of exception occurred
  2. Where it occurred (file and line number)
  3. What exactly happened (error message)
- Create minimal reproducible examples when asking for help

### Common Exception Types

| Exception | Cause |
|-----------|-------|
| `ValueError` | Invalid value passed to function |
| `KeyError` | Missing dictionary key or typo |
| `TypeError` | Wrong type (e.g., unhashable key) |
| `ImportError` | Typo in import or missing module |
| `NameError` | Variable not defined |

---

# Debugging

## Core Philosophy

Debugging is a learnable skill that accounts for 25-50% of programming time. There are
two complementary modes:

1. **Inspeculation** - A hybrid of inspection, simulation, and speculation
2. **Data Gathering** - Collecting information about program state

---

## Bug Prevention

Prevention is better than cure. The best debugging is the debugging you never have to do.

### DO: Write Preventive Code

- **Write comprehensive unit tests**
  - Test all code paths, not just the happy path
  - Cover edge cases explicitly
  - One test per function is usually NOT enough

- **Implement thorough error handling**
  - Validate inputs at function boundaries
  - Write clear, informative error messages

- **Write readable, modular code**
  - Give functions a clear, single purpose
  - Use informative variable names
  - Keep functions small enough to understand at a glance

### DON'T

- Don't skip writing tests because "it's simple code"
- Don't write vague error messages like "invalid input"
- Don't use cryptic variable names like `x`, `temp`, or `data`
- Don't write functions that do multiple unrelated things

---

## Psychology of Debugging

### DON'T: Give in to Counterproductive Urges

1. **The urge to skip reading**
   - Tracebacks contain valuable information
   - Always identify: the line, the error type, and the message

2. **The urge to just run it again**
   - Computers are deterministic
   - The same code produces the same result

3. **The urge to tell yourself it should work**
   - If you are debugging, something clearly did not work
   - Accept reality and investigate

4. **The urge to try random things**
   - Random changes rarely fix bugs
   - Changes without reason make things worse

5. **The urge to blame libraries**
   - Most libraries are well-tested
   - Bugs in your code are far more likely

---

## Debugging Strategies (Agans' Rules)

### Rule 0: Get It Right the First Time
- Invest in unit testing
- Implement proper error handling
- Write readable, modular code

### Rule 1: What Is It Supposed to Do?
- Define exactly what is going wrong
- Know how you determined something is wrong

### Rule 2: Is It Plugged In?
- Verify you're running the code you think you're running
- Check test data is correct
- Confirm configuration is as expected

### Rule 3: Make It Fail
- Find a test case that reproduces the failure
- Simplify the test case as much as possible

### Rule 4: Divide and Conquer
- Narrow the gap between cause and effect
- Start with the simplest failing test case
- Step through with a debugger

### Rule 5: Change One Thing at a Time, for a Reason
- Make a git commit BEFORE starting to debug
- Have a hypothesis before making any change
- Re-run all tests after every change
- Undo changes that were not helpful

### Rule 6: Write It Down
- Keep records of what you tried
- Document parameter combinations tested

### Rule 7: Be Humble
- Ask for help after 15 minutes of being stuck
- Explain the problem aloud (rubber duck debugging)

---

## Data Gathering Techniques

### DO: Use Debuggers Over Print Statements

- Debuggers are interactive and show only what you need
- Set breakpoints with `import pdbp; breakpoint()`
- Essential debugger commands:
  - `n` - execute **n**ext line
  - `s` - execute next **s**tep (steps into functions)
  - `c` - **c**ontinue until next breakpoint
  - `u` - go one frame **u**p
  - `d` - go one frame **d**own
  - `exit` or `ctrl+d` - stop debugging

### DON'T: Rely Solely on Print Statements

- Print statements are time-consuming to write well
- They produce either too much output or risk missing important information
- They cannot be adjusted interactively

---

# Software Engineering

## Naming Conventions

Good naming is one of the defining differences between good and bad programmers.

### DO

- Use `lowercase_with_underscores` for functions, methods, and local variables
- Use `UPPERCASE_WITH_UNDERSCORES` for global constants
- Use `CamelCase` for classes
- Start function names with a verb in imperative mode: `create_`, `calculate_`,
  `convert_`, `get_`
- Use descriptive names proportional to scope
- Start private/helper functions with `_underscore`
- Use `lambda_` (with trailing underscore) to avoid Python keywords

### DON'T

- Use abbreviations, especially ambiguous ones
- Use misspelled words
- Use meaningless distinctions (`Beta` and `beta` for different concepts)
- Append type to variable names (`names_list` instead of just `names`)
- Use built-in keywords as names: `list`, `var`, `dict`, `type`
- Use single letters that cause debugger issues: `n`, `c`, `u`, `s`
- Start function names with `return_` or `call_`
- Use `and` in function names (split into two functions instead)

---

## Pure Functions

Write pure functions whenever possible. A pure function:
1. Returns identical values for identical arguments
2. Has no side effects (does not modify external state)

### DO

- Pass all required data as function arguments (explicit interfaces)
- Return results instead of modifying inputs
- Push impure operations (file I/O) to the boundaries of your code
- Keep the core logic in pure functions

### DON'T

- Depend on global variables or external state
- Modify mutable input arguments
- Mix file I/O with data processing logic

### Example: Push Impurities to Boundaries

```python
# Good: Separate I/O from pure logic
def task_clean_data(
    data=SRC / "original_data" / "data.csv",
    produces=BLD / "data.pkl",
):
    df = pd.read_csv(data)        # Impure: file read
    clean = clean_data(df)         # Pure: data processing
    clean.to_pickle(produces)      # Impure: file write


def clean_data(df):
    """Pure function - all logic here."""
    ...
    return cleaned_df
```

---

## Error Handling

### DO

- Raise errors as early as possible
- Use descriptive error messages that explain what went wrong and how to fix it
- Use `TypeError` for wrong argument types
- Use `ValueError` for correct types but wrong values
- Create `_fail_if_...` helper functions for each check
- Define custom exceptions for domain-specific errors

### DON'T

- Duplicate error handling code
- Run checks repeatedly in nested functions
- Use error handling for things that should be tested instead

### Example: Fail Functions

```python
def convert_lod_to_dol(lod):
    _fail_if_lod_is_not_a_list(lod)
    _fail_if_list_of_wrong_types(lod)
    _fail_if_list_of_dicts_with_different_keys(lod)
    # ... actual implementation


def _fail_if_lod_is_not_a_list(lod):
    if not isinstance(lod, list):
        msg = f"lod must be a list, not {type(lod)}."
        raise TypeError(msg)
```

---

## Testing

### What to Test

- Typical input scenarios
- Corner cases and edge cases
- Expected exceptions
- Any bugs encountered (add to test suite before fixing)

### How to Test

- Write granular tests (one assert per test function)
- Always perform counterchecks (verify test fails when it should)

### DO

- Name test files `test_XXX.py` where XXX is the module being tested
- Name test functions `test_YYY_ZZZ` where YYY is the function and ZZZ describes the
  behavior
- Structure tests clearly: define expected, calculate actual, assert equality
- Use `pytest.raises` to test that errors are raised correctly
- Use `@pytest.mark.parametrize` to test multiple inputs with one function

### DON'T

- Test implementation details (only test interfaces)
- Write tests that pass for the wrong reasons
- Skip counterchecks

### Example: Parametrized Tests

```python
@pytest.mark.parametrize("invalid_input", [-77, "typo"])
def test_clean_agreement_scale_invalid_data(invalid_input):
    with pytest.raises(ValueError):
        _clean_agreement_scale(pd.Series([invalid_input]))
```

---

## Data Structures: Choosing Containers

### When to Use Each

| Structure | Use When |
|-----------|----------|
| `dict` | Free/variable fields, fast lookup by key, unknown keys at design time |
| `NamedTuple` | Fixed fields, immutability required, simple data containers |
| `dataclass` | Fixed fields, mutability needed, complex options required |

### Immutability

> "Where it is not necessary to change, it is necessary not to change." -- Lucius Cary

- Immutable objects prevent many bugs
- Prefer NamedTuple (immutable) over dataclass (mutable by default)
- Use `@dataclass(frozen=True)` if you need dataclass features but want immutability

---

# Pandas

## Modern Pandas Configuration

Always enable modern pandas features at the start of any script or notebook:

```python
import pandas as pd

pd.options.mode.copy_on_write = True
pd.options.future.infer_string = True
```

**DO:**
- Use pandas version 2.1 or higher
- Use pyarrow version 13.0 or higher
- Use `engine="pyarrow"` when loading CSV files for better dtypes

**DON'T:**
- Use the deprecated `inplace` argument
- Rely on implicit copies of DataFrames

---

## DataFrames and Series

### Creating DataFrames

**DO:**
- Create small DataFrames for debugging and testing:
  ```python
  df = pd.DataFrame(
      data=[[1, "bla"], [3, "blubb"]],
      columns=["a", "b"],
      index=["c", "d"]
  )
  ```
- Use tiny inputs to recreate and solve problems before applying to real data

### Index Alignment

**DO:**
- Understand that assignment is index-aligned:
  ```python
  sr = pd.Series([2.71, 3.14], index=["d", "c"])
  df["new_col"] = sr  # Aligns by index, not position
  ```
- Use meaningful indices (not just RangeIndex) for safer operations

**DON'T:**
- Use float values in indices
- Have duplicate values in indices when possible

---

## Data Types

### Type Selection

**DO:**
- Set optimal dtypes explicitly:
  ```python
  better_dtypes = {
      "country": pd.CategoricalDtype(),
      "continent": pd.CategoricalDtype(),
      "year": pd.UInt16Dtype(),
      "life_exp": pd.Float64Dtype(),
  }
  df = df.astype(better_dtypes)
  ```
- Use `pd.CategoricalDtype()` for variables with a fixed, small set of values
- Use `pd.StringDtype()` for actual text data

**DON'T:**
- Accept default dtypes without consideration
- Use strings when categoricals are more appropriate

---

## Loading and Saving Data

### File Formats

**DO:**
- Use `.pkl` (pickle) for intermediate files not shared with others
- Use `.arrow` (Apache Arrow) for files to share
- Use `engine="pyarrow"` when reading CSV files

**DON'T:**
- Use `.dta` unless sharing with Stata users

---

## Selection

### Row Selection

**DO:**
- Use `.loc` for label-based selection:
  ```python
  df.loc[1]                    # Single row
  df.loc["Cuba"]               # By label
  df.loc[("Cuba", 2002)]       # MultiIndex
  ```
- Use Boolean Series for filtering:
  ```python
  df[df["year"] >= 2005]
  ```
- Use `.query()` for readable conditions:
  ```python
  df.query("year >= 2005 & continent == 'Europe'")
  ```

**DON'T:**
- Use `.iloc` (position-based) unless absolutely necessary

---

## Creating Variables

### Vectorized Operations

**DO:**
- Use numpy functions for math operations:
  ```python
  df["log_life_exp"] = np.log(df["life_exp"])
  ```
- Use arithmetic between Series:
  ```python
  df["gdp_billion"] = df["gdp_per_cap"] * df["pop"] / 1e9
  ```

### Looping Guidelines

**DO: Loop over columns**
```python
clean = pd.DataFrame()
for var in varlist:
    clean[var] = clean_variable(df[var])
```

**DON'T: Loop over rows**
- Avoid `df.iterrows()`, `df.apply()` row-wise, list comprehensions over rows
- These are just Python loops in disguise and are slow
- Use vectorized operations instead

---

## Merging Datasets

### Merging

**DO:**
- Always specify merge keys explicitly:
  ```python
  pd.merge(left, right, on=["country", "year"])
  ```
- Choose the appropriate join type:
  ```python
  pd.merge(left, right, on=["country", "year"], how="left")
  ```
- Check data before and after merging
- Verify expected number of observations

**DON'T:**
- Leave merge arguments at defaults without consideration
- Assume inner join (default) is what you want

---

## Functional Data Cleaning

### The Three Rules

1. **Start with an empty DataFrame**
2. **Touch every variable just once**
3. **Touch with a pure function**

### Implementation Pattern

**DO:**
```python
def clean_data(raw):
    df = pd.DataFrame(index=raw.index)
    df["coding_genius"] = clean_agreement_scale(raw["Q001"])
    df["learned_a_lot"] = clean_agreement_scale(raw["Q002"])
    df["favorite_language"] = clean_favorite_language(raw["Q003"])
    return df


def clean_agreement_scale(sr):
    sr = sr.replace({"-77": pd.NA, "-99": pd.NA})
    categories = ["strongly disagree", "disagree", "neutral", "agree", "strongly agree"]
    dtype = pd.CategoricalDtype(categories=categories, ordered=True)
    return sr.astype(dtype)
```

### Why Functional Approach

- Function names document what the code does (better than comments)
- No intermediate invalid states
- Code cannot be executed in wrong order
- Functions are reusable and testable

---

# Scientific Computing

## NumPy Fundamentals

### Mental Models for Arrays

- 1D array: A vector
- 2D array: A matrix
- 3D array: A "list" of matrices

### DO

- Think of arrays as homogeneous collections where all elements have the same dtype
- Use NumPy when you need fast numerical calculations
- Remember that NumPy knowledge transfers to JAX, PyTorch, TensorFlow

### DON'T

- Don't assume arrays can have mixed types like Python lists
- Don't write pure Python loops over array elements for performance-critical code

---

## Creating Arrays

```python
import numpy as np

# From lists
arr = np.array([1, 2, 3, 4])
arr_2d = np.array([[1, 2], [3, 4]])

# Constructors
np.ones(3)                    # [1., 1., 1.]
np.zeros((3, 4))              # 3x4 matrix of zeros
np.arange(5)                  # [0, 1, 2, 3, 4]
np.linspace(0, 1, 5)          # 5 evenly spaced values from 0 to 1
np.eye(3)                     # 3x3 identity matrix
```

---

## Calculations on Arrays

### Vectorization

Vectorization means operating on entire arrays at once instead of looping over elements.

### DO

- Use NumPy functions instead of Python loops - they are faster and more readable
- Use the `axis` argument for reductions along specific dimensions
- Use `axis=-1` to operate along the last axis regardless of array dimensionality

### DON'T

- Don't use Python loops or list comprehensions for numerical operations
- Don't forget that NumPy functions typically apply elementwise

---

## Calculations Between Arrays

### Multiplication Types

```python
a * b         # Elementwise multiplication
a @ b         # Matrix multiplication
a.dot(b)      # Matrix multiplication (alternative syntax)
```

### DO

- Use `*` for elementwise multiplication
- Use `@` or `.dot()` for matrix multiplication
- Be aware that division by zero produces `inf` or `nan`, not an error

### DON'T

- Don't confuse `*` (elementwise) with `@` (matrix multiplication)

---

## Broadcasting

Broadcasting allows operations between arrays of different shapes.

### Broadcasting Rule

> Two arrays are compatible for broadcasting if for each trailing dimension the axis
> lengths match or if either of the lengths is 1.

```python
a = np.zeros((2, 3), dtype=np.int64)

# Scalar broadcasting
a + 1                           # Add 1 to every element

# Row-wise broadcasting
a + np.array([1, 2, 3])         # Shape (3,) broadcasts to (2, 3)

# Column-wise broadcasting
a + np.array([[4], [5]])        # Shape (2, 1) broadcasts to (2, 3)
```

### DO

- Use broadcasting instead of repeating arrays - it saves memory and is faster
- Prefer broadcasting over explicit `np.repeat` or `np.tile`

---

## Random Number Generation

### Modern API (Use This)

```python
# Create a random number generator with a seed
rng = np.random.default_rng(5471)

# Generate random numbers
rng.uniform(low=0, high=1, size=3)      # Uniform distribution
rng.normal(loc=0, scale=1, size=(2, 3)) # Normal distribution
rng.integers(0, 10, size=5)              # Random integers
```

### DO

- Always create an RNG with a seed: `rng = np.random.default_rng(seed)`
- Generate seeds randomly (don't always use 123, 42, etc.)
- Verify that your main results don't change when you change the seed
- Pass the `rng` object to functions that need randomness

### DON'T

- **Never use the legacy global seed API**: `np.random.seed()` is deprecated
- **Never use `np.random.default_rng()` without a seed** - results won't be reproducible
- Don't use `np.random.rand()`, `np.random.randn()`, etc. (legacy API)

---

## Performance Optimization

### The Optimization Process

1. **Get it to run** - Make sure code works correctly
2. **Get it right** - Add tests to verify correctness
3. **Find the bottleneck** - Use profiling (snakeviz, line_profiler)
4. **Speed up the bottleneck on one core** - Vectorization, better algorithms
5. **Consider parallelization** - Only after single-core optimization

### DO

- **Vectorize everything** - Use array operations instead of loops
- **Use broadcasting** instead of repeating arrays
- **Prefer few large arrays** over many small arrays
- **Profile before optimizing**

### DON'T

- **Don't use array operations inside loops** - This is typically very slow

```python
# BAD - Array operations inside a loop
def slow_function(factors, weights, a):
    out = np.empty(len(factors))
    for i in range(len(factors)):
        out[i] = a * np.prod(factors[i] ** weights)
    return out

# GOOD - Fully vectorized
def fast_function(factors, weights, a):
    return a * np.prod(factors ** weights, axis=-1)
```

---

## Using Numba

Numba is a just-in-time compiler that can make Python loops as fast as C/Julia.

```python
from numba import njit

@njit
def numba_function(factors, weights, a):
    out = np.empty(len(factors))
    for i in range(len(factors)):
        out_i = a
        for j in range(len(weights)):
            out_i *= factors[i, j] ** weights[j]
        out[i] = out_i
    return out
```

### DO

- **Write out all loops explicitly** for best performance with Numba
- **Use only scalars and arrays** inside Numba functions
- **Only apply Numba to bottlenecks**, not your entire codebase

### DON'T

- Don't use dicts, lists, or complex objects inside Numba functions
- Don't expect Numba to magically speed up already-vectorized NumPy code

---

# Numerical Optimization

## Using optimagic

optimagic provides a unified interface to optimization algorithms from many libraries.
Always use optimagic for numerical optimization in this codebase.

### Basic Usage

```python
import numpy as np
import optimagic as om

def sphere(x):
    return (x ** 2).sum()

start_params = np.ones(5)

res = om.minimize(
    fun=sphere,
    params=start_params,
    algorithm="scipy_lbfgsb",
)
```

### DO

- **DO** use `om.minimize()` for minimization and `om.maximize()` for maximization
- **DO** explicitly specify the algorithm - there is no default optimizer
- **DO** use structured parameter formats (dicts, nested structures) for complex problems
- **DO** inspect the result object attributes: `res.params`, `res.criterion`,
  `res.n_criterion_evaluations`, `res.success`, `res.message`

### DON'T

- **DON'T** rely on a default optimizer - always specify one explicitly
- **DON'T** assume the optimization succeeded without checking `res.success`

---

## Algorithm Selection

### Three-Step Process

1. **Theory**: Use problem properties to select candidate algorithms
2. **Experimentation**: Compare algorithms using criterion plots
3. **Refine**: Iterate until convergence is achieved

### Algorithm Quick Selection

| Situation | First Choice |
|-----------|--------------|
| Smooth, no constraints | `scipy_lbfgsb` |
| Smooth, with constraints | `ipopt` |
| Least-squares, smooth | `scipy_ls_lm` |
| Not smooth, few params | `nlopt_bobyqa` |
| Global search, few params | `scipy_brute` |
| Global search, many params | Multistart with local optimizer |

### DO

- **DO** always compare multiple algorithms using criterion plots
- **DO** refine the result of a global optimizer with a local optimizer
- **DO** use multistart optimization for non-convex problems when feasible

### DON'T

- **DON'T** assume one algorithm works for all problems
- **DON'T** use grid search with more than 3 parameters (curse of dimensionality)
- **DON'T** expect global optimizers to be precise - always refine locally
- **DON'T** use Nelder-Mead by default - it is widely used but rarely optimal

---

## Debugging and Diagnostics

### Criterion Plots

Always visualize optimization histories to compare algorithm performance.

```python
# Single optimization
om.criterion_plot(res)

# Compare multiple optimizations
results = {}
for algo in ["scipy_neldermead", "nlopt_neldermead", "fides"]:
    results[algo] = om.minimize(sphere, np.arange(10), algorithm=algo)

om.criterion_plot(results, max_evaluations=200)
```

### DO

- **DO** always run at least two optimizers and compare them in a criterion plot
- **DO** use `monotone=True` when there are extreme values in the history
- **DO** use dictionaries as input to `criterion_plot` for automatic legends

### DON'T

- **DON'T** assume an optimization succeeded without visual inspection
- **DON'T** assume you found the global optimum just because an optimizer converged

---

# Projects

## Reproducibility Principles

### DO

- Include all source data, starting from the original format you obtained it
- Include all source code needed to produce results
- Document all programs/packages needed to run the code
- Use environment files to automate package installation
- Keep raw data and source code under version control
- Put all generated files in a separate folder (e.g., `bld/`) that can be safely deleted
- Provide a README documenting directory structure and how to run code

### DON'T

- Put generated/output files under version control
- Rely on notebooks that need manual execution
- Use manual clicking, copy-pasting, or commenting out code
- Require running multiple files in a specific order manually

---

## Directory Structure

### DO

- Maintain clear separation of inputs (`src/`) and outputs (`bld/`)
- Group files by analysis step inside `src/`:
  - `original_data/` - raw source data
  - `data_management/` - data cleaning and preparation
  - `analysis/` - regressions, estimations, computations
  - `final/` - visualizations and final outputs

### Example Structure

```
my_project/
├── src/
│   └── my_project/
│       ├── config.py
│       ├── original_data/
│       ├── data_management/
│       │   └── task_clean_data.py
│       ├── analysis/
│       │   └── task_run_model.py
│       └── final/
│           └── task_plot_results.py
├── bld/
├── tests/
└── pyproject.toml
```

---

## Path Handling

### DO

- Start paths relative to the project root folder
- Use `pathlib.Path` for all file paths
- Define common paths (SRC, BLD, etc.) in a central `config.py` file

### Example config.py

```python
from pathlib import Path

SRC = Path(__file__).parent.resolve()
BLD = SRC.joinpath("..", "..", "bld").resolve()
```

### DON'T

- Use hardcoded absolute paths
- Use string paths instead of `pathlib.Path` objects

---

## Writing Pytask Tasks

### DO

- Name task files as `task_*.py` (e.g., `task_clean_data.py`)
- Name task functions as `task_*` (e.g., `task_clean_data`)
- Use `pathlib.Path` objects as default arguments for all file dependencies
- Use the reserved keyword `produces` for output files
- Keep task functions focused: read, compute (via helper), write

### Example Simple Task

```python
from pathlib import Path
import pandas as pd

BLD = Path(__file__).parent / "bld"


def task_clean_data(raw_file=Path("gapminder.arrow"), produces=BLD / "data.pkl"):
    raw = pd.read_feather(raw_file)
    clean = _clean_data(raw)
    clean.to_pickle(produces)


def _clean_data(raw):
    df = raw.rename(columns={"lifeExp": "life_exp", "gdpPercap": "gdp_per_cap"})
    return df.query("continent == 'Asia'")
```

### DON'T

- Use function names that do not start with `task_`
- Use string paths instead of `pathlib.Path` objects

---

# Texts

## Markdown Syntax

### Headings

```markdown
# Title (Level 1)
## Subtitle (Level 2)
### Section (Level 3)
```

### DO

- Use heading levels hierarchically (don't skip levels)
- Keep heading text concise and descriptive
- Use a single Level 1 heading (`#`) per document for the main title

### DON'T

- Don't use hashtags for comments (they create headings in Markdown)
- Don't skip heading levels

---

## Code Snippets

### DO

- Always use proper code blocks with language identifiers for syntax highlighting
- Include the language identifier (python, pytb, bash, etc.) after the opening backticks
- Format code snippets properly when asking questions or reporting issues

````markdown
```python
def cobb_douglas(labor, capital, alpha):
    return labor**alpha * capital ** (1 - alpha)
```
````

### DON'T

- Don't take screenshots of code (use text-based code blocks instead)
- Don't paste unformatted code in communications
- Don't omit the language identifier in code blocks

---

## Writing README Files

### Essential Content

Every README should address:

1. **Entry point to the project**
   - What is the goal?
   - How is that being achieved?

2. **How to get it running**
   - For experienced users: Bare minimum requirements and precise commands
   - For less experienced users: Links to background information

3. **Basic purpose of the project**
   - What problem does it solve?
   - Why would someone use it?

### DO

- Write READMEs in Markdown
- Include clear installation/setup instructions
- State assumptions about the system required to run the project
- Keep it concise; respect the reader's time

### DON'T

- Don't make READMEs excessively long
- Don't include detailed API documentation in the README (link to it instead)

---

# Plotting

## Standard Imports and Setup

```python
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set default template
pio.templates.default = "plotly_dark"

# Enable plotly as pandas plotting backend
pd.options.plotting.backend = "plotly"
```

---

## Two Types of Plots

1. **Exploratory plots** - For discovering patterns in data
   - Speed is essential
   - Use `plotly.express` or pandas backend

2. **Publication plots** - For communicating results
   - Must be self-explanatory
   - May need `plotly.graph_objects` for fine control

---

## Five Core Visualization Guidelines

Based on Schwabish's principles:

### 1. Show the Data
- DO: Let the data be visible and interpretable
- DON'T: Obscure data with excessive decoration

### 2. Reduce the Clutter
- DO: Remove unnecessary gridlines, borders, and decorations

### 3. Integrate Graphics and Text
- DO: Label data directly on the plot when possible
- DO: Write titles like newspaper headlines (convey the insight)

### 4. Avoid the Spaghetti Chart
- DO: Use facets to separate groups (`facet_col`, `facet_row`)
- DON'T: Plot many overlapping lines without differentiation

### 5. Start with Grey
- DO: Use grey as the default color for most elements
- DO: Use accent colors only for the most important data points

---

## plotly.express Quick Reference

```python
# Basic Line Plot
fig = px.line(
    df,
    x="year",
    y="value",
    color="category",
    labels={"value": "Human-Readable Label"},
)

# Faceted Plots (Avoiding Spaghetti)
fig = px.line(
    df,
    x="year",
    y="life_expectancy",
    color="country",
    facet_col="continent",
)

# Cleaning Up Facet Labels
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
```

---

## DO's and DON'Ts Summary

### DO

- Use `plotly.express` for exploratory analysis
- Use `plotly.graph_objects` when you need full customization
- Use facets to avoid spaghetti charts
- Use grey for background elements, accent colors for highlights
- Label axes with human-readable names using the `labels` parameter
- Ensure plots are self-explanatory

### DON'T

- Create overly cluttered plots with too many overlapping lines
- Use many bright colors without clear purpose
- Rely on legends when direct labels would be clearer
- Create plots that require external explanation to understand

---

# Machine Learning and Econometrics

## Fundamental Differences: ML vs Econometrics

### Econometrics
- Goal: Estimate **fundamentally unobservable** parameters and test hypotheses
- Cannot directly test how well estimation worked
- Focus on justifying assumptions (identification, exogeneity, etc.)
- Parameters have causal/structural interpretations

### Machine Learning (Supervised)
- Goal: Predict observable outcomes
- Can directly measure prediction quality on held-out data
- Focus on experimentation, evaluation, and finding what works
- Parameters generally should NOT be interpreted causally

### DO

- Use econometrics (statsmodels) when the goal is causal inference or hypothesis testing
- Use machine learning (scikit-learn) when the goal is prediction
- Always clarify the goal before choosing an approach

### DON'T

- Do NOT interpret ML model parameters as causal effects
- Do NOT use ML predictions as evidence of causal relationships
- Do NOT skip holdout samples when the goal is prediction

---

## Statsmodels Usage

```python
import statsmodels.formula.api as smf

# Create model object
model = smf.ols(
    formula="y_variable ~ x_variable1 + x_variable2",
    data=df,
)

# Fit the model to get results
results = model.fit()

# Or with robust standard errors
results = model.fit(cov_type="HC1")
```

### DO

- Use the formula interface (`smf`) for readable, maintainable code
- Always call `.fit()` on the model object to get results
- Use `cov_type` parameter for robust standard errors when appropriate

### DON'T

- Do NOT forget that the intercept is implicit in OLS (included by default)
- Do NOT confuse the model object with the results object

---

## Scikit-learn Usage

### Basic Workflow Steps

1. Arrange data into features matrix (X) and target vector (y)
2. Split into training and test sets
3. Choose and import an estimator class
4. Instantiate with hyperparameters
5. Fit the model using `.fit()`
6. Generate predictions using `.predict()`
7. Evaluate predictions

### Train-Test Split

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=1234,
)
```

### DO

- Always split data into training and test sets BEFORE fitting
- Set `random_state` for reproducibility
- Fit on training data only
- Evaluate on test data only

### DON'T

- Do NOT evaluate on the same data used for training (leads to overfitting)
- Do NOT leak test set information into training

---

## Cross-Validation and Hyperparameter Tuning

### Grid Search for Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression

param_grid = {
    "penalty": ["l1", "l2"],
    "C": [0.1, 1, 10],
}

grid = GridSearchCV(
    LogisticRegression(solver="liblinear", max_iter=3000),
    param_grid,
    cv=5,
)

grid.fit(X_train, y_train)

best_params = grid.best_params_
best_model = grid.best_estimator_
test_score = best_model.score(X_test, y_test)
```

### DO

- Use cross-validation for hyperparameter tuning
- Reserve the test set for final evaluation only
- Use `GridSearchCV` for systematic hyperparameter search
- Set `max_iter` high enough to ensure convergence

### DON'T

- Do NOT tune hyperparameters directly on the test set
- Do NOT use the test set multiple times during model development
- Do NOT ignore convergence warnings
