# multi_galaxy features parity — phase 1: SLaM baseline + simple features

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/multi_galaxy_features_group_parity.md

Phase 1 of 4. See the parent for the original request, the full audit of what
`group/features` has that `multi_galaxy/features` lacks, the scope decisions
(`group_halo` omitted, `potential_correction` and `los_halos` out), and the
**authoring rules that apply to every script in every phase** — regime motivation
rewritten rather than translated, the `shear_galaxy` idiom, the 3.0" mask, the
`__Contents__` block, the README voice, and the cross-link-don't-fork rule.

## Deliverables

- `scripts/multi_galaxy/slam.py` — the regime's SLaM baseline, playing the role
  `group/slam.py` (1086 lines) plays for the group package. Note `imaging/` has **no**
  top-level `slam.py`: its features anchor on `guides/modeling/slam_start_here`. A
  multi-galaxy baseline is warranted for the same reason group's is — the composition
  (N co-dominant deflectors in a loop, shear in its own `shear_galaxy`) diverges enough
  from `slam_start_here` that each feature's `slam.py` needs a regime-local thing to
  diff against. `features/scaling_relation/slam.py` currently has to re-explain that
  divergence from scratch; once this lands it should be re-pointed at the baseline.
- `scripts/multi_galaxy/features/no_lens_light/` — `README.md`, `__init__.py`,
  `simulator.py` (writes `dataset/multi_galaxy/simple__no_lens_light`), `modeling.py`,
  `slam.py`. Sibling references: `group/features/no_lens_light` (294/273/614 lines),
  `imaging/features/no_lens_light` (289/258/403).
- `scripts/multi_galaxy/features/linear_light_profiles/` — `README.md`, `__init__.py`,
  `modeling.py`, `fit.py`, `likelihood_function.py`, `slam.py`. Reuses the existing
  `simple` dataset, so no simulator. Sibling references:
  `group/features/linear_light_profiles` (304/216/293/995),
  `imaging/features/linear_light_profiles` (400/253/680/496) — imaging is the deeper
  one on `likelihood_function`.
- `scripts/multi_galaxy/features/extra_galaxies/slam.py` — the imaging-parity gap
  (`imaging/features/extra_galaxies/slam.py`, 570 lines). The folder otherwise shipped
  in PR#391.
- `scripts/multi_galaxy/features/README.md` — rewritten. Currently it describes a
  two-folder package and tells readers that "standard single-galaxy features
  (pixelized source reconstructions, linear light profiles, MGE variations) apply to
  multi-galaxy lenses unchanged — see `imaging/features`". That paragraph is what this
  arc is deleting; replace it with the real inventory. Add the `group_halo`
  non-analogue paragraph: no host halo at this scale, which is why the scaling tier is
  untruncated, pointing at `group/features/group_halo` as the regime boundary.

## Regime motivation to write (phase-specific)

Do not reuse group's "the group model contains many galaxies in tiers" framing — the
multi-galaxy default model has no tiers.

- **no_lens_light**: at galaxy scale removing lens light is mostly a dimensionality
  win. Here it also removes the *asymmetric* absorber: with two co-dominant deflectors,
  residual unmodelled flux is soaked up unevenly by the two light models and biases the
  flux ratio, which is usually the measurement (this is the mechanism already recorded
  in the `extra_galaxies` prose). A mass-only model has nowhere to hide it.
- **linear_light_profiles**: both deflectors' `intensity` parameters leave the
  non-linear search, and — the point worth making at this scale — so do the
  `intensity`-vs-`effective_radius` degeneracies *within each* galaxy, which otherwise
  compound with the across-galaxy mass-split degeneracy the package's core scripts
  document (`multi_galaxy/modeling.py`).
- **extra_galaxies/slam.py**: where the perturber tier's centres and capped Einstein
  radii are carried through the SLaM stages, and where promoting a perturber costs
  identifiability rather than fit quality (the subtle tier error the folder's
  `modeling.py` already teaches).

## Acceptance

- All new scripts green under the smoke env from a clean dataset slate
  (`PYAUTO_TEST_MODE=2`, workspace root as CWD, target `dataset/multi_galaxy/<name>`
  deleted first — `should_simulate` tests directory existence only). Run sequentially.
- Selective `smoke_tests.txt` registration only; prove new entries by the count rising.
- Notebooks + navigator catalogue regenerated (repo as CWD, project key `al`).
- `grep -rn "group" scripts/multi_galaxy/` shows only deliberate ladder cross-refs.
- `features/README.md` inventory matches the folders on disk.
