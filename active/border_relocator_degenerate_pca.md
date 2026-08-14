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
