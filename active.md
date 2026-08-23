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

## mask1d-shape-native-scalar-widening
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/484
- issued: 2026-08-23
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/mask1d-shape-native-scalar-widening
- prompt: active/scalar_widening_residual_sites.md
- repos:
  - PyAutoArray: feature/mask1d-shape-native-scalar-widening
- summary: |
    Residual sites the PyAutoArray#464 scalar-widening sweep (`8298d74e`, 2026-08-22)
    did not reach. Two live, both repro'd on main:
      1. `Mask1D.__init__` (mask_1d.py:71) hand-rolls `type(x) is float` and never routes
         through `convert_pixel_scales_1d` — `pixel_scales=1` stores a bare `1` and
         `.geometry.scaled_maxima` raises `TypeError: 'int' object is not subscriptable`.
         `Mask2D.__init__` already routes through the chokepoint (mask_2d.py:218), so this
         is a 1D/2D divergence.
      2. `convert_shape_native_1d` (geometry_util.py:27) keeps `type(x) is int` —
         `Array1D.full(shape_native=np.int32(5))` raises
         `IndexError: invalid index to scalar variable`.
    Site 1 brings `validate_pixel_scales` to `Mask1D`, so it starts rejecting 0/-1/nan —
    a real contract change; read any suite failure rather than adjusting the test.
    Out of scope, unfiled: tuple entries returned unnormalised, `(1, 1)` staying ints.
    The originating prompt shipped as #464 and is recorded at
    complete/2026/08/autoarray-pixel-scales-scalar-widening.md (backfilled — it sat in
    draft/ while the work shipped).
    Next: /start_library → worktree + branch, then the two source edits and their tests.
