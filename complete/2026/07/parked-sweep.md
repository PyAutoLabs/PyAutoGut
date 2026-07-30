Stale parked-script sweep: 11 → 0, every verdict measured, one real bug found.

- issue: PyAutoLabs/autolens_workspace_test#234 (left open for human close; carries
  the full verdict table)
- prs: autogalaxy_workspace#193, autolens_workspace#406, autolens_workspace_test#236 — merged
- method: entries deleted in a worktree, each directory re-run through run_python.py
  under profile_smoke (SEQUENTIAL — parallel fakes failures); verdicts from evidence:
  - UN-PARKED: ag guides/results/workflow/csv_make (61.1s < the real 300s cap — 61s
    explains the mythical-60s-cap parking exactly).
  - NEEDS_FIX (were never slow): ag+al guides/results/database/start_here fail fast
    in a clean checkout (missing generated dataset/).
  - NEEDS_FIX (new REAL finding): imaging modeling_visualization_{delaunay,rectangular}_jit
    now FAIL their own JIT-cache assertion at 36-52s (cached call not < 0.5x compile)
    — closure cache-busting suspected; bug prompt filed:
    draft/bug/autolens/jit_cache_not_hit_modeling_visualization.md.
  - SLOW re-dated 2026-07-30 with measured evidence: 4 scrape scripts + imaging
    modeling_visualization_jit (300s timeouts), interferometer modeling_visualization_jit
    (historically >300s; local rerun OOM-killed — annotated).
- doctrine: a parked entry's justification must cite the real cap and a measurement;
  seven entries had cited a 60s cap that never existed.

## Original prompt

# Stale parked-script sweep: re-measure 11 no_run entries against the real cap

Type: maintenance
Target: workspaces
Repos:
- autogalaxy_workspace
- autolens_workspace
- autolens_workspace_test
Difficulty: small
Autonomy: supervised
Priority: normal
Status: issued — https://github.com/PyAutoLabs/autolens_workspace_test/issues/234

11 stale SLOW entries; seven cite a 60s cap that never existed. Delete, re-run
each directory through run_python.py under profile_smoke (sequential), keep
deletions under cap, restore over-cap with 2026-07-30 dates + corrected reasons.
Filed from the 2026-07-30 CI/release audit follow-on assessment.
