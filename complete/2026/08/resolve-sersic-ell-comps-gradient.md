## resolve-sersic-ell-comps-gradient
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/123
- completed: 2026-08-14
- workspace-pr: https://github.com/PyAutoLabs/autolens_profiling/pull/124
- merge-commit: 27bdb8b0c5cbf35852c1e22e9bbcbea0324e437b
- source-fix: https://github.com/PyAutoLabs/PyAutoGalaxy/pull/571
- summary: Reconciled the numerical-hazard evidence after the Sersic Cartesian-radius fix. The stable conditional detector remains for regression detection; the resolved record, plot, semantic-index entry, and generated README row were removed.
- validation: GitHub Actions lint run 31761926948 succeeded across ruff lint/format, README idempotence, 38 tests, links, and all section smoke tests; the full NumPy/JAX likelihood scan and repeat check found two persistent likelihood findings, zero new IDs, and no Sersic origin finding; no reviews or review threads.
- evidence: the origin likelihood remained -15.477240141252718 and its JAX gradient is finite at [1.1569945714414, -0.5449763942867472]; the semantic index now contains seven persistent findings.
- release: not performed; the merged workspace PR remains in the pending-release queue.

## Original prompt

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
