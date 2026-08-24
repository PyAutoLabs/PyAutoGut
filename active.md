# Active Tasks

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

## smoke-runner-delegation
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/260 (issued 2026-08-24)
- issued: 2026-08-24
- prompt: active/run_smoke_copy_drift.md
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/smoke-runner-delegation
- decision: the prompt's blocking question is ANSWERED before any repo is touched —
  the timeout/kill behaviour was PROMOTED to everyone (PyAutoHands#226/#227 → 52408a84;
  all 10 copies import timeout_for + kill_group). Shape chosen: full delegation to a
  PyAutoHands-owned runner, staged. Phase 1 = --list allowlist mode + the 4 *_workspace_test
  copies; phase 2 = notebook leg + the 3 workspace copies; phase 3 = HowTo, no work.
- measured: 2026-08-24, from every repo's main — 10 copies, 3 variants, ZERO functional
  drift inside any variant (workspace 356L byte-identical; workspace_test 198L comment-only;
  HowTo 75L differ by PROJECT alone). Prompt steps 1 and 4 verified already done.
- registered: 2026-08-24 by the start_dev session (claude/smoke-copy-drift-ci-docs-ozntvv);
  worktree_check_conflict clean (exit 0) for all 8 repos.
- repos:
