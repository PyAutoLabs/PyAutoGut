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

## imaging-ci-heritage-sweep
- issue: https://github.com/PyAutoLabs/autocti_workspace_test/issues/19
- issued: 2026-08-24
- prompt: active/imaging_ci_heritage_sweep.md
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/imaging-ci-heritage-sweep
- repos:
  - autocti_workspace_test: feature/imaging-ci-heritage-sweep
- summary: |
    DECISION task, not a foregone move (the prompt is explicit about this). Top-level
    `imaging_ci/` in autocti_workspace_test behaves like the `legacy/` tree beside it
    — undocumented, unexercised, unmaintained since 2023, 13 files on the removed
    plotter-object API — but sits outside it, so an API-drift sweep reads it as live
    breakage. Split out of aplt-output-drift-remaining-repos (PyAutoGalaxy#585).
    Three options on the table: (1) git mv into legacy/, (2) condemn via the Gut,
    (3) keep and modernise (would be a dev task, not maintenance). `profiling/`
    (17 files) and `temporal/` are NOT among the 13 broken and need the same
    decision on their own evidence, not by association.
    Evidence re-derivation must precede the choice; check against the CTI
    resurrection epic (PyAutoCTI#82) for anything slated for modernisation.
    Planned in a web-github session — the worktree above does not exist yet.
