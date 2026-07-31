# multi-galaxy-features-phase-2c

Phase 2c — the final slice of phase 2 of the multi_galaxy features parity arc. Completed
`scripts/multi_galaxy/features/pixelization/`, which phase 2b left holding only `README.md`,
`modeling.py` and `fit.py`.

## Shipped

- **autolens_workspace#427** (MERGED 2026-07-31, human merge; commit `7fd11daa`, merge `bb1f850c`).
  Issue autolens_workspace#426. 23 files, +7379 −34.

Seven new scripts, each ported from its `group/` and `imaging/` sibling with the single lens galaxy
replaced by the package's `lens_0`/`lens_1` composition and over-sampling centred on every deflector:
`adaptive.py` (420), `delaunay.py` (384), `cpu_fast_modeling.py` (325), `likelihood_function.py` (346),
`slam.py` (664), `source_science.py` (409), `plot.py` (247). Folder total 3336 lines / 9 files, against
group's 3234 / 8.

Also: folder README to the full nine-file inventory; `features/README.md` "Not yet written" cleared of
`multi_gaussian_expansion` and `pixelization` (stale since 2a/2b shipped them); `modeling.py` wrap-up
de-staled; `smoke_tests.txt` 25 → 27 entries.

## Arc

PR#417 (phase 1) → #421 (slam follow-up) → #422 (2a MGE) → #423 (2b pixelization core) → #424 (section
parity) → **#427 (2c)**. Phase 2 is now COMPLETE. Phases 3 (advanced light) and 4 (advanced mass) remain;
prompts already drafted in `draft/docs/workspaces/`.

## Findings worth keeping

- **Linear light profiles put the deflectors' SOLVED INTENSITIES into `inversion.reconstruction`,**
  alongside the source pixel fluxes. Two scripts died on this during validation: `source_science.py`
  raised `ValueError: different number of values and points` from `griddata` (mesh grid length ≠
  reconstruction length), and `delaunay.py` raised `AttributeError: 'LightProfileLinearObjFuncList'
  object has no attribute 'source_plane_mesh_grid'` because `inversion.linear_obj_list[0]` was the
  linear light profiles, not the `Mapper`. Fix: fixed-intensity `al.lp.Sersic` deflectors (what both
  siblings use) plus `inversion.cls_list_from(cls=al.Mapper)`. **The shipped `fit.py` has the same
  latent bug** — its "Number of source pixels reconstructed" over-counts by 2. Left as a follow-up.
- **`likelihood_function.py` was missing from the phase's own 2c file list** but present in its
  Deliverables, and every other multi_galaxy feature folder with a `fit.py` has one. Six named, seven
  actually needed — check the Deliverables against the phase note, not just the note.
- **Length model is the group tier, not imaging.** multi_galaxy consistently tracks group (shipped
  `modeling.py` 334 vs group 331 / imaging 546). The older "match imaging" line in the phase
  Deliverables was superseded by the 2026-07-31 re-steer.
- **`slam.py` copies the baseline's stages, never imports them** — `multi_galaxy/slam.py` is a script,
  so importing executes its whole pipeline. Its contribution is the `__Pixelization Choices__` /
  `__Mesh Shape__` sections, following `group/features/pixelization/slam.py`'s "documents the
  pixelization-specific choices" shape rather than inventing a new pipeline.
- **Brain sized this too-large (11) and proposed a generic 4-way split** — rejected: the prompt was
  already phased and 2c was one folder in one repo, the same shape as 2a (7 files, 1 PR). The sizing
  heuristic measures prose length, not scope.
- **Smoke registration stayed selective:** `adaptive.py` and `cpu_fast_modeling.py` only — the adapt
  mesh + adapt regularization pairing and the CPU sparse-operator route are the two paths nothing else
  in the suite reaches. `delaunay.py` was left out because `imaging/features/pixelization/delaunay.py`
  already covers the Delaunay inversion. No `slam.py` is smoke-registered anywhere.

## Heart

Shipped with human authorization against three RED reasons, none reachable from a workspace docs
change: `release validation FAILED (stage integrate)`; `manifest drift: tenant firewall (organ code) —
1 mismatch(es) vs PyAutoMind/repos.yaml` (hardcoded `'PyAutoLabs'` at
`PyAutoHeart/heart/checks/release_run.py:42`); `test run status unknown (no report.json)`. Two further
reasons (`PyAutoLens` / `PyAutoGalaxy` behind origin) were cleared by `pull_all_main.sh` first.

## Validation

Full smoke suite from a clean dataset slate, sequential: 29/29 passed. Navigator path + banner checks
clean. `check_sizes.sh` OK. Catalogue 325 → 332 scripts. CI green on all five checks (navigator ×2,
smoke `changes`, smoke 3.12, smoke 3.13).

## Follow-ups left open

- `fit.py`'s source-pixel over-count (same root cause as the two bugs above).
- `__Dataset Auto-Simulation__` still missing on the five existing `multi_galaxy/features/*/slam.py`
  files — needs docstring restructuring, not a text insert (a naive insert broke all five with
  `SyntaxError` in an earlier session). The new `slam.py` has it from birth.
- House-style cleanup over merged #417 / #422 (measured tables, parameter arithmetic in tutorial
  prose) — offered, still unrequested.
- `PyAutoHeart/heart/checks/release_run.py:42` tenant-firewall literal holds Heart RED until fixed.

## Original prompt

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
  `cpu_fast_modeling`, `slam`, `source_science`, `plot`.

  **Base these on `imaging/features/pixelization` and `group/features/pixelization` ONLY.** Human directed
  2026-07-31: tutorials are seeded from the normal workspace, NOT from `autolens_workspace_test`. An earlier
  version of this note pointed at workspace_test's standalone `AdaptImages` construction — that steer is
  WITHDRAWN, do not use it.

  The siblings solve the adapt-images problem self-containedly, and this is the pattern to copy: `adaptive.py`
  runs TWO searches inside the one script. Search 1 uses `RectangularAdaptDensity` + `reg.Constant`, which needs
  no adapt images; `adapt_images = al.AdaptImages(galaxy_name_image_dict=...)` is then built from search 1's OWN
  result; search 2 uses `RectangularAdaptImage` + `reg.Adapt` with them
  (`imaging/features/pixelization/adaptive.py:245,365,394`; `group/features/pixelization/adaptive.py:223,272,281`).
  So "the Adapt schemes need a prior fit" is real but self-resolved — the script supplies its own prior fit.

  Sibling sizes, for scale: imaging adaptive 479 / delaunay 1518 / cpu_fast_modeling 639; group adaptive 387 /
  delaunay 364 / cpu_fast_modeling 308. Group is the closer model for length.


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
