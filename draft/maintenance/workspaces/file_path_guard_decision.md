# Decide the 11 file-path auto-simulate guards

Type: maintenance
Target: workspaces
Repos:
- autolens_workspace
- autofit_workspace
Difficulty: easy
Autonomy: supervised
Priority: low
Status: formalised

Split from the raw-guard migration (dataset-bulk series leg 3): 11 auto-simulate guards
whose guarded path is a **file**, not a directory. They have a paired simulator, but
`should_simulate` calls `shutil.rmtree(path)` → `NotADirectoryError` on a file, and
passing the parent dir instead changes the guard's semantics (dir-exists vs file-exists).
Each needs a per-site call: pass the parent dir, or leave the raw guard with a comment.

Sites (2026-07-27 census):
- autolens_workspace: `multi/features/pixelization/modeling.py:91`,
  `guides/plot/examples/plotters.py:351`, `guides/modeling/customize.py:54`,
  `imaging/features/advanced/shapelets/modeling.py:116`,
  `imaging/features/pixelization/{adaptive.py:101, cpu_fast_modeling.py:94, modeling.py:158, source_science.py:66}`,
  `interferometer/features/pixelization/many_visibilities_preparation.py:90`
- autofit_workspace: `features/graphical_models.py:74`, `features/shared_analysis_state.py:80`
  (both guard `.../dataset_0/data.json`; note autofit_workspace has no should_simulate
  namespace today — see the leg-3 rejection rationale)
