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

## loggaussian-prior-support
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1526
- issued: 2026-08-25
- prompt: active/17_loggaussian_prior_declares_own_support.md
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/loggaussian-prior-support
- repos:
  - PyAutoFit: feature/loggaussian-prior-support
- summary: |
    Follow-up 3 owed by the prior-support Clipper (PyAutoFit#1477). LogGaussianPrior
    reports (-inf, inf) while its support is (0, inf); declare it on the prior, add a
    general strictness contract to Prior, derive Prior.limits from the declared bounds,
    and retire the clipper's isinstance special case. Adversarial review completed
    against a running 3.12 install before dev: identifiers and the unit-cube mapping
    verified unchanged; prior passing is the one downstream-visible behaviour change.
    Environment is web-github (direct clone, no local worktree root).

