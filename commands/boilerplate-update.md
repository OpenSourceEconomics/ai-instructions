---
description: Compare project config against boilerplate templates and propose updates
allowed-tools: Read, Grep, Glob, Bash(pixi:*), Bash(git:*)
---

# Boilerplate Update

Compare this project's configuration files against the latest boilerplate templates and
propose targeted updates. Preserve all project-specific customizations.

## Steps

1. **Determine project tier.** Ask the user which tier this project belongs to (A, B, or
   C). Do not guess.

   | Tier            | Description                                  |
   | --------------- | -------------------------------------------- |
   | **A: Full**     | Installable packages, complex research       |
   | **B: Standard** | Research with pytask, courses with notebooks  |
   | **C: Minimal**  | Documentation, simple LaTeX projects, notes   |

2. **Ask about AI tool configuration.** Ask whether to generate or update AGENTS.md and
   CLAUDE.md for this project. Explain:

   - `AGENTS.md` is the primary agent instruction file — read by Claude, Gemini, Codex,
     Copilot, and Cursor. It contains `@`-includes for shared standards (resolved by
     Claude and Gemini) plus project-specific instructions.
   - `CLAUDE.md` is a thin wrapper (`@AGENTS.md`) only needed for Claude Code, which
     doesn't auto-read AGENTS.md.
   - No other tool-specific files are needed.

   Also ask which **additional modules** beyond the tier profile to include (e.g., jax,
   optimagic).

3. **Read the boilerplate templates.** The reference templates are in:
   - If `.ai-instructions/` exists: `.ai-instructions/boilerplate/README.md`
   - Otherwise ask the user for the path to the ai-instructions repo

   Read the full boilerplate README to understand the expected configuration for the
   determined tier.

4. **Read the project's current configuration.** Read these files:
   - `pyproject.toml`
   - `.pre-commit-config.yaml`
   - `.gitignore`
   - `.yamllint.yml` (if exists)
   - `AGENTS.md` (if exists)
   - `CLAUDE.md` (if exists)
   - Any GitHub Actions workflow files in `.github/workflows/`

5. **Compare and report deviations.** For each file, compare against the tier-appropriate
   boilerplate template. Report:

   - **Hook version mismatches**: e.g., ruff v0.15.1 vs template v0.15.5
   - **Missing hooks**: hooks in the template but not in the project
   - **Extra hooks**: hooks in the project but not in the template (note these, don't
     remove — they may be intentional)
   - **Incompatible hooks**: flag `forbid-submodules` for removal — projects use
     `.ai-instructions` as a git submodule
   - **Configuration gaps**: missing ruff rules, ty config, etc.
   - **Structural issues**: wrong build backend, missing hatch-vcs, etc.
   - **Pixi environment names**: should follow the standard set
     (`py3XX`, `numpy`, `jax`, `cpu`, `cuda`, `cuda12`, `cuda13`, `tests`, `docs`,
     `type-checking`), combined like `py314-jax`, `tests-cuda13`. Flag non-standard
     names (e.g., `test-cpu` should be `tests-cpu`, `default` should be `py3XX`).
   - **Pixi task names**: should follow the standard set
     (`tests`, `tests-with-cov`, `tests-jax`, `ty`, `build-docs`, `view-docs`,
     `view-paper`, `view-pres`). The `ty` task should run `ty check`. Flag non-standard
     names.

6. **Generate or update AGENTS.md.** If the user requested it, generate or update the
   project's `AGENTS.md`. Structure:

   ```markdown
   @.ai-instructions/profiles/<tier-profile>.md
   @.ai-instructions/modules/<extra-module>.md

   # Project Name

   ## Overview

   <brief project description>

   ## Build & Test

   <pixi run commands for this project>

   ## Architecture

   <project-specific structure, key directories, conventions>
   ```

   If an AGENTS.md already exists, preserve existing project-specific content and only
   update the `@`-include lines at the top.

7. **Generate or update CLAUDE.md.** If the user requested it, ensure CLAUDE.md contains:

   ```
   @AGENTS.md
   ```

   If CLAUDE.md already has project-specific content beyond `@`-includes, migrate that
   content to AGENTS.md (so all tools benefit) and replace CLAUDE.md with just
   `@AGENTS.md`.

8. **Propose changes.** Show each proposed change as a before/after diff. Group by file.
   For environment/task renames, also check and update:
   - `AGENTS.md` / `CLAUDE.md` command references
   - `.github/workflows/` CI environment references
   - Any `Makefile` or scripts referencing old names

## Rules

- **Never overwrite** existing ruff exclusions, ty ignore rules, or per-file-ignores
  unless explicitly asked
- **Never add pixi** if the project already uses `uv` — flag this and skip
- **Never remove** project-specific hooks (nbstripout, codespell, custom validators)
- **Preserve** custom pytest markers, filterwarnings, and test paths
- **Preserve** custom pixi environments and platform-specific tasks
- **Do not auto-apply changes** — present them for review, then apply only what the user
  approves
- **Update GitHub Actions** workflow references if task/environment names change
- **Migrate CLAUDE.md content** to AGENTS.md when possible so all tools benefit
