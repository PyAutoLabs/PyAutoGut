# The test-performance board — the organism always knows what makes testing slow

PyAutoHeart#164 → `d8c125e` and PyAutoBrain#261 → `1b79bb3`, closing
PyAutoHeart#163, both merged 2026-08-24 on branch
`claude/test-performance-dashboard-y3fdy7`. Design record:
[`docs/pyautoheart/test_performance_board_assessment.md`](../../../docs/pyautoheart/test_performance_board_assessment.md)
— the deep-research pass that preceded the code, with receipts into the board
family, the kill-timer arc, the NO_RUN policy history and the Actions API.

The want: development speed tracks test speed, and knowing what is slow took a
manual archaeology session over CI job logs each time. The Heart board now
carries a standing **⏱ performance surface** — run times of the PR smoke gates,
unit-test gates, Workspace Smoke and Nightly Release, with history to flag
drops, kill-timer/hang events, and the NO_RUN census — every actionable row
carrying its own ready-to-paste `/bug` prompt. The Brain board renders the
headline verbatim. Advisory only: the readiness verdict and `badge.json` shape
are untouched.

## What shipped

- **`heart/checks/ci_timing.{sh,py}`** (cloud-safe, API-only, the `ci_status`
  shape): per polled repo, one `actions/runs?per_page=50` fetch — deliberately
  NO branch filter and NO `exclude_pull_requests`, because the
  contributor-facing number is what someone waits on before a merge. Durations
  from `run_started_at`→`updated_at`, success-only medians per tracked gate
  (the group's `required_workflows` + `performance.extra_workflows`), queue
  delay, conclusion mix. Cancelled runs disambiguated: superseded-by-a-newer
  same-branch PR run is benign; cancelled on main or successorless is a
  suspect hang event; `timed_out` always an event.
- **Self-carrying history**: the aggregate pass re-reads the previously
  published `board.json`, appends today's p50 per gate, dedupes by date, caps
  at 30 — no commits, idempotent per date; a publish gap costs a sparkline,
  never a render (the Brain board's `updated_history` trick, generalised).
- **`heart/checks/no_run_census.{sh,py}`**: contents-API census of every
  workspace's `config/build/no_run.yaml` — SLOW / NEEDS_FIX / permanent tiers
  with marker dates and reasons; SLOW rows whose reason carries no real
  seconds figure are flagged **unmeasured** (the 2026-08-23 audit's "a SLOW
  marker is not evidence of slowness" made this a first-class distinction);
  a missing file records `present: false` honestly.
- **`heart/dashboard.py`**: "CI wall-clock" and "NO_RUN census" sections
  (events → FAIL, drift → WARN, both advisory) and the additive `performance`
  block in `board.json` — the `blockers` contract extended to timings.
- **Drift thresholds** (`config/repos.yaml thresholds.ci_timing`): warn only
  when ratio ≥1.5 AND ≥120s absolute — the profiling conductor's
  both-gates doctrine, imported wholesale so the alarm never cries wolf.
- **PyAutoBrain `board/_board.py`**: one Heart `board.json` read now serves
  blockers and performance; the `⏱ Test performance` section renders flagged
  rows' prompts verbatim; hang events count as attention, never blocking.
- Both checks run in `heart-health.yml`'s daily cloud step — deliberately not
  the <30s tick (internals rule 3).
- Tests: Heart 573 (+73), Brain 447 (+5); stdlib+PyYAML, hermetic, fake names.

## Key traps / findings

- **The tenant firewall fired exactly as predicted.** Every board that shipped
  hit it, and so did this one: a real library repo name in the new
  `tests/test_ci_timing.py` (an "instance fact in a new file") reddened the
  first CI run; `LibA` serves. Budget for it in any organ-code PR that adds
  files.
- **A shallow `--depth 1` clone push looks unpushed.** The single-branch fetch
  refspec means `git push -u` succeeds but the local branch shows no upstream
  and no remote-tracking ref — `git ls-remote` proved the remote had the
  commit all along. Widen `remote.origin.fetch` before trusting `git status`
  on such clones.
- **Absent ≠ empty on the machine surface.** The `performance` block is
  omitted entirely when neither slice was observed — "not measured" must stay
  distinguishable from "measured, nothing there" (the hygiene
  `unscanned ≠ clean` invariant, applied to a board block). The Brain consumer
  renders no section and no degraded row for an absent block.
- **The measured-SLOW heuristic needs a cap guard.** "flakes at the 1800s cap"
  contains a seconds figure but is not a measurement; the regex refuses a
  seconds figure immediately followed by "cap".
- **`data-copy`/`data-cmd` attributes vs html self-containment tests**: prompt
  payloads legitimately embed URLs, so self-containment assertions must strip
  those attributes first — third board in a row to note it; it is in the
  assessment's caution list.

## Follow-ups (tracked, not started here)

- Phase 0 (prerequisite for per-script trends):
  `draft/bug/pyautoheart/script_timing_baselines_orphaned_and_window_filled.md`
  — still unissued.
- Phase 2: per-script `smoke_timings.json` from the delegated PyAutoHands
  runner (one change, ten repos inherit) — answers item 4 of
  `draft/research/ci/smoke_timing_and_profiling.md` with "yes".
- First `heart-health.yml` run seeds the history; sparklines are meaningful
  from ~day 3. If the run flags Pages enablement ("Resource not accessible by
  integration"), create the site once with
  `gh api -X POST repos/<owner>/PyAutoHeart/pages -f build_type=workflow`.
- Cloud session: no task worktree existed; the dev-box worktree survey has
  nothing to release.

## Original prompt

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
Issued: 2026-08-24

Development speed tracks test speed, and today knowing what is slow takes a
manual archaeology session over CI job logs. Build the standing surface: a
**⏱ Performance section on the Heart board** that always shows the run times
of the testing/integration infrastructure — PR smoke gates (`*_workspace_test`,
normal workspaces, HowTo), unit-test gates, weekly `workspace-smoke`, the
nightly release driver, import time — with enough history to flag drops,
kill-timer/hang events surfaced, the NO_RUN census with reasons, and a one-tap
Claude prompt on every row so "speed this up" is a paste.

Full design rationale, data-plane analysis, chip payloads, and the trap list:
[`docs/pyautoheart/test_performance_board_assessment.md`](../docs/pyautoheart/test_performance_board_assessment.md).
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
