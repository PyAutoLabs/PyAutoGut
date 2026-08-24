# Active Tasks

## test-performance-board
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/163
- issued: 2026-08-24
- status: library-dev
- prompt: active/test_performance_board.md
- repos:
  - PyAutoHeart: claude/test-performance-dashboard-y3fdy7
  - PyAutoBrain: claude/test-performance-dashboard-y3fdy7
- summary: |
    Phase 1 of the test-performance board (assessment:
    docs/pyautoheart/test_performance_board_assessment.md). Heart grows two
    cloud-safe checks (ci_timing Actions scrape + no_run_census), two dashboard
    sections and an additive `performance` block in board.json; the Brain board
    consumes it verbatim as a ⏱ Test performance section. Advisory only —
    readiness untouched. Developed in a cloud session (no local worktree);
    Mind-side changes ride the same branch. Phase 0 (script_timing baselines
    bug prompt) and phase 2 (per-script smoke_timings.json in PyAutoHands)
    are separate follow-ups.

## transformed-message-factor-gradient-unpack
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1501 (issued 2026-08-19)
- issued: 2026-08-19
- prompt: active/16_transformed_message_factor_gradient_unpack.md
- status: HOLD — do not start dev. Fix-or-delete hangs off the PyAutoFit#1498 logpdf-contract
  decision (parked #1500 design bundle); dead code (zero production callers), crashes on first
  call if ever exercised.
- external: community PR https://github.com/PyAutoLabs/PyAutoFit/pull/1502 (@trexfr-ops) targets
  this exact unpack — review via /community before any local work; the #1498 adjudication decides
  whether the method should exist at all.
- registered: 2026-08-19 by the wake_up session — the issuing session (claude/autofit-priors-messages-audit-ylvenv)
  filed the prompt + issue but not this entry, tripping Lifecycle Drift on main.
- repos-none-claimed: this entry claims NO repos — one line deliberately, not 2-space bullets.
