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
