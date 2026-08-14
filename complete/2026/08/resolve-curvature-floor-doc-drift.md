## resolve-curvature-floor-doc-drift
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/119
- completed: 2026-08-14
- workspace-pr: https://github.com/PyAutoLabs/autolens_profiling/pull/120
- merge-commit: 0feb0beac55d53fe95ec8efa28d39518e1173d41
- summary: Reconciled the curvature-floor documentation finding after PyAutoArray#444. The detector now requires both runtime docstrings to name the live packaged default; the resolved record and plot are removed while the stable finding ID remains available for regression detection.
- validation: GitHub Actions lint run 31759122456 succeeded across lint, format, tests, README, links, and smoke; 35 local tests, compile, the three-finding NumPy/JAX scan, README, and smoke checks passed; no review threads.
- evidence: the helper and Settings docs both parse as 1.0e-3, matching live configuration; the remaining likelihood records are unchanged.
- release: not performed; the merged workspace PR remains in the pending-release queue.

## Original prompt

# Reconcile the curvature-floor documentation finding after the source fix

Type: maintenance
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: small
Autonomy: supervised
Priority: high
Status: issued
Source: PyAutoArray#444 · autolens_profiling finding `likelihood.imaging-pixelization.curvature-floor-doc-config-drift`

PyAutoArray#444 aligned both the curvature-diagonal helper and `Settings`
documentation with the packaged `1.0e-3` configuration default. The profiling
check still emits the finding unconditionally and therefore cannot record that
the documentation drift has been fixed.

Add a pure parser and persistence predicate that reads the two runtime
docstrings, requires both documented packaged defaults to agree with the live
configured value, and keeps the finding persistent when either value is
missing, stale, non-finite, or inconsistent. Preserve the stable finding ID so
future documentation drift returns under the same identity.

Regenerate the complete likelihood evidence against the merged PyAutoArray
documentation, remove the resolved record, and refresh the semantic index and
generated README table.

Do not change PyAutoArray, the configured floor, or numerical behavior.

