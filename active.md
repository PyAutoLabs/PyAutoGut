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

## small-datasets-regime-stamp
- issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/153 (issued 2026-08-22, pre-existing — start_dev did NOT create it)
- session: cloud web-github session, branch claude/small-datasets-regime-stamp-s3i9o7
- status: library-dev — PLAN PRESENTED, awaiting human approval before any code edit
  (prompt is Autonomy: supervised and this run has no --auto, so checkpoint 1 holds)
- prompt: active/small_datasets_regime_stamp_at_writer_funnel.md
- worktree: n/a — web-github environment; clones at /home/user/pyautonerves, /home/user/pyautoarray
- FINDING that changes the plan: the prompt's premise "every FITS write funnels through
  `output_to_fits`" is only half true. `output_to_fits` is the only definition of that NAME,
  but it is NOT the only write path — the multi-HDU dataset writers
  (`autoarray/dataset/plot/{imaging,interferometer}_plots.py`) call
  `hdu_list_for_output_from` + `write_hdu_list` directly and never touch `output_to_fits`.
  Stamping at `fitsable.py:89` as written would MISS the interferometer multi-HDU write,
  i.e. the exact silent case this task exists to catch. Terminal funnel is
  `write_hdu_list` (`fitsable.py:127`, sole `hdu_list.writeto` in either repo).
- risk surface is SMALLER than the prompt feared: no md5/sha256/golden-file pins over FITS
  anywhere in PyAutoNerves or PyAutoArray; header tests assert per-key, not whole-header.
- repos:
  - PyAutoNerves: (branch not yet created)
  - PyAutoArray: (branch not yet created)
