# Potential-Correction Algorithm Review & Code Improvement Report

*Prepared for the upstream author (Cao et al. 2025 `lensing_potential_correction`) as part of
PyAutoLens#672. Reviewer: Claude (Fable 5), 2026-07-31. Verification artifacts: side-by-side runs on the
200×200 demo dataset shipped in `for_qiuhan_PT_jax` (both implementations consuming the identical
`masked_imaging`), archived under the task worktree `phase2_experiments/`.*

## 1. Verification summary — is the implementation correct?

**Yes.** The ported `al.pc` and your original implementation are numerically equivalent at every level tested:

| Level | Result |
|---|---|
| dpsi mesh geometry (2168 points) + Hamiltonian (dpsi→dkappa) operator | exactly identical (max abs diff 0.0) |
| Matérn-5/2 regularization matrix (c=2000, s=4) | agrees to ~3×10⁻⁷ relative (float construction-order noise) |
| One-shot joint inversion (single-step method, your paper) | log evidence 1.693447×10⁴ both, diff 5.9×10⁻⁷; corr(dkappa, dkappa)=1.000000; max dpsi diff 3.5×10⁻⁷ |
| Iterative LM (Simona's method), damping matched | cost trajectories agree to 4 significant figures at every iteration (6.2696×10³ vs 6.2694×10³ at iter 4) |

The discrepancy you observed ("same regularization parameters, different recovered mass-perturbation
signal") was real, reproducible, and fully explained — see §2.1. It was not a numerical bug in either code.

## 2. Algorithm findings

### 2.1 The LM damping form is load-bearing (root cause of your discrepancy)

Your engine damps `H + μI`; the port had switched to Marquardt scaling `H + μ·diag(H)` (chosen for
visibility-space curvatures spanning ~10¹¹). These are not interchangeable at a fixed iteration budget: with
μ₀=1, identity damping barely perturbs directions whose curvature ≫ 1, so your first accepted step is nearly a
full Gauss–Newton step and the imaging problem converges in ~3 iterations from a cold start. Marquardt damping
scales the damping to the local curvature, halving every step at the same μ — after the same `n_iter=5` budget
it sits at cost 1.04×10⁴ vs your 6.27×10³, and its dkappa is noise (corr 0.024 vs truth). Same cost function
(identical initial cost 5.0276×10⁶), same accept/reject schedule — purely the damping matrix.

*Adopted fix (PyAutoLens#676):* `damping="identity"|"marquardt"` on both engines; imaging defaults to
identity (your published behavior), interferometer keeps Marquardt. **Recommendation for your code:** none —
your choice is correct for imaging; if you ever port to visibility space, revisit.

### 2.2 End-of-budget rejection storm (affects your implementation too)

At a converged state no cost-decreasing step exists, so the inner LM loop rejects trial steps — each a full
re-trace + interpolator rebuild + dense products (~2 min at 200×200) — until μ exceeds 10¹⁵ (~22 consecutive
rejections, ~47 min wasted). Your `tol` check fires only on *accepted* steps, so it can never terminate this
storm. On our 15 GB test machine your engine died of OOM mid-storm (each rejected trial allocates fresh dense
matrices). *Adopted fix (#676):* a rejected step with ‖δx‖ < tol returns as converged (growing μ only shrinks
the step further), plus a `max_consecutive_rejections` cap. **Recommendation: apply the same two guards to
your `iterative.py` — a few lines in each engine's reject branch.**

### 2.3 Hyper-parameter calibration: your stored demo-2 values are evidence-suboptimal

At your stored iterative hyper-parameters (Matérn-5/2 c=803465.55, s=0.4497) the *converged* solution — in
both codes, they agree — scores corr 0.177 / peak 2.33″ against the true subhalo convergence. At c=2000, s=4
the same cold-start engine recovers corr 0.743 / 0.205″, with higher Laplace evidence. A scale of ~0.45″ is
~1 dpsi pixel: the prior approaches diagonal and the reconstruction soaks up noise. This is exactly why your
proposed evidence-maximization acceptance test is the right protocol; it self-corrects such miscalibration
(§4). No algorithmic error — a calibration footnote for the paper's demo configuration.

### 2.4 Smaller algorithmic observations (no action strictly required)

- **Step-norm tolerance is unit-mixed.** ‖δx‖ mixes source amplitudes and dpsi (different units/scales); a
  relative tolerance (per-block, or scaled by ‖x‖) would make `tol` transferable across datasets.
- **Laplace evidence uses the Gauss–Newton Hessian** (J^T C⁻¹ J + R) rather than the full Hessian — standard
  and consistent with the inversion's linearization; worth one sentence in the paper's evidence description.
- **Source gradients via a finite-difference cross** (`SrcFactory.eval_grad`) with a fixed spacing: fine for
  the analytic/ITP factories in use; if noisy pixelized sources are ever fed in directly, the FD step becomes
  a noise amplifier — an analytic gradient of the interpolant would be sturdier.
- **Gauge handling is sound**: the KKT equality-constrained step (constraint rows undamped) plus re-imposition
  on accepted states is consistent; the port adds `gauge_project_x0` for un-gauged warm starts (the projected
  modes are the Hamiltonian's null space, so recovered dkappa is unchanged).

## 3. Code improvement report (ranked; port-side unless noted)

1. **[shipped, #676]** Damping option + stall guards (§2.1, §2.2).
2. **Hard-coded over-sampling override** — `IterFitDpsiSrcImaging.__init__` forces
   `apply_over_sampling(over_sample_size_lp=4, over_sample_size_pixelization=4)` on the input dataset
   (iterative.py:134), silently discarding the caller's configuration. Should respect the dataset's own
   over-sampling (the one-shot fit does). Profiling shows the over-sampled KNN interpolator rebuild is ~46% of
   every Jacobian rebuild, so this override also quietly sets the engine's dominant cost.
3. **`log_evidence()` pays a full extra Jacobian rebuild** — it calls `get_L_Js_Jdpsi` at the optimized state
   the solver just left (iterative.py:573). Caching the last accepted (L, J_s, J_dpsi) and reusing it
   (opt-in) removes one of ~7 rebuilds per solve (~15% of iterative runtime).
4. **Evidence-sampling analysis fast path** — `dense_util.log_evidence_from_fixed_curvature` exists and is
   validated (smoke-tested numpy+JAX+jit) but no `af.Analysis` uses it: `DpsiSrcInvAnalysis` rebuilds the full
   fit per sample. When only regularization hyper-parameters vary, caching (curvature, data-vector, mapping)
   makes per-sample cost ≈ two reg-matrix builds + three Choleskys (~6× faster; the Phase 3 script uses
   exactly this recipe in-script). Wiring it into the Analysis (with a guard that the sampled instance varies
   only reg hyper-params) is the natural next step, and would let the interferometer engine's existing
   in-loop `reg_optimize_every` evidence optimization unify with the imaging path.
5. **Analysis instance contract inconsistency** — `DpsiInvAnalysis.log_likelihood_function` passes the
   sampled instance as a bare `DpsiPixelization`, while the two joint analyses expect a `DpsiSrcPixelization`
   and unpack `.dpsi_pixelization` / `.src_pixelization`. Unify (accept either, or split parameters
   explicitly) before evidence sampling becomes a user-facing workflow.
6. **`analysis.py` has no unit tests** (`test_autolens/potential_correction/` covers every other module).
   The evidence-sampling path is validated only end-to-end by workspace scripts.
7. **KNN interpolator hot loop** (autoarray) — `knn.py::_mappings_sizes_weights` spends its time in ~970
   `numpy.asarray` calls (71.6 s of a 156 s Jacobian rebuild at 120×120/over-sample 4). Vectorizing the
   per-neighbour conversion would speed every KNN-meshed inversion in the stack, not just `al.pc`.
8. **Dense PSF product** — `dpsi_mapping_matrix_from` computes `psf_mat @ (src_grad @ dpsi_grad)` with a
   dense n_data² PSF matrix (~42% of each rebuild). The stack's `Convolver` applies the same PSF sparsely;
   routing this product through it (or keeping `psf_mat` sparse, as your original does) trims the other
   dominant cost.
9. **Workspace documentation** — `potential_correction/start_here.py` documents the `af.Model` evidence-
   sampling composition as prose only (never executed). Point it at the new `subhalo_recovery_evidence.py`
   acceptance run, or make the snippet runnable, so the recipe cannot drift.

## 4. The quantitative acceptance test (your proposal, implemented)

`autolens_workspace_test/scripts/imaging/subhalo_recovery_evidence.py`: on the standard 120×120 mock
(isothermal lens + 10¹⁰ M☉ NFW subhalo), (1) a 13×12 grid over log₁₀-coefficient × log₁₀-scale of the
one-shot inversion's evidence via the fixed-curvature fast path, and (2) a 5×5 grid where the iterative
engine runs to convergence (cold start, identity damping) and returns the converged Laplace evidence.
Acceptance = the input subhalo is recovered at each method's evidence maximum.

**Results (2026-07-31):**

| | evidence max | at the max | at the hand-calibrated ridge |
|---|---|---|---|
| One-shot | **9350.60** at c=1000, s=1 (interior) | peak **0.36"** (localized), corr **0.13** | c=2000, s=4: evidence 9160.93, corr **0.82**, peak 0.06" |
| Iterative | **9148.53** at c=10⁵, s=0.63 (interior) | peak **0.16"** (localized), corr **0.27** | (same ridge family) |

Term breakdown of the one-shot max's +190-nat gain over the ridge point: **+401 prior-misfit relief**
(reg_cov — the compact, cuspy NFW dkappa pays heavily against a long-scale smooth prior), +102 chi²,
−313 Occam. Smoothing the evidence-max map does not recover the corr (0.13 → 0.16): the admitted extra
structure is extended, not merely rough.

**Conclusion for your protocol.** Both methods *localize* the input subhalo at their evidence maxima —
under a detection/localization reading of "successfully recover", **the test passes and the
implementation + algorithm are validated**. But the experiment also shows that within the Matérn family
**evidence-max ≠ map-fidelity-max**: the evidence correctly prefers shorter scales (the smooth long-scale
prior genuinely misfits a compact cusp), and those same short scales dilute map-level correlation with the
truth. If you want evidence maximization to *also* deliver the highest-fidelity dkappa map, the prior
family needs a hypothesis matching the expected signal morphology — e.g. freeing the Matérn ν, a
compactness-adapted or multi-scale kernel, or a hierarchical prior centred on localized corrections. That
is a modelling refinement, not an implementation issue; happy to prototype it if useful.
