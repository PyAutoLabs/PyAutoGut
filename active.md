# Active Tasks

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

## small-datasets-rmtree-committed-data
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/470
- pr: https://github.com/PyAutoLabs/autolens_workspace_test/pull/264 (open, awaiting review)
- prompt: active/small_datasets_rmtree_of_committed_data.md
- status: workspace-dev — implementation complete, PR open
- worktree: ~/Code/PyAutoLabs-wt/small-datasets-rmtree-committed-data
- design-call: option 2 (workspace ENV declaration), taken by the human 2026-08-22 after an
  organism-wide sweep found exactly one at-risk should_simulate call site. Options 1 and 3
  (library-level) deliberately NOT taken — see the prompt for the evidence.
- issue-repo-mismatch: #470 is filed on PyAutoArray but the fix landed entirely in
  autolens_workspace_test. Kept as the tracking issue rather than opening a duplicate;
  transfer if that mismatch becomes a problem.
- follow-up: draft/feature/pyautohands/dataset_allowlist_small_datasets_guard.md — the durable
  guard + a PyAutoArray docstring correction. BLOCKED: PyAutoHands is claimed by
  'hands-hygiene-leftovers'.
- repos:
  - autolens_workspace_test: feature/small-datasets-rmtree-committed-data
