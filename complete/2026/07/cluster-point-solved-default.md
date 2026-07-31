## cluster-point-solved-default
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/436 (follow-up of the point-source-chi-squared-variants series, #657 wrap-up decision)
- completed: 2026-07-31
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/441 (merged 2026-07-31)
- summary: Cluster examples' demonstrated default moved from free-centre `al.ps.Point` to parameter-free `al.ps.PointSolved` + `fit_positions_cls=al.FitPositionsSourceSolved` (search source-plane, validate image-plane). `scripts/cluster/modeling.py`: point components swapped via `setattr(galaxy_models[f"source_{i}"], f"point_{i}", af.Model(al.ps.PointSolved))` (name pairing preserved; point.csv centres now truth-record only), GaussianPrior centre loop removed, N=10→6; prose updated (chi-squared framing, solver relegated to visualization/validation, name-pairing cell flips free-centre to the documented alternative, JAX note now says deflection sum dominates, stale "lens-equation not differentiable" claim softened). `scripts/cluster/start_here.py`: same swap for the 7 a2744 sources, N=20→6, capabilities/JAX/search prose updated (n_live=150 kept, "6-D" noted). `scripts/cluster/likelihood_function.py`: closing when-to-use-which prose now states the modeling scripts demonstrate the recommended solved configuration. `lenstool/modeling.py` deliberately unchanged (Lenstool free-centre mirror). Notebooks regenerated + workspace_index.json refresh. Galaxy-scale point_source examples keep free-centre per the original #657 decision (note: superseded same-day by the solved-everywhere campaign — this task is a subset of that direction, not in conflict).
- gotchas: cluster scripts are NOT in smoke_tests.txt — smoke was ad-hoc under the profile_smoke env. modeling.py smoke PASS; start_here.py smoke ran healthy ~35 min on the contended single-core box and was deliberately aborted when the human authorized merge ahead of the superseding campaign; the real-inference Nautilus convergence run was skipped for the same reason. Shipped under Heart RED (release-validation integrate-stage failure + repos.yaml manifest drift, unrelated to this workspace change) on explicit human merge instruction.
- follow-ups: the human's larger test campaign (solved-everywhere defaults) supersedes/extends this; start_here.py full-execution validation rides on that campaign (its notebook also runs on Colab CI paths).

## Original prompt

# Cluster examples: move demonstrated default to PointSolved + solved fits

Human decision (2026-07-31, #657 wrap-up): galaxy-scale `point_source` examples KEEP the
free-centre `al.ps.Point` / `PointFlux` demonstrated defaults; the CLUSTER examples move
their demonstrated default to `al.ps.PointSolved` + the solved fit classes.

## Scope (autolens_workspace only)

- `scripts/cluster/modeling.py` + `scripts/cluster/start_here.py`: source-tier `Point`
  components -> `al.ps.PointSolved`; analyses gain
  `fit_positions_cls=al.FitPositionsSourceSolved` (the recommended search-stage fit per
  `guides/point_source_pairing.py`); prose updated (each source drops 2 free params;
  validate image-plane on the max-likelihood model).
- `scripts/cluster/likelihood_function.py`: the "search source-plane, validate
  image-plane" walkthrough advice already names the solved fit — check the surrounding
  prose still reads correctly once the modeling scripts demonstrate it.
- `scripts/cluster/lenstool/modeling.py` STAYS free-centre `FitPositionsSource`
  (deliberately mirrors Lenstool's convention — table row already documents the solved
  sibling).
- Guard: priors/GaussianPrior initialisation of the old per-source centres must be
  removed with the parameters; check `galaxy_af_models_from_csv_tables` interaction
  (point_table centres become PointSolved-irrelevant).
- Regenerate notebooks; smoke the cluster scripts.

## Evidence base

- Phase-3 profiling: analytic beta* ~ timing-noise overhead, -2 params/source.
- 2026-07-31 truth-anchored benchmark: free-centre scalar-mu^2 source-plane likelihood
  prefers wrong over-lensed models by ~4 orders of magnitude in chi^2 on the galaxy-scale
  toy; solved tensor weighting is the recommended flavour.
- Pending: prodigy image_plane_solved cell result (running at filing time).

## Exit criteria

Cluster modeling + start_here demonstrate PointSolved/solved fits; notebooks regenerated;
ship_workspace PR; pairing-guide recommendation and demonstrated practice now consistent.
