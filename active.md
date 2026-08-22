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

## should-simulate-capped-branch-reuse
- issue: none — shipped directly as a PR; the prompt is the spec (small, single-repo, follow-up
  of an already-closed issue). Raise one if it needs tracking beyond the PR.
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/476 (pending-release)
- status: library-shipped, awaiting-merge — stopped at PR-open; merge is human
- prompt: active/should_simulate_capped_branch_ignores_the_stamp.md
- worktree: n/a — web-github session, clone at /home/user/pyautoarray
- branch: claude/small-datasets-regime-stamp-s3i9o7 (restarted from origin/main after #474 merged;
  its prior commits were all already merged, so force-with-lease was safe)
- FINDING that changed the scope: the fix is NOT the `if stamp is not True:` one-liner recorded
  in the prompt's parent. `SMALLDAT = T` means "capped at whatever the cap was when written",
  not "capped at today's cap" — reusing on the stamp alone would silently feed stale wrong-sized
  data if SMALL_DATASETS_SHAPE_NATIVE ever changes, reintroducing the exact bug the stamp
  prevents, through the opposite branch. Reuse requires stamp T AND shape == current cap.
- interferometer decision, taken explicitly: never qualifies for reuse. Its data.fits is
  (n_visibilities, 2), shape fixed by the committed uv file and unchanged by the cap, so shape
  cannot corroborate the stamp. Keeps regenerating every run.
- gate: Heart NOT consulted (no PyAutoHeart checkout). Suite fallback: 1106 passed / 0 failed,
  green with PYAUTO_SMALL_DATASETS=1 exported AND unset, tree clean both ways.
- repos:
  - PyAutoArray: claude/small-datasets-regime-stamp-s3i9o7 (a9ae5f6)
