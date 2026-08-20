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
