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
