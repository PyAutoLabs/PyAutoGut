# Per-script smoke timings as a standing dataset — one runner change, ten repos inherit

Type: feature
Target: pyautohands
Repos:
- @PyAutoHands
- @PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

Phase 2 of the test-performance board
([`../../../docs/pyautoheart/test_performance_board_assessment.md`](../docs/pyautoheart/test_performance_board_assessment.md);
phase 1 shipped 2026-08-24 as PyAutoHeart#164 + PyAutoBrain#261). Today the
smoke runner's per-entry timings exist only as `[PASS] <name> — <n>s` lines in
job logs, recovered by hand-scraping; the 2026-08-23 slow-vs-stall audit and
the jax_grad budget work both had to rebuild their datasets that way. Since
the smoke-runner delegation (PyAutoHands#260–#263) all ten workspace runners
are thin shims over `autohands/run_python.py` — **so recording per-script
timings routinely is now one PyAutoHands change, not ten repo sweeps.** This
answers item 4 of `draft/research/ci/smoke_timing_and_profiling.md`
("should the runner record per-script timings routinely?") with yes.

## Task

1. **PyAutoHands** — the report machinery (`result_collector.RunReport`,
   already mandatory in the PR gate via `--report-dir`) additionally emits a
   consolidated `smoke_timings.json` in the report dir: one entry per
   script/notebook — `{entry, kind, status, seconds, cap_s (the cap in force
   from build_util.timeout_for), exit_code}` — plus run metadata (project,
   env profile, python version). When `$GITHUB_STEP_SUMMARY` is set, append a
   compact per-entry timing table (slowest first) so every smoke run's
   timings are one click away in the Actions UI with no artifact download.
2. **PyAutoHeart** — the reusable `smoke-tests.yml` uploads the report dir as
   a run artifact (`smoke-timings-<python-version>`, `if: always()`,
   `if-no-files-found: ignore`), so the dataset persists the full artifact
   retention window for every gate run across all ten repos at once.
3. Timing must come from the runner's own measurement (the same clock the
   `[PASS] — <n>s` line prints), never re-derived; a TIMEOUT entry records
   the cap it hit.

## Acceptance

- A PR-gate smoke run on any workspace produces `smoke_timings.json` with one
  timed entry per executed script/notebook and a step-summary table, with no
  per-repo changes.
- TIMEOUT entries carry `cap_s`; skipped entries are absent or explicitly
  marked, never silently timed as 0.
- Existing report consumers (`run_all.py`, Heart `test_run`/`script_timing`)
  are unaffected.

Follow-up (not this task): the Heart board ingesting these artifacts into
per-script rows with STALL/SLOW verdicts (reuse `retime.py`'s vocabulary)
once a few weeks of data exist.
