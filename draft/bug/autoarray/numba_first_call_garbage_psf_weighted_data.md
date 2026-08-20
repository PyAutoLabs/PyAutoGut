# Numba sparse-operator likelihood: first-call garbage / intermittent worker corruption

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
- @PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

Found 2026-08-20 while building the numba CPU profiling infrastructure
(autolens_profiling#151, `scripts/imaging/{likelihood_runtime,parallel_scaling}/pixelization_numba.py`).

## Symptom 1 — cold-cache first call returns garbage (deterministic)

With a **cold numba cache** (`NUMBA_CACHE_DIR` empty), the first
`AnalysisImaging(use_jax=False)` likelihood evaluation on a dataset with
`apply_sparse_operator_cpu()` returns **NaN**; the second call with byte-identical
inputs is correct. Localised: `psf_weighted_data_from`
(`autoarray/inversion/inversion/imaging_numba/inversion_imaging_numba_util.py:9`)
returns values ~1e298-1e299 (uninitialized-memory scale) on its first
freshly-compiled call — inputs verified identical between call 1 (garbage) and
call 2 (correct), same dispatcher object. Warm cache → first call fine.
Downstream this overflows `regularization_term`'s matmul → NaN figure of merit.

Repro (euclid profiling dataset, numba 0.62.1, autoarray main 2026-08-20):
`rm -rf /tmp/numba_cache_cold && NUMBA_CACHE_DIR=/tmp/numba_cache_cold python <fit script>` —
`fit.inversion.psf_weighted_data` max |.| = 4.8e299 on fit #1, 2.98e02 on fit #2.

## Symptom 2 — intermittent corruption in forked multiprocessing workers

In a `fork_context().Pool(P)` (exactly what `af.Nautilus(number_of_cores=P)`
builds), mapping `fitness.call_wrap` over **identical parameter vectors**
intermittently returns the `resample_figure_of_merit` sentinel (-1e99) for a
subset of evaluations — observed 2/8 corrupted in one steady-state map (P=2,
warm parent, workers forked after numba compile), 0/24 in the next run.
Production impact: **a fraction of likelihood evaluations in every
`number_of_cores>1` CPU run is silently discarded as resamples** (and any
non-sentinel wrong-value variant would silently corrupt sampling).

The `parallel_scaling/pixelization_numba.py` harness now counts these per map
(`corrupt_evals_first_map` / `corrupt_evals_steady_maps` in its JSON) — use it
as the regression probe.

## Suspects / notes

- `psf_weighted_data_from`'s `weight_map_native = image_native / noise_map_native**2`
  produces NaN (0/0) in the padded border, guarded by `np.isnan`; an **inf**
  (finite image / zero noise) would pass the guard — but the first-vs-second
  call divergence with identical inputs points at numba codegen/caching
  (first-call-after-compile executing wrong/uninitialized code), not the maths.
- numba 0.62.1, `cache=True`, lazy materialization via `autoarray/numba_util.py`
  (`_materialize_all`). Worth testing: `cache=False`, numba version pin, and
  whether symptom 2 reproduces with symptom 1 fixed (they may share a cause).
- Keep the profiling-harness corruption counters as the acceptance test.
