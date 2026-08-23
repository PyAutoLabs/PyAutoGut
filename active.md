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

## pynufft-removal-residue-phase-1
- issue: https://github.com/PyAutoLabs/autolens_workspace_developer/issues/128
- pr: https://github.com/PyAutoLabs/autolens_workspace_developer/pull/129 (open, pending-release)
- status-note: awaiting-merge — merge BLOCKED by Heart RED (see heart-ack); PR-open only.
- issued: 2026-08-23
- session: claude --resume session_01JEXzQpvG3QNUdTh6tZcaAE
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/pynufft-removal-residue-phase-1
- prompt: active/pynufft_removal_downstream_residue_phase_1_developer_break.md
- heart-ack: authorized 2026-08-23 by the human for push + PR-open only (merge stays blocked).
  Acknowledged RED reason list, verbatim from `pyauto-heart readiness --json`:
    - "release validation FAILED"
  Release run at ack time: v2026.8.23.1.dev73401, profile=release,
  2026-08-23T15:02:41Z, stages reported: integrate:pass. Unrelated to this task
  (docs//script-only). The ack covers THIS reason list only — any new RED reason
  re-blocks the gate.
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
- pr: https://github.com/PyAutoLabs/autogalaxy_workspace/pull/225 (autogalaxy_workspace)
- pr: https://github.com/PyAutoLabs/autogalaxy_assistant/pull/19 (autogalaxy_assistant)
- pr: https://github.com/PyAutoLabs/autolens_assistant/pull/115 (autolens_assistant)
- status-note: awaiting-merge — all three open + pending-release; merge BLOCKED by Heart RED.
- issued: 2026-08-23
- session: claude --resume session_01JEXzQpvG3QNUdTh6tZcaAE
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/pynufft-removal-residue-phase-2
- prompt: active/pynufft_removal_downstream_residue_phase_2_workspace_assistant_docs.md
- heart-ack: authorized 2026-08-23 by the human for push + PR-open only (merge stays blocked).
  Acknowledged RED reason list, verbatim from `pyauto-heart readiness --json`:
    - "release validation FAILED"
  Release run at ack time: v2026.8.23.1.dev73401, profile=release,
  2026-08-23T15:02:41Z, stages reported: integrate:pass. Unrelated to this task
  (docs//script-only). The ack covers THIS reason list only — any new RED reason
  re-blocks the gate.
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
