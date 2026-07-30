# features/scaling_relation packages: BGC-anchored Faber-Jackson tier across four regimes

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
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
