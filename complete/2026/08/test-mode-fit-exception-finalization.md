## test-mode-fit-exception-finalization
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1462
- completed: 2026-08-10
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1463
- merge-commit: `18aae0f32d59dcc9221d5e218310948849b02e44`
- summary: `PYAUTO_TEST_MODE=1` no longer finalizes a model point whose reconstruction raises `FitException`; it substitutes bounded deterministic representative samples that are all validated before result creation and chaining.
- safety: normal searches and non-`FitException` failures are unchanged, and an impossible model fails clearly after a bounded 100 attempts instead of hanging.
- root-cause: the newer physical profile constructor guard correctly exposed invalid samples that previously passed silently, while reduced Nautilus mode stopped after one rejected evaluation and rebuilt that rejected point during finalization.
- validation: focused regression 4 passed; surrounding search tests 32 passed; full PyAutoFit suite 1707 passed / 2 skipped; GitHub docs, Python 3.12, and Python 3.13 checks all passed.
- downstream: no public symbol migration or workspace edit required; no live release was performed.

## Original prompt

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
