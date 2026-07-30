# scaling_relation BGC-anchored — phase 1: imaging + multi_galaxy

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/scaling_relation_bgc_anchored_feature_packages.md

Phase 1 of 2. Read the parent for the verbatim request, the verified research findings
(top-level `scaling_galaxies` collection, zero-free-parameter BGC tie, two-tier structure,
per-regime constraints, untruncated-vs-dPIE thread) and the known PR collisions.

**Phase split rationale (overrides Brain):** Brain scored the parent `too-large (13)` and proposed
four generic phases (`design` / `core_api` / `workspace_examples` / `docs`). That is the known
repo-count difficulty proxy misfiring — this is one repo with zero library API change, so a
`core_api` phase is vacuous. Split by regime instead, on the seam that actually exists: **imaging
and multi_galaxy have a light fit**, so they carry the canonical prose and the
measure-luminosities-in-`light_lp` `slam.py`. Phase 2 ports to the two mass-only regimes.

## Scope

Both packages get `simulator.py`, `modeling.py`, `fit.py`, `likelihood_function.py`, `slam.py`,
`README.md`, `__init__.py`.

1. `scripts/imaging/features/scaling_relation/` — rewrite. The existing files teach the Lenstool
   free-`einstein_radius_ref` convention; replace with the BGC-anchored tie, where at galaxy scale
   the anchor is the single main lens's own free `einstein_radius`. Keep the two-tier structure
   (bounded-free `extra_galaxies` + tied `scaling_galaxies`) but move the scaling tier out of the
   `extra_galaxies` collection into the top-level `scaling_galaxies` collection.
2. `scripts/multi_galaxy/features/scaling_relation/` — `git mv` from `features/scaling_galaxies`,
   then rewrite `modeling.py` onto the top-level collection with the BGC selected by
   `argmax(luminosity)` over the co-dominant lenses, and add the three missing files. Its `slam.py`
   is the workspace's first multi_galaxy SLaM pipeline, adapted from `mgl_slam_batch.py`.

New datasets `dataset/imaging/scaling_relation` and `dataset/multi_galaxy/scaling_relation` (not a
reuse of `extra_and_scaling_galaxies` / `scaling_galaxies` with changed truths — `should_simulate`
tests directory existence only, so a stale local dataset would silently fit the wrong truths).

## Docs register

Minimal, deferring to `scripts/<regime>/{fit,modeling,likelihood_function,simulator}.py` for
anything not specific to the scaling tier. In every file: JSON centres + explicit Python luminosity
list documented FIRST as the primary interface; `al.galaxy_table_from_csv` near the END. The
non-`slam.py` files assume measured luminosities and say plainly that they must be measured,
pointing at the package's own `slam.py`. Untruncated isothermals with the tidal-stripping reasoning,
and the pointer to truncated `dPIEMass` at group/cluster scale, appear in all of them.

## Housekeeping

- `smoke_tests.txt`: replace the `multi_galaxy/features/scaling_galaxies/modeling.py` entry with the
  two new `modeling.py` paths.
- Repoint cross-references that assume the old imaging convention:
  `imaging/features/extra_galaxies/modeling.py:486-490`,
  `group/features/scaling_relation/modeling.py:33-34`, `multi_galaxy/modeling.py` Features section,
  `multi_galaxy/features/README.md`.
- No `"""Finish."""` / `"""Finished."""` trailer (the convention PR#384 is removing; the source
  `mgl_slam_batch.py` still has one — do not copy it).
- `scripts/check_sizes.sh --update` in the same diff; notebooks + navigator regenerated.

## Acceptance

- Smoke green for both `modeling.py` under `PYAUTO_TEST_MODE=2` + `PYAUTO_SMALL_DATASETS=1`.
- Both `fit.py` and `likelihood_function.py` run for real (no search, so fast).
- Each `modeling.py` demonstrates `model.prior_count` is unchanged by the scaling tier.
- `mge_model_from` duplicate-kwarg bug from `mgl_slam_batch.py:269-270` not carried into `slam.py`.
