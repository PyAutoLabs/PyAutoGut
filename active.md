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

## pynufft-removal-residue-phase-1
- issue: https://github.com/PyAutoLabs/autolens_workspace_developer/issues/128
- issued: 2026-08-23
- session: claude --resume session_01JEXzQpvG3QNUdTh6tZcaAE
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/pynufft-removal-residue-phase-1
- prompt: active/pynufft_removal_downstream_residue_phase_1_developer_break.md
- repos:
  - autolens_workspace_developer: feature/pynufft-removal-residue-phase-1
- summary: |
    Phase 1 of 3 cleaning up residue the pynufft removal (@PyAutoArray#475,
    @PyAutoGalaxy#583, @PyAutoLens#709) left behind. That work's "workspace tier"
    was scoped to autolens_workspace + autolens_workspace_test only and never
    swept the sibling repos.
    THE BREAK (repro'd on clean main 2026-08-23):
    `jax_profiling/dataset_setup/interferometer.py:140` still names the deleted
    `al.TransformerNUFFTPyNUFFT`. The dict at :137 is built EAGERLY inside
    `simulate()` (:106), so EVERY instrument raises AttributeError — not just the
    `alma_high_res` config at :76 that selects it. Confirmed via `simulate('sma')`,
    a DFT dataset, which still fails. All jax_profiling dataset setup is broken.
    This is the ONLY executable reference to the deleted class in any repo.
    FIX: drop the "nufft_pynufft" dict arm; repoint alma_high_res to "nufft"
    (nufftax-backed TransformerNUFFT), NOT dft — its ~20GB dense-matrix OOM is
    real (5000 vis x 512x512 = 1.31e9, far above the ~1e7 crossover). The
    comment's other objection ("nufftax needs >=3.12, venv is 3.10") is OBSOLETE:
    the whole stack floors requires-python >=3.12 and nufftax 0.6.1 needs >=3.11.
    VERIFY across EVERY instrument key — the eager dict means a one-instrument
    check would not prove the fix.
    Phases 2 (autogalaxy_workspace + both assistants, prose) and 3 (Hands/Heart CI
    + PyAutoCTI install doc) stay in draft/maintenance/workspaces/, independent —
    no library API change, so no library-first gate.
    Next: /start_workspace → worktree + branch feature/pynufft-removal-residue.
- also-pending: close out draft/bug/autoarray/pynufft_scipy_pinv2_dev_extra.md
  (Status: superseded; its acceptance is met — the removal PRs merged).

## pynufft-removal-residue-phase-2
- issue: https://github.com/PyAutoLabs/autogalaxy_workspace/issues/224
- issued: 2026-08-23
- session: claude --resume session_01JEXzQpvG3QNUdTh6tZcaAE
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/pynufft-removal-residue-phase-2
- prompt: active/pynufft_removal_downstream_residue_phase_2_workspace_assistant_docs.md
- repos:
  - autogalaxy_workspace: feature/pynufft-removal-residue-phase-2
  - autogalaxy_assistant: feature/pynufft-removal-residue-phase-2
  - autolens_assistant: feature/pynufft-removal-residue-phase-2
- summary: |
    Phase 2 of 3. Prose-only: autogalaxy_workspace (the sibling of the repo fixed
    by @autolens_workspace#497, never swept) plus both science assistants still
    document the deleted `TransformerNUFFTPyNUFFT` as an available "non-JAX
    fallback". Zero executable refs — the one live ref was phase 1 (#128).
    Edit scripts/ ONLY in autogalaxy_workspace; notebooks/ and markdown/ are
    GENERATED (generate.py autogalaxy, and a SEPARATE generate_markdown.py).
    Mirror the #497 wording, adapting "strong lens" -> "galaxy". Assistant wiki
    BODY edits need --write-provenance. paper/ dirs stay untouched (JOSS records).
- also: phase 1 (#128) implemented on feature/pynufft-removal-residue-phase-1,
  2 commits, not yet PR'd. Phase 3 (Hands/Heart CI + PyAutoCTI doc) still draft.

