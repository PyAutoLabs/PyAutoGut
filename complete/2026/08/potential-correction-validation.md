Closed the potential-correction JAX-vs-Python discrepancy (no implementation
bug: the LM damping form was the whole story), fixed the flaky smoke entry,
implemented the author's evidence-sampled acceptance test (passes end-to-end),
and delivered the algorithm review + code improvement report.

- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/672 (CLOSED completed
  2026-08-01 on wrap-up; comments stay open for the upstream author's review of
  the report — permalink issuecomment-5144563213)
- prs (all MERGED 2026-07-31/08-01): PyAutoLens#676 (`c8acdd3e9`, damping=
  identity|marquardt on both iterative engines — imaging default restored to
  identity, uv keeps marquardt; rejected-step-below-tol returns converged +
  max_consecutive_rejections cap, ending a ~47-min shared rejection storm);
  autolens_workspace_test#238 (`b4085a0`, subhalo_recovery.py over_sample 4→2
  + n_iter 5→3: CI 232s→170s vs the 300s cap, metrics improved 0.78→0.82);
  autolens_workspace_test#243 (subhalo_recovery_evidence.py acceptance test +
  no_run SLOW exclusion, upstream-gated on #676).
- phase 2 verdict (side-by-side on the author's 200x200 tar demo, identical
  masked_imaging): one-shot parity at machine precision (evidence diff 6e-7,
  corr 1.000000); iterative trajectories agree to 4 sig figs once damping
  matches (mu*I). The reported "same params, different signal" = Marquardt
  mu*diag(H) under-converging at fixed n_iter (corr 0.024 vs 0.743 cold at
  c=2000/s=4). Author's stored demo-2 params are evidence-suboptimal: the
  CONVERGED solution there scores corr 0.18 in both codes.
- phase 3 acceptance (120x120 mock): one-shot 13x12 evidence grid (fixed-
  curvature fast path) max 9350.60 @ c=1000/s=1; iterative 5x5 converged-
  Laplace grid max 9148.53 @ c=1e5/s=0.63; BOTH localize the subhalo at their
  evidence maxima (0.36"/0.16"). KEY FINDING: within the Matern family
  evidence-max ≠ map-fidelity-max (+190 nats = +401 prior-misfit relief +102
  chi2 −313 Occam; the smooth long-scale prior misfits a compact NFW cusp) —
  map corr 0.13 at the max vs 0.82 on the ridge; a morphology-matched prior
  family is the recommended follow-up. Acceptance = localization + ridge
  reference, documented in the script.
- phase 4: review report posted to #672 (verification tables, 4 algorithm
  findings incl. a 2-line stall-guard recommendation for the author's own
  code, ranked 9-item improvement list: apply_over_sampling(4,4) hardcode,
  log_evidence's extra Jacobian rebuild, fast-path Analysis wiring, KNN
  asarray hot loop in autoarray, dense PSF product, analysis.py untested,
  Analysis instance-contract inconsistency, start_here prose-only snippet).
- artifacts: ~/Code/PyAutoLabs/potential_correction_validation_artifacts/
  (evidence-surface npz, side-by-side results, run logs, the report).
- gotchas hit: two OOM kills on the 1-core/15GB box (dense per-trial
  allocations; per-point process isolation is the pattern), detached chains
  die with WSL teardown (copy artifacts durably + re-arm), FitDpsiSrcImaging
  .best_fit_dpsi is lazy (trigger log_evidence first), branch-off-main ships
  from a drifted worktree need the file edit re-applied on main's version.
- shipped under human-acked Heart RED (release-integrate commit_shas
  dispatcher regression from ci-dedupe #131 — user chose to leave it).

## Wrap-up follow-up (2026-08-01)

- The #676 identity default regressed the smoke script it had just been fixed
  by #238: subhalo_recovery.py warm-starts at the one-shot optimum, where
  identity's near-GN trial steps are rejected (the capped 10-rejection storm,
  each a full Jacobian rebuild) — main run 30669142115 timed out 300s on both
  legs at identical results. Fixed by pinning damping="marquardt" (wst#244,
  merged `ae3598a`): CI legs back to 171.7s/170.4s. Attribution measured
  locally under the smoke profile: marquardt 310-321s local vs identity 663s
  local with the engine's own "10 consecutive rejected LM steps" warning.
- PyAutoLens#666 (iterative underperforms one-shot on the workspace example)
  verified fixed by #676 on the exact reproducer: iterative peak now (1.45,
  0.15) = one-shot's, evidence 9.0625e3 vs the collapsed 4.2083e3 on
  2026.7.23.1. Closed completed.
- Also closed: wst#196 (per-script timeout shipped in #197; never closed).
- Damping-mode coverage is now deliberate: smoke pins marquardt warm-start;
  the workspace example exercises the identity cold-start default.

## Original prompt

# Potential correction: end-to-end evidence-sampled validation + JAX-vs-Python discrepancy hunt + smoke timeout fix

Type: bug
Target: autolens
Repos:
- PyAutoLens
- autolens_workspace_test
Difficulty: high
Autonomy: supervised
Priority: high
Status: formalised

Follow-up to the potential-correction port (PyAutoLens#618, complete/2026/07/
potential-correction-port.md). Three coupled legs plus a review deliverable:

**1. Smoke timeout fix.** `imaging/subhalo_recovery.py` in
autolens_workspace_test runs at 232s/224s against the 300s smoke cap — it flakes
into timeout on slower runners ("broken a lot"). Make it materially faster (or
restructure) while keeping the one-shot + iterative recovery assertions
meaningful.

**2. Suspected correctness bug.** The upstream author reports that for the SAME
potential-correction regularization parameters, the recovered mass-perturbation
signal differs between their original pure-Python code (believed correct, slow)
and the ported JAX version, beyond numerical error. Note the port history is
suggestive: the ported iterative engine cold-started to corr 0.032 and needed an
x0 warm start from the one-shot solution (PyAutoLens#630) to recover the
subhalo, and Phase 5 concluded the demo-2 stored iterative hyper-params were
"miscalibrated" — the author's report may mean the ORIGINAL code recovers the
signal at those same params, i.e. a real divergence in the iterative engine, not
miscalibration. Side-by-side the original code and `al.pc` at identical
hyper-params, diffing intermediate quantities until the divergence point is
found (or parity is certified end-to-end).

**3. Quantitative end-to-end test (the author's proposed acceptance test).**
Sample the potential-correction regularization hyper-params by Bayesian
evidence, for BOTH methods:
  (a) single-step: per sample run the already-implemented one-shot inversion,
      return its evidence; maximize evidence over reg params;
  (b) iterative (Simona's method): per sample run the iterative correction to
      convergence, return the converged solution's evidence.
Success criterion: BOTH recover the input subhalo in mock data at the
evidence-preferred hyper-params. Prior art: Phase 5 already showed evidence
self-corrects miscalibrated iterative hyper-params on the 200x200 demo
(corr 0.18 → 0.73 with higher Laplace evidence at c=2000/s=4).

**4. Algorithm double-check + code improvement report.** A judgment-tier
(Fable5) review of the author-written algorithm (single-step per the paper,
Cao et al. 2025, + the iterative method) against the implementation, plus a code
improvement report the author can review and selectively adopt.

Supersedes/absorbs `draft/bug/autolens/subhalo_recovery_iterative_dkappa_collapsed.md`
(its specific collapse was fixed by #630's warm start; its underlying concern —
iterative-path fragility — is leg 2 here).

## Original request (verbatim)

> fix this which is broken a lot and the single smoke failure
> (imaging/subhalo_recovery.py timeout at 300s), however we also want to look
> for a bug in potential corrections based on this: The potential bug I've
> noticed before is that, for the same set of regularization parameters for the
> potential correction, the recovered mass-perturbation signal differs between
> my original pure Python code (which I believe is correct, although slow) and
> the new JAX-ported version. The discrepancy cannot be explained by numerical
> error alone. I've reviewed the implementation report produced by the AI agents
> on the AutoLens GitHub issue pages, and it appears that the current code works
> in principle. Therefore, I would suggest performing one final end-to-end test.
> If this test passes, I believe we can be confident that everything is
> functioning correctly.
>
> In the current tests (for both the single-step potential correction method
> described in my paper and Simona's iterative potential correction method), we
> manually choose reasonably good regularization hyperparameters for the lensing
> potential and then check whether we can qualitatively recover the input
> subhalo in the mock data. I would now suggest a more quantitative test, in
> which the regularization hyperparameters for the lensing potential correction
> are determined optimally by sampling the Bayesian evidence.
>
> 1. For the single-step potential correction method:
> We allow the sampler to explore different values of the regularization
> parameters for the lensing potential correction. For each set of parameters,
> we perform the single-step inversion that has already been implemented,
> compute the evidence, and identify the set of regularization parameters that
> maximizes the evidence.
> 2. For the iterative potential correction method:
> The procedure is similar. We let the sampler explore different sets of
> regularization parameters. For each set, we run the iterative potential
> correction until convergence, then return the evidence of the final converged
> solution to the sampler.
>
> If both approaches (1) and (2) successfully recover the input subhalo, I
> believe we can conclude that the implementation and algorithm are correct.
>
> By the way, it might also be helpful to have Fable5 double-check the
> algorithm. The current version was written entirely by me, and I may have made
> mistakes. Since we have already provided the AI with a solid algorithmic
> framework, it may be well suited to identifying any potential errors I may
> have overlooked.
>
> P.S. If Fable5 can provide a code improvement report, I would be happy to
> review it and decide whether we should adopt its suggestions and update the
> code accordingly.
