# Profile validation: restore search and results compatibility

Type: bug
Target: PyAutoGalaxy
Repos:
- PyAutoGalaxy
- autogalaxy_workspace
- autolens_workspace
- autogalaxy_workspace_test
- autolens_workspace_test
Difficulty: medium
Autonomy: human-required
Priority: urgent

## Original request (verbatim)

> Can we target making heart red

Clarified after assessing a full joint-prior redesign:

> Just do 1 i agree 2 is too much

## Problem

The profile-constructor validation guards shipped in PyAutoGalaxy now raise raw
`ValueError` for unphysical sampled parameters. PyAutoFit search fitness treats
`FitException` as a rejected sample, so the raw exception aborts release and
workspace validation. Separately, component-wise posterior summaries can combine
valid marginal values into a non-physical profile instance, and several regression
fixtures deliberately use invalid all-ones vectors.

Heart's exact RED reason is `release validation FAILED (stage integrate)` in
PyAutoHeart Actions run 31354307923. The same regression contributes most of the
45 workspace-validation failures.

## Scope

- Preserve direct constructor validation as `ValueError` for user mistakes while
  making invalid fit samples rejectable as `FitException`.
- Keep current priors and scientific parameter support unchanged.
- Update results tutorials where marginal/error vectors are statistical values,
  not guaranteed-valid physical profile instances.
- Replace deliberately invalid aggregator fixture components with valid values.
- Redesign the intentional NaN regression so injection happens downstream of
  constructor validation.
- Verify the PyAutoGalaxy guard contract, the previously failed script set,
  workspace validation, release integration, and Heart readiness.

## Out of scope

- A joint unit-disk prior or axis-ratio/position-angle reparameterization.
- Global catching of arbitrary `ValueError` in PyAutoFit.
- Artificially narrowing each ellipticity component's prior bounds.
- Tenant-firewall drift unrelated to this profile-validation regression.
