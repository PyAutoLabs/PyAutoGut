# imaging/subhalo_recovery.py exceeds the 300s smoke cap but carries no SLOW marker

Type: maintenance
Target: autolens_workspace_test
Repos:
- @autolens_workspace_test
Difficulty: small
Autonomy: supervised
Priority: low
Status: draft

## Finding (2026-07-28, smoke run for PyAutoFit#1414)

`autolens_workspace_test/scripts/imaging/subhalo_recovery.py` fails every smoke
run with exit 124 — the harness's 300s per-script timeout — while being listed
in `smoke_tests.txt` and **not** marked in `config/build/no_run.yaml`.

Baselined on unmodified `main`, sequential and unloaded, under the smoke profile
env (`PYAUTO_TEST_MODE=2`, `PYAUTO_SKIP_FIT_OUTPUT=1`, `PYAUTO_SKIP_VISUALIZATION=1`,
`PYAUTO_SKIP_CHECKS=1`, `PYAUTO_DISABLE_JAX=1`):

    real  8m25.673s   exit 0

So the script is **not broken** — it passes, at ~505s, roughly 1.7x the cap. Its
interferometer sibling (`interferometer/subhalo_recovery_interferometer.py`)
passes inside the cap, so the cost is specific to the imaging variant (the run
masks 5835 image-pixels, far more than the other smoke scripts).

Every smoke run therefore reports a failure that is really a budget overrun,
which dilutes the signal — a real regression in this script would look identical
to the status quo.

## Task

Decide and implement one of:

1. Make the script cheap enough to finish inside 300s under the smoke profile
   (smaller mask / fewer subhalo grid points in test mode) — preferred, keeps
   the coverage.
2. Add it to `config/build/no_run.yaml` with the
   `# SLOW <YYYY-MM-DD> - <reason>` marker convention so the mega-run surfaces
   it deliberately instead of failing it silently every time.

Option 1 is the better outcome: the script exercises subhalo recovery end-to-end,
which nothing else in the smoke set covers.

## Notes

- Do not simply raise the cap — 300s is the harness-wide budget and other
  workspaces depend on it.
