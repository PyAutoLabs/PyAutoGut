# Active Tasks

## test-mode-bypass-assertion-ties
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1519
- issued: 2026-08-24
- prompt: active/test_mode_bypass_ordered_assertion_ties.md
- status: library-shipped, awaiting-merge
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1520 (pending-release)
- environment: web-github (no local worktree; PyAutoBrain/skills/WORKFLOW.md)
- repos:
  - PyAutoFit: feature/test-mode-bypass-assertion-ties
- summary: |
    TEST_MODE=2/3 bypass evaluates at the prior medians, so a model with identical
    priors plus an ordering assertion ties and raises FitException. Verified on
    PyAutoFit main d3625a8 that this reproduces at THREE sites, not the one the
    prompt names: the instantiation outside the try (abstract_search.py:1007), the
    uniformly-scaled fake samples (:1112, so every stored sample fails too), and
    SamplesSummary.max_log_likelihood (interface.py:122, recover="raise") which
    makes result.max_log_likelihood_instance raise SamplesException. TEST_MODE=3 is
    therefore broken as well. Chosen fix (human-approved): share TEST_MODE=1's
    existing deterministic valid-point search (medians, then seeded prior draws)
    so the bypass evaluates AND stores an assertion-valid vector, fixing all three.
    Implemented and pushed: PyAutoFit feature/test-mode-bypass-assertion-ties
    (d49275c33). Shared _test_mode_valid_parameter_vector now picks the bypass
    point (medians, then seeded prior draws) so modes 2 AND 3 store an
    assertion-valid vector. Verified: repro failed both modes before, passes
    after; 5 new tests fail without the source change; full test_autofit
    2016 passed / 34 skipped. Shipped as PyAutoFit#1520 (pending-release).
    GATE CAVEAT: pyauto-heart is unreachable from this web-github session, so
    the readiness gate ran in the WORKFLOW.md fallback form (full library suite
    as the gate) — this is NOT a Heart GREEN verdict; confirm from a
    Heart-reachable environment before merge. Workspace impact: API Changes are
    "none — internal", but the workspace clones are absent here so the
    reference.md grep was NOT run; option (iii) is inferred, not measured.
    Next step: /prm (CI green → merge → close-out).

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
