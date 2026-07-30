# extra-galaxies-point-source

Phase 1 of the extra-galaxies parity task. Added
`autolens_workspace/scripts/point_source/features/extra_galaxies/` — `README.md`,
`__init__.py`, `simulator.py`, `modeling.py` — closing the last gap in
extra-galaxies coverage at galaxy scale. **No `slam.py`**, per the user: SLaM is
an extended-source workflow.

- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/374 (CLOSED)
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/376 (MERGED `e005caca`)
- parent: `draft/docs/workspaces/extra_galaxies_feature_parity.md`
- phase 2 (`multi_galaxy`, both workspaces): prompt drafted, not yet issued

## Scope decisions

`group/` (already uses the API correctly in `start_here.py` + `modeling.py`) and
`cluster/` (correctly omits it) are **out of scope, confirmed by the user**.
`imaging/` and `interferometer/` in both workspaces are the confirmed standard to
copy.

Brain scored this `too-large (13) / split-into-4-phases` (design, core_api,
workspace_examples, docs) off its repo-count proxy. The `core_api` and `design`
phases are vacuous — no library code is touched at all. **Overridden** to two
phases split by regime: point_source, then multi_galaxy.

## Why the point-source example is not a port of imaging

For extended sources extra galaxies cause two problems — their light blends with
the source emission, and their mass perturbs the ray-tracing — so the imaging
example teaches two levers (noise-scale the emission out, or model light + mass).

A `PointDataset` holds image positions and fluxes, not an image. There is no
extra-galaxy light in the data, nothing to mask or noise-scale. The example is
**mass-only**, and three sections were rewritten rather than ported: Data
Preparation (the centres can only come from the accompanying imaging), Approaches
to Extra Galaxies (model-their-mass vs omit-them, with no middle ground), and
Wrap Up (points up the ladder to `group`, then `cluster`).

Verified no library change needed: `AnalysisPoint(AgAnalysis, AnalysisLens)`
(`PyAutoLens/autolens/point/model/analysis.py:36`) inherits
`tracer_via_instance_from`, which appends `instance.extra_galaxies` to the
tracer's galaxy list (`PyAutoLens/autolens/analysis/analysis/lens.py:127-129`).

## The effect is far larger than imaging intuition suggests

The first draft said "tens of mas". Measured instead: re-solving the simulated
system with the extra galaxies removed moves the four images by **50, 177, 537 and
795 mas** — one to two orders of magnitude above the 5 mas astrometric precision.

A multiple image *solves* the lens equation rather than reading out the deflection
field linearly, so near the Einstein ring a 0.1" deflection slides an image along
a nearly-degenerate direction until ray-tracing rebalances. Do not describe
point-source extra galaxies as a small correction.

## The information budget is the design driver

A quad gives 8 positional data points against a 10-parameter model, so the
simulated dataset **includes fluxes** (4 more points) to make the extra-galaxies
model identifiable. This is also what forces the fixed centres, the capped
`einstein_radius` and the omitted `ExternalShear` — constraints that read as
stylistic in the imaging example. Both scripts make the budget explicit.

## PyAutoFit#1179 is script-specific, not package-wide

`smoke_tests.txt:7` disables `point_source/start_here.py` for a bypass-mode
tuple-path `KeyError`, and the plan assumed no point-source script could be
smoke-gated. Wrong — the new `modeling.py` passes under `PYAUTO_TEST_MODE=2` and
is **enabled** in smoke (17/17, up from 16), with a comment scoping the ban.

**Trap:** the first bypass attempt appeared to pass but had silently **resumed**
the earlier `PYAUTO_TEST_MODE=1` run. Both modes share the `output/test_mode/`
namespace — the segment separates test from prod, not the two test modes from each
other. `rm -rf output/test_mode` before trusting a bypass result.

## CI fallout: PyAutoHands#213

The first push went red on `navigator / Navigator paths + banner lint` with 5
missing references in files this PR never touched. PyAutoHands#213 ("gate relative
folder references in README prose") merged at 08:28 UTC, between
autolens_workspace main's last green navigator run (08:21, `f7d7884d`) and this
PR's first (08:32) — this branch was simply the first to run under the stricter
checker. Cloning main and running under the CI root layout reproduced the identical
5 findings, so main was red too.

Fixed in commit `3dc5058e`: the 5 are literal `autolens_workspace/scripts/...`
references, where the convention everywhere else is the wildcard
`autolens_workspace/*/...` form the gate tolerates; `scripts/README.md` refers to
its own folder so the redundant prefix was dropped.

**Root-name trap worth a PyAutoHands follow-up:** `check_navigator.py`'s
`normalise()` strips a leading `<root.name>/` prefix, and CI clones the workspace
as `workspace/`, so an `autolens_workspace/`-prefixed literal can never be
stripped there. Running `--root autolens_workspace` locally passes on
byte-identical content. Reproduce CI by cloning into a directory literally named
`workspace` and passing `--root workspace`.

## Validation

- `run_smoke.py`: **17/17 passed** (16 before, +1 new entry)
- `scripts/check_sizes.sh`: clean
- Notebooks + navigator catalogue regenerated; diff scoped to the new folder plus
  `llms-full.txt` / `workspace_index.json`
- CI: 4/4 green (navigator paths + catalogue, smoke 3.12 + 3.13)
- **Real non-test-mode Nautilus fit**: lens `einstein_radius` 1.5987 (true 1.6),
  source centre (0.076, 0.075) (true 0.07, 0.07), flux 1.04 (true 1.0), perturbers
  0.1014 (true 0.1) and 0.1434 (true 0.15)
- `group/` and `cluster/` untouched

## Heart

Shipped on an acknowledged **YELLOW** (score 65), 3 reasons, all pre-existing and
unrelated: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33
stale parked script(s); release validation stale — source moved since rehearsal
(PyAutoFit, PyAutoGalaxy, PyAutoLens).

## Concurrency

`likelihood-function-jax-pointer` (#368) held a parallel claim on the same repo and
merged mid-task as PR#375, harmlessly — zero source-file overlap. Its merge also
**unblocks** the queued `multi-galaxy-imaging-parity` task in `planned.md`, which
touches `multi_galaxy/simulator.py` and is complementary to (not overlapping with)
phase 2. `worktree_check_conflict` again reported no conflict despite the live
claim.

## Original prompt

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
