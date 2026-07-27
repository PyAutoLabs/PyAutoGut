# Point-source chi-squared variants (arXiv:2406.15280) — Phase 2: core API

Parent: `point_source_chi_squared_paper_variants.md`. Phase 2 of 5.
Blocked on phase 1 design approval — the class names, variant set and
centre-resolution API below are placeholders until phase 1 lands.
Mechanical execution delegated (Sonnet) per `PyAutoBrain/skills/WORKFLOW.md`;
design deviations come back to the lead session.

## Scope (repos: autoarray? + autogalaxy + autolens — per phase 1 decision)

1. **Model class** (`PyAutoGalaxy/autogalaxy/profiles/point_sources.py`):
   add the parameter-free point-source class from the phase 1 design
   (working name `al.ps.PointSolved`). No free (y,x); composes via
   `af.Model` contributing zero non-linear parameters; dataset-name pairing
   (`autolens/point/fit/abstract.py:84-90`) keeps working. Export via
   `autogalaxy/__init__` `ps` alias → `al.ps`.
2. **Fit classes** (`PyAutoLens/autolens/point/fit/`): per the phase 1 API
   decision, implement analytic source-centre resolution — β* = precision-
   weighted mean of back-traced observed positions (weights per phase 1:
   full local inverse-magnification tensor; paper Eqs. ~41–48) — for:
   - source-plane chi-squared (tensor-weighted; supersedes/complements
     `FitPositionsSource`'s scalar µ² weighting),
   - image-plane pair-repeat and all-to-all: forward-solve model images
     from β* via the existing `PointSolver` path
     (`fit/positions/image/abstract.py:121-127`) instead of a sampled
     `profile.centre`.
   Keep the `source_plane_coordinate` single funnel
   (`fit/abstract.py:144-153`); no silent None-guards — a fit given a
   centre-free profile with a centre-requiring configuration must raise
   loudly.
3. **Docstring truth sweep**: the five false "barycenter" docstrings
   (`fit/positions/abstract.py:48`, `image/abstract.py:49`,
   `image/pair.py:30`, `image/pair_all.py:26`, `image/pair_repeat.py:18`)
   become true (pointing at the new machinery) or are corrected.
4. **JAX**: thread `xp` through all new code paths (fixed-shape only);
   register new fit classes in `AnalysisPoint._register_fit_point_pytrees`
   (`model/analysis.py:181-218`). If phase 1 approved it: fix
   `Grid2DIrregular.grid_2d_via_deflection_grid_from`
   (`PyAutoArray/autoarray/structures/grids/irregular_2d.py:170`) to accept
   and propagate `xp`, and add `FitPositionsSource` to the pytree
   registrations (its two known jit blockers).
5. **Fluxes/time delays — alternatives to current implementation** (per
   phase 1 §6-7 design): analytic-flux fit (magnification-first flux
   space: `F*` solved by linear least squares from `|µᵢ|` at the observed
   positions, unless phase 1 chose magnitude space) removing `flux` as a
   free parameter, + the flux-free model-class sibling; analytic
   reference-time treatment for time delays as an alternative to
   min-subtraction (`fit/times_delays.py:109-110`). Requires adding
   pluggable hooks (`fit_flux_cls` / `fit_time_delays_cls` mirroring
   `fit_positions_cls`) since both are hard-wired in
   `fit/dataset.py:114,130` — keep current classes as the defaults.
6. **Missing-image penalty** (per phase 1 §8): verify
   `FitPositionsImagePairAll`'s `-log(n_permutations)` equals the paper's
   `1/|Σ| = 1/P^I`; implement whatever phase 1 approved (without-repetition
   normalization and/or a paper-principled `unmatched_model_policy` option
   alongside `PairRepeat`'s existing ad-hoc penalties).
7. **Config/priors**: add any needed default-prior/config entries for the
   new classes (a parameter-free class may need none — verify, don't
   assume; check the autogalaxy prior config dirs and workspace config
   overrides).

## Tests (numpy-only — never JAX in unit tests)

- Analytic-centre correctness: β* equals the brute-force minimizer of the
  source-plane chi-squared over centre on a fixed mock tracer.
- Profile-likelihood parity: solved-centre fit log-likelihood ≈ free-centre
  fit maximized over centre (same scheme), on pair-repeat, all-to-all, and
  source-plane variants.
- Tensor vs scalar weighting: on an anisotropic-magnification mock, tensor
  weighting reproduces the image-plane chi-squared ordering that scalar µ²
  gets wrong (concrete case from phase 1 §5).
- Analytic-flux correctness: `F*` equals the brute-force minimizer over
  flux on a fixed mock; solved-flux likelihood ≈ free-flux likelihood
  profiled over flux. Same pattern for the analytic reference time vs a
  brute-force scan over T.
- Penalty: with-repetition normalization equals `-I log P` on a counted
  mock configuration; predicted-image surplus lowers the likelihood
  monotonically.
- Loud-failure tests for invalid combinations (e.g. current `FitFluxes`
  given the flux-free class must raise, not silently skip).
- Mirror the existing test taxonomy under
  `PyAutoLens/test_autolens/point/` (`__Env__` declarations, existing
  file layout).

JAX validation lives in scripts, not unit tests (vmap/value_and_grad-based,
per workspace conventions) — that is phase 3's paired examples.

## Paired examples (updated in phase 3, listed here for traceability)

- `autolens_workspace_test/scripts/point_source/jax_likelihood/{image_plane,source_plane,point}.py`
- `autolens_workspace_test/scripts/point_source/jax_grad/gradient.py`
- `autolens_profiling/scripts/point_source/likelihood_runtime/{image_plane,source_plane}.py`
- `autolens_profiling/scripts/cluster/likelihood_breakdown/{image_plane,source_plane}.py`

## Exit criteria

Library PRs open behind the ship gate (`ship_library`): tests green,
pytrees registered, docstrings truthful. Downstream workspace impact
analysis recorded for phases 3–4.

## Phase 1 design outcome (2026-07-27 — supersedes placeholders above)

Approved design: https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5095032024

Deltas binding on this phase:
- Model class is `al.ps.PointSolved` (parameter-free; NO flux sibling — the
  analytic-flux fit never reads `profile.flux`, so `PointSolved` covers
  positions+fluxes+delays datasets alone).
- Fit-side API is a `SolvedCentre` mixin overriding the single
  `source_plane_coordinate` funnel to return the tensor-weighted analytic
  β* (paper §5.1: `β* = (ΣAᵢᵀΘᵢAᵢ)⁻¹ ΣAᵢᵀΘᵢβ̂ᵢ`, A from
  `ag.LensCalc.hessian_from`); concrete classes `FitPositionsSourceSolved`
  (+ `weighting = "jacobian"|"magnification"` class attribute, incl. the
  marginalization det term), `FitPositionsImagePairAllSolved`,
  `FitPositionsImagePairRepeatSolved`, `FitFluxesSolved` (flux-space
  `F* = Σµᵢf̂ᵢ/σᵢ² / Σµᵢ²/σᵢ²`), `FitTimeDelaysSolved` (precision-weighted
  `T*`). Hungarian `Pair` gets NO solved variant (skip recorded).
- Missing-image penalty: verification + docs only — `PairAll` already
  implements the paper's `1/P^I`; `PairRepeat` policies stay as-is; the
  without-repetition `P!/(P−I)!` form is rejected (factorial, JAX-hostile).
- Mismatch behaviour: BOTH directions raise loudly (centre-requiring fit ×
  `PointSolved`, and Solved fit × `Point`/`PointFlux`).
- PyAutoArray IS in scope (xp fix + pytree registration for
  `FitPositionsSource`) — 3-repo series, override recorded.
- Attribution: centre-free IMAGE-plane variants are OUR extension (glafic
  precedent), not from the paper — docs/prose must not cite the paper for
  them.
