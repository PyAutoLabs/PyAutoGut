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

## pynufft-removal-residue-phase-3
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/258 (issued 2026-08-23)
- issued: 2026-08-23
- prompt: active/pynufft_removal_downstream_residue_phase_3_ci_install_docs.md
- status: workspace-dev — CI recipes + one install doc; NO PyAuto* library source, so no
  library-first merge gate. Phase 3 of 3; phases 1-2 shipped 2026-08-23.
- session: mobile/web session (no local checkout, no worktree) — branches pushed from fresh
  clones via the GitHub API.
- branch: feature/pynufft-removal-phase-3 (same name in all three repos)
- repos:
  - PyAutoHands (primary — release.yml, 3 sites)
  - PyAutoHeart (workspace-validation.yml, 1 site)
  - PyAutoCTI (docs/installation/source.rst, 1 line)
- heart-ack: RED "release validation FAILED" — pre-existing and unrelated to this task;
  acknowledged by the human at launch, PR-open authorized, merge stays a human act.
- verification-caveat: every changed line is on a RELEASE path (release.yml is
  workflow_dispatch-only; Heart's line is in the mode=release step), so ordinary PR CI cannot
  exercise them. Full green lands on the next release rehearsal / nightly run.
