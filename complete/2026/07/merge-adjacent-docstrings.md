## merge-adjacent-docstrings
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/341
- completed: 2026-07-24
- workspace-pr: https://github.com/PyAutoLabs/autocti_workspace/pull/9, https://github.com/PyAutoLabs/autofit_workspace/pull/118, https://github.com/PyAutoLabs/autogalaxy_workspace/pull/163, https://github.com/PyAutoLabs/autolens_workspace/pull/342, https://github.com/PyAutoLabs/HowToGalaxy/pull/45, https://github.com/PyAutoLabs/HowToLens/pull/55
- summary: Phase 3 of the adjacent-docstrings arc (PyAutoHands#196 → PyAutoBrain#162 → here). Merged 80 adjacent-docstring boundaries across 57 scripts in 6 workspace repos (autolens PR #340 had already removed the 81st); HowToFit verified zero-change. Final Hygiene scan 0 findings / 0 parse errors; exact prose-transform and compile witnesses passed; post-generation validation AutoFit 10/10, AutoGalaxy 8/8, AutoLens 11/11, HowToGalaxy 4/4, HowToLens 6/6, AutoCTI rc=0. Shipped under the 2026-07-24 heart-ack (exact YELLOW reasons recorded in the active.md entry at the time). All six PRs merged 2026-07-24; issue closed and worktree released 2026-07-27.

## Original prompt

# Phase 3: Merge adjacent documentation blocks in workspaces and HowTos

Type: maintenance
Target: workspaces
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

Depends on:
- `draft/bug/pyautobuild/back_to_back_docstrings_notebook.md`
- `draft/feature/pyautobrain/adjacent_docstring_hygiene.md`

## Requested scope

Run the new Hygiene adjacent-docstring scan across @autofit_workspace,
@autogalaxy_workspace, @autolens_workspace, @autocti_workspace, @HowToFit,
@HowToGalaxy and @HowToLens. Merge every confirmed pair of consecutive top-level
triple-quoted documentation blocks separated only by whitespace, preserving all prose and
section ordering. Do not change ordinary string literals or blocks separated by code.

The initial read-only survey on 2026-07-24 found 79 adjacent boundaries in 56 scripts across
six of the seven repositories (none in HowToFit). Re-run the implemented scanner rather than
treating this provisional count as the source of truth. After cleanup, require a zero-finding
Hygiene result and validate representative generated notebooks, including
`autolens_workspace/start_here.py`, contain no literal `# %%`/triple-quote artifact cells.

This is phase 3 of the original request recorded verbatim in
`draft/bug/pyautobuild/back_to_back_docstrings_notebook.md`.
