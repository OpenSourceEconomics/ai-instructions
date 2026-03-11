# AI Instructions

Common coding standards and guidelines for AI coding agents, derived from the
[Effective Programming Practices for Economists](https://effective-programming-practices.vercel.app/)
course.

## Quick Start

### 1. Add as a git submodule

```bash
cd your-project
git submodule add git@github.com:OpenSourceEconomics/ai-instructions.git .ai-instructions
```

### 2. Create or update your `CLAUDE.md`

Pick the profile matching your project tier and prepend `@` includes to your
`CLAUDE.md`:

```
@.ai-instructions/profiles/tier-b-research.md

# Your Project

Project-specific instructions below...
```

Add cross-cutting modules individually as needed:

```
@.ai-instructions/profiles/tier-a.md
@.ai-instructions/modules/jax.md
@.ai-instructions/modules/optimagic.md
```

### 3. Remove `forbid-submodules` hook

If your `.pre-commit-config.yaml` has a `forbid-submodules` hook, remove it — it
conflicts with the `.ai-instructions` submodule.

### 4. (Optional) Install slash commands globally

Symlink the commands for use in any project:

```bash
mkdir -p ~/.claude/commands
ln -s "$(pwd)/.ai-instructions/commands/"*.md ~/.claude/commands/
```

Or from a local clone of this repo:

```bash
ln -s /path/to/ai-instructions/commands/*.md ~/.claude/commands/
```

## Project Tiers

| Tier             | Profile              | Description                            | Included modules                                          |
| ---------------- | -------------------- | -------------------------------------- | --------------------------------------------------------- |
| **A**            | `tier-a.md`          | Installable packages, complex research | core + numpy                                              |
| **B (research)** | `tier-b-research.md` | Research with pytask, data processing  | core + pandas, numpy, project-structure, pytask, plotting |
| **B (course)**   | `tier-b-course.md`   | Courses with notebooks                 | core + pandas, numpy, plotting, ml-econometrics           |
| **C**            | `tier-c.md`          | Documentation, LaTeX, minimal projects | core only                                                 |

JAX and optimagic cross-cut tiers — add them individually alongside your profile.

## Structure

```
ai-instructions/
├── AGENTS.md              # Universal core (type hints, immutability, pixi, code quality)
├── modules/               # Topic-specific standards
│   ├── pandas.md
│   ├── numpy.md
│   ├── jax.md
│   ├── optimagic.md
│   ├── project-structure.md
│   ├── pytask.md
│   ├── plotting.md
│   └── ml-econometrics.md
├── profiles/              # Pre-composed module sets per tier
│   ├── tier-a.md
│   ├── tier-b-research.md
│   ├── tier-b-course.md
│   └── tier-c.md
├── commands/              # Claude Code slash commands
│   ├── update-boilerplate.md
│   ├── verify-standards.md
│   └── new-task.md
└── boilerplate/           # Dev environment config templates
    └── README.md
```

## Slash Commands

Available after symlinking `commands/` to `~/.claude/commands/`:

| Command                   | Description                                                                                                            |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `/update-boilerplate`     | Compare project config against boilerplate templates, propose updates (hook versions, ruff rules, pixi env/task names) |
| `/verify-standards`       | Audit Python code for coding standard compliance, produce deviation report                                             |
| `/new-task <description>` | Generate a pytask task file with correct patterns (Annotated/Product, helper separation)                               |

## Updating

To update the submodule in a downstream project:

```bash
cd .ai-instructions
git pull origin main
cd ..
git add .ai-instructions
git commit -m "Update ai-instructions"
```

## Other Agents

Non-Claude agents can read `AGENTS.md` and the module files directly. Downstream repos
can keep a thin root `AGENTS.md` pointing to the submodule for discoverability:

```
See .ai-instructions/AGENTS.md for coding standards.
```

## Source

These guidelines are extracted from course materials at:
https://github.com/OpenSourceEconomics/epp_topics
