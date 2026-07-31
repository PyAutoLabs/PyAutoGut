# multi_galaxy features parity — phase 2: MGE + pixelization

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: large
Autonomy: supervised
Priority: normal
Status: SPLIT — 2a (MGE) shipped PR#422; 2b (pixelization core: README, modeling, fit) shipped PR#423;
  2c (adaptive, delaunay, cpu_fast_modeling, slam, source_science, plot) NOT STARTED and is what remains
Parent: draft/docs/workspaces/multi_galaxy_features_group_parity.md
Blocked-by: phase 1 (needs `multi_galaxy/slam.py` as the baseline each `slam.py` diffs against)

Phase 2 of 4 — the largest by volume. See the parent for the original request, scope
decisions and the authoring rules that apply to every script.

## Split into 2a / 2b (2026-07-30)

This phase was scoped as MGE + pixelization together — 15 scripts, the largest phase of the arc. It was split
during execution because the MGE half completed and shipped on its own:

- **Phase 2a — `multi_gaussian_expansion`: SHIPPED.** autolens_workspace PR#422. README, simulator, modeling,
  fit, likelihood_function, source_science, slam. Catalogue 317 -> 323.
- **Phase 2b — `pixelization` core: PARTIALLY SHIPPED.** autolens_workspace PR#423 added README, `modeling.py`
  and `fit.py` (3 hand-written files, 736 lines). Catalogue 323 -> 325.
- **Phase 2c — pixelization variants: NOT STARTED.** The six remaining scripts: `adaptive`, `delaunay`,
  `cpu_fast_modeling`, `slam`, `source_science`, `plot`. Human flagged 2026-07-31 that delaunay + the Adapt
  schemes are worth real work, and that `autolens_workspace_test` has the end-to-end setup. **Confirmed** —
  `autolens_workspace_test/scripts/imaging/model_fit.py:127-139` composes
  `al.mesh.Delaunay(pixels=100)` + `al.reg.ConstantSplit` and builds `AdaptImages` STANDALONE via
  `galaxy_name_image_plane_mesh_grid_dict={"('galaxies', 'source')": image_plane_mesh_grid}` — no preceding fit
  needed. That unblocks `delaunay.py` directly.

  **Precision to carry, not to assume away:** that dict supplies a mesh GRID, not surface-brightness adapt
  IMAGES. It solves the mesh half. Whether `al.reg.Adapt` (which needs a brightness estimate to decide where to
  smooth harder) can be driven standalone is UNVERIFIED — check it before writing `adaptive.py`. PR#423's README
  says the Adapt schemes need adapt-images from an earlier fit; that is true for `reg.Adapt` and must not be
  restated as "no adaptive mesh works standalone", which the Delaunay example above disproves.

  Other verified API constraints from 2b: `AdaptSplit` raises `PixelizationException` against any rectangular
  mesh (needs split-cross mappings); `al.mesh.Rectangular` does not exist (`RectangularUniform`);
  `al.PositionsLHPenalty` does not exist (`al.PositionsLH`).

Findings from 2a that phase 2b should build on rather than re-derive:

- The two deflectors' MGE bases correlate at **max 0.9877** in the curvature matrix (mean 0.119), versus 0.296 for
  a single linear profile each and 0.098-0.384 to the source. Coupling values are stable to 4 d.p. across
  re-simulations; log likelihoods are NOT (unseeded Poisson noise, ~1-2% scatter) so quote them to 2 s.f.
- A pixelized source is the natural next step in that story: a free-form mesh has enough freedom to absorb an
  incorrect mass split into source structure. The plan's phase-2 prose already flags this; **verify it
  numerically before asserting it**, as 2a did.
- `slam.py` must COPY the baseline's stages, not import them — `multi_galaxy/slam.py` is a script, so importing
  executes its whole pipeline on the `simple` dataset as a side effect (verified: the import hangs).

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
