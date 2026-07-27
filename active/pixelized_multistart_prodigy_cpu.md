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
