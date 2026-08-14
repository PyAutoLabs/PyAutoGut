## border-relocator-degenerate-pca
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/445
- completed: 2026-08-14
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/446
- merge-commit: 394514c09e4fc9fc774e9346e9119f7bb01203e2
- summary: Stabilized near-isotropic border PCA axes with a deterministic axis-aligned branch at a scale-aware eigenvalue-gap tolerance. Worst-point curvature parity returned to 1.583e-16 with identical likelihood and support; NNLS behavior is unchanged.
- validation: GitHub Actions run 31757530171 succeeded on Python 3.12 and 3.13 with coverage uploads; two focused tests, direct JAX jit/vmap, and downstream full-likelihood parity passed; no review threads.
- api-changes: none
- release: not performed; the merged PR remains in the pending-release queue.
- follow-up: autolens_profiling#117 reconciles the resolved semantic finding.

## Original prompt

# Stabilize border relocation for degenerate PCA axes

Type: bug
Target: PyAutoArray
Repos:
- PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: high
Status: issued
Source: autolens_profiling#115 · finding `likelihood.imaging-pixelization.positive-solver-backend-divergence`

A full likelihood reproducer proved NumPy and JAX construct identical traced
source grids, but `ellipse_params_via_border_pca_from` receives a near-isotropic
border covariance whose eigenvectors are mathematically non-unique. Backend
eigensolvers choose different valid axes; deriving max extents along those axes
then creates a 28.35% relocated-grid difference and a 0.899% reconstruction
difference.

Compute the covariance eigenvalue gap relative to its scale. When the gap is no
larger than `sqrt(machine epsilon)`, select a deterministic axis-aligned frame
before deriving ellipse extents. Retain the PCA major axis for non-degenerate
covariance.

Add NumPy unit tests for the degenerate and anisotropic cases. Validate the JAX
`xp` path with the downstream full-likelihood reproducer: worst-point matrix
and vector differences should return to floating-point noise, likelihoods and
supports must agree, and no solver settings may change.

Do not add configuration or public API, and do not change NNLS behavior.
