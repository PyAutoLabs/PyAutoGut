# multi-galaxy-features-phase-3

Phase 3 of 4 of the multi_galaxy features parity arc — advanced light features. Created
`scripts/multi_galaxy/features/advanced/`, which did not exist, and its first three folders.

## Shipped

- **autolens_workspace#429** (MERGED 2026-07-31, human merge; commit `636d7f07`, merge `974fc3d7`).
  Issue autolens_workspace#428. 12 new files.

| Folder | Files | Lines |
|---|---|---|
| `advanced/` | `README.md`, `__init__.py` | 39 |
| `advanced/operated_light_profile/` | `README.md`, `simulator.py`, `modeling.py` | 272 + 322 |
| `advanced/shapelets/` | `README.md`, `modeling.py`, `fit.py` | 354 + 282 |
| `advanced/sky_background/` | `README.md`, `simulator.py`, `modeling.py`, `fit.py` | 245 + 320 + 217 |

Two new datasets: `dataset/multi_galaxy/operated` (the `simple` pair with a nuclear point source per
deflector) and `dataset/multi_galaxy/sky_background` (`subtract_background_sky=False`, sky level 5.0).
`features/README.md` gained an `advanced/` section and its "Not yet written" list narrowed to phase 4's
three folders. `smoke_tests.txt` 27 -> 30. Catalogue 332 -> 339.

## Arc

#417 (ph1) -> #421 -> #422 (2a) -> #423 (2b) -> #424 -> #427 (2c) -> **#429 (ph3)**. Phase 4 (advanced
mass: `double_source_plane_lens`, `mass_stellar_dark`, `subhalo`) is the last; prompt drafted at
`draft/docs/workspaces/multi_galaxy_features_group_parity_phase_4_advanced_mass.md`.

## Findings worth keeping

- **The phase prompt's stated motivation for shapelets was wrong, and the library says so.** The prompt
  motivated the folder by disturbed *deflector* morphology (the merging pair). But
  `imaging/features/advanced/shapelets/modeling.py` documents under its own `__Lens Shapelets__` section
  that lens-light shapelets are "not used in the literature", their advantages are unclear, and "for most
  massive early-type galaxies, an MGE model will be faster and give higher quality results" — which both
  deflectors are. The scripts put the basis on the **source** and leave the deflectors as MGEs, saying so
  explicitly in each file, the folder README and the PR body. The disturbed-deflector case was already
  answered by `features/multi_gaussian_expansion`. **Read the sibling's own caveats before writing a
  prompt's stated motivation into a tutorial.**
- **`al.SettingsInversion` does not exist.** Inversion settings reach `FitImaging` through its
  `settings=al.Settings(...)` argument. Caught by running the script, not by reading it.
- **Depth: group tier throughout, including where imaging is deeper.** Group is the deeper sibling for
  `operated_light_profile` and `sky_background`. For `shapelets` imaging is ~2x deeper (1072 vs 567) and
  group tier was still chosen — the extra imaging depth is the scale-independent basis API walkthrough,
  and the parent prompt's "cross-link, do not fork where the physics is regime-independent" rule beats its
  "match the deeper sibling" rule. Same conclusion phase 2c reached independently.
- **Smoke registration:** all three `modeling.py` scripts registered, because each reaches a code path
  nothing else in the suite touches — operated (non-PSF-convolved) profiles, the shapelet basis with
  `use_positive_only_solver=False`, and a `DatasetModel` sky. The `fit.py` / `simulator.py` files were left
  out; the `modeling.py` entry exercises the same API and auto-simulates the dataset.
- **`point` is the package's established galaxy slot for a nuclear component** — `multi_galaxy/slam.py`
  already threads `bulge`, `disk`, `point` through every stage, so the operated profile needed no new
  attribute name. Group's equivalent uses `psf=`.

## Heart

Shipped against the same three RED reasons the human authorized for #427, unchanged and none reachable from
a workspace docs change: `release validation FAILED (stage integrate)`; `manifest drift: tenant firewall
(organ code)` (hardcoded `'PyAutoLabs'` at `PyAutoHeart/heart/checks/release_run.py:42`); `test run status
unknown (no report.json)`.

## Validation

Full smoke suite from a clean dataset slate (`rm -rf dataset/multi_galaxy`), sequential: 32/32 passed.
Navigator path + banner checks clean. `check_sizes.sh` OK. CI green on all five checks.

## Original prompt

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
