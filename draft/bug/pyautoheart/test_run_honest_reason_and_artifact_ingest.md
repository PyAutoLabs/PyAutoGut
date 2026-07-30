# Heart test_run: never assert counts it didn't measure; name the failing scripts

Type: bug
Target: pyautoheart
Repos:
- PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft

## Symptom

Heart readiness reported `workspace validation not passing (0 failed, cloud#30516167217)`
while the referenced run had 2 failed + 1 timeout. Mechanics:
`heart/checks/test_run.py` takes `ready` from the cloud run *conclusion*
(`_cloud_verdict()`) but the counts from a local `run_logs/latest/report.json` that
does not exist for cloud runs — counts default to 0 and `heart/readiness.py:328`
prints them anyway. Dashboard shows the same contradiction (`NOT ready — 0p/0f/0s`).

## Scope

1. When the verdict comes from the cloud conclusion and no count evidence exists,
   the reason must say so: `workspace validation failing (cloud#<id>; counts not
   ingested — see run)` — never a fabricated `0 failed`.
2. Better: on a completed cloud run, fetch that run's `workspace-validation-report`
   artifact (single small JSON; `gh run download -n workspace-validation-report`)
   and surface real counts plus the top failing script names in the reason line.
   This kills the manual archaeology — a failed validation immediately names the
   scripts and links the run.
3. Keep `run()` side-effect-free / no-network for library callers (PyAutoHeart#83
   discipline); the artifact fetch belongs on the tick/CLI entrypoint next to the
   existing `gh run list` call, with the same never-raise contract.

## Evidence

- `heart/checks/test_run.py` lines ~226-248 (merge), `heart/readiness.py:319-346`.
- Run 30516167217's artifact carries exact per-script failures/tracebacks.
