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

## fits-header-comment-literal-list
- issue: none — shipped directly as a PR (small, single-repo, cosmetic)
- library-pr: https://github.com/PyAutoLabs/PyAutoNerves/pull/155 (pending-release)
- status: library-shipped, awaiting-merge — stopped at PR-open; merge is human
- prompt: active/fits_header_dict_comment_is_a_literal_list.md
- worktree: n/a — web-github session, clone at /home/user/pyautonerves
- branch: claude/fits-header-comment-literal-list
- DECISION taken explicitly, not by omission: did NOT add real per-key comments (the
  prompt's step 2). autonerves receives an opaque header_dict and does not know the key
  vocabulary — PIXSCAY/ORIGINY are autoarray's Mask2DKeys — so hardcoding their meanings
  in the base serialization layer would couple it to a downstream key set, the wrong
  direction for the dependency. If descriptive comments are wanted the CALLER should
  supply them, which is a separate API change to header_dict's shape.
- fixture: test_autonerves/files/array_out.fits refreshed (write target, bytes change with
  the comment). Verified byte-stable across repeated runs and identical with
  PYAUTO_SMALL_DATASETS exported AND unset — the autouse conftest fixture from #154 is
  what makes that deterministic.
- gate: Heart NOT consulted (no PyAutoHeart checkout). Suite fallback: 166 passed, green
  both env states.
- NEXT after merge: release PyAutoNerves. Until a stamped autonerves is published, the
  #153/#154 regime stamp is not live — autoarray's floor `autonerves>=2026.8.22.1` is the
  newest release on PyPI and predates the stamp.
- repos:
  - PyAutoNerves: claude/fits-header-comment-literal-list (0c283e4)
