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

## tracer-fits-existence-guard
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/503 (issued 2026-08-24)
- issued: 2026-08-24
- prompt: active/bug_fix_the_tracer_fits_existence_guard.md
- status: awaiting-merge
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/504 (pending-release)
- question: https://github.com/PyAutoLabs/autolens_workspace/issues/503#issuecomment-5402138356 (answered: human typed /prm = ship as-is + close out)
- worktree: ~/Code/PyAutoLabs-wt/tracer-fits-existence-guard
- environment: web-github (cloud session; no local worktree — operates on the session clone,
  branch claude/tracer-fits-existence-guard-zihsnn)
- autonomy: --auto launch; header safe, bug cap supervised -> effective supervised. Plan written
  to the issue; ship sign-off parks for a human (checkpoint 2 -> the question above).
- progress: fix implemented + verified and pushed to branch claude/tracer-fits-existence-guard-zihsnn
  on autolens_workspace (scripts/imaging/modeling.py, scripts/multi_galaxy/modeling.py).
  Notebooks regenerated (0c14d00). PR #504 open; /prm watching CI to merge + close out.
- repos:
  - autolens_workspace: claude/tracer-fits-existence-guard-zihsnn
