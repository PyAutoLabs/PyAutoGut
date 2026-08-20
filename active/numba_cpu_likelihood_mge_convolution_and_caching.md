# Numba CPU likelihood phase 1: MGE operated-matrix cross-eval memo (fixed-MGE campaigns)

Type: feature
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

> Phase 1 of the CPU-likelihood speed restoration
> (autolens_profiling#151 profiling; user request 2026-08-20 recorded verbatim
> in the phase-2 prompt `numba_cpu_likelihood_kernel_cdf_fast_path.md`).
> Exact-identical wins on files disjoint from phase 2's kernel-CDF work.

## Context (from the 2026-08-20 profiling + source hunt)

On the numba CPU sparse-operator likelihood (`apply_sparse_operator_cpu()` +
`use_jax=False`, MGE-60 linear lens light + rectangular pixelization —
the `cpu_fast_modeling.py` production route):

1. The 60 MGE linear-Gaussian operated images cost ~19% of a euclid evaluation
   (0.42 s of 2.15 s; 0.87 s at hst): `AbstractLinearObjFuncList.
   operated_mapping_matrix_override`
   (`PyAutoGalaxy autogalaxy/profiles/light/linear/abstract.py:319-382`) loops
   the Gaussians and calls `psf.convolved_image_from` **60 separate times**,
   each re-padding to fft_shape and re-transforming the PSF. A batched exact
   equivalent already exists and handles the blurring region:
   `Convolver.convolved_mapping_matrix_via_real_space_np_from`
   (`PyAutoArray autoarray/operators/convolver.py:1437`) — one scipy FFT
   convolution amortized over all 60 columns.
   `AbstractLinearObjFuncList.mapping_matrix` (`linear/abstract.py:291`)
   already produces the stacked unblurred matrix; only the blurring-grid stack
   is missing.
2. `linear_func_operated_mapping_matrix_dict`
   (`PyAutoArray autoarray/inversion/inversion/imaging/abstract.py:184`) is an
   **uncached `@property`** rebuilt on every access; the numba sparse inversion
   accesses it ~5 times per evaluation (`imaging_numba/sparse.py:194,419,443,
   451,509`), including inside an O(60^2) loop that also repeats a
   `(N_pix, 60)` noise-map division per pair. Cache it (`cached_property`,
   consistent with the inversion's per-evaluation lifetime) and hoist the
   noise division out of the pair loop.

## Scope narrowed (user direction, 2026-08-20)

Keep the change inside the numba inversion bit (`imaging_numba/sparse.py`),
minimal source interference, and active only when the MGE is *actually fixed*.
That rules the original item 1 (batched convolution in PyAutoGalaxy
`linear/abstract.py`) out of scope — DEFERRED, and largely mooted for
fixed-MGE campaigns by the memo below (the convolution runs once per worker).
Note the source-hunt's item 2 premise weakened on inspection: the override is
already a `cached_property` on the func object, so intra-eval rebuilds were
cheap; the real cost was fresh func objects re-paying the convolution stack
*every evaluation* even with identical parameters.

## Goal (as implemented)

`InversionImagingSparseNumba.linear_func_operated_mapping_matrix_dict`
overridden with (1) per-inversion `cached_property` and (2) a module-level
cross-evaluation memo keyed by sha256 of the linear func's full pickled state
(profiles + grids + PSF): fixed profiles fingerprint identically -> matrix
reused across evals; any free parameter changes the key -> recompute exactly
as before. Unpicklable objects fall back to the uncached path; failure modes
are misses, never stale hits; entries are read-only copies, bounded at 8;
`AUTOARRAY_NUMBA_OPERATED_MEMO=0` disables.

## Results (validated 2026-08-20, 4-core container, Delaunay-1250 fiducial)

- Euclid "MGE operated mapping matrix" step: 0.56 s -> 0.004 s on memo hits.
- Euclid steady-state eval: 2.34 s -> **1.34 s** (on top of the fnnls solver
  speed-up PyAutoArray#453; 4.92 s -> 1.34 s = 3.7x total today).
- Both autolens_profiling delaunay_numba pins PASS (rtol 1e-6);
  test_autoarray 1034 passed (+8 new memo tests).
