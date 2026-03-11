# AI Instructions

Common coding standards and guidelines for AI coding agents, derived from the
[Effective Programming Practices for Economists](https://effective-programming-practices.vercel.app/)
course.

## Structure

- **`AGENTS.md`** — Universal core standards (type hints, immutability, pixi, code
  quality). All projects include this.
- **`modules/`** — Topic-specific standards, selectively included per project:
  - `pandas.md` — DataFrame conventions, functional data cleaning
  - `numpy.md` — Vectorization, modern random API
  - `jax.md` — JIT, vmap, jaxtyping, pytree registration
  - `optimagic.md` — Optimization with optimagic, algorithm selection
  - `project-structure.md` — Directory layout, config, reproducibility
  - `pytask.md` — Task runner patterns with Annotated/Product
  - `plotting.md` — Plotly conventions
  - `ml-econometrics.md` — Statsmodels vs scikit-learn guidelines
- **`profiles/`** — Pre-composed module sets for downstream projects:
  - `tier-a.md` — Full packages (core + numpy)
  - `tier-b-research.md` — Research projects (core + pandas, numpy, project-structure,
    pytask, plotting)
  - `tier-b-course.md` — Course projects (core + pandas, numpy, plotting,
    ml-econometrics)
  - `tier-c.md` — Minimal projects (core only)
- **`boilerplate/`** — Dev environment configuration templates
- **`commands/`** — Claude Code slash commands (skills):
  - `/update-boilerplate` — Compare project config against boilerplate templates,
    propose updates
  - `/verify-standards` — Audit project code for coding standard compliance
  - `/new-task <description>` — Generate a pytask task file from a description

## Usage

### For downstream projects

Reference a profile in your project's `CLAUDE.md`:

```
@.ai-instructions/profiles/tier-b-research.md
```

Add cross-cutting modules individually as needed:

```
@.ai-instructions/profiles/tier-b-research.md
@.ai-instructions/modules/jax.md
@.ai-instructions/modules/optimagic.md
```

### For this repo

`CLAUDE.md` includes core + all modules to load the full standard set.

## Source

These guidelines are extracted from course materials at:
https://github.com/OpenSourceEconomics/epp_topics
