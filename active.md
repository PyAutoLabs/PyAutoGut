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

## dataset-allowlist-small-datasets-guard
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/252
- pr: https://github.com/PyAutoLabs/PyAutoHands/pull/253 (open)
- pr: https://github.com/PyAutoLabs/PyAutoArray/pull/480 (open, docstring-only)
- prompt: active/dataset_allowlist_small_datasets_guard.md
- status: library-dev — implementation complete, both PRs open
- worktree: ~/Code/PyAutoLabs-wt/dataset-allowlist-small-datasets-guard
- parallel-claim: PyAutoHands is ALSO claimed by 'hands-hygiene-leftovers'. Verified disjoint at
  file level before starting (that branch touches AGENTS.md, generate_release_notes.py,
  bin/autohands, tests/test_autohands_registry.py, tests/test_slack_release_notes.py; this one
  touches autohands/check_dataset_allowlist.py, autohands/env_config.py and a new test file).
  Whichever merges second should re-run the suite, not hand-merge.
- follows: complete/2026/08/small-datasets-rmtree-committed-data.md (PyAutoArray#470)
- repos:
  - PyAutoHands: feature/dataset-allowlist-small-datasets-guard
  - PyAutoArray: feature/dataset-allowlist-small-datasets-guard
