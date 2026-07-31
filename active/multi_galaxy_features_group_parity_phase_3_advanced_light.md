# multi_galaxy features parity — phase 3: advanced light features

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/multi_galaxy_features_group_parity.md
Blocked-by: phase 1

Phase 3 of 4. See the parent for the original request, scope decisions and the
authoring rules that apply to every script.

## Deliverables

Creates `scripts/multi_galaxy/features/advanced/` (does not yet exist).

- `advanced/README.md` — the four-folder inventory, in the voice of
  `group/features/advanced/README.md` but multi-galaxy framed.
- `advanced/operated_light_profile/` — `README.md`, `__init__.py`, `simulator.py`
  (dataset `operated`), `modeling.py`. Siblings:
  `group/features/advanced/operated_light_profile` (358/238),
  `imaging/features/advanced/operated_light_profile`.
- `advanced/shapelets/` — `README.md`, `__init__.py`, `modeling.py`, `fit.py`
  (reuses `simple`). Siblings: `group/features/advanced/shapelets` (312/255),
  `imaging/features/advanced/shapelets`.
- `advanced/sky_background/` — `README.md`, `__init__.py`, `simulator.py` (dataset
  `sky_background`), `modeling.py`, `fit.py`. Siblings:
  `group/features/advanced/sky_background` (290/227/185),
  `imaging/features/advanced/sky_background`.

Check each imaging sibling's line counts at implementation time and match the deeper
of the two, per the parent's depth rule.

## Regime motivation to write (phase-specific)

- **operated_light_profile**: a PSF-convolved point-source component per deflector —
  relevant when either co-dominant galaxy hosts an AGN. The multi-galaxy angle is that
  an unmodelled central point source in *one* of two deflectors biases that galaxy's
  light model, and therefore its share of the mass split.
- **shapelets**: a basis flexible enough to capture disturbed morphology — which is
  the norm for the systems this package models. The reference system,
  SDSS J1011+0143 (`multi_galaxy/modeling.py`), is a *merging* pair, so tidal features
  and asymmetry are expected rather than exceptional. That is a stronger motivation for
  shapelets here than at galaxy scale, and the prose should say so.
- **sky_background**: a single uniform sky across an image containing two bright
  galaxies. The multi-galaxy angle: a mis-estimated sky is a *shared* systematic that
  both light models absorb, so it biases the flux ratio rather than cancelling.

## Acceptance

Same as phase 1: clean-slate smoke green (sequential), selective `smoke_tests.txt`
registration proven by count, notebooks + navigator regenerated (repo as CWD, key
`al`), no stray "group" framing, README inventories (both `features/README.md` and the
new `advanced/README.md`) matching disk.
