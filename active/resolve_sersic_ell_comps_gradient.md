# Reconcile the resolved Sersic ell_comps gradient finding

Type: maintenance
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: small
Autonomy: supervised
Priority: high
Status: issued
Source: PyAutoGalaxy#571 · autolens_profiling finding `likelihood.imaging-sersic.ell-comps-origin-nonfinite-gradient`

PyAutoGalaxy#571 replaced the Sersic image path's singular Cartesian-to-polar ellipticity conversion with an algebraically equivalent Cartesian eccentric-radius calculation. The complete off-centre likelihood remains `-15.477240141252718` at `ell_comps=(0, 0)`, while the JAX gradient is now finite at `[1.1569945714414, -0.5449763942867472]`.

Make the stable detector conditional on the origin gradient still being non-finite while its bounded neighbourhood is finite. Retain the finding ID for regression detection, regenerate the complete NumPy/JAX evidence against the merged source fix, remove the resolved record and plot, and refresh the semantic index and generated README table.

Cover both persistence branches with pure synthetic unit tests. Do not change PyAutoGalaxy, priors, configuration, or numerical behavior. Label the profiling PR `pending-release` and merge it only after exact-head CI is green.
