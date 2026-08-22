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

## plot-utils-duplicate-modules
- issue: none — shipped directly as a PR (small, single-repo, behaviour-preserving)
- library-pr: https://github.com/PyAutoLabs/PyAutoGalaxy/pull/584 (pending-release)
- status: library-shipped, awaiting-merge — stopped at PR-open; merge is human
- prompt: active/plot_utils_duplicate_modules.md
- worktree: n/a — web-github session, clone at /home/user/pyautogalaxy
- branch: claude/plot-utils-duplicate-modules
- METHOD NOTE worth keeping: the first importer search used a LINE-ANCHORED grep
  (`^from autogalaxy.plot.plot_utils`) and returned ZERO, so the deletion looked safe.
  It was not — `test_visuals.py:41` has an indented, function-local import, which the
  anchored pattern silently skipped. The test suite caught it (passes on main, failed with
  the change). Search UNANCHORED when removing a module; Python's function-local imports
  do not sit at column zero.
- also in the diff: a Sphinx cross-ref in galaxies_plots.py pointed at the deleted module
  (re-pointed), and a stray `/btw ok` line committed into the `_critical_curves_from`
  docstring in 3ca31bf (#582) and inherited by both copies (removed — it renders into the
  API docs).
- gate: Heart NOT consulted (no PyAutoHeart checkout). Suite fallback: 1099 passed /
  5 skipped, an IDENTICAL count to clean main, which is the behaviour-preserving evidence.
- repos:
  - PyAutoGalaxy: claude/plot-utils-duplicate-modules (247e4a3)
