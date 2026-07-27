# Latent dataset_Path NameError in subhalo sensitivity SLaM scripts

Type: bug
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: easy
Autonomy: safe
Priority: low
Status: formalised

Found during the 2026-07-27 raw-guard census (dataset-bulk series leg 3):

- `scripts/imaging/features/advanced/subhalo/sensitivity/slam_source_parametric.py:876`
- `scripts/imaging/features/advanced/subhalo/sensitivity/slam_source_pixelized.py:1003`

both read `if not dataset_Path().exists():` — `dataset_Path` is defined nowhere in the
workspace, a guaranteed `NameError` at that line. Masked only because
`imaging/features/advanced/subhalo/sensitivity/` is listed in
`config/build/no_run.yaml:42`, so nothing ever executes them.

Fix: correct to the standard guard over the script's actual `dataset_path` (and migrate
to `should_simulate` to match the post-leg-3 idiom), regenerate the two paired
notebooks, and prove the scripts at least reach past the guard (full runs are slow —
that's why they're no_run; a truncated/import-level witness is acceptable, state what
was run). Also worth checking the rest of the guard block for copy-paste rot since the
line was never executed.
