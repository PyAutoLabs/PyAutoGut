# Teach hygiene `refs` the workspace-README drift class

Type: feature
Target: pyautobrain
Repos:
- PyAutoBrain
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

The hygiene `refs` mode cannot see the dominant reference idiom in workspace
`README.md` files, so a whole class of restructure debt accumulates invisibly.
`autolens_workspace/README.md` still lists `slam_pipeline` as a top-level
directory; it has not existed for a long time (SLaM lives under
`scripts/guides/modeling/slam_start_here.py` and `scripts/multi/features/slam/`).

Two independent gaps in `agents/conductors/hygiene/_hygiene_refs.py`:

1. **Scanned set too narrow.** `scanned_files()` reads `scripts/**/*.py` plus the
   *top-level* README only. Nearly all of the drift lives in nested
   `scripts/**/README.md` and `config/**/README.md`.
2. **`is_reference()` cannot match the README idiom.** It accepts a reference
   only when it ends in `/` (multi-segment) or its last segment matches
   `\.(py|ipynb)$`. Workspace READMEs instead write:
   - bare structure-list bullets — ``- `slam_pipeline`: The SLaM pipelines…``
   - directory paths with no trailing slash — `` `data_preparation/imaging` ``
     (the real package is `imaging/data_preparation`)
   - config file names — `` `mcmc.yaml` ``, `` `generag.yaml` ``

Extend the scanner to cover all three shapes, plus the widened file set. Keep
every existing precision suppression (`RUNTIME_DIRECTORIES`, bare `name.py`,
single-segment folder refs, un-checked-out siblings) — this tier's value depends
on staying high-precision. Confine the bare-name rule to the ``- `x`: `` bullet
idiom so a backticked word in running prose is never treated as a reference.

Resolution reuses the existing `RepositoryIndex.has_directory` / `has_file`
machinery; no new resolver is needed.

Add cases to `tests/test_hygiene_conductor.py` covering each new rule **and**
each known false-positive class, specifically these verified non-findings which
must stay unreported: runtime-generated targets (`main_lens_centres.json`,
`dataset/imaging/clumpy`, `search_internal/`, `activate.sh`) and cross-repo refs
that genuinely resolve in a sibling checkout.

Update the `refs` row in `agents/conductors/hygiene/AGENTS.md` and the `refs`
gloss in `skills/hygiene/hygiene.md` to describe the widened scope.

Acceptance: `bin/pyauto-brain hygiene refs` surfaces the audited autolens /
autogalaxy README findings (structure-list entries, reversed relative paths,
`generag.yaml`, stale config inventories) with no verified false positive
present, and `bin/pyauto-brain hygiene` still emits a coherent ranked worklist.

## Original request

> the autolens workspacde readme has API drift (e.g. it refers to slam_pipeline).
> Can you do a sweep of this over autolens_workspaceand gaalxy and then put the
> thing in the hygeine agent?
