# Point-source chi-squared variants (arXiv:2406.15280) — Phase 3: test + profiling examples

Parent: `point_source_chi_squared_paper_variants.md`. Phase 3 of 5.
Blocked on phase 2 merge. Mechanical — delegated (Sonnet); these are
test/dev scripts, not tutorial prose.

## Goal

Pair every new likelihood variant with JAX-regression and
likelihood-runtime examples, per the original request.

## autolens_workspace_test (`scripts/point_source/`)

- `jax_likelihood/image_plane.py` (currently `FitPositionsImagePairAll`,
  jit end-to-end): add/extend to cover the centre-free all-to-all and
  pair-repeat variants — jit the full `analysis.fit_from`, assert
  numpy-vs-jax parity.
- `jax_likelihood/source_plane.py` (currently `FitPositionsSource`; prints
  a BLOCKER line for the known jit failure): add the tensor-weighted
  solved-centre variant; if phase 2 fixed the
  `grid_2d_via_deflection_grid_from` xp gap + pytree registration, remove
  the BLOCKER path and assert jit works for both old and new source-plane
  fits.
- `jax_likelihood/point.py`: cover the centre-free variants alongside
  `FitPositionsImagePairAll`; ALSO fix its wrong header docstring (it is a
  copy-paste of "Func Grad: Light Parametric Operated" — a point-source
  script; hygiene fix in passing).
- Flux/time-delay terms: where the phase 2 analytic-flux / analytic-T
  alternatives shipped, extend the jax_likelihood scripts (or add
  siblings) so at least one config exercises a dataset with fluxes and
  one with time delays through the new fit classes, numpy-vs-jax parity
  asserted.
- `jax_grad/gradient.py`: gradient finiteness + finite-difference checks
  for the SOLVED-CENTRE SOURCE-PLANE variants only (analytic β*/F*/T* are
  plain autodiff — no solver in the loop). Image-plane gradients through
  `PointSolver` are PHASE 5 — do not attempt them here; leave an explicit
  pointer comment instead of a BLOCKER hack.
- Follow existing script structure/style in these files; validate via the
  standard workspace_test run conventions before shipping.

## autolens_profiling

- `scripts/point_source/likelihood_runtime/image_plane.py` and
  `source_plane.py`: add the centre-free variants to the profiled configs
  (or sibling scripts per the existing naming pattern) — lower/compile/
  first-call/steady-state timings, `af.ModelInstance` pytree JIT input as
  in the existing harness. Record results JSON+PNG under
  `results/likelihood/point_source/` following the existing
  `*_summary_v<version>` naming.
- `scripts/cluster/likelihood_breakdown/image_plane.py` and
  `source_plane.py` (NOTE: the request said `cluster/likelihood_runtime`;
  the actual directory is `likelihood_breakdown/`): add per-step
  decomposition entries for the centre-free variants on the standard
  cluster model (2 dPIE + 10 scaling dPIE + NFW / 2 source planes). Key
  question: how much runtime the analytic β* adds/saves vs the
  ~14-parameter-smaller non-linear space (cluster fits drop 2 params per
  point source).
- Developer mirrors if touched by convention:
  `autolens_workspace_developer/jax_profiling/{jit,gradient}/point_source/`.

## Exit criteria

All paired scripts run green (jit parity asserted, no BLOCKER lines left
for fixed paths), profiling numbers recorded, `ship_workspace` PRs open
behind the library-first merge gate.

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
