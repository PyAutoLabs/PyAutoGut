# Phase 1 — extra_galaxies feature: point_source

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/extra_galaxies_feature_parity.md

Phase 1 of the extra-galaxies parity task. The user confirmed
`imaging/features/extra_galaxies` and `interferometer/features/extra_galaxies` are the
standard; `point_source/` contains **zero** references to extra galaxies today.

> Add to point_source/features, same style but wont have a slam.py

## Scope

New `autolens_workspace/scripts/point_source/features/extra_galaxies/`:
`README.md`, `__init__.py`, `simulator.py`, `modeling.py`. **No `slam.py`** — user-specified
(SLaM is imaging/interferometer-only).

Plus: add `extra_galaxies` to the `# Folders` list in
`scripts/point_source/features/README.md`.

## The physics that drives the prose

Point-source data has no image pixels, so **neither** lever the imaging example teaches
transfers directly: there is nothing to noise-scale and no extra-galaxy light to fit.
The example is **mass-only** — extra galaxies perturb the deflection field and therefore
the solved multiple-image positions.

Support verified in the library (no library change needed):
`AnalysisPoint(AgAnalysis, AnalysisLens)` (`PyAutoLens/autolens/point/model/analysis.py:36`)
inherits `tracer_via_instance_from`, which appends `instance.extra_galaxies` to the tracer's
galaxy list (`PyAutoLens/autolens/analysis/analysis/lens.py:127-129`).

## Script content

`simulator.py` — one main lens (`Isothermal` + `ExternalShear`), two perturbers
(`IsothermalSph`, small `einstein_radius`), source `Point`; `PointSolver` locates the images;
writes `point_dataset.json`, `extra_galaxies_centres.json` and the tracer json to
`dataset/point_source/extra_galaxies/`. Mirror `point_source/simulator.py` and
`point_source/features/multiple_sources/simulator.py` for boilerplate.

`modeling.py` sections: Dataset (+ `al.util.dataset.should_simulate` auto-simulation block),
Point Solver, Extra Galaxies Centres, Model, Extra Galaxies Model, Name Pairing,
Search + Analysis, Run Time, Model-Fit, Result, Approaches to Extra Galaxies, Wrap Up.

Reuse the imaging example's model idiom verbatim where it transfers (`IsothermalSph` with
`mass.centre` fixed to the loaded centre, `einstein_radius` capped by a `UniformPrior`,
collected into `af.Collection(...)` passed as `extra_galaxies=` —
`imaging/features/extra_galaxies/modeling.py:363-394`). Three sections must be rewritten,
not ported:

- **Data Preparation** — the centres come from the *accompanying imaging*
  (`imaging/data_preparation/examples/optional/extra_galaxies_centres.py`); point-source data
  alone cannot supply them.
- **Approaches to Extra Galaxies** — replaces imaging's noise-scaling-vs-modeling contrast
  with the point-source one: model the perturber mass, or omit it and accept positional
  systematics.
- **Wrap Up** — points up the ladder: many point sources behind many deflectors is `cluster/`.

## Constraints / known traps

- **No point-source script is smoke-enabled.** `smoke_tests.txt:7` disables
  `point_source/start_here.py` for a bypass-mode tuple-path `KeyError`
  (rhayes777/PyAutoFit#1179), so `PYAUTO_TEST_MODE=2` cannot validate these scripts. Add the
  new `modeling.py` as a **commented-disabled** entry citing the same reason, and validate by
  a real short local run (`PYAUTO_TEST_MODE=1`).
- `should_simulate` tests directory EXISTENCE only — `rm -rf dataset/point_source/extra_galaxies`
  before any validation run ([[feedback_should_simulate_existence_only]]).
- Workspace bulk-edit rule: never whole-file `Write` a file not fully read; run
  `scripts/check_sizes.sh` before committing.
- Parallel claim on `autolens_workspace`: #368 (likelihood-function-jax-pointer, in dev).
  (#366 multistart-prodigy MERGED 2026-07-29 — no longer a claim.) Human decision
  2026-07-29: proceed in parallel — this task creates only NEW folders. Generated artifacts
  (`notebooks/`, `llms-full.txt`, `workspace_index.json`) collide; last PR to merge re-runs
  `generate.py`.

## Acceptance

- `simulator.py` writes the dataset + `extra_galaxies_centres.json` from a clean
  `dataset/point_source/extra_galaxies/`.
- `modeling.py` runs end-to-end under `PYAUTO_TEST_MODE=1`.
- `python .github/scripts/run_smoke.py` green; `scripts/check_sizes.sh` clean.
- `point_source/features/README.md` `# Folders` updated (README ref-drift is CI-gated).
- Notebooks + navigator catalogue regenerated via PyAutoHands `generate.py`.
- `group/` and `cluster/` untouched.
