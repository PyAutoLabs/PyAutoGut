# multi-galaxy-features-phase-4c

Phase 4c — `subhalo`, the last sub-phase. **This closed the multi_galaxy features parity arc.**

## Shipped

- **autolens_workspace#435** (MERGED 2026-07-31, human merge; commit `81a3a4fe`, merge `19131cf5`).
  Issue autolens_workspace#434. `simulator.py` 260, `detect/start_here.py` 929, two READMEs (51 + 28).
  New `dataset/multi_galaxy/subhalo`. `smoke_tests.txt` 34 -> 35. Catalogue 351 -> 353.

## THE ARC IS CLOSED

`scripts/multi_galaxy/features/` now equals `scripts/group/features/` minus `group_halo` plus
`extra_galaxies`, and `features/advanced/` matches `group/features/advanced/` folder for folder.

Full arc: #417 (ph1) -> #421 (slam follow-up) -> #422 (2a MGE) -> #423 (2b pixelization core) -> #424
(section parity) -> #427 (2c pixelization variants) -> #429 (ph3 advanced light) -> #431 (4a DSPL) ->
#433 (4b mass_stellar_dark) -> #435 (4c subhalo). Ten PRs.

Arc-closing checks all pass and are recorded in the PR body. The parent prompt's "Remaining" entry is
struck in `draft/docs/autolens/multi_galaxy_package.md` (Mind commit `3de106f`); only the real-data
SDSS J1011+0143 MAST swap-in remains open there, still blocked from cloud sessions.

## THE FINDING: the false-positive claim holds, in a STRONGER form than stated

The prompt said a subhalo false positive here can be a mis-split rather than a perturber. Measured at
MATCHED total residual power (mis-split at fixed total Einstein radius vs a 1e10 Msun NFW subhalo):

| | mis-split | subhalo |
|---|---|---|
| participation ratio (pixels carrying the residual power) | **145.4** | 313.8 |
| power in brightest 1% of pixels | **0.789** | 0.639 |

The mis-split residual is not diffuse — it is MORE concentrated than the subhalo's. And the amplitude is
tiny: moving **0.022"** of Einstein radius between the two galaxies (~1% of the total) matches that
subhalo's residual power. A compact-perturber grid search can genuinely be fooled.

Built into the pipeline rather than only described:
- `lens_dict_model_from` carries EVERY deflector into all three subhalo stages.
- The script prints each deflector's Einstein radius in the smooth model beside the subhalo model, so a
  detection arriving alongside a shifted mass split is visible, not inferred.

## UPSTREAM BUG CONFIRMED (needs its own issue)

`group/features/advanced/subhalo/detect/start_here.py` builds all three subhalo stages with
`lens_dict = {"lens_0": lens_0}`, **dropping every main lens galaxy after the first** from the
no-subhalo baseline, the grid search and the refine. The comparison model is therefore a mis-split model
— exactly the failure mode the regime prose is about. Not fixed here (different package); file separately
against `group/`.

## PROMPT-MOTIVATION TALLY across the phases where the stated motivation was checked

- **phase 3 shapelets — WRONG.** The prompt wanted the basis on the deflectors (merging pair, disturbed
  morphology). `imaging/features/advanced/shapelets/modeling.py`'s own `__Lens Shapelets__` section says
  lens-light shapelets are not used in the literature and MGE is faster/better for massive early-types.
  Shapelets went on the SOURCE.
- **4a DSPL — WRONG.** The prompt said the redshift ratio breaks the mass-split degeneracy. Controls
  showed it is the second source's SKY POSITION: same position -> effect gone (8.17 -> 0.89); massless
  first source (no multi-plane structure) -> effect stronger (17.48).
- **4b mass-to-light tying — RIGHT.** Anti-correlated direction 12.3x flatter than the tied-surviving one;
  parameter count 16 -> 15.
- **4c subhalo false positives — RIGHT, and understated.**

**Lesson: always measure the stated motivation before writing it into a tutorial. Two of four were wrong,
and both wrong ones were plausible-sounding.**

## Heart

Shipped against the same three RED reasons the human authorized for #427, unchanged across all five PRs
of this session. The `PyAutoHeart/heart/checks/release_run.py:42` tenant-firewall literal remains
unfixed and will keep holding the gate RED.

## Validation

Full smoke suite from a clean dataset slate, sequential: 37/37 passed. Navigator + banner checks clean.
`check_sizes.sh` OK. CI green on all five checks.
