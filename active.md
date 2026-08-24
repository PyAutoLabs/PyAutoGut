# Active Tasks

## script-timing-baselines-fix
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/165
- issued: 2026-08-24
- status: library-dev
- prompt: active/script_timing_baselines_orphaned_and_window_filled.md
- repos:
  - PyAutoHeart: claude/test-performance-dashboard-y3fdy7
- summary: |
    Phase 0 of the test-performance board arc: run-identity dedup (the real
    cause of the one-value-repeated-7x windows), >=3-distinct-run
    classification floor, rename-aware slug migration with loud orphan
    counts, per-duration run provenance. Cloud session, no local worktree.

## smoke-timings-dataset
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/264
- issued: 2026-08-24
- status: library-dev
- prompt: active/smoke_timings_dataset.md
- repos:
  - PyAutoHands: claude/test-performance-dashboard-y3fdy7
  - PyAutoHeart: claude/smoke-timings-artifact-y3fdy7
- summary: |
    Phase 2 of the test-performance board arc: the delegated runner emits
    smoke_timings.json + a step-summary timing table for every gate run
    (one change, ten repos inherit); Heart's reusable smoke-tests.yml
    uploads the report dir as a run artifact. Answers item 4 of
    draft/research/ci/smoke_timing_and_profiling.md with yes. Cloud
    session, no local worktree.

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
