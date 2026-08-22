# Active Tasks

## optional-dependency-skip-guards
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1511 (issued 2026-08-22)
- prompt: active/17_optional_dependency_skip_guards.md
- status: PR OPEN — https://github.com/PyAutoLabs/PyAutoFit/pull/1512, CI GREEN
  (unittest 3.12 + 3.13 + nojax, run 32575550710), mergeable clean, awaiting review
- scope-note: tests only, no `autofit/` source touched. Verified inert in the CI env
  (2024 passed / 3 skipped, identical to main), so no coverage is lost.
- context: closes follow-up 4 of complete/2026/08/uniform-prior-bounds-numpy-path.md,
  filed there 2026-08-18 but never turned into a prompt. Ends the recurring
  "test_nautilus fails pre-existing on main" false alarm — see the correction trail
  in the prompt.
- repos:
  - PyAutoFit: claude/test-nautilus-single-core-builds-35kyot

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

## hands-hygiene-leftovers
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/249
- session: claude --resume 08f77ea2-bf3a-42f4-a427-e01da3a4ce2d
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/hands-hygiene-leftovers
- prompt: active/hands_hygiene_leftovers.md
- scope-note: the prompt's third bullet (~30 stale PyAutoHands remote branches, incl.
  origin/master, origin/release) is deliberately OUT of this task's PR — run it as a
  separate /repo_cleanup sweep so a destructive branch delete never rides a code diff.
- repos:
  - PyAutoHands: feature/hands-hygiene-leftovers
