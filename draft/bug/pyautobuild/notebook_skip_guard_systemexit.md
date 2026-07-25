> **RESOLVED 2026-07-25 — implemented as PyAutoHands#198 commit f924785
> (merged).** Runner-side `is_clean_skip_exit` classifier in the authoritative
> executor (`build_util.execute_notebook`): ANSI-aware, last CellExecutionError
> line must be exactly `SystemExit: 0` → PASS; nonzero/real errors stay FAIL.
> 9 tests + live blackjax-absent check. Remaining: per-repo adoption of the 9
> drifted run_smoke.py copies — tracked in
> draft/maintenance/ci/run_smoke_copy_drift.md (rollout in progress).

# sys.exit(0) skip-guards fail in generated notebooks (SystemExit -> cell error)

Type: bug
Target: pyautobuild
Repos:
- @PyAutoHands
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

## Finding (2026-07-25 full health sweep)

The workspace convention for optional-dependency skip guards is:

    if importlib.util.find_spec("<optional-dep>") is None:
        print("Skipping ...")
        sys.exit(0)

This works for `.py` scripts (clean exit 0) but BREAKS in the generated
notebooks: under Jupyter/nbclient, `sys.exit(0)` raises `SystemExit` in the
kernel, the cell errors, and the notebook run exits non-zero. Observed on
`autofit_workspace` `searches/mcmc.ipynb` on a box without `blackjax`:
stdout shows the intended "Skipping BlackJAXNUTS example ..." message followed
by `SystemExit: 0` and `[FAIL (exit 1)]`.

CI never sees this because its matrices install the optional deps, so the
guard branch never executes there. Any user running a generated notebook
without the optional extras hits a spurious failure.

## Task

Decide and implement a notebook-safe skip idiom, e.g.:
- PyAutoHands generation rewrites `sys.exit(0)` guards into a notebook-safe
  form (e.g. raising `KeyboardInterrupt`-free early-stop via wrapping the rest
  in the conditional), or
- the smoke notebook runner treats `SystemExit: 0` as success, or
- the guard convention changes to an `if/else` structure that both forms
  execute correctly.

Audit all `find_spec` + `sys.exit(0)` guards across the workspaces once the
idiom is chosen (autogalaxy_workspace interferometer/start_here.py,
autolens_workspace interferometer/modeling.py, autofit_workspace
searches/mcmc.py at minimum).

## Acceptance

A generated notebook whose optional dep is absent skips green (runner PASS),
and the script form still exits 0.
