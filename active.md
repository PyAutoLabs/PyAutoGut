# Active Tasks

## phase5-smoke-ordered-trap-scripts
- issue: https://github.com/PyAutoLabs/autocti_workspace/issues/27
- issued: 2026-08-24
- prompt: active/phase5_smoke_reenable_ordered_trap_scripts.md
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/phase5-smoke-ordered-trap-scripts
- repos:
  - autocti_workspace: feature/phase5-smoke-ordered-trap-scripts
- summary: |
    CTI epic Phase 5. PR autocti_workspace#28 open, CI running. The prompt's
    premise was wrong: autocti_workspace has no smoke_tests.txt and never had one
    (no .github/, no config/build/, nothing deleted in history), so this creates
    the repo's first CI rather than re-enabling anything — which also closes
    pre-existing drift, since PyAutoHeart/config/repos.yaml already lists this
    repo under `workspaces` with required checks "Smoke Tests" + "Navigator
    Check". All nine modeling/start_here.py-class scripts verified running
    bypassed against PyAutoFit 438f56fac; a curated three promoted (132s cold)
    rather than all nine (~522s), per the repos' no-mass-promote convention.
    Navigator Check deliberately left out of scope.

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
