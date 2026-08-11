# TEST_MODE=1 must not finalize rejected samples

Type: bug
Target: PyAutoFit
Repos:
- @PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: urgent

## Original request (verbatim)

> OK do this quickly then albeit why did it not cause issues before I guess the guard didn't exist so yeah FitException handling in test mode

## Problem

Fresh post-merge release validation run 31441556729 passed 660 scripts and all
TestPyPI install checks, but `autolens_workspace/scripts/imaging/features/extra_galaxies/slam.py`
failed when `PYAUTO_TEST_MODE=1` produced an unphysical `PowerLaw.ell_comps`
candidate. `ModelParameterException` is now correctly both `ValueError` and
`FitException`, so likelihood evaluation rejects the candidate, but the reduced
search subsequently attempts to materialize a rejected sample during
finalization/update and lets the exception escape.

## Goal

Make reduced real-sampler test mode honor `FitException` through the complete
search lifecycle. A rejected first or only candidate must be resampled or yield
a clear no-valid-sample outcome; it must never be reconstructed as a result.
Keep the fix generic to PyAutoFit and deterministic under test.

## Evidence

- Heart run: https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/31441556729
- Failure: `ell_comps=(-0.9257683911051445, -0.5502774378326348)`, magnitude `1.0769644249264025`.
- Release profile sets `PYAUTO_TEST_MODE=1`; `Nautilus.apply_test_mode()` sets `n_like_max=1`.
- The configured independent truncated-Gaussian ellipticity priors retain a small but non-zero invalid unit-disk tail, so rerunning may pass but cannot make the lifecycle bug safe.

## Constraints

- Do not redesign scientific priors or narrow workspace prior support.
- Do not catch arbitrary exceptions; preserve the existing `FitException` boundary.
- Add a deterministic regression covering an invalid first/only reduced-mode candidate.
- No live release; validate the focused path and the PyAutoFit test suite before shipping.
