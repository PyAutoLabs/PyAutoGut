# Fix the test-mode representative-sample fallback for multi-analysis models

Type: bug
Target: health_fixes
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

## Context

The nightly release has been blocked at Stage 3 (release-fidelity integration) since
2026-08-10. On the night of **2026-08-11** the dominant cause is a single new
regression: **17 scripts** fail with

```
AttributeError: 'ModelInstance' object has no attribute 'galaxies'
AttributeError: 'ModelInstance' object has no attribute 'centre'   # autofit cookbook
```

Evidence: PyAutoHeart integrate run
[31456732688](https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/31456732688),
driven by nightly run
[31456340441](https://github.com/PyAutoLabs/PyAutoBrain/actions/runs/31456340441).
Four jobs failed; every failing script in three of them carries this one error.

Owners: @PyAutoFit (fix locus), @autolens_workspace, @autogalaxy_workspace,
@autofit_workspace (affected surface).

## The regression is pinned to one PR

The two nightly rehearsals bracket it exactly. Only **PyAutoFit** and **PyAutoGalaxy**
moved between them; PyAutoNerves, PyAutoArray and PyAutoLens were byte-identical.

| Night | PyAutoFit rehearsal SHA | This error |
|---|---|---|
| 2026-08-10 | `fbe9f45deac2f8f4646d61bdf5f4cb75ac950e30` | absent (0 scripts) |
| 2026-08-11 | `18aae0f32d59dcc9221d5e218310948849b02e44` | present (17 scripts) |

That window contains exactly two commits — one logical change:
**PyAutoFit PR [#1463](https://github.com/PyAutoLabs/PyAutoFit/pull/1463)**
("fix: handle rejected final samples in test mode 1", squash `41b0eadc`, merged
`18aae0f3` at 2026-08-11T02:56Z — **49 minutes before the nightly ran**). It closes
PyAutoFit issue #1462, whose completion record is the current HEAD of PyAutoMind
(`188c1e3`).

## Mechanism

#1463 added to `autofit/non_linear/search/abstract_search.py::start_resume_fit`:

```python
samples_summary = samples.summary()

if mode == 1:
    try:
        samples_summary.instance
    except exc.FitException as error:
        samples = self._test_mode_samples_after_rejected_fit(model=model, error=error)
        samples_summary = samples.summary()
```

`_test_mode_samples_after_rejected_fit` discards the real samples and rebuilds a
`SamplesPDF` from prior medians (then seeded prior draws) via `_build_fake_samples`.
For a **multi-analysis / multi-dataset** model the replacement instance does not
expose the per-analysis attributes (`.galaxies`, `.centre`) that
`analysis.make_result` and every downstream workspace script read, so result
construction dies with `AttributeError` instead of the intended graceful fallback.

Two things make this specifically a multi-dataset fault: every failing script is under
`scripts/multi_dataset/` (plus autofit `cookbooks/multiple_datasets.py`), and
`autolens_test/multi_dataset` — a different script set against the same libraries —
**passed**.

It is release-only visible because the fallback is gated on `PYAUTO_TEST_MODE=1`,
which is the release/smoke profile; ordinary source-profile CI never enters the branch.

## Failing scripts (18 total, 17 of them this error)

`integrate / run_scripts (3.12, autolens, multi_dataset)` — 9 of 18:

- `scripts/multi_dataset/start_here.py`
- `scripts/multi_dataset/modeling.py`
- `scripts/multi_dataset/features/dataset_offsets/modeling.py`
- `scripts/multi_dataset/features/imaging_and_interferometer/modeling.py`
- `scripts/multi_dataset/features/imaging_and_point_source/modeling.py`
- `scripts/multi_dataset/features/pixelization/modeling.py`
- `scripts/multi_dataset/features/same_wavelength/modeling.py`
- `scripts/multi_dataset/features/slam/simultaneous.py`
- `scripts/multi_dataset/features/wavelength_dependence/modeling.py`

`integrate / run_scripts (3.12, autogalaxy, multi_dataset)` — 7 of 14:

- `scripts/multi_dataset/start_here.py`
- `scripts/multi_dataset/modeling.py`
- `scripts/multi_dataset/features/dataset_offsets/modeling.py`
- `scripts/multi_dataset/features/imaging_and_interferometer/modeling.py`
- `scripts/multi_dataset/features/pixelization/modeling.py`
- `scripts/multi_dataset/features/same_wavelength/modeling.py`
- `scripts/multi_dataset/features/wavelength_dependence/modeling.py`

`integrate / run_scripts (3.12, autofit, cookbooks)` — 1 of 11:

- `scripts/cookbooks/multiple_datasets.py` (`'ModelInstance' object has no attribute 'centre'`)

The 18th failure is a different defect — see
[profile_validation_aggregator_reconstruction.md](profile_validation_aggregator_reconstruction.md).

## Why the tests did not catch it

`test_autofit/non_linear/search/test_abstract_search.py::TestReducedModeRejectedFinalSample`
exercises only a **single flat model** — `af.Model(cls)` with one `UniformPrior` on
`value`. There is no `af.Collection`, no `AnalysisFactor`, and no combined/multi-analysis
case anywhere in the new coverage, which is precisely the shape that breaks. Any fix
must close that gap, not just the symptom.

## Required work

1. Reproduce under the release profile with `PYAUTO_TEST_MODE=1` on a multi-dataset
   model — `autolens_workspace/scripts/multi_dataset/start_here.py` is the cheapest
   entry point. Confirm the fallback branch is entered before changing anything.
2. Establish *why* `samples_summary.instance` raises `FitException` for these models in
   the first place. If the real samples are in fact reconstructable, the eager
   `try: samples_summary.instance` probe is itself the defect and the fallback should
   never fire here.
3. Fix in **PyAutoFit**. The replacement samples must be built against the same model
   structure as the original fit, so the resulting instance keeps its per-analysis
   children. Do not special-case `.galaxies`/`.centre` — the fallback must be
   structure-preserving for any model, or it must decline to fire and let the original
   error surface.
4. Extend `TestReducedModeRejectedFinalSample` to cover an `af.Collection` /
   multi-analysis model. That test is the regression gate.
5. Do **not** park these scripts in `no_run.yaml` and do not edit the workspace scripts
   to work around it — they are user-facing documentation, and parking would hide a
   live library regression behind a green release run (see this folder's 2026-08-09
   sweep note, point 3).
6. Re-run Stage 3 and confirm all 17 clear.

## Note on rollback

If a correct fix is not quick, reverting #1463 restores a known-good Stage 3 for this
error class and re-opens PyAutoFit #1462 — the condition #1463 addressed only affects
reduced test-mode fits whose final sample is rejected, which is a narrower blast radius
than 17 broken multi-dataset scripts. Weigh that against the fix before spending a
third blocked night.

<!-- filed by the Bug Agent (health-issue mode) on 2026-08-11 from nightly run 31456340441 -->
