# scaling_relation scripts fail under the smoke/test-mode profile with misleading errors

Type: bug
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft
Found-during: scaling-relation-brightest-galaxy (#407 / PR#416, merged 2026-07-30) — surfaced while
verifying that rename; neither failure is caused by it, and both predate it.

## Summary

Three `features/scaling_relation` scripts fail when run under the automated-run env profile
(`config/build/profile_smoke.yaml`). None of them is a science bug — all pass in a normal
environment. In each case a *degraded-profile* knob silently produces garbage inputs, and the script
then dies with an error that points somewhere other than the real cause. None of the three is in
`smoke_tests.txt` or `no_run.yaml`, so nothing catches them today.

## Part A — `scaling_relation/slam.py`: measured luminosities are 0.0, giving `0.0 / 0.0` = NaN

**Affected** (verified failing):
- `scripts/imaging/features/scaling_relation/slam.py`
- `scripts/multi_galaxy/features/scaling_relation/slam.py`

**Not affected** (verified passing, rc=0): `scripts/interferometer/features/scaling_relation/slam.py`.
The distinguishing factor is how the luminosity is obtained — interferometer hardcodes
`luminosity_anchor = 31.0962`, while imaging and multi_galaxy *measure* it from a preceding light
stage. That measurement is what breaks.

**Mechanism.** Under `PYAUTO_TEST_MODE` the light stage produces no usable samples, so the script
prints:

    Measured main lens luminosities: [np.float64(0.0), np.float64(0.0)]

The scaling relation then evaluates `einstein_radius_brightest * (0.0 / 0.0) ** 0.5` → **NaN**, which
propagates into the model and explodes far from its origin. The symptom depends on the mode:

- `PYAUTO_TEST_MODE=2` (the profile default, skip sampler) —
  `IndexError: index -9223372036854775808 is out of bounds for axis 0 with size 785`
  in `PyAutoArray/autoarray/inversion/mappers/mapper_util.py:73`
  (`adaptive_pixel_signals_from`), reached via adapt-regularization in `source_pix_2`.
  `-9223372036854775808` is `INT_MIN` — a NaN cast to int.
- `PYAUTO_TEST_MODE=1` (reduced iterations) —
  `ValueError: cannot convert float NaN to integer`
  in `PyAutoFit/autofit/mapper/identifier.py:142`, while hashing the search paths identifier.

Neither traceback mentions luminosity, the scaling relation, or test mode.

**Reproduce:**

    python3 <runner> autolens_workspace multi_galaxy/features/scaling_relation/slam.py
    # profile_smoke.yaml defaults; or override PYAUTO_TEST_MODE=1 for the second symptom

**Fix options** (needs a judgment call, hence not fixed inline):
1. `no_run.yaml` entries for the two scripts — consistent with the existing
   `mass_stellar_dark/slam` precedent. Cheapest, but hides them from automated runs entirely.
2. `# ENV: real_search` declarations (unsets `PYAUTO_TEST_MODE`) — keeps them covered, but means a
   real SLaM run per script, which is likely well past the timeout cap. Measure before choosing.
3. Independently of 1/2: make the relation **fail fast and honestly** when a measured luminosity is
   non-positive — "measured luminosity for lens_N is 0.0; the light stage produced no usable
   samples" beats an INT_MIN IndexError three libraries deep. Note this is *not* a silent
   None-guard: the script should still crash, just at the right place with the right message.

## Part B — `point_source/features/scaling_relation/fit.py`: 15×15 grid cap breaks the solver, and the assertion blames the dataset

**Verified passing** in a normal environment (rc=0): 4 multiple images, per-image shifts
`182 / 398 / 1596 / 1633` mas.

**Verified failing** under `profile_smoke.yaml`, whose `PYAUTO_SMALL_DATASETS: "1"` caps grids and
masks to 15×15. At that resolution `PointSolver` returns only **2** images, at the suspiciously round
`Grid2DIrregular([[1., 0.], [0., 1.]])`, identically with and without the tier — so the measured
shift is `0` mas and the script's own assertion fires:

    AssertionError: The tier should move every image by far more than the astrometric precision;
    if it does not, the dataset has drifted from the configuration this example describes.

That message is actively misleading: **the dataset has not drifted**. The grid was capped, and the
solver silently returned a degenerate result rather than reporting that it could not resolve the
images.

**Verified fix.** Adding an `# ENV: full_datasets` declaration (unsets `PYAUTO_SMALL_DATASETS`) makes
it pass under the smoke profile — confirmed by building the smoke env, popping
`PYAUTO_SMALL_DATASETS`, and re-running: rc=0, 4 images, shifts `182 / 398 / 1596 / 1633` mas.
This is the same escape hatch the profile's own comments describe for `*/start_here` and `guides/`.

Worth considering separately: a solver that returns 2 round-numbered points instead of signalling
failure is a trap for any script that trusts its output. That part belongs upstream in PyAutoLens if
it is judged real — this prompt only covers the workspace-side declaration.

## Acceptance

- `imaging` and `multi_galaxy` `scaling_relation/slam.py` either run clean under automated runs or
  are declared skipped with a reason that names the 0/0 luminosity cause.
- `point_source/features/scaling_relation/fit.py` passes under `profile_smoke.yaml`.
- `interferometer/features/scaling_relation/slam.py` still passes (it does today — do not regress it
  while touching the siblings).
- If a fail-fast guard is added, it crashes with a message naming the zero luminosity — it does not
  silently substitute a default.
