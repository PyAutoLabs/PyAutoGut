## pixelized-multistart-prodigy-cpu
- completed: 2026-07-28
- issue: autolens_workspace_developer#117 (closed)
- prs: autolens_workspace_developer#119, autolens_profiling#91, autolens_workspace#363 (all merged 2026-07-28)
- branch: `feature/pix-prodigy-cpu` (3 repos; deleted post-merge)
- verdict: SHIPPED — MultiStartProdigy recovers the exact truth on pixelized meshes; the #100/#101 "Nautilus wins pix" verdict is overturned
- summary: |
    Broad-start af.MultiStartProdigy (16 starts, resurrect, lr-free) on the
    SLaM source_pix[1] objective, RAL CPU (both A100 nodes unavailable).
    knn: exact truth (+29724, r_E 1.599, free AdaptSplit; late reg-mode
    breakout ~step 1300). Delaunay: exact truth via inherited reg (+30202,
    ~150 steps), free Matern (+29792, no wall), even free AdaptSplit after a
    ~2000-step resurrection tax. Beats matched-settings Nautilus baselines
    by 10-24k nats in a fraction of the wall. THE MECHANISM WAS THE
    REGULARIZATION AXIS, not mesh landscape: AdaptSplit's double-squared
    coefficients are escape-taxed (knn) or NaN-walled (delaunay); Matern or
    SLaM reg inheritance removes the hazard at equal fit quality. Rectangular
    left open: throughput-bound (~17x knn step cost — A100 follow-up) with
    the sharp-bandwidth (0.1) hypothesis arms still running.

    Found + fixed two library bugs mid-campaign (PyAutoFit#1423 cadence arc;
    PyAutoArray PR#411 Delaunay NaN-callback hardening — validated under
    fire). Deliverables: pix_prodigy_findings.md + harness + artifacts
    (wsdev); mature first-class Prodigy cells + knn/delaunay_matern model
    types + campaign knowledge (autolens_profiling); user-facing lessons in
    guides/modeling/searches.py (autolens_workspace). The Brain learned the
    findings maturation lane (samplers faculty AGENTS.md; SamplerSurface
    scan extension filed). 6 follow-ups in ideas.md. Ops traps recorded:
    library upgrades invalidate multi-start resume chains (FoM sanity
    check); smoke tests must exercise the production min()-branch.

## Original prompt

# Does MultiStartProdigy sampling work for pixelized source meshes? (RAL CPU campaign)

Type: research
Target: autolens_workspace_developer
Repos:
- autolens_workspace_developer
Difficulty: large
Autonomy: supervised
Priority: high
Status: draft

## Original request (verbatim)

Yesterday, we showed that gradients are robust for all 3 pixelized meshes,
rectangular, knn, delaunay. In autolens_workspace_developer and
autolens_profiling, we eventually landed on MultiStartProdigy being the best
gradient initializer based on an MGE source model. We basic doing a bit of work
on testing its performance for pixelized mehses, which had a search akin to
source_pix[1] of a SLaM pipeline (e.g. lens light uses fixed values from
previous fit, or probably in this case from the simulator truth). We didnt
finish that investigation. I therefore want us to confirm that MultiStartProdigy
sampling works for these pixelized source meshes, or to demonstrate that it does
not, even thought for MGE source it does. we have done work on this, albeit the
docs I can find (e.g. pix_gradient_findings.md) imply we did this with
MultiStartAdam not MultiStartProdigy. You have freedom to try other optimizers
if you think it would be more suitable for pixelized models, and investigate if
small changes to the likelihood function (e.g. linear algebra implementation,
regularization scheme) might help. Finally, not that thw A100s on RAL seem busy,
so we will likely need to do this investigation using RAL CPUs. The overall run
times will thus be slow as likelihood evaluations are slow on CPU for
pixelizations, but we really just want to confirm gradients can get to the
right solution and monitor how many steps it takes, overall run time profiling
on A100s can thus be a follow up. JAX compile times may also be slow, which
we'll just deal with and follow up to optrimize once we have our final appraoch,
so long as they compile eventually and thus we can figure out the right methods.

## Prior-art anchors (from the memory faculty / Mind records)

- Gradients certified for all 3 mesh families: kernel-CDF rectangular
  (C-infinity, os_pix=1), adaptive rectangular at os_pix=4, and Delaunay via
  frozen integer tables (merged PyAutoArray PR #408, 2026-07-26);
  knn barycentric gradients from the same mesh-gradients arc.
- wsdev#100/#101 tested MultiStartAdam (not Prodigy) on pix: trajectory NaN
  mortality; resurrection (Fit#1400) made it searchable (adam -51201 → +1718 /
  3000 steps) but converged Nautilus (+17419, ~22min warm) won decisively.
- `af.MultiStartProdigy` shipped 2026-07-20 (Fit#1398): lr-free, per-start
  vmapped opt state, apply_if_finite + max_consecutive_nan, resurrect knob.
  On MGE it matches hand-tuned adam with no learning rate. Its pixelized
  validation was explicitly deferred (then assumed A100-only).
- NaN wall localised (wsdev#104): `log_det_regularization_matrix_term` —
  absolute 1e-8 lift below the eigenvalue noise floor at high reg coefficient;
  opt-in `Settings.log_det_method="slogdet"` shipped (PyAutoArray#391/PR#392)
  — a candidate likelihood tweak for exactly this campaign; reg.Adapt
  double-squaring makes production regularization ~100x more fragile.
- Setup: SLaM source_pix[1]-like — fixed lens light (simulator truth), free
  Isothermal+shear mass, free regularization; truth-centred starts certified,
  broad-start basin recovery is the open question.
- RAL CPU constraints: SLURM `--mem`/`--cpus-per-task` must be set explicitly;
  JAX_ENABLE_X64 not inherited by sbatch; warm JAX_COMPILATION_CACHE_DIR turns
  35min pix compiles into seconds; nohup+setsid+DONE-sentinel for remote runs;
  a pix value_and_grad needed ~10.9 GiB (batch_size lever Fit#1374).

## Deliverable

Findings doc in `autolens_workspace_developer/searches_minimal/` (successor to
`pix_gradient_findings.md` / `lr_free_findings.md`) answering: does
MultiStartProdigy (or a better-suited optimizer / likelihood variant) reach the
right solution on rectangular, knn and delaunay pixelized sources, and in how
many steps — CPU wall-time acceptable, A100 profiling deferred.
