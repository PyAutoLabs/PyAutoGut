# multi_galaxy features parity — phase 2: MGE + pixelization

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: large
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/multi_galaxy_features_group_parity.md
Blocked-by: phase 1 (needs `multi_galaxy/slam.py` as the baseline each `slam.py` diffs against)

Phase 2 of 4 — the largest by volume. See the parent for the original request, scope
decisions and the authoring rules that apply to every script.

## Deliverables

- `scripts/multi_galaxy/features/multi_gaussian_expansion/` — `README.md`,
  `__init__.py`, `simulator.py`, `modeling.py`, `fit.py`, `likelihood_function.py`,
  `source_science.py`, `slam.py`. Sibling references:
  `group/features/multi_gaussian_expansion` (343/245/269/326/303/482),
  `imaging/features/multi_gaussian_expansion` (597/306/356/828/317/334) — imaging is
  substantially deeper on `modeling` and `likelihood_function`; match imaging.
- `scripts/multi_galaxy/features/pixelization/` — `README.md`, `__init__.py`,
  `modeling.py`, `fit.py`, `likelihood_function.py`, `slam.py`, `adaptive.py`,
  `delaunay.py`, `cpu_fast_modeling.py`, `source_science.py`, **plus `plot.py`**
  (imaging has one, group does not). Sibling references: `group/features/pixelization`
  (331/272/357/826/387/364/308/389), `imaging/features/pixelization`
  (546/566/985/504/479/1518/639/510/273) — imaging is far deeper on `delaunay`
  (1518 vs 364) and `cpu_fast_modeling` (639 vs 308); match imaging.

Both reuse the existing `simple` dataset for modeling where the group siblings do
(`group/features/pixelization/modeling.py` uses `simple`; the MGE folder has its own
simulator — check what `group/features/multi_gaussian_expansion/simulator.py` actually
writes before deciding whether multi_galaxy needs a separate dataset or can reuse
`simple`).

## Regime motivation to write (phase-specific)

- **multi_gaussian_expansion**: the MGE is already the default in
  `multi_galaxy/modeling.py`, so this folder is not introducing it — it is the
  *variations* walkthrough. Say so explicitly and point at the core script for the
  basic composition, rather than re-teaching MGE from scratch. What is regime-specific:
  one MGE basis per co-dominant deflector, with the over-sampling applied at every
  deflector's centre, and the cost/benefit when the two galaxies overlap.
- **pixelization**: the sharpest multi-galaxy point in the whole arc. A free-form
  source mesh has enough freedom to absorb an *incorrect mass split* into source
  structure — the two deflectors' masses are degenerate against a well-constrained
  total deflection (`multi_galaxy/modeling.py`), and a pixelized source can rearrange
  itself to keep the fit good while the split is wrong. That makes regularization and
  the adapt cycle load-bearing for identifiability here, not just for image quality.
  Verify this claim numerically before asserting it (perturb the split in the truth
  tracer and look at where the residuals land) — the parent arc's precedent is that
  these effects get measured, not assumed.

## Acceptance

Same as phase 1: clean-slate smoke green (sequential), selective `smoke_tests.txt`
registration proven by count, notebooks + navigator regenerated (repo as CWD, key
`al`), no stray "group" framing, README inventory matching disk.

Watch run times — pixelization scripts are the slowest in the package; check the
script-timing baseline does not regress.
