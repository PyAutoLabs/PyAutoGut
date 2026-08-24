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

## smoke-surface-retime-sweep
- issue: https://github.com/PyAutoLabs/autolens_workspace_test/issues/274
- issued: 2026-08-24
- prompt: active/smoke_timing_and_profiling.md

## numba-kernel-shift-axes
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/486
- issued: 2026-08-24
- prompt: active/numba_kernel_shift_axes_swapped.md
- status: library-dev
- classification: library (PyAutoArray only)
- environment: web-github — session clone at /home/user/pyautoarray is the working tree;
  no `~/Code/PyAutoLabs-wt/` worktree exists or is claimed by this task.
- repos:
  - PyAutoArray: claude/numba-kernel-shift-axes-j5wo2p
- summary: |
    Both numba PSF gathers derive the kernel half-widths from the transposed kernel
    axes (y from shape[1], x from shape[0]) — silent wrong answer for non-square odd
    PSFs, invisible for square ones. Reproduced on main (9e47505): 3x5 kernel gives
    max|numba - numpy| = 1420.0, square control 0.0. Fixing both gather sites together
    plus the test helper that mirrors the same transposition.
