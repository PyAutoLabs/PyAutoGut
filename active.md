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

## local-pixel-scale-vs-dataset-pixel-scales
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/501
- issued: 2026-08-24
- prompt: active/script_local_pixel_scale_vs_dataset_pixel_scales.md
- status: workspace-dev
- worktree: none — web-github session, clone at /home/user/autolens_workspace (no local worktree root exists; do not treat as a deleted worktree on resume)
- repos:
  - autolens_workspace (claude/autolens-pixel-scale-script-3wx8m6)
- summary: |
    Sweep fix: 8 workspace scripts let a module-level pixel_scale literal escape its
    from_fits argument into geometry, luminosity (/ pixel_scale**2) and Hilbert-mesh
    arithmetic that also reads the loaded dataset. Under PYAUTO_SMALL_DATASETS=1 the
    literal and dataset.pixel_scales diverge (0.05/0.1 vs 0.6) and the arithmetic is
    silently wrong — multi_galaxy/features/scaling_relation/slam builds an empty mask
    and dies in ConvolverState. Fix is one rebind per file,
    pixel_scale = float(dataset.pixel_scales[0]) after the load, matching the idiom
    already at group/features/scaling_relation/modeling_for_luminosities.py:88.
- branch-note: |
    Branch is claude/autolens-pixel-scale-script-3wx8m6, mandated by the session, not
    the usual feature/<task-name>.
- verification-outstanding: |
    The capped run (PYAUTO_TEST_MODE=2 PYAUTO_SMALL_DATASETS=1) CANNOT be executed in
    this session — no numpy, no autolens. It must run before merge; the bug is
    invisible in an uncapped run because the two values coincide. Clear both
    output/<path> and output/test_mode/<path> first or the run fakes green as
    "Fit Already Completed".
    multi_galaxy/features/scaling_relation/slam stays parked in no_run.yaml with its
    NEEDS_FIX reason rewritten; un-park only if that capped run exits 0 (PR#312
    un-parked group/slam on an assumed fix and cost a full cycle).
