# Test-performance section on the Heart board — run times, hangs, NO_RUN, with one-tap fix prompts

Type: feature
Target: pyautoheart
Repos:
- @PyAutoHeart
- @PyAutoHands
- @PyAutoBrain
Difficulty: large
Autonomy: supervised
Priority: high
Status: formalised
Filed: 2026-08-24

Development speed tracks test speed, and today knowing what is slow takes a
manual archaeology session over CI job logs. Build the standing surface: a
**⏱ Performance section on the Heart board** that always shows the run times
of the testing/integration infrastructure — PR smoke gates (`*_workspace_test`,
normal workspaces, HowTo), unit-test gates, weekly `workspace-smoke`, the
nightly release driver, import time — with enough history to flag drops,
kill-timer/hang events surfaced, the NO_RUN census with reasons, and a one-tap
Claude prompt on every row so "speed this up" is a paste.

Full design rationale, data-plane analysis, chip payloads, and the trap list:
[`docs/pyautoheart/test_performance_board_assessment.md`](../../../docs/pyautoheart/test_performance_board_assessment.md).
Read it before starting — it cites the mechanisms (kill timer, no_run tiers,
board contracts, Actions API fields) with receipts.

## Shape (from the assessment)

- **Ownership**: Heart measures and publishes ("measurement lives in Heart");
  rows land in the Heart's `board.json` (schema v2, additive `performance`
  block), each carrying its **own** prompt string; the Brain board renders a
  headline row consuming it verbatim — the exact `heart_blockers` contract.
  Advisory only: the GREEN/STALE/YELLOW/RED verdict is untouched.
- **Plane A (this task's core)**: scrape completed workflow runs of the
  tracked gates via the Actions API with the default `GITHUB_TOKEN`
  (production precedent: `PyAutoMind/.github/workflows/morning_health.yml`).
  Duration = `updated_at − run_started_at` (never `created_at`), queue delay,
  conclusion mix, per-job fanout only for runs worth the detail. Tracked
  `repo:workflow` list is declared config in `PyAutoHeart/config/repos.yaml`,
  never code (tenant firewall).
- **History**: per-gate daily aggregates via the self-carrying published
  artifact roll-forward (the Brain board's `updated_history`/`sparkline`
  pattern, 30-day cap); durable per-script baselines stay Heart's tracked
  legs (phase 0 below).
- **Kill-timer/hang rows**: per-script `TIMEOUT (<cap>s)` events; job-level
  `cancelled` disambiguated (≈`timeout-minutes` or no successor → kill/hang,
  red; superseded PR run → benign; `cancelled` on `main` → always red);
  missing `=== Smoke test summary ===` line → aborted run, coverage
  discarded. Coverage counts render beside every duration.
- **NO_RUN census**: parse each workspace's `config/build/no_run.yaml`;
  SLOW/NEEDS_FIX rows with marker age and reason, chips that say re-measure
  first ("a marker is a claim with a timestamp, not a fact"); flag entries
  whose reason carries no measurement and matchers matching zero files;
  untagged permanent skips are a collapsed count.

## Phasing

0. **Prerequisite, separate PR** — issue
   `draft/bug/pyautoheart/script_timing_baselines_orphaned_and_window_filled.md`
   (filed 2026-08-04, never issued): rename-aware slugs, real 7-run windows,
   run-id provenance. Plane C reads what it fixes.
1. **This task** — the Heart board section + `board.json` `performance` block
   (plane A + NO_RUN census + kill-timer rows + history/sparklines), and the
   Brain board headline row (can ride
   `draft/feature/pyautobrain/brain_board_follow_ups.md`).
2. **Follow-up, PyAutoHands** — per-script standing dataset: one change in
   the delegated runner (`autohands/run_python.py` report machinery) emits
   `smoke_timings.json` per gate run for all ten repos; the board ingests it
   and gains per-script rows with STALL/SLOW verdicts (reuse `retime.py`'s
   vocabulary; bimodality is first-class). This answers item 4 of
   `draft/research/ci/smoke_timing_and_profiling.md` with "yes".

Regression flagging reuses the profiling conductor's drift doctrine verbatim:
≥2.0× the pin AND ≥1.0s absolute, sticky pins, explicit re-pin. Comparability
key includes runner image × Python leg × event type.

## Acceptance

- The Heart board page shows, per tracked gate: latest duration, p50/max over
  the window, trend sparkline, conclusion mix, coverage count — refreshed on
  the Heart's existing render cadence with no commit noise.
- A hang/kill event (per-script TIMEOUT, unexplained `cancelled`, aborted
  summary) appears within one render, red, with a `/bug … — <run url>` chip.
- Every SLOW/NEEDS_FIX `no_run.yaml` entry is listed with marker age, reason,
  and a re-measure-first fix chip; unmeasured SLOW markers are visibly
  flagged.
- The Brain board carries the headline row consuming the published block
  verbatim.
- Nothing gates: readiness verdict and `badge.json` message shape unchanged.
