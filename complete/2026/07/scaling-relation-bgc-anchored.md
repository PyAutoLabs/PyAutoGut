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

## Original prompt

# features/scaling_relation packages: BGC-anchored Faber-Jackson tier across four regimes

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: shipped 2026-07-30 — BOTH phases merged (autolens_workspace PR#396 `63dbafe8`, PR#398 `4fb2c776`);
  issues #385 and #397 closed. Completion record: complete/2026/07/scaling-relation-bgc-anchored.md
Supersedes: draft/docs/workspaces/galaxy_scale_scaling_extra_features.md (scaling half; its
extra_galaxies half shipped as autolens_workspace#376 / autogalaxy_workspace#184)

## Original request (verbatim)

> The file mgl_slam_batch.py shows how we compose scaling_galaxies for a multi_galaxy lens
> model, **Scaling Galaxies**
>
> Scaling galaxies are a larger ensemble of companions whose masses are constrained through a
> Faber-Jackson scaling relation anchored to the brightest main galaxy (BGC, `lens_0`). They each
> carry a free MGE light profile, but their Einstein radii follow:
>
>     einstein_radius = einstein_radius_bgc * (luminosity / luminosity_bgc)^0.5
>
> where `einstein_radius_bgc` is the free Einstein radius of the brightest main lens (Isothermal
> in `source_lp[1]`, PowerLaw in `mass_total[1]`) and `luminosity_bgc` is its fixed luminosity
> computed from the preceding light fit. The exponent 0.5 is the Faber-Jackson index appropriate
> for multi-galaxy lensing. This anchoring means no additional free scaling parameters are
> introduced; the full ensemble of scaling galaxies adds zero extra degrees of freedom beyond
> the BGC's own Einstein radius.
>
> The choice between these two categories is determined by which JSON file each galaxy's centre
> appears in (`extra_galaxies_centres.json` vs `scaling_galaxies_centres.json`)., including teir
> light as an MGE, and their mass via a scaling relation where the mass of the scaling galaxies is
> tied to that of the brightest galaxy or bcg. Study this script in detail, we now want to make it
> so that imaging, interferometer, point_source and multi_galaxy all have a
> features/scaling_relation (not features/scaling_galaxies) package which includes fit.py,
> likelihood_function.py, modeling.py, and simulator.py), noting that in the style of
> imaging/scaling_Relation these are more minimal on docs assumign readers have read the core files
> for these in the main package. This file should document first the non .csv API and interface, and
> then do the .csv interface near the end. Note that imaging/scaling_relation is, I believe, an old
> featrue which uses a different scaling approach (does not tie to BCG) and thus should be
> overwritten for the most part. We should also include a slam.py in all folders ((but not for point
> source), given the example I sent uses a slam.py, and that is where we measure luminosities. So in
> the not slam.py I think you just assumingt he right luminositires and note they need to be
> measured. I think multi_galaxy/features//scaling_galaxies/modeling.py is the right model AP, but
> I'm not totally sure. Anyway, double check with proper research and then build all these feature
> packages. Also rememebr to mention that scaling galaxies are not truncated dPIEMass, but group /
> cluster scale equialents will be.

## Research findings (pre-planning, verified against the installed stack)

1. **`scaling_galaxies` is a first-class top-level collection**, not a naming convention:
   `autogalaxy/analysis/analysis/analysis.py:86` and `autolens/analysis/analysis/lens.py:131`
   append `instance.scaling_galaxies` to the tracer galaxy list; `autolens/aggregator/tracer.py:97`
   and `autogalaxy/aggregator/galaxies.py:72` do the same on result load. So
   `af.Collection(galaxies=..., extra_galaxies=..., scaling_galaxies=...)` — the
   `mgl_slam_batch.py` / `group/features/scaling_relation` form — is canonical.
   `multi_galaxy/features/scaling_galaxies/modeling.py:177` currently folds the tier into
   `galaxies=af.Collection(**lens_dict, **scaling_dict, ...)`; numerically identical, but it
   forfeits the labeled collection and the `scaling_galaxies` aggregator path. Fix.

2. **The BGC tie really is zero-free-parameter** — verified live:
   `mass.einstein_radius = lens_dict["lens_0"].mass.einstein_radius * (L / L_bgc) ** 0.5` gives
   `model.prior_count == 6` for 2 main lenses + 2 scaling galaxies, and sampled radii come back at
   exactly ratio `L**0.5`. This is the substantive difference from the existing
   `imaging/` and `group/` files, which introduce a *new* free `einstein_radius_ref`
   (the Lenstool `mag0` convention) — a different physical model, hence "overwrite".

3. **Two tiers, not one.** `mgl_slam_batch.py` uses both: `extra_galaxies` with
   luminosity-**bounded** free radii (`min(2*(theta_E_bgc/sqrt(L_bgc))*sqrt(L), cap)`) and
   `scaling_galaxies` **tied**. Carry both through; this also fixes the existing imaging file's
   habit of stuffing the scaling tier into `extra_galaxies`.

4. **Per-regime constraints that change the scripts:**
   - `point_source` — mass-only (`PointDataset` is positions + fluxes, no light), so luminosities
     cannot come from the fit; they come from ancillary imaging. No `slam.py`.
   - `interferometer` — `interferometer/features/extra_galaxies/slam.py` has **no `light_lp`
     stage** (source_lp -> source_pix_1 -> source_pix_2 -> mass_total): foreground light is not
     detected at mm wavelengths. Its `slam.py` cannot measure luminosities either — they load from
     ancillary optical/NIR photometry. Only `imaging` and `multi_galaxy` get the
     measure-luminosities-in-`light_lp` pattern.

5. **Untruncated is the physical point.** Scaling galaxies here use untruncated isothermals;
   truncation encodes tidal stripping by a host halo, which these regimes lack by definition.
   Truncated `dPIEMass` members belong to the group/cluster Lenstool-style workflows
   (`al.mp.dPIEMass` and friends exist). This thread must appear in every package's prose.

6. **Bug in the source script (not a target file, report only):** `mgl_slam_batch.py:269-270`
   passes `mask_radius=mask_radius` twice to `mge_model_from` — `TypeError` on any run reaching
   `lens_light_2`.

## Scope

For each of `imaging`, `interferometer`, `point_source`, `multi_galaxy` under
`autolens_workspace/scripts/<regime>/features/scaling_relation/`:

- `simulator.py`, `modeling.py`, `fit.py`, `likelihood_function.py`
- `slam.py` for all except `point_source`
- `README.md`, `__init__.py`

Docs register: minimal, deferring to the regime's core `scripts/<regime>/{fit,modeling,
likelihood_function,simulator}.py`. Non-CSV (JSON centres + explicit luminosity list) API
documented FIRST; `al.galaxy_table_from_csv` interface near the END of each file. Non-`slam.py`
files assume measured luminosities and say explicitly that they must be measured, pointing at the
regime's `slam.py` (or ancillary imaging for point_source / interferometer).

Rewrite `imaging/features/scaling_relation/*` (old free-`einstein_radius_ref` approach) and
`git mv multi_galaxy/features/scaling_galaxies` -> `multi_galaxy/features/scaling_relation`.
Datasets get uniform new names `dataset/<regime>/scaling_relation` rather than reusing
`extra_and_scaling_galaxies` with changed truths.

Out of scope (confirmed): `group/` and `cluster/` keep the Lenstool free-`einstein_radius_ref` +
truncated-dPIE convention, which is correct for them; cross-link the contrast instead.

## Known collisions

Two open `autolens_workspace` PRs touch target files:

- **#384 `remove-finish-docstring-hack`** — edits
  `scripts/imaging/features/scaling_relation/simulator.py` and
  `scripts/multi_galaxy/features/scaling_galaxies/simulator.py` (removes the trailing
  `"""Finished."""` block). Both files are rewritten/renamed by this task, so resolution is
  "take ours" — and the new files must NOT reintroduce a `Finish.`/`Finished.` trailer
  (`mgl_slam_batch.py` ends with one; do not copy it).
- **#383 `script-prose-ref-drift`** — edits `group/features/scaling_relation/modeling.py` and the
  imaging/interferometer `extra_galaxies/simulator.py`; disjoint from our targets, but adds
  cross-references that may point at the files we rewrite.

Both also touch `notebooks/`, `llms-full.txt` and `workspace_index.json` — whichever merges last
must re-run `generate.py`.

## Acceptance

- Smoke suite green; the four `modeling.py` entries registered in `smoke_tests.txt` (replacing the
  `multi_galaxy/features/scaling_galaxies/modeling.py` entry at line 17).
- `model.prior_count` demonstrably unchanged by adding scaling galaxies, in each `modeling.py`.
- Notebooks + navigator regenerated; `scripts/check_sizes.sh` clean.
- Untruncated-vs-dPIE reasoning and the ladder wrap-up present in all four packages.
