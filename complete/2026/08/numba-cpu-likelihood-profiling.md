# numba-cpu-likelihood-profiling — numba-CPU sparse-operator likelihood profiling

**Date:** 2026-08-20 (merged) / recorded 2026-08-21
**Issue:** [autolens_profiling#151](https://github.com/PyAutoLabs/autolens_profiling/issues/151) (closed, completed)
**PR:** [autolens_profiling#152](https://github.com/PyAutoLabs/autolens_profiling/pull/152) — **merged 2026-08-20 by Jammy2211**, merge commit `564d51e7`, 5 commits / 30 files
**Repos edited:** `autolens_profiling` only

## What shipped

Numba-CPU sparse-operator likelihood profiling infrastructure in `autolens_profiling`: a runtime
cell, a step-by-step breakdown cell (euclid default, hst/jwst), a multiprocessing scaling harness
(serial vs Nautilus object-pool vs initializer-cached pool, pickle payload, BLAS interplay), and
RAL SLURM submit — plus the first local pass.

Campaign fiducial, set by user pivot on 2026-08-20: **Delaunay + Hilbert(1500) AdaptImage +
ConstantSplit**. The Rectangular kernel-CDF speed-up was **deferred**.

## Headline finding

Delaunay at euclid: **4.6 s/eval**, of which the **reconstruction solve is 3.73 s (~78%)** for a
1560-parameter positive-only solve. MGE matrices account for 0.51 s; triplet construction only
15 ms — i.e. the cost is overwhelmingly the solve, not the geometry.

Prime restoration suspect: the legacy numba `fnnls` + `cholesky_funcs` deleted in PyAutoArray
`8bb449a1` (2025-06-18).

Full findings trail: the comments on issue #151.

## Outstanding follow-ups (NOT done — this record does not claim them)

Carried forward from the task's own RESUME list. Two are already filed as prompts; two are not:

- **Filed as prompts:**
  - `draft/feature/autoarray/numba_cpu_likelihood_mge_convolution_and_caching.md` (still valid)
  - `draft/bug/autoarray/numba_first_call_garbage_psf_weighted_data.md`
- **Not yet filed — need a prompt if they are still wanted:**
  - Verify which solver actually runs (`settings.use_positive_only_solver`) and its source-pixel
    scaling.
  - Write + `start_dev` a **PyAutoArray solver-restoration** prompt against the `8bb449a1` deletion
    above — this is the direct consequence of the headline finding.
  - The **RAL scaling sweep** (`hpc/batch_cpu/...`), which the task listed as post-merge work.

A hst runtime/breakdown pin for `delaunay_numba` was also on the RESUME list as "push to PR #152";
that is now moot — the PR merged without it.

## Record provenance

Written 2026-08-21 by a different session while clearing a `lifecycle issues` DRIFT report
(tracking issue CLOSED but `active.md` still listed the task as pending). The merge, issue state and
PR metadata were verified against GitHub; the technical findings above are transcribed from the
task's `active.md` entry and issue #151, not independently re-measured.

## Original prompt

# Profiling infrastructure for the numba CPU sparse-operator likelihood

Type: feature
Target: autolens_profiling
Repos:
- @autolens_profiling
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

## Original request (verbatim, 2026-08-20)

> https://github.com/PyAutoLabs/autolens_workspace/blob/main/scripts/imaging/features/pixelization/cpu_fast_modeling.py
> describes the use of fast CPU modeling via numba. I am about to do a large
> round of lens modeling using this as CPU resources are more abundant. Can you
> check if autolens_profiling has any dediciated infrastructure for profiling
> this likelihood funtion (e.g. step by step profiling of each function, working
> out if anything more can be dne to make Python multiprocessing or another
> parallelization thing fast)? Can you either make this infrastructure or build
> on it, so we can begin to make this type of modeling as fast as possible. I am
> going to be modeling systems at Euclid resolution, but feel free to do
> profiling at higher resolution too.

## Context (survey, 2026-08-20)

`autolens_profiling` today profiles the **JAX** likelihood stack only. The
imaging pixelization cells (`scripts/imaging/likelihood_runtime/pixelization.py`,
`scripts/imaging/likelihood_breakdown/pixelization.py`) have a `--sparse` flag,
but it engages the **JAX** sparse operator (`dataset.apply_sparse_operator()`).
Nothing profiles:

- the **numba CPU** path the workspace `cpu_fast_modeling.py` example uses:
  `dataset.apply_sparse_operator_cpu()` → `SparseLinAlgImagingNumba`
  (`PyAutoArray autoarray/inversion/inversion/imaging_numba/inversion_imaging_numba_util.py`)
  with `AnalysisImaging(use_jax=False)`;
- **multiprocessing scaling** — `scripts/misc/searches/README.md` pins
  `number_of_cores=1` by convention and explicitly lists "Pool scaling.
  `number_of_cores > 1` sweeps are future work."

## Goal

Build dedicated infrastructure in `@autolens_profiling` so the numba CPU
sparse-operator likelihood (rectangular pixelization, `use_jax=False`) can be
made as fast as possible for large Euclid-resolution modeling campaigns:

1. **Runtime cell** — per-evaluation likelihood runtime for the numba CPU path,
   framed by instrument (euclid primary; hst/jwst for higher resolution),
   following the existing `likelihood_runtime` conventions (`_profile_cli`,
   versioned `results/` JSON+PNG artifacts).
2. **Breakdown cell** — step-by-step decomposition of the numba likelihood
   (mapping matrix, curvature via sparse operator, regularization, solve,
   log-det terms, mapped reconstruction) so the dominant steps are visible.
3. **Parallel-scaling profiling** — measure how likelihood throughput scales
   with Python `multiprocessing` `number_of_cores` (Nautilus pool as in the
   workspace example) and numba threading, identify the serial/overhead
   fraction, and report what more can be done (fork vs spawn cost, sparse
   operator pickling/shared-memory, numba `parallel=True` opportunities,
   core-count guidance for HPC nodes).
4. **Results + README** — record findings so the workspace example and HPC
   campaigns can quote concrete core-count and settings guidance.
