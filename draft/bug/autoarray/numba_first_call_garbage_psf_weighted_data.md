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

## Root cause — confirmed 2026-08-21

Not a numba codegen or caching bug. `psf_weighted_data_from` gathers the
weight map at `[ip0_y + k0_y + kernel_shift_y, ip0_x + k0_x + kernel_shift_x]`
with **no bounds check**. numba `@jit()` does not bounds-check array reads, so
for any unmasked pixel within `kernel_shape // 2` of the array edge the gather
reads uninitialized heap memory instead of raising `IndexError`. Negative
indices are unsafe in the same way — they wrap to the opposite edge.

Proof: compiling the shipped source unchanged under `boundscheck=True` raises
`IndexError: index is out of bounds` for a mask reaching the array edge, and is
clean for an interior-only mask. With the guard added, the numba output matches
the zero-padded numpy twin exactly across array sizes and kernel sizes.

This explains **both** symptoms, and explains why the inputs were verified
identical between call 1 and call 2 — they were; the function reads memory
*outside* its inputs:

- **Symptom 1** — a cold-cache first call runs right after numba's compilation
  has churned the heap, so the memory next to the freshly allocated weight map
  holds compiler garbage (~1e299). Warm cache: no compile, benign neighbour.
- **Symptom 2** — each forked worker has a different heap layout, so whether
  the neighbouring memory is poisonous varies per worker and per run. Hence
  2/8 corrupted in one map and 0/24 in the next.

The `np.isnan` guard was doing real work (masked border is `0/0 = NaN`) but
never protected the array bounds. The sibling `psf_precision_value_from` was
already hardened against exactly this — `psf_weighted_data_from` was missed.

The inf suspect (finite image / zero noise passing the `isnan` guard) is **not
reachable** via the caller: `.native` zeroes both data and noise outside the
mask, giving `0/0 = NaN`, never `inf`. An inf would require a zero noise value
*inside* the mask, which is a data-validation error and should stay loud. The
`isnan` guard is therefore left as-is.

Fix: @PyAutoArray PR #456 (branch `claude/autoarray-numba-psf-garbage-hfxnjv`) — bounds
guard mirroring the sibling, plus a numba-vs-numpy equivalence regression test
on an edge-touching mask (fails without the fix, passes with it). Full
`test_autoarray` suite: 1034 passed, 3 pre-existing pynufft failures unrelated
to this change.

Not done: the `parallel_scaling/pixelization_numba.py` corruption counters
named as the acceptance probe could not be run here (needs the profiling
workspace and its datasets). Symptom 2 should be re-measured against this
branch before the prompt is closed.

Split out while fixing this: `draft/bug/autoarray/numba_kernel_shift_axes_swapped.md`
— both numba gathers derive the y/x kernel shifts from the transposed kernel
axes, harmless for square kernels but wrong for non-square odd PSFs.
