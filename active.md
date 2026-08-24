# Active Tasks

## testmode-assertion-note-removal
- issue: https://github.com/PyAutoLabs/autocti_workspace/issues/24
- issued: 2026-08-24
- prompt: active/testmode_assertion_workaround_note_removal.md
- status: workspace-shipped, awaiting-merge
- workspace-pr: https://github.com/PyAutoLabs/autocti_workspace/pull/25
- workspace-pr: https://github.com/PyAutoLabs/autocti_workspace_test/pull/17
- workspace-pr: https://github.com/PyAutoLabs/autocti_assistant/pull/21
- environment: web-github (no local worktree; PyAutoBrain/skills/WORKFLOW.md)
- repos:
  - autocti_workspace: feature/testmode-assertion-note-removal
  - autocti_workspace_test: feature/testmode-assertion-note-removal
  - autocti_assistant: feature/testmode-assertion-note-removal
- summary: |
    Follow-up to test-mode-bypass-assertion-ties (PyAutoFit#1520, merged 438f56fac).
    Three repos documented the now-fixed bypass crash as a live artifact. Deleted
    per the testmode-env-drift precedent rather than updated. Sites found and fixed:
    autocti_workspace/AGENTS.md (standalone paragraph, deleted); autocti_workspace_test
    /AGENTS.md (the claim was a RATIONALE for the single-trap convention — dropped the
    rationale, kept the convention, flagged the constraint as revisitable since its
    stated reason is gone); autocti_assistant/skills/ac_fit_cti_model.md (artifact
    sentence removed; .claude/skills/ copy is a symlink so one edit covered both).
    Verified: grep for assertion/prior-median claims across all three returns only
    legitimate API examples. Docs-only, no scripts or smoke_tests.txt touched.
    Merge is human; next step /prm once reviewed.

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
