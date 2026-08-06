- issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/555 (auto-closed by the merge via "Closes #555")
- completed: 2026-08-06
- pr: https://github.com/PyAutoLabs/PyAutoGalaxy/pull/557 (MERGED, merge 66fe21ca), `pending-release`
- notes: `EllProfile.transformed_from_reference_frame_grid_from` checked `startswith("Sph")` while its mirror checks `endswith("Sph")`; spherical profiles are suffix-named so the inverse transform's spherical branch never fired — numerically benign (angle=0 identity rotation) but asymmetric and wasted rotation work on the hot path. Fixed to `endswith("Sph")`. Stack-wide sweep confirmed the single occurrence. New regression test `test__sph_named_profile__both_transforms_use_translation_only_path` control-verified (fails unfixed, passes fixed); 1028 tests green at ship.
- known-residual: `IsothermalSphMLR` (name ends "MLR") is missed by BOTH name checks and takes the elliptical path — numerically correct, deliberately not fixed rather than inventing a new dispatch mechanism for one class. Flagged in the PR body.
- merge-context: merged 2026-08-06 ~20:30 UTC on explicit human authorization ("merge anything"), after the sibling-claim PR PyAutoGalaxy#558 (astropy-cap-bump) — the recorded parallel-override held, overlap nil (geometry_profiles.py + test vs pyproject.toml + cosmology docstrings). PR checks could not run (GitHub Actions major outage); merge evidence is the ship-time local test runs in the PR body.
- heart-context: shipped under the recorded human RED override ("do 1"); RED reason verbatim: "release validation FAILED (stage integrate)" — unrelated MGE interferometer singular-solve, fix e658f684 pending nightly verification.

## Original prompt

# The following line in @autogalaxy/profiles/geometry_profiles.py is probbaly a bug

Type: bug
Target: PyAutoGalaxy
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

The following line in @autogalaxy/profiles/geometry_profiles.py is probbaly a bug:

- if self.__class__.__name__.startswith("Sph"):

- Can you check you agree and apply a fix.

<!-- formalised retroactively by the Intake (Conception) Agent on 2026-07-08 -->
