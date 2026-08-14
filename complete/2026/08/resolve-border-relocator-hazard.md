## resolve-border-relocator-hazard
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/117
- completed: 2026-08-14
- workspace-pr: https://github.com/PyAutoLabs/autolens_profiling/pull/118
- merge-commit: 1817052deeb14fa0f9d8172503d6e2219fc713d6
- summary: Reconciled the likelihood hazard instrument after the border-relocator source fix. The resolved backend-divergence record and plot are removed, while the stable finding ID remains gated at a 1e-8 relative tolerance so a regression reappears under the same identity.
- validation: GitHub Actions lint run 31758232026 succeeded; 30 local tests passed; ruff, scoped format, compile, the four-finding NumPy/JAX scan, README, and smoke checks passed; no review threads.
- evidence: deterministic border PCA leaves the full NumPy/JAX likelihood below the parity threshold; the refreshed active-set scan contains five bounded transitions and the conditioning conclusion is unchanged.
- release: not performed; the merged workspace PR remains in the pending-release queue.

## Original prompt

# Resolve the border-relocator backend hazard after the source fix

Type: maintenance
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: small
Autonomy: supervised
Priority: high
Status: issued
Source: PyAutoArray#446 · autolens_profiling finding `likelihood.imaging-pixelization.positive-solver-backend-divergence`

PyAutoArray#446 restored NumPy/JAX likelihood parity for the degenerate border
PCA. The profiling check still emits the finding unconditionally and therefore
cannot record that the hazard has been fixed.

Add a pure scale-free persistence predicate over the full-likelihood backend
error curves and emit the stable finding only when any reconstruction or
figure-of-merit error exceeds the tested parity tolerance. Preserve the finding
ID so a later regression returns under the same identity.

Run the full NumPy/JAX scan against the merged behavior, remove the resolved
record and plot, regenerate the hazard index, and prove the scan reports no new
IDs. Do not change PyAutoArray, solver settings, or geometry behavior.

