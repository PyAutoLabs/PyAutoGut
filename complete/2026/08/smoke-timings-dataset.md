# Per-script smoke timings are a standing dataset — one runner change, ten repos inherit

PyAutoHands#265 → `d2a22f4` (closing PyAutoHands#264) + PyAutoHeart#167 →
`3df42b5`, merged 2026-08-24. Phase 2 of the test-performance board arc
(`complete/2026/08/test-performance-board.md`); answers item 4 of
`draft/research/ci/smoke_timing_and_profiling.md` — "should the runner record
per-script timings routinely?" — with **yes, shipped**. The smoke-runner
delegation (#260–#263) is what made this one change instead of ten repo
sweeps.

## What shipped

- **`smoke_timings.json`** (schema `smoke_timings/1`) emitted from
  `RunReport.write()` — one call site covers `run_python.py`, `run.py` and
  `generate.py`, so every delegated gate inherits it with zero per-repo
  edits. Per entry: `{entry, kind, status, seconds, cap_s, exit_code}` —
  `seconds` is the runner's own measured duration (the number the
  `[PASS] — <n>s` line prints), TIMEOUT entries carry the cap they hit,
  skips are `seconds: null`, never a fabricated 0. One merged file per
  report directory, rows keyed on entry path (script + notebook legs both
  survive; a re-run replaces its own rows; `legs` records contributors).
- **Step summary**: with `$GITHUB_STEP_SUMMARY` set, a slowest-first timing
  table per leg — every gate run's timings one click away, no artifact
  download.
- **`ScriptResult` gained `cap_seconds`/`exit_code`** at all 8 execution
  sites — deliberately absent from `to_dict()` so the per-run JSONs Heart's
  `script_timing`/`test_run` and `aggregate_results` read stay
  byte-compatible (pinned by a test); `aggregate_results` skips the sidecar
  by name so the mega-run surface stays clean.
- **PyAutoHeart `smoke-tests.yml`** uploads the report dir as
  `smoke-timings-<python-version>` (`if: always()`,
  `if-no-files-found: ignore`, no `retention-days` — full default artifact
  retention). The path is a glob (`test-results/` + `**/smoke_timings.json`)
  because the reusable workflow never passes `--report-dir` — each
  workspace's `run_smoke.py` does.
- Drive-by fix: `run.py` never passed `env_profile`, so every notebook
  report claimed `unknown` — threaded through, negative-tested.
- Tests: PyAutoHands 363 → 382 passed (14 pre-existing environmental
  failures unchanged — missing `ipynb-py-convert`/`pngquant` locally,
  identical set on main); PyAutoHeart 573 → 576.

## Key traps / findings

- **The notebook report leg is `run.py`, not `run_notebook.py`** — the
  latter is the single-notebook kernel-cwd shim `build_util` shells out to
  and has no report path. Emit from `RunReport.write()` and every leg is
  covered.
- **A fixed per-leg filename would clobber across directories in the
  mega-run** — one report dir hosts many `(project, directory, run_type)`
  invocations; hence the merged file keyed on entry path. Known limit: two
  workspaces sharing a relative path in one mega-run dir collapse to one
  row (documented in the docstring; that dir is not a consumer).
- **Keep new fields out of `to_dict()` until every consumer is audited** —
  the per-run JSON shape is load-bearing for three downstream readers;
  extending the dataclass without extending the serialization is the
  compatible move, pinned by a byte-compat test.
- `aggregate_results` globs `**/*.json` — any new sidecar in the report dir
  becomes a phantom run unless excluded by name.

## Follow-ups

- The Heart board ingesting these artifacts into per-script rows with
  STALL/SLOW verdicts (reuse `retime.py`'s vocabulary; bimodality
  first-class) once a few weeks of data exist — the deferred phase 3 named
  in the board record.

## Original prompt

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
