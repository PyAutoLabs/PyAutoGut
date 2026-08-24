# Phase 2: workspace READMEs made assistant-first

- shipped: 2026-07-24, inside the phase-1 task rather than as a separate PR —
  see `complete/2026/07/assistant-first-docs.md`.
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/645
- workspace-prs: https://github.com/PyAutoLabs/autolens_workspace/pull/329,
  https://github.com/PyAutoLabs/autogalaxy_workspace/pull/155
  (library legs PyAutoLens#646 + PyAutoGalaxy#521 were phase 1).
- summary: this prompt's whole scope — one concise **AI Assistant** route first in
  each workspace README's Getting Started, **Three Ways to Learn PyAutoLens**
  removed, Colab/notebook/browsable-example routes preserved, remaining links
  described as human-readable documentation — landed as the workspace leg of
  `assistant-first-docs`, which unified library README, Read the Docs *and*
  workspace onboarding in one pass. The PyAutoGalaxy assistant URL was
  deliberately allowed to 404 until its repository exists.

## Lifecycle note

Phase 1 recorded the workspace PRs but the phase-2 prompt file was never advanced,
so it kept rendering as pickable backlog long after the work merged. Recorded here
by the 2026-08-24 completed-prompt reconciliation sweep — the split into phases 1/2
was a planning artefact that the shipping session collapsed.

## Original prompt

# Phase 2: Make workspace READMEs assistant-first

Filed: 2026-07-24 (backfilled from git)

Update @autolens_workspace and @autogalaxy_workspace after the library and Read
the Docs phase. Put one concise **AI Assistant** route first in Getting Started,
covering conversation agents (for example ChatGPT) and coding agents (for
example Claude Code and Codex), with the full setup and capabilities left to the
relevant assistant repository.

Preserve the existing installation, Google Colab, notebook, and browsable
example routes. Remove **Three Ways to Learn PyAutoLens** from the lens workspace
README and describe the remaining resources as human-readable documentation and
examples.

The intended PyAutoGalaxy assistant URL must resolve before its links are
published.

## Original request

- All readthedocs / README.md explaining the assistant should not have two separate splits for **AI chat assistant** 
and **Fully agentic AI**, but instead just say AI assistant. They should concisely say conversation agents (e.g. ChatGPT)
and coding agents (e.g Claude, codex) and then point to the assistant URL, which is where the user gets the full scope.
- 
- PyAutoLens and PyAutoGalaxy README.md should point to their assistant in the "Getting Started" section, and
then have the bit The following links are useful for new starters but say they are human readable docs.
- It feels like we are oging to get rid fo this section "## Three Ways to Learn PyAutoLens", and these style changes
will also hapepen on readthedocs and the workspace README.md files.

- the worksapce readme should keep the colab stuff, but point to the assistant in Getting Started first. Again
I think "## Three Ways to Learn PyAutoLens" will thus go.
