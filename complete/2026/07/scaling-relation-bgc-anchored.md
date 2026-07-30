# scaling_relation: BGC-anchored Faber-Jackson tier across four regimes

Shipped 2026-07-30 as two stacked PRs on `autolens_workspace`, both merged.

- Phase 1 — issue #385, PR#396 merged `63dbafe8` (imaging + multi_galaxy)
- Phase 2 — issue #397, PR#398 merged `4fb2c776` (interferometer + point_source)

## What shipped

A `features/scaling_relation` package in all four regimes, exposing the tier from
the user's `mgl_slam_batch.py`, where each member's Einstein radius is tied to the
brightest main galaxy's **own free** `einstein_radius`:

    einstein_radius_i = einstein_radius_bgc * (L_i / L_bgc) ** 0.5

The anchor is a parameter the model already fits, so the tier costs **zero** free
parameters. Each package has `simulator`, `modeling`, `fit`, `likelihood_function`
and `README`; `slam.py` in all but `point_source` (which has no light to measure).

This REPLACED `imaging/features/scaling_relation`, which taught a standalone free
`einstein_radius_ref` at a fixed reference magnitude (Lenstool `mag0`) costing one
parameter, and renamed `multi_galaxy/features/scaling_galaxies` to
`features/scaling_relation`. `group/` and `cluster/` deliberately keep `mag0` plus
truncated `dPIEMass`, correct where a host halo exists; the contrast is
cross-linked both ways.

Docs register per the request: non-CSV interface (JSON centres + explicit
luminosity list) documented FIRST, `al.galaxy_table_from_csv` at the END.

## Verified answers to the three open questions

1. **Model API.** The top-level `af.Collection(galaxies=…, extra_galaxies=…,
   scaling_galaxies=…)` form is canonical — `scaling_galaxies` is a first-class
   collection (`autogalaxy/analysis/analysis/analysis.py:86`,
   `autolens/analysis/analysis/lens.py:131`, `autolens/aggregator/tracer.py:97`,
   `autogalaxy/aggregator/galaxies.py:72`). The old multi_galaxy file folded it
   into `galaxies`, forfeiting the labeled collection and the aggregator path.
2. **The old imaging feature.** Confirmed a different physical model, hence
   overwritten rather than extended.
3. **Untruncated vs dPIE.** Stated in all four packages with the tidal-stripping
   reasoning.

## Findings

- **A spherical fixed-centre MGE has `prior_count == 0`** — so a scaling galaxy is
  free in light AND mass. Proven in-script by composing a freed-tier variant:
  imaging 21 vs 26, multi_galaxy 20 vs 25, interferometer 14 vs 19, point_source
  8 vs 13.
- **point_source is where the relation matters most**: 12 data points, 8 free
  params tied, **13** freed — freeing the tier makes the model under-determined.
  Removing the tier moves the four images by 182/398/1596/1633 mas vs 5 mas
  astrometry, while per-member deflections are only 150-300 mas: the lens equation
  amplifies ~5x rather than averaging.
- **Simulator truths derived from the relation**, not typed in — light is the
  input, `luminosity_within_circle_from` integrates it, the Einstein radius
  follows. Drift is now an error rather than a mistuned constant.

## Bugs fixed

Two in the user's source script, reported to them:

1. `mgl_slam_batch.py:269-270` passes `mask_radius` twice to `mge_model_from` —
   `TypeError` on any run reaching `lens_light_2`.
2. `mgl_slam_batch.py` passes `dataset_larger` to `light_lp` with `adapt_images`
   from a standard-mask fit. Adapt images are defined on their own mask, so this
   raises `TypeError: mul got incompatible shapes ... (1, 11304, 1),
   (512, 68836, 2)`. Fires only when scaling galaxies push `mask_radius_larger`
   above `mask_radius` — exactly the case the pipeline exists for.

Two of mine, caught before they could mislead:

3. `luminosities_from` offset the tiers by the lens count, but from `source_lp` on
   the `galaxies` collection also holds the source — a pixelization source has no
   `bulge`, so the re-measurement raised `AttributeError`. Now offset by the whole
   collection's length.
4. multi_galaxy `lens_light[2]` fixes both lenses as instances, so a
   zero-parameter tier emptied the model (`Model has no priors!`). Its tier light
   is now elliptical; both pipelines assert `prior_count > 0` in the light stage.

Plus: `mass_total`'s bounded-tier cap could collapse to a zero-width prior
(floored); the point_source dataset's first draft put companions at 2-3" where
derived radii reached 0.51" and `PointSolver` returned SIX images, breaking the
quad (moved to ~4.3-4.9").

**Design decision recorded:** multi_galaxy does NOT re-measure luminosities after
`light[1]`. Only the ratio `L_i / L_bgc` enters, so taking numerator and
denominator from different light fits on different masks injects a systematic into
every member's mass. `lens_light[2]` is the single source.

## The late merge catch

PR#396 went `CONFLICTING` at merge time: four PRs (#391, #393, #394, #395) landed
while it was open. **#391 added `multi_galaxy/features/extra_galaxies/` with five
references to `features/scaling_galaxies`** — the folder this arc renames. Those
references could not exist when the branch was cut, so only the merge tree exposed
them. The navigator gate caught the one in README prose; the other four were in
docstrings, which the path check does not validate, and would have shipped dead.
All five repointed, and main's claim that the tier "costs a fixed couple of
parameters" corrected to zero.

## Validation

Both PRs 4/4 green on CI (navigator paths + banner lint, catalogue staleness,
smoke 3.12 + 3.13). Locally: smoke 20/20 on the phase-1 merged tree, 22/22 on
phase 2; all three `slam.py` pipelines end-to-end under bypass (imaging 6/6,
multi_galaxy 7/7, interferometer 4/4); `fit.py` / `likelihood_function.py`
deflection-sum assertions passing in every regime; navigator reproduced in the CI
directory layout (clone named `workspace`, `--root workspace`).

`smoke_tests.txt` grew from 16 to 21 entries (four new `scaling_relation`
`modeling.py`, plus main's `multi_galaxy/features/extra_galaxies`).

Heart YELLOW (score 70, no RED) acknowledged by the human before shipping; reasons
unrelated (cloud run reported 0p/0f/0s, manifest drift, stale release validation).

## Process notes

- Brain scored the parent `too-large (13)` with four vacuous phases
  (design/core_api/workspace_examples/docs) — the repo-count proxy misfiring on a
  one-repo, zero-library-change task. Overridden to two phases split by regime.
- `worktree_check_conflict` returned 0 while `worktree_list_claimed` showed two
  claims on autolens_workspace. Both colliding PRs merged before any edit.
- Phase 2 was stacked on phase 1 so its cross-references to phase-1 files resolved
  for the navigator gate; the stack collapsed to phase-2-only once #396 merged.
- Worktrees removed, local and remote branches deleted, no orphan registrations.
