# AI Instructions

Common coding standards and guidelines for AI coding agents, derived from the
[Effective Programming Practices for Economists](https://effective-programming-practices.vercel.app/)
course.

## Quick Start

### 1. Add as a git submodule

```bash
cd your-project
git submodule add https://github.com/OpenSourceEconomics/ai-instructions.git .ai-instructions
```

### 2. Create your `AGENTS.md`

All agent instructions live in `AGENTS.md`. Put `@`-includes at the top (resolved by
Claude and Gemini; ignored as plain text by Codex, Copilot, Cursor), then
project-specific content below:

```markdown
@.ai-instructions/profiles/tier-b-research.md
@.ai-instructions/modules/jax.md

# Your Project

Project-specific instructions below...
```

### 3. Create your `CLAUDE.md`

Claude Code doesn't auto-read `AGENTS.md`, so it needs a thin wrapper:

```
@AGENTS.md
```

### 4. Create your `GEMINI.md`

Gemini CLI reads `AGENTS.md` directly but doesn't resolve `@`-includes from it. Create a
`GEMINI.md` so the Gemini CLI (and roborev reviews) picks up the shared standards:

```
@AGENTS.md
```

All other tools (Codex, Copilot, Cursor) read `AGENTS.md` directly.

### 5. Remove `forbid-submodules` hook

If your `.pre-commit-config.yaml` has a `forbid-submodules` hook, remove it — it
conflicts with the `.ai-instructions` submodule.

### 6. (Optional) Install slash commands globally

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

| Tier             | Profile              | Description                            | Included modules                                         |
| ---------------- | -------------------- | -------------------------------------- | -------------------------------------------------------- |
| **A**            | `tier-a.md`          | Installable packages, complex research | core + beartype, math                                    |
| **B (research)** | `tier-b-research.md` | Research with pytask, data processing  | core + pandas, project-structure, pytask, plotting, math |
| **B (course)**   | `tier-b-course.md`   | Courses with notebooks                 | core + pandas, plotting, math                            |
| **C**            | `tier-c.md`          | Documentation, LaTeX, minimal projects | core only                                                |

The math module (`modules/math.md`) is included by default in tiers A and B — it applies
whenever a project implements equations, estimators, or numerical algorithms, not just
JAX/optimagic-based ones. JAX, optimagic, and dags cross-cut tiers — add them
individually alongside your profile.

## Structure

```
ai-instructions/
├── AGENTS.md              # Universal core (type hints, immutability, pixi, code quality)
├── modules/               # Topic-specific standards
│   ├── pandas.md
│   ├── math.md
│   ├── jax.md
│   ├── optimagic.md
│   ├── project-structure.md
│   ├── pytask.md
│   ├── plotting.md
│   ├── dags.md
│   └── beartype.md
├── profiles/              # Pre-composed module sets per tier
│   ├── tier-a.md
│   ├── tier-b-research.md
│   ├── tier-b-course.md
│   └── tier-c.md
├── commands/              # Claude Code slash commands
│   ├── boilerplate-update.md
│   ├── verify-standards.md
│   ├── new-task.md
│   ├── implement-math.md
│   ├── repair-math-root-cause.md
│   └── close-pro-audit.md
├── hooks/                 # Scripts invoked by downstream pre-commit configs
│   └── fix_notebook_cell_source.py
└── boilerplate/           # Dev environment config templates
    └── README.md
```

Because `.ai-instructions/` is a submodule in every downstream project, hooks in
`hooks/` can be referenced directly from a project's `.pre-commit-config.yaml` as
`.ai-instructions/hooks/<script>.py` — no per-project copy to drift.

## Slash Commands

Available after symlinking `commands/` to `~/.claude/commands/`:

| Command                         | Description                                                                                                            |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `/boilerplate-update`           | Compare project config against boilerplate templates, propose updates (hook versions, ruff rules, pixi env/task names) |
| `/verify-standards`             | Audit Python code for coding standard compliance, produce deviation report                                             |
| `/new-task <description>`       | Generate a pytask task file with correct patterns (Annotated/Product, helper separation)                               |
| `/implement-math <claim>`       | Implement a mathematical/statistical feature reference-first, per `modules/math.md`                                    |
| `/repair-math-root-cause <bug>` | Repair a math/numerics root-cause defect class as one batch, per `modules/math.md`                                     |
| `/close-pro-audit`              | Prepare and enforce closure for an external `pro-*-audit` skill finding                                                |

## Maintenance

This repo should not just grow. Every module and command here was written to close a gap
in some model generation's default behavior; as models get stronger, some of those gaps
close on their own, and the instruction becomes pure cost (context, attention) with no
remaining benefit. This mirrors Anthropic's own practice for Claude Code's system prompt
— rebuilt from scratch on each model release, with ~80% of Opus 5's predecessor prompt
cut once the model no longer needed it.

Periodically, e.g. on each new Claude generation, re-test a module by running a
representative task with it removed and comparing against a run with it included.
Modules whose absence produces no observable difference are candidates for trimming.
Prioritize the newest, most elaborate additions first — they were written against a
specific model's gaps and are least likely to have been re-validated since.

This does not apply to house-specific conventions a model cannot infer regardless of
capability — naming, docstring/comment style, pixi/prek tooling choices, or anything
encoding a concrete bug workaround (`modules/beartype.md`) or an obscure library's API
(`modules/dags.md`). Only prune content whose absence a stronger model can compensate
for on its own.

## Updating

To update the submodule in a downstream project:

```bash
cd .ai-instructions
git pull origin main
cd ..
git add .ai-instructions
git commit -m "Update ai-instructions"
```

## Multi-Tool Support

| Tool           | Reads `AGENTS.md`? | Resolves `@` includes? | Extra file needed?            |
| -------------- | ------------------ | ---------------------- | ----------------------------- |
| Claude Code    | Via `@AGENTS.md`   | Yes                    | `CLAUDE.md` with `@AGENTS.md` |
| Gemini CLI     | Yes (auto)         | Yes                    | `GEMINI.md` with `@AGENTS.md` |
| OpenAI Codex   | Yes (primary)      | No                     | None                          |
| GitHub Copilot | Yes (auto)         | No                     | None                          |
| Cursor         | Yes (auto)         | No                     | None                          |

Tools without `@`-include support ignore the `@` lines as plain text but still read the
project-specific content in `AGENTS.md`.

## Source

These guidelines are extracted from course materials at:
https://github.com/OpenSourceEconomics/epp_topics
