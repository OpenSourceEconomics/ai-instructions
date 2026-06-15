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
   git -C .ai-instructions remote prune origin 2>/dev/null; \
   echo "---CURRENT---"; \
   git -C .ai-instructions log --oneline -1; \
   echo "---BRANCH---"; \
   git -C .ai-instructions branch --show-current; \
   echo "---REMOTE-BRANCHES---"; \
   git -C .ai-instructions branch -r; \
   echo "---HAS-MODULES---"; \
   ls .ai-instructions/modules/ .ai-instructions/profiles/ 2>/dev/null || echo "MISSING"
   ```

   Then show the user the current branch/commit and all remote branches. If there is
   only **one** remote branch (typically `main`), skip the branch selection question and
   use it automatically. If there are 2-4 branches, use AskUserQuestion with
   single-select. If there are > 4 branches, list them as plain text and ask the user
   to type their choice (AskUserQuestion has a 4-option limit).

   After the branch is selected, switch to it if needed. **Always use `git -C`** to
   operate on the submodule — never `cd` into it:

   ```bash
   git -C .ai-instructions checkout <branch> && git -C .ai-instructions pull
   ```

   Then verify `.ai-instructions/modules/` and `.ai-instructions/profiles/` exist. If
   they don't, warn the user that the submodule may be on an old commit.

   **Submodule URL must use HTTPS.** Check the submodule URL in `.gitmodules`. If it
   uses SSH (`git@github.com:...`), flag it for replacement with HTTPS
   (`https://github.com/...`). SSH URLs fail on CI runners and ReadTheDocs which don't
   have SSH keys configured.

   Do not proceed until the submodule is confirmed ready with modules/ and profiles/.

2. **Interview: project tier.** First, check if `CLAUDE.md` (or `AGENTS.md`) already
   contains a `@.ai-instructions/profiles/` include line. If so, infer the tier from the
   profile name and skip this question — just confirm to the user what tier was detected.

   If no tier is stored, use AskUserQuestion with a single-select question. Options:

   - **A: Full** — Installable packages, complex research
   - **B: Standard** — Research with pytask, courses with notebooks
   - **C: Minimal** — Documentation, simple LaTeX projects, notes

   Do not guess. Do not proceed until the user answers. Do not combine this question
   with any other question.

3. **Interview: additional modules.** First, check if `AGENTS.md` already contains
   `@.ai-instructions/modules/` include lines. If so, show the user the currently
   included modules and ask if they want to change anything. If they're happy, skip
   ahead.

   If no modules are stored (or the user wants to change), read the tier profile to see
   which modules are already included. Then list ALL available modules from
   `.ai-instructions/modules/` as plain text, marking which ones the tier profile already
   includes. Ask the user to type which additional modules they want. Do NOT use
   AskUserQuestion for this — the option list is too long for its 4-option limit.

   Do not skip this step. Do not proceed until the user answers. Do not combine this
   question with any other question.

4. **Interview: AI tool files.** Use AskUserQuestion with a multi-select question.
   Options:

   - **AGENTS.md** — primary agent instruction file, read by all tools (Claude, Gemini,
     Codex, Copilot, Cursor). Contains `@`-includes for shared standards plus
     project-specific instructions.
   - **CLAUDE.md** — thin `@AGENTS.md` wrapper, only needed for Claude Code (the only
     tool that doesn't auto-read AGENTS.md).
   - **GEMINI.md** — thin `@AGENTS.md` wrapper for the Gemini CLI (used by roborev for
     code reviews).

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
   - `GEMINI.md` (if exists)
   - Any GitHub Actions workflow files in `.github/workflows/`

7. **Compare and report deviations.** For each file, compare against the tier-appropriate
   boilerplate template. Report:

   - **Hook version mismatches**: e.g., ruff v0.15.1 vs template v0.15.5
   - **Missing hooks**: hooks in the template but not in the project
   - **Extra hooks**: hooks in the project but not in the template (note these, don't
     remove — they may be intentional)
   - **Incompatible hooks**: flag `forbid-submodules` for removal — projects use
     `.ai-instructions` as a git submodule
   - **Legacy section comments in pyproject.toml**: Remove decorative banner comments
     like `# ====... \n # Ruff configuration \n # ====...`. These add no value — the
     `[tool.ruff]` headers are self-documenting. Flag all such banners for removal.
   - **Ruff ignore rule descriptions**: Every rule code in `extend-ignore`,
     `per-file-ignores`, and `extend-per-file-ignores` (in ALL sections including
     `[tool.ruff.lint]` and any `[tool.pixi.feature.*.dependencies]`-adjacent overrides)
     must have a brief inline comment explaining what it does. Example:
     ```toml
     extend-ignore = [
       "COM812",  # Avoid conflicts with ruff-format
       "D100",    # TEMPORARY: Missing docstring in public module
       "EM101",   # Exception must not use a string literal
       "F722",    # https://docs.kidger.site/jaxtyping/faq/#flake8-or-ruff-are-throwing-an-error
     ]
     ```
     Flag any rule codes missing descriptions. For `TEMPORARY` suppressions, keep the
     `TEMPORARY:` prefix so they're easy to grep for.
   - **GitHub Actions schema validation**: If the project has `.github/workflows/`,
     ensure `.pre-commit-config.yaml` includes the `check-github-workflows` hook from
     `python-jsonschema/check-jsonschema`. Flag if missing.
   - **GitHub Actions file extensions**: Workflow files in `.github/workflows/` should
     use `.yml` (not `.yaml`), matching GitHub's own convention. Flag any `.yaml` files
     for renaming.
   - **Configuration gaps**: missing ruff rules, ty config, etc.
   - **Structural issues**: wrong build backend, missing hatch-vcs, etc.
   - **Pixi environment names**: should follow the standard set
     (`py3XX`, `numpy`, `jax`, `cpu`, `cuda`, `cuda12`, `cuda13`, `tests`, `docs`),
     combined like `py314-jax`, `tests-cuda13`. Flag non-standard
     names (e.g., `test-cpu` should be `tests-cpu`, `default` should be `py3XX`).
   - **nbstripout kernelspec**: Check if `pyproject.toml` has `jupyter-book` or `mystmd`
     as a dependency anywhere (including `[project.dependencies]`,
     `[tool.pixi.dependencies]`, `[tool.pixi.pypi-dependencies]`, and any
     `[tool.pixi.feature.*.dependencies]` or `[tool.pixi.feature.*.pypi-dependencies]`
     sections). If so, flag that `metadata.kernelspec` should NOT
     be in nbstripout's `--extra-keys`. If the project doesn't use JB2, ensure
     `metadata.kernelspec` IS being stripped.
   - **GitHub Actions versions**: For each `.github/workflows/*.yml`, check ALL versioned
     references: `uses: <action>@<version>` tags (e.g., `actions/checkout`,
     `prefix-dev/setup-pixi`, `codecov/codecov-action`, `actions/setup-python`,
     `pypa/gh-action-pypi-publish`) and pinned tool versions (e.g., `pixi-version:`).
     For each, check the latest available version (via the action's GitHub tags page) and
     flag outdated ones.
   - **mdformat for mystmd projects**: If the project uses `mystmd` (detected via
     dependencies, see nbstripout check above) and has a `docs/` and/or `documents/`
     directory, the project needs **two** mdformat hooks under the same repo entry —
     one for GFM (root-level markdown) and one for MyST (docs). Do NOT replace the
     existing GFM hook; add a second hook alongside it. The expected config:
     ```yaml
     - repo: https://github.com/executablebooks/mdformat
       rev: 1.0.0
       hooks:
         - id: mdformat
           additional_dependencies:
             - mdformat-gfm
             - mdformat-gfm-alerts
             - mdformat-ruff
           args:
             - --wrap
             - "88"
           files: (AGENTS\.md|CLAUDE\.md|README\.md)
         - id: mdformat
           additional_dependencies:
             - mdformat-myst
             - mdformat-ruff
           args:
             - --wrap
             - "88"
           files: (docs/.|documents/.)
           exclude: (documents/presentation.md)
     ```
     The first hook uses `mdformat-gfm` for root-level files only (AGENTS.md, CLAUDE.md,
     README.md). The second hook uses `mdformat-myst` for docs directories. These MUST
     be separate hooks because `mdformat-gfm` and `mdformat-myst` are incompatible
     parsers.
     Adjust the second hook's `files:` pattern to cover whichever of `docs/`/`documents/`
     exist. Only include the `exclude: (documents/presentation.md)` line if
     `documents/presentation.md` exists and is a Slidev presentation (look for
     `theme:`, `---` slide separators, or Slidev frontmatter). Flag if the project has
     only a single mdformat hook trying to cover both GFM and MyST files.
   - **TEMPORARY ruff ignores**: Grep for `TEMPORARY` in `extend-ignore` and
     `per-file-ignores`. For each, ask the user whether it is still needed.
   - **jaxtyping F722**: If the project uses `jaxtyping` (check dependencies), ensure
     `"F722"` is in `extend-ignore` with comment linking to the jaxtyping FAQ.
   - **Pixi task names**: should follow the standard set
     (`tests`, `tests-with-cov`, `tests-jax`, `build-docs`, `view-docs`,
     `view-paper`, `view-pres`). Type checking is **not** a pixi task — ty runs as the
     `ty` pre-commit hook (`astral-sh/ty-pre-commit`), resolving imports from
     `[tool.ty] environment.python`. Flag non-standard names, a leftover `ty` /
     `type-checking` pixi task or environment, and a missing ty hook.

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

10. **Generate or update GEMINI.md.** If the user selected it in step 4, ensure GEMINI.md
    contains:

    ```
    @AGENTS.md
    ```

    If `AGENTS.md` is not at the repo root (e.g., in a parent directory), adjust the path
    to match whatever `CLAUDE.md` uses.

11. **Propose changes.** Show each proposed change as a before/after diff. Group by file.
    For environment/task renames, also check and update:
    - `AGENTS.md` / `CLAUDE.md` command references
    - `.github/workflows/` CI environment references
    - Any `Makefile` or scripts referencing old names

12. **Run prek.** After applying approved changes, run:

    ```bash
    pixi run prek run --all-files
    ```

    If any hooks fail on files that don't exist or don't apply to this project (e.g., a
    hook targeting `.md` files in a project with none), list those hooks and ask the user
    to confirm removal. Remove confirmed hooks from `.pre-commit-config.yaml`.

## Rules

- **Never overwrite** existing ruff exclusions, ty ignore rules, or per-file-ignores
  unless explicitly asked
- **Preserve project-specific ty suppressions**: When updating `[tool.ty]` rules, keep
  any rules set to `"ignore"` or `"warn"` — these are intentional project overrides
  (e.g., `rules.empty-body = "ignore"` for decorator patterns). Only replace the
  standard promoted-to-error rules from the boilerplate template
- **Never add pixi** if the project already uses `uv` — flag this and skip
- **Never remove** project-specific hooks (nbstripout, codespell, custom validators)
- **Preserve** custom pytest markers, filterwarnings, and test paths
- **Preserve** custom pixi environments and platform-specific tasks
- **Do not auto-apply changes** — present them for review, then apply only what the user
  approves
- **Update GitHub Actions** workflow references if task/environment names change
- **Migrate CLAUDE.md content** to AGENTS.md when possible so all tools benefit
