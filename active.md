# Active Tasks

## transformed-message-factor-gradient-unpack
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1501 (issued 2026-08-19)
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

## point-source-dataset-cap-guard
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/710 (issued 2026-08-23)
- prompt: active/point_source_dataset_cap_guard.md
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/point-source-dataset-cap-guard
- branch: feature/point-source-dataset-cap-guard (both repos)
- session: cloud (claude.ai/code) — no local worktree; repos cloned into the session
- classification: both (PyAutoLens primary, autolens_workspace_test follows)
- DIAGNOSIS SETTLED 2026-08-23, in-session, against libraries 2026.8.23.1 + PyAutoLens main:
  - `should_simulate('dataset/point_source/simple')` returns True and rmtree's the committed
    JSON dataset under `PYAUTO_SMALL_DATASETS=1`; returns False and leaves it intact with the
    cap unset. Direct A/B, not a run tally.
  - `PointSolver.solve` returns `[(1.0, 0.0), (0.0, 1.0)]` for every lens model under the cap
    (verified at einstein_radius 1.0/1.6/2.5) and is silent at DEBUG level.
  - `scripts/point_source/jax_likelihood/point.py` PASSES on current main under the correct
    profile: `-83.38049778` (pin exact) and `-82.33883111` (all-solved). The original report is
    explained; no library numerical bug exists.
- remaining scope is hardening only, NOT a bug hunt:
  1. `modeling_visualization_jit.py` declares `ENV: real_output`, which does not release the cap
     (missed by the autolens_workspace_test#264 sweep).
  2. The five point_source parity scripts have no pre-should_simulate cap guard.
  3. `PointSolver.solve`'s short-circuit warns nobody.
- repos:
  - PyAutoLens
  - autolens_workspace_test
