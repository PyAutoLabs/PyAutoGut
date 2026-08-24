# script_timing baselines made real — run-identity dedup + rename-aware slugs

PyAutoHeart#166 → `ee915f3`, closing PyAutoHeart#165, merged 2026-08-24 on
branch `claude/test-performance-dashboard-y3fdy7` (restarted from main after
the phase-1 board merge). Phase 0 of the test-performance board arc
(`complete/2026/08/test-performance-board.md`) — the per-script trend surface
reads what this fixes.

## What shipped

- **The "every history is one value repeated 7×" defect was not seeding — it
  was re-ingestion.** `run()` re-read `run_logs/latest` on every tick and
  re-appended the same observation until the window filled with copies of one
  run. History entries now carry `{duration_s, run_id, ts}` (run_id = the
  resolved timestamped run dir behind the `latest` symlink); a re-tick on the
  same run replaces the newest entry, so windows only grow across distinct
  runs. Legacy bare-float histories still read; a legacy window of
  all-identical values collapses to the single observation it provably was.
- **Classification floor**: the yellow/red ratio fires only against ≥3
  distinct-run samples (`MIN_BASELINE_RUNS`); below that a script counts as
  `building_count` instead of being judged against a fake-stable median.
  `red/yellow/green_count` keep their exact meaning; `dashboard.py` untouched.
- **Rename-aware slugs, loud orphans**: history files untouched by a scan are
  orphans; a new slug with no history adopts an orphan on an unambiguous
  (workspace, script-name) match — the #216 restructure scenario now heals
  itself (`migrated_count`). Ambiguous/unmatched orphans are reported
  (`orphaned_count`), never deleted, never silent.
- Histories written via `atomic_write_json` (was a bare `write_text`).
- Tests 573 → 583; `test_script_timing.py` 6 → 16.

## Key traps / findings

- **Four existing tests had encoded the bug itself** — they re-ran `run()` on
  the same results dir as a stand-in for repeated runs, which is exactly the
  defect. When a test suite's fixture shape mirrors a bug, the tests pass for
  the wrong reason; the fixtures now create one dir per run.
- **Legacy empty run_ids each count as a distinct run** in the floor — history
  that predates provenance is real accumulation once the identical-window
  collapse has run; treating it as one run would have zeroed every surviving
  baseline.
- Orphan reporting is scan-relative: pointing Heart at a partial results dir
  surfaces other workspaces' histories as "orphaned" (reporting only —
  migration matching is workspace-scoped, so nothing can be misattached).

## Follow-ups

- `unit_test_timing` / `workspace_testmode_timing` keep their own history
  mechanics — if they share the re-ingestion pattern, the same dedup applies;
  not audited here (out of the prompt's scope).

## Original prompt

# Heart script_timing baselines are orphaned by path moves and filled with one repeated value

Type: bug
Target: PyAutoHeart
Repos:
- PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: medium
Status: formalised
Filed: 2026-08-04 (backfilled from git)
Issued: 2026-08-24

Two independent defects in `PyAutoHeart/heart/checks/script_timing.py`, both found
while diagnosing the jax_grad smoke timeouts (PyAutoHands#226). Neither is fixed by
that task — it needed the baselines and found them unusable.

## 1. Slugs are path-derived, so any script move orphans its history

`slug_for()` (`heart/checks/script_timing.py:59`) builds the history filename from the
script's full workspace-relative path:

```
autolens_test__scripts__jax_grad__imaging_lp.json
```

The autolens_workspace_test #216 restructure moved `scripts/jax_grad/imaging_lp.py` to
`scripts/imaging/jax_grad/lp.py`. The slug changed with it, so:

- every pre-restructure baseline is stranded under a filename nothing writes to again,
- no new-layout slug exists for ANY of these scripts, so Heart has been accumulating
  **no** timing history for them since 2026-07-24,
- the regression check silently has nothing to compare against — it does not report
  "no baseline", it just never fires.

Verify: `ls ~/.pyauto-heart/timings/ | grep jax_grad` returns only old-layout names;
`grep -E "imaging__jax_grad|point_source__jax_grad"` returns nothing.

The docstring already anticipates collisions ("so scripts in nested subdirs do not
collide on a shared leaf name") but not moves. A rename-aware scheme, or at minimum a
loud "no baseline for this slug" signal, would have surfaced this immediately.

## 2. Every history is one value repeated 7 times

Every file in `~/.pyauto-heart/timings/` holds the same number `baseline_window` (7)
times:

```
autolens_test__scripts__jax_grad__imaging_lp.json => [45.99, 45.99, 45.99, 45.99, 45.99, 45.99, 45.99]
autolens_test__scripts__jax_grad__point_source.json => [39.24, 39.24, 39.24, 39.24, 39.24, 39.24, 39.24]
```

`update_history()` appends one duration per call and truncates to the window, so seven
identical values means the window was seeded/filled from a single observation rather
than accumulated across seven runs.

Consequence: `classify()` compares the latest duration against
`median(rolling_window)`, and a median over seven copies of one number IS that number.
So the yellow/red ratio is a **single-observation comparison** wearing the clothes of a
7-run median — it will read as stable regardless of real variance, and one unlucky run
becomes a "regression".

## Why it matters

These two combine badly. #226 needed exactly this data to answer "real slowdown, or a
cap that never fitted?" and could not: the only stored baseline for
`point_source/jax_grad/gradient.py` (39.24s) was both orphaned by the move AND a
single observation — and it turned out to describe a script that had since grown ~8x
by design. The diagnosis had to be rebuilt from CI job logs by hand.

## Suggested scope

- Decide the slug policy (rename-aware, or accept moves but emit a loud no-baseline
  signal instead of silently skipping).
- Fix history accumulation so a window of 7 means 7 distinct runs; do not seed a
  window by repetition.
- Consider recording the source run id alongside each duration so a baseline is
  traceable to the run that produced it.

<!-- Split out of PyAutoHands#226 (jax_grad smoke timeouts) on 2026-08-04; that task
     deliberately did not absorb these. -->
