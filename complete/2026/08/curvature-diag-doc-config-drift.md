## curvature-diag-doc-config-drift
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/443
- completed: 2026-08-13
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/444
- merge-commit: 61844927ce4e6dd060847adb2cf925910f69e93a
- summary: Aligned PyAutoArray's curvature-diagonal helper and Settings docs with the packaged 1e-3 default; numerical behavior unchanged.
- validation: GitHub Actions run 31743635821 succeeded on Python 3.12 and 3.13; one-commit, two-file documentation-only diff; no review threads.
- api-changes: none
- release: not performed; PR remains part of the pending-release queue.

## Original prompt

# Align curvature-diagonal floor documentation with configuration

Type: bug
Target: autoarray
Repos:
- PyAutoArray
Difficulty: small
Autonomy: safe
Priority: normal
Status: issued
Source: autolens_profiling#110 · finding `likelihood.imaging-pixelization.curvature-floor-doc-config-drift`

The tier-2 likelihood hazard scan proved that
`curvature_matrix_with_added_to_diag_from` documents a fixed `1.0e-8`
diagonal addition while the packaged PyAutoArray configuration supplies
`1.0e-3` through
`Settings.no_regularization_add_to_curvature_diag_value`. The ratio is
`1e5`, and workspaces may override the packaged setting.

Correct the public-facing source documentation so it describes the value
actually passed by the caller, names the packaged `1.0e-3` default and the
workspace override seam, and documents the helper's currently omitted
parameters. Do not change the configured value or any numerical behavior.

Acceptance:
- No PyAutoArray source documentation claims that this helper always adds
  `1.0e-8`.
- The helper and Settings documentation agree with
  `autoarray/config/general.yaml`.
- The PyAutoArray test suite is green.
