# Point-source chi-squared variants (arXiv:2406.15280) — Phase 5: JAX gradients

Parent: `point_source_chi_squared_paper_variants.md`. Phase 5 of 5 (final).
Blocked on phase 2 merge (phase 3's gradient scripts mark the boundary).
Delegated execution; the paper's gradient results are embedded below so
the executing model does not re-derive them — deviations come back to the
lead session.

## Goal

Differentiable point-source likelihoods across the full variant matrix,
certified against finite differences, so gradient searches
(`af.MultiStartProdigy` / Adam-family) work on point-source fits.

## Paper gradient results (Lombardi 2024, arXiv:2406.15280)

- **Eq. 30 — image-plane positions w.r.t. source position** (inverse
  function theorem): `∂logP/∂β = Σᵢ Aᵢ⁻ᵀ Θᵢ (θ̂ᵢ − θᵢ)` where `Aᵢ` is the
  lens Jacobian at predicted image `θᵢ` and `Θᵢ` the position precision
  matrix. The general mechanism for lens parameters `p`: the solved images
  satisfy `β = θᵢ − α(θᵢ, p)`, so `∂θᵢ/∂p = Aᵢ⁻¹ ∂α/∂p |_{θᵢ}` — an
  implicit-differentiation rule at the solver's fixed point.
- **Eqs. 35–36 — marginalized (all-to-all) likelihood**: the gradient is
  the softmax-weighted sum of per-pairing gradients. This is exactly what
  autodiff of the existing LogSumExp form in
  `FitPositionsImagePairAll.chi_squared` produces — no custom rule needed
  ONCE solver gradients exist. Eq. 38 is the without-repetition analogue
  (softmax over permutations).
- **Flux/magnitude caveat**: the paper states no analytic likelihood
  derivative for magnitudes exists "without higher order derivatives of
  the lens mapping" — magnification gradients need third derivatives of
  the potential. In JAX nested autodiff supplies these mechanically
  (our magnifications come from a Hessian already:
  `AbstractFitPoint.magnifications_at_positions`,
  `autolens/point/fit/abstract.py:111` via `ag.LensCalc`) — the questions
  are numerical stability near critical curves and compile cost, not
  derivation.

## Work items

1. **Solver gradients** (the hard part): `PointSolver.solve` is
   jit-traceable (`solver/point_solver.py:97-135`, inf-padded fixed
   shape) but its triangle-refinement iteration must not be
   differentiated through. Implement a `custom_jvp`/`custom_vjp` (or
   `lax.custom_root`-style implicit-diff wrapper) applying the fixed-point
   rule above: forward = existing solve; tangent = `A⁻¹ ∂α/∂p` evaluated
   at the solved positions. Handle the inf-padding (masked tangents for
   padded slots) and near-critical images (|det A| → 0: follow phase 1's
   guidance; no silent clamping — surface the instability explicitly).
   Prior art: PyAutoMemory `wiki/methods/concepts/autodiff-implicit-diff.md`;
   the JAX gradient audit + Delaunay `custom_jvp` work (see Mind records).
2. **Variant coverage**: with solver gradients in place, verify autodiff
   end-to-end for centre-free and centre-sampled versions of `PairAll` and
   `PairRepeat` (the softmax/LogSumExp parts are autodiff-native;
   `PairRepeat`'s nearest-with-repeats min-selection is piecewise —
   confirm subgradient behaviour is acceptable or document the
   non-smoothness). Source-plane solved-centre variants and analytic
   F*/T* are linear solves — plain autodiff, certified in phase 3;
   re-certify here only if their code moved.
3. **Flux/time-delay gradients**: enable nested autodiff through
   `magnifications_at_positions` (vectorize the list comprehension at
   `fit/fluxes.py:118-124` if it blocks tracing); finite-difference
   certification; document stability limits near critical curves.
4. **Certification scripts** (not unit tests — never JAX in unit tests;
   validation via vmap/value_and_grad scripts):
   `autolens_workspace_test/scripts/point_source/jax_grad/gradient.py`
   extended to every variant — finiteness + finite-difference agreement,
   mirroring the existing `FitPositionsSource` checks (:126).
5. **Profiling pairing**:
   `autolens_workspace_developer/jax_profiling/gradient/point_source/{image_plane,source_plane}.py`
   extended to the new variants;
   `autolens_profiling/scripts/point_source/likelihood_runtime/` gains
   gradient-timing entries if the existing harness convention supports it.
6. **Search integration smoke**: one small end-to-end
   `af.MultiStartProdigy` (or Adam) fit on a mock quad with the
   centre-free all-to-all likelihood, demonstrating the gradient search
   converges (workspace_test-style script, TEST_MODE-friendly).

## Exit criteria

Every shipped variant either has certified gradients or a documented,
explicit non-differentiability note (e.g. Hungarian `Pair`); solver
implicit-diff merged with tests; certification + profiling scripts green;
`ship_library`/`ship_workspace` PRs open behind the gates.
