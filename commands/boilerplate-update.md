---
description: Compare project config against boilerplate templates and propose updates
allowed-tools: Read, Grep, Glob, Bash(pixi:*), Bash(git:*)
---

# Boilerplate Update

Compare this project's configuration files against the latest boilerplate templates and
propose targeted updates. Preserve all project-specific customizations.

**Always execute every step from scratch.** Do not skip steps based on prior conversation
context. Do not reuse answers from previous runs. Each invocation is independent.

## Steps

1. **Update .ai-instructions submodule.** Check if `.ai-instructions/` exists and is a
   git submodule. If not, ask the user for the path to the ai-instructions repo.

   If it exists, run a **single** bash command to gather all info at once:

   ```bash
   git submodule update --init .ai-instructions 2>/dev/null; \
   git -C .ai-instructions fetch --all 2>/dev/null; \
   echo "---CURRENT---"; \
   git -C .ai-instructions log --oneline -1; \
   echo "---BRANCH---"; \
   git -C .ai-instructions branch --show-current; \
   echo "---REMOTE-BRANCHES---"; \
   git -C .ai-instructions branch -r; \
   echo "---HAS-MODULES---"; \
   ls .ai-instructions/modules/ .ai-instructions/profiles/ 2>/dev/null || echo "MISSING"
   ```

   Then show the user the current branch/commit and all remote branches. Do NOT use
   AskUserQuestion for branch selection — it has a 4-option limit which can't fit all
   branches. Instead, list the branches as text and ask the user to type their choice.

   After the user picks a branch, switch to it if needed. **Always use `git -C`** to
   operate on the submodule — never `cd` into it:

   ```bash
   git -C .ai-instructions checkout <branch> && git -C .ai-instructions pull
   ```

   Then verify `.ai-instructions/modules/` and `.ai-instructions/profiles/` exist. If
   they don't, warn the user that the submodule may be on an old commit.

   Do not proceed until the submodule is confirmed ready with modules/ and profiles/.

2. **Interview: project tier.** Use AskUserQuestion with a single-select question.
   Options:

   - **A: Full** — Installable packages, complex research
   - **B: Standard** — Research with pytask, courses with notebooks
   - **C: Minimal** — Documentation, simple LaTeX projects, notes

   Do not guess. Do not proceed until the user answers. Do not combine this question
   with any other question.

3. **Interview: additional modules.** First, read the tier profile to see which modules
   are already included. Then use AskUserQuestion with a multi-select question listing
   every module from `.ai-instructions/modules/` that is NOT already in the tier profile.
   Show what the profile already includes for context.

   Do not skip this step. Do not proceed until the user answers. Do not combine this
   question with any other question.

4. **Interview: AI tool files.** Use AskUserQuestion with a multi-select question.
   Options:

   - **AGENTS.md** — primary agent instruction file, read by all tools (Claude, Gemini,
     Codex, Copilot, Cursor). Contains `@`-includes for shared standards plus
     project-specific instructions.
   - **CLAUDE.md** — thin `@AGENTS.md` wrapper, only needed for Claude Code (the only
     tool that doesn't auto-read AGENTS.md).

   Do not skip this step. Do not proceed until the user answers. Do not combine this
   question with any other question.

5. **Read the boilerplate templates.** The reference templates are in:
   - If `.ai-instructions/` exists: `.ai-instructions/boilerplate/README.md`
   - Otherwise ask the user for the path to the ai-instructions repo

   Read the full boilerplate README to understand the expected configuration for the
   determined tier.

6. **Read the project's current configuration.** Read these files:
   - `pyproject.toml`
   - `.pre-commit-config.yaml`
   - `.gitignore`
   - `.yamllint.yml` (if exists)
   - `AGENTS.md` (if exists)
   - `CLAUDE.md` (if exists)
   - Any GitHub Actions workflow files in `.github/workflows/`

7. **Compare and report deviations.** For each file, compare against the tier-appropriate
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
   - **nbstripout kernelspec**: Check if `pyproject.toml` has `jupyter-book` or `mystmd`
     as a dependency (in `[project.dependencies]`, `[tool.pixi.dependencies]`, or
     `[tool.pixi.pypi-dependencies]`). If so, flag that `metadata.kernelspec` should NOT
     be in nbstripout's `--extra-keys`. If the project doesn't use JB2, ensure
     `metadata.kernelspec` IS being stripped.
   - **GitHub Actions versions**: For each `.github/workflows/*.yml`, check ALL versioned
     references: `uses: <action>@<version>` tags (e.g., `actions/checkout`,
     `prefix-dev/setup-pixi`, `codecov/codecov-action`, `actions/setup-python`,
     `pypa/gh-action-pypi-publish`) and pinned tool versions (e.g., `pixi-version:`).
     For each, check the latest available version (via the action's GitHub tags page) and
     flag outdated ones.
   - **Pixi task names**: should follow the standard set
     (`tests`, `tests-with-cov`, `tests-jax`, `ty`, `build-docs`, `view-docs`,
     `view-paper`, `view-pres`). The `ty` task should run `ty check`. Flag non-standard
     names.

8. **Generate or update AGENTS.md.** If the user selected it in step 4, generate or update the
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

9. **Generate or update CLAUDE.md.** If the user selected it in step 4, ensure CLAUDE.md contains:

   ```
   @AGENTS.md
   ```

   If CLAUDE.md already has project-specific content beyond `@`-includes, migrate that
   content to AGENTS.md (so all tools benefit) and replace CLAUDE.md with just
   `@AGENTS.md`.

10. **Propose changes.** Show each proposed change as a before/after diff. Group by file.
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
