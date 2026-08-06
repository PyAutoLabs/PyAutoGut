## ep-hierarchical-scale-collapse
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1405
- completed: 2026-07-22
- library-pr: none (report-only — PyAutoFit was exercised, NOT edited; no worktree claimed)
- workspace-pr: none
- notes: Deliverable was a DIAGNOSIS, and it landed one. Spun out of slope_hierarchy#1 goal 2 to settle whether the EP parent-scale pathology there was problem-specific (N=5 / sigma->0 boundary / lensing) or a framework property. Verdict: FRAMEWORK — it reproduces on a clean CPU toy (HowToFit chapter-3 hierarchical model, 5 low-SNR 1-D Gaussians, parent scatter truth sigma=10 sitting FAR from the boundary), numpy-only, no JAX, no lensing. The sharper finding is that it is STOCHASTIC INSTABILITY, not a bias: 30 runs of an IDENTICAL known-answer problem across max_steps in {20,25,30,50,60} gave 21 RECOVER (scatter 9-13, sane errors) / 2 COLLAPSE (scatter 0.003-0.80 with an over-confident ~0 error) / 7 CRASH (InitializerException hard-abort). The joint Dynesty fit of the SAME factor graph is stable and correct every time (12.8 [9.9, 16.3]) — the graph and data are fine, EP is the sole source. On f83f2f493, i.e. DOWNSTREAM of the #1383 projection fix: a distinct, deeper issue. MECHANISM, all three candidates settled: delta-method/boundary artefact REFUTED (base-space message unbounded, TransformedMessage.variance is faithfully reading a genuinely over-confident posterior); over-shrinkage feedback CONFIRMED as the collapse basin (per-group posterior means cluster to ~0.6 spread vs true +/-10, parent sees near-identical draws, infers tiny scatter, shrinks harder — positive feedback to scatter~0); under-convergence is only the transient into/out of basins, NOT a crawl toward truth. TRAP RECORDED: the science case's variant is stickier and near-boundary — it converged to a STABLE WRONG fixed point (0.026 vs truth 0.1) and plateaued, so "run longer" is not the fix. TRAP 2: the diagnostics' standing hint "consider damping, delta < 1" is actively counterproductive on this mode (delta=0.5 gave full collapse, 67 BAD_PROJECTION, log-evidence to 5e7) and must be revised alongside any fix. Two defects reported on #1405: (1) scale-hyperparameter collapse that the F10 sigma-collapse guard passes SILENTLY, (2) InitializerException killing the whole graph fit instead of degrading to a flagged bad projection. Repro + full forensics preserved at complete/2026/07/ep_scale_collapse_assets/ (ep_toy_diagnostic.py, EP_TOY_FINDINGS.md). Collapse is only ~7% per run, so any future "fixed it" claim needs a LOOP of runs, not one. FOLLOW-UPS FILED: draft/bug/autofit/ep_initializer_exception_should_not_abort.md (small, safe, do first — 23% of runs, pure robustness, no statistical judgment) and draft/bug/autofit/ep_hierarchical_scale_collapse_moment_match.md (medium, supervised — F10 must fire first, then the moment-match/basin work; acceptance bar is "never silently report a collapsed scale as confident", not "collapse never happens"). Also retired draft/research/graphical_ep/ep_scale_parameter_error_diagnostic.md to Status: execution-complete — that prompt IS the one this task executed, and it would otherwise have been re-picked by /feature.

## Original prompt

# Hierarchical EP: parent scale hyperparameter collapses (over-confident ~0) and can hard-crash

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: high
Status: issued
Issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1405

## Summary

A hierarchical EP fit of a parent scale hyperparameter (the `sigma` of a
`HierarchicalFactor` parent Gaussian) is **unstable**: repeated fits of an *identical,
known-answer* problem land in three qualitatively different outcomes. On a clean CPU toy
(no JAX, no lensing, parent scatter truth σ=10 sitting far from the σ→0 boundary):

- **RECOVER (~70%)** — scatter ≈ 9–13, sane errors, matches a joint nested-sampler fit.
- **COLLAPSE (~7%)** — scatter → ~0 (0.003–0.80) with an **over-confident ~0 error**;
  the F10 sigma-collapse guard does **not** flag it. This is the exact readout seen in
  the `slope_hierarchy` science project (parent scatter 4–12× too low, errors ~1000×
  too tight).
- **CRASH (~23%)** — `InitializerException` ("initial samples all have the same figure
  of merit") hard-aborts mid-EP when a factor's Dynesty init degenerates.

Measured over 30 identical-problem runs across max_steps ∈ {20,25,30,50,60}:
21 RECOVER / 2 COLLAPSE / 7 CRASH. Both COLLAPSEs were at the shortest setting
(max_steps=20); zero collapse at 25–60. CRASH appears at every max_steps.

The joint fit — `Dynesty` on `factor_graph.global_prior_model` for the same graph — is
stable and correct every time (scatter 12.8 [9.9, 16.3]). **The graph and data are fine;
EP is the sole source of the instability.**

This is on PyAutoFit `f83f2f493` (i.e. *includes* the #1383 projection fix). It is a
distinct, deeper issue than #1383.

## Two distinct defects

1. **Scale-hyperparameter COLLAPSE (over-shrinkage basin).** When it collapses, the
   per-group drawn-variable posterior *means* cluster far tighter than truth (spread ~0.6
   vs true ~±10); the parent factor then sees near-identical draws and infers a tiny
   scatter, tightening the shrinkage further — positive feedback to a fixed point at
   scatter ≈ 0 with ~0 reported error. It is **not** a delta-method/boundary artefact:
   truth σ=10, the base-space scatter message is unbounded
   (`TruncatedNormal(mean≈0, lower=-inf, upper=inf)`), so `TransformedMessage.variance`
   is faithfully reading a genuinely over-confident posterior. `ep_history.csv` shows
   recurring `BAD_PROJECTION` on the `HierarchicalFactor` and wildly swinging
   log-evidence during collapse.
2. **`InitializerException` CRASH.** ~1-in-4 runs hard-abort when EP drives a factor to a
   degenerate all-equal-likelihood state its per-factor `DynestyStatic` cannot initialise
   (`autofit/non_linear/initializer.py:185`). Should degrade to a flagged BAD_PROJECTION
   / skipped update, not kill the whole fit.

## Minimal repro

`ep_scale_collapse_assets/ep_toy_diagnostic.py` (self-contained; run from the HowToFit
repo root, numpy-only, minutes on CPU). It builds the HowToFit chapter-3 hierarchical toy
(5 low-SNR 1-D Gaussians, `centre ~ N(50, 10)`), runs EP and a joint Dynesty fit on the
same graph, and prints an `OUTCOME:` tag. Reproduce the distribution:

```bash
cd HowToFit
export NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib PYAUTO_SKIP_VISUALIZATION=1
for r in $(seq 1 10); do TOY_MAX_STEPS=20 TOY_JOINT=0 TOY_TAG=rep_$r \
  python3 /path/to/ep_toy_diagnostic.py 2>/dev/null | grep OUTCOME; done
```

Full forensics + trajectories: `ep_scale_collapse_assets/EP_TOY_FINDINGS.md`.

## Triage questions for the fix owner

- Is COLLAPSE curable by a **more robust / damped `HierarchicalFactor` scale
  moment-match** (or a deterministic per-factor optimiser to cut the sampler noise that
  drives basin selection)? Note: naive damping (delta=0.5) made `slope_hierarchy` *worse*
  — so the standing diagnostics hint "consider damping, delta < 1" likely mis-diagnoses
  this mode and should be revised alongside the fix.
- Should the **F10 sigma-collapse guard** fire on the COLLAPSE run? It currently passes a
  scatter≈0 / error≈0 parent silently.
- Should the **`InitializerException`** be caught inside the EP loop and recorded as a bad
  projection rather than aborting the fit?

## Origin

Cheap CPU diagnostic spun out of `slope_hierarchy#1` goal 2 (private repo
Jammy2211/slope_hierarchy) to decide whether the EP scale-parameter pathology there was
problem-specific (N=5 / boundary / lensing) or a framework property. It is a framework
property — reproduced here off-boundary and off-lensing. Companion research prompt:
`draft/research/graphical_ep/ep_scale_parameter_error_diagnostic.md`.

## Original prompt (ep_scale_parameter_error_diagnostic — the prompt this task executed)

# Diagnose why EP reports parent-scatter errors that are far too small

Type: research
Target: graphical_ep
Repos:
- PyAutoFit
- HowToFit
- autofit_workspace
Difficulty: medium
Autonomy: supervised
Priority: high
Status: execution-complete (2026-07-21) — the toy diagnostic was run and the
verdict reached: the pathology is a FRAMEWORK property (reproduces off-boundary,
off-lensing), specifically stochastic instability (70% recover / 7% collapse /
23% crash over 30 identical runs), NOT a delta-method/boundary artefact. Filed as
PyAutoFit#1405. Findings + repro: `complete/2026/07/ep_scale_collapse_assets/`
(`EP_TOY_FINDINGS.md`, `ep_toy_diagnostic.py`). Fix work continues in
`draft/bug/autofit/ep_hierarchical_scale_collapse_moment_match.md` and
`draft/bug/autofit/ep_initializer_exception_should_not_abort.md`.
DO NOT re-pick this prompt for execution.

## The question

In the `slope_hierarchy` science project (private repo Jammy2211/slope_hierarchy, issue #1 has
the full forensics), a hierarchical fit of N=5 strong lenses — per-lens power-law `slope` drawn
from a parent Gaussian N(mean, sigma) — gave this parity between JAX-gradient NUTS and EP, both
fitting the SAME factor graph:

| parent  | truth | NUTS                     | EP (converged)      |
|---------|-------|--------------------------|---------------------|
| mean    | 2.0   | 2.028 [2.000, 2.063]     | 2.051 ± 0.0001      |
| scatter | 0.1   | 0.143 [0.117, 0.185]     | 0.026 ± 0.00001     |

EP recovers the parent MEAN but (a) its parent SCATTER point estimate is ~4x low and, more
puzzlingly, (b) its reported ERROR bars are ~300–3000x tighter than NUTS's. We do NOT yet know
why, and two facts make it non-obvious:
 - The scatter (0.026) is BELOW even the per-lens measurement-error floor (~0.03), so simple
   "EP over-shrinks the per-lens messages" would predict scatter ~= raw spread ~= 0.1, not 0.026.
   Something actively pulls the scatter DOWN.
 - The EP error readout is `sqrt(mean_field.variance[hierarchical_factor.sigma])`, which I
   confirmed IS physical-space (delta-method Jacobian in `TransformedMessage.variance`), so it is
   NOT a naive transformed-vs-base-space readout bug.
 - "Converged at 0.026" is weakly established: the scatter climbed over EP sweeps
   (0.0007 -> 0.0037 -> 0.0135 -> 0.0264) and plateaued for only ~2 sweeps — it may still be
   crawling toward 0.1.

## The task

Run a CHEAP toy hierarchical EP fit with a KNOWN parent, on CPU in minutes (no JAX, no HPC, no
lensing), to decide whether the small-error pathology is PROBLEM-SPECIFIC (N=5, boundary,
identifiability) or a FRAMEWORK / delta-method property of PyAutoFit EP that reproduces on any
hierarchical model.

Use `HowToFit/scripts/chapter_3_graphical_models/tutorial_optional_hierarchical_ep.py` as the
base (it builds a `HierarchicalFactor` parent Gaussian over per-dataset Gaussian `centre`s; its
`factor_graph.optimise(...)` EP call is currently commented out — enable it). Cross-reference
`autofit_workspace/scripts/features/expectation_propagation.py` for the low-level API and the
diagnostics calls. Confirm the TRUE parent (mean, sigma) from the tutorial's data simulator.

Then:
1. Fit the toy with EP (`factor_graph.optimise(af.LaplaceOptimiser(), ep_history=af.EPHistory(
   kl_tol=0.05), max_steps=...)`). Read the parent mean/sigma and their EP errors exactly as
   slope_hierarchy does: `mean_field = result.updated_ep_mean_field.mean_field`, then
   `mean_field.mean[hierarchical_factor.sigma]` and `sqrt(mean_field.variance[...])`.
2. Fit the SAME toy graph jointly with a nested sampler (Nautilus or Dynesty) to get the
   trustworthy parent-sigma posterior + error (percentile-based, `samples.values_at_upper_sigma`).
3. Compare: (a) does EP recover the parent sigma point estimate on the toy? (b) are EP's
   parent error bars sane vs the sampler, or also orders-of-magnitude too tight? (c) push
   max_steps up (e.g. 5, 20, 50) — does the sigma estimate keep climbing (under-convergence)
   or sit at a fixed point?
4. Separate the two candidate mechanisms:
   - Delta-method under-statement: is the parent-sigma BASE message near the sigma->0 boundary,
     where `TransformedMessage.variance`'s Jacobian linearization breaks down?
   - Genuine EP over-counting: inspect per-group message widths over sweeps in
     `mean_field_history.csv` (written to the EP output folder) — do the drawn-variable messages
     over-shrink across iterations?
5. Verdict: framework/delta-method property (=> a fixable PyAutoFit issue, file it) vs inherent
   EP-for-scale-parameter caveat (=> a methods caveat to document). Either way, report whether the
   small-error effect reproduces on the toy.

## EP / API state you must know (changes from this work + the related 2026-07 EP wave)

- **MERGED — projection fix, PyAutoFit#1383 (commit b32e58b16, on main).** Fixed TWO stacked
  defects that were causing EP boundary-collapse: (1) `TransformedMessage.project`
  (autofit/messages/composed_transform.py) now maps samples through `self._transform` into the
  base message's space before the moment match — it previously projected PHYSICAL samples
  directly, pinning messages at prior bounds; (2) `Result.projected_model`
  (autofit/non_linear/result.py) now converts linear `samples.weight_list` to LOG weights, and
  `Prior.project` (autofit/mapper/prior/abstract.py) renamed its kwarg `weights` ->
  `log_weight_list`. Regression test: `test_autofit/graphical/test_unification.py::
  test_projected_model_moments`. ENSURE your PyAutoFit checkout includes b32e58b16 — everything
  below assumes the fixed projection.
- **EP diagnostics wave, PyAutoFit#1335 (+ #1350/#1353/#1364, umbrella #1330).** Use these tools:
  `from autofit.graphical import mean_field_summary, check_sigma_collapse` and the auto-written
  output artifacts `ep_history.csv`, `mean_field_history.csv`, `mean_field_evolution.png`,
  `graph_factors.png`, `ep_diagnostics.results` (the F10 sigma-collapse guard). These behaved
  correctly throughout slope_hierarchy — trust them.
- **FILED, NOT YET IMPLEMENTED — updater/delta API gap:** PyAutoMind/draft/feature/autofit/
  ep_optimise_expose_updater_delta.md. `factor_graph.optimise()` cannot pass an `updater`/`delta`
  through, so to damp EP you must use the private workaround:
  `opt = factor_graph._make_ep_optimiser(laplace, paths=paths, ep_history=...);
   opt.updater = SimplerUpdater(delta); mf = opt.run(factor_graph.mean_field_approximation(),
   max_steps=...)` (pattern is in slope_hierarchy/scripts/ep.py). If you damp, use this.
- **Finding — damping did NOT help slope_hierarchy; it made things WORSE** (delta=0.5 -> full
  collapse, 67 BAD_PROJECTION, log-evidence blew up to 5e7). The diagnostics' standing hint
  "consider damping, delta < 1" was actively counterproductive on that problem, so do not assume
  damping is the fix — the toy result should inform whether that hint needs revising.
- **Repo note:** `autoconf` was renamed to `autonerves`; imports may be `from autolens import ...`
  (config surface) or `autonerves`. Unit/toy work is numpy-only — no JAX needed.

## Deliverable

A short findings note: does the tiny-error effect reproduce on the known-answer toy? Which
mechanism (delta-method vs EP over-counting vs under-convergence) is live? Is it a fixable
PyAutoFit issue (file a bug prompt with a minimal repro) or an inherent EP scale-parameter
caveat to document? This unblocks the goal-2 write-up in Jammy2211/slope_hierarchy#1.

<!-- Grounding: this diagnostic is the cheap CPU/toy follow-up to slope_hierarchy goal 2
(Jammy2211/slope_hierarchy#1). Companions in this folder: ep_framework_review.md (the #1335
diagnostics wave), ep_scoping.md / graphical_scoping.md (EP scale-up). Related filed prompts:
draft/feature/autofit/ep_optimise_expose_updater_delta.md. -->
