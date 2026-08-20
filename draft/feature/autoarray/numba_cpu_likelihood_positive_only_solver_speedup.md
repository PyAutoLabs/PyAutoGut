# Numba CPU likelihood: positive-only solver speed-up (the Delaunay 60-78% lever)

Type: feature
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: large
Autonomy: supervised
Priority: high
Status: formalised

> The Delaunay-fiducial sibling of the CPU-likelihood speed programme
> (autolens_profiling#151 profiling; Rectangular kernel-CDF prompt is phase 2,
> deferred). Supersedes the "restore the solver deleted in `8bb449a1`" idea —
> see the corrected diagnosis below.

## Context (profiling + instrumented probe, 2026-08-20)

On the campaign fiducial — Delaunay + Hilbert(1500) AdaptImage mesh +
ConstantSplit, MGE-60 linear lens light, numba CPU sparse-operator route
(`apply_sparse_operator_cpu()` + `use_jax=False`) — the reconstruction solve
dominates the likelihood at **both** resolutions, and is **parameter-bound**
(same cost at euclid 3841 and hst 15361 masked pixels; 1560 params = 1500 mesh
+ 60 MGE):

- euclid: solve 3.73 s of a 4.6 s eval (~78%) [8-core box]
- hst: solve 4.23 s of a 6.97 s eval (~60%) [4-core container, ~1.2x slower]

**Corrected diagnosis.** The earlier hypothesis that the fast numba fnnls +
Cholesky solver was deleted in PyAutoArray `8bb449a1` (2025-06-18) is wrong for
the shipping code: `autoarray/util/fnnls.py` and `autoarray/util/
cholesky_funcs.py` are present and are the live path in autoarray 2026.8.20.1.
With the config defaults (`use_positive_only_solver: true`,
`use_edge_zeroed_pixels: true` — the edge-zeroed subset is a no-op for this
fiducial, 1560/1560 kept since `Delaunay(zeroed_pixels=0)`), the numpy branch of
`inversion_util.reconstruction_positive_only_from` runs `fnnls_cholesky` with a
dense-solve warm start.

**Instrumented probe** (euclid fiducial, single-thread BLAS, 4-core container;
`fnnls_cholesky` total 5.06 s, agrees bitwise with production):

| piece | time |
|---|---|
| warm-start `np.linalg.solve` (n=1560, 1411 positives) | 0.10 s |
| initial `slg.cholesky` of warm passive set | 0.06 s |
| `cholinsertlast`/`choldeleteindexes` up/down-dates | **3.58 s** |
| `cho_solve` calls | 0.99 s |
| `w = ZTx - ZTZ @ d` matvecs | 0.26 s |
| iterations: 154 outer (Bro–Jong adds ONE index each) + 102 constraint-fix | |
| reference: ONE from-scratch `slg.cholesky` at n=1560 | **0.081 s** |

So ~70% of the solve is the up/down-dating machinery, and the reason is
implementation, not linear algebra: `cholinsertlast` and `choldeleteindexes`
(`autoarray/util/cholesky_funcs.py`) rebuild the full ~1400x1400 factor with
`np.insert`/`np.delete` — two O(n^2) allocations+copies per active-set change,
~154 sequential single-index changes per likelihood call ≈ gigabytes of memcpy.
The numba-jitted Givens kernels themselves are fine.

## Goal

Make `reconstruction_positive_only_from` (numpy branch) several times faster at
n≈1500 without changing the solution (bitwise where feasible, else within the
1e-6 rtol the profiling pins use). Candidate directions, roughly in order of
expected win/effort:

1. **In-place factor buffer** — preallocate U at n_max once per solve; grow
   (`cholinsertlast`) by writing the new column into the buffer view and shrink
   (delete) in place, eliminating every `np.insert`/`np.delete` copy. Pure
   implementation change, exactly the same iterates.
2. **Block pivoting** — replace one-index-per-iteration Bro–Jong with a block
   active-set method (add all `w > tol` violators at once, refactorize from
   scratch at 81 ms/factorization, e.g. block principal pivoting / TNT-NN).
   ~150 iterations → a handful of factorizations; changes the iterate path but
   converges to the same KKT point.
3. **Cross-evaluation warm starts** — within a sampler worker, successive
   likelihood calls have similar active sets; carrying the previous call's
   passive set as `P_initial` (already a supported argument) could cut the
   ~150 adds to a few. Needs a place to thread per-worker state through
   `Inversion` construction, so scope carefully.
4. **BLAS-thread guidance only** (no code): the solve is single-thread BLAS
   under the workspace `OMP_NUM_THREADS=1` convention; measure whether 2-4
   BLAS threads help the dense pieces once 1-2 land, and record the guidance
   in autolens_profiling.

Acceptance: euclid + hst `delaunay_numba` runtime/breakdown cells in
@autolens_profiling re-run with the pinned log-likelihoods passing and the
solve step materially reduced; the fnnls unit surface in PyAutoArray keeps its
existing tests green (plus new ones for the in-place/block paths).

## Verification instrument

`autolens_profiling` branch `feature/numba-cpu-likelihood-profiling` (PR #152):
`scripts/imaging/likelihood_runtime/delaunay_numba.py` and
`scripts/imaging/likelihood_breakdown/delaunay_numba.py` carry pinned
log-likelihoods (euclid 7193.174444838345, hst 29110.92075682961, rtol 1e-6,
hardware-independent — verified across two machines).
