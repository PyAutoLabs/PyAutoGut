Made Heart's workspace-validation reporting honest: a summary may only carry
counts somebody measured, and a failing cloud run now names its failing scripts.

- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/119 (auto-closed)
- pr: PyAutoHeart#120 (`0a9fc045f`) — merged unchanged (tree diff 0 vs reviewed
  head `fe93a68`); CI green both Python legs
- the bug (CI/release audit 2026-07-30, finding B): `test_run.py` took `ready`
  from the cloud run *conclusion* but counts from a local
  `run_logs/latest/report.json` that does not exist for cloud runs → zeros
  printed as fact ("0 failed, cloud#30516167217" while the run had
  2 failed + 1 timeout).
- fix: explicit `counts_measured` flag honored by readiness, dashboard, and the
  check's own CLI line (legacy cloud-shaped sidecars detected as unmeasured);
  new `_cloud_report()` fetches the run's `workspace-validation-report`
  artifact — cached per run id via the persisted sidecar (one download per new
  validation run, not per 30 s tick); compact `failing_scripts` (never
  tracebacks) carried into the reason:
  `workspace validation not passing (2 failed, 1 timeout, cloud#…: autogalaxy
  scripts/interferometer/start_here.py, …)`.
- boundary preserved: `run()` stays no-network/side-effect-free (fetcher
  injected only by the tick entrypoint — the PyAutoHeart#83 discipline).
- trap: bare `pyauto-heart readiness` serves the persisted `release_ready.json`
  (last daemon tick) — live-compute via `--profile release-ci` or
  `readiness.run()`; the cached verdict refreshes on the first tick after merge.
- suite 316 passed (13 new tests).

## Original prompt

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
