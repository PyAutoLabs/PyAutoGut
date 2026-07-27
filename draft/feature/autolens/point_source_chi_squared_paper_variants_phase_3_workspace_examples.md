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
