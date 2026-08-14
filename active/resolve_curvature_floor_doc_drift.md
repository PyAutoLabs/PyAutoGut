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
