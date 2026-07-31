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
