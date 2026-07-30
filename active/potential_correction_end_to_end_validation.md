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
