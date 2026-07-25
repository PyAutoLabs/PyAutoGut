# compute_latent_samples crashes on a resumed completed fit (samples is None)

Type: bug
Target: autofit
Repos:
- @PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: low
Status: draft

## Finding (2026-07-25 full health sweep)

Running `autolens_workspace_test` `misc/latent/latent_variables_smoke.py` (and
`latent_nan_robustness.py`) twice in the same output tree fails on the second
run: the search resumes ("Fit Already Completed: skipping non-linear search"),
`result.samples` comes back `None` on the resume path (PYAUTO_TEST_MODE=2
bypass), and

    autofit/non_linear/analysis/latent.py:113  latent_samples_from
    -> samples.model  ->  AttributeError: 'NoneType' object has no attribute 'model'

A fresh run (output cleared) passes. So the latent pipeline works, but the
resume/load path hands `compute_latent_samples` a `None` samples object
instead of the persisted samples (or a clear error).

## Task

Determine whether the resume path should (a) reload persisted samples so
latent computation works on resumed results, or (b) raise a clear, guarded
error from `compute_latent_samples` when samples are unavailable. May be
test-mode-specific — check whether a real (non-bypass) resumed fit also
returns samples=None.

## Acceptance

Second invocation of the latent smoke scripts in an existing output tree
either computes latent samples or fails with an intentional, documented
message — never an AttributeError from inside latent_samples_from.
