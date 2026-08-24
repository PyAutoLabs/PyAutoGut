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

## smoke-runner-delegation
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/260 (issued 2026-08-24)
- issued: 2026-08-24
- prompt: active/run_smoke_copy_drift.md
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/smoke-runner-delegation
- decision: the prompt's blocking question is ANSWERED before any repo is touched —
  the timeout/kill behaviour was PROMOTED to everyone (PyAutoHands#226/#227 → 52408a84;
  all 10 copies import timeout_for + kill_group). Shape chosen: full delegation to a
  PyAutoHands-owned runner, staged. Phase 1 = --list allowlist mode + the 4 *_workspace_test
  copies; phase 2 = notebook leg + the 3 workspace copies; phase 3 = HowTo, no work.
- measured: 2026-08-24, from every repo's main — 10 copies, 3 variants, ZERO functional
  drift inside any variant (workspace 356L byte-identical; workspace_test 198L comment-only;
  HowTo 75L differ by PROJECT alone). Prompt steps 1 and 4 verified already done.
- registered: 2026-08-24 by the start_dev session (claude/smoke-copy-drift-ci-docs-ozntvv);
  worktree_check_conflict clean (exit 0) for all 8 repos.
- status-detail: HANDS LEGS MERGED, workspace collapses not started. The task stays
  active deliberately — issue #260 scopes seven workspace PRs that have zero commits,
  so this is not complete and must not be recorded as such.
- library-pr: https://github.com/PyAutoLabs/PyAutoHands/pull/261 MERGED 2026-08-24 → c0e2e53
  (both Hands legs: phase 1 `--list` opt-in script lists on run_python.py; phase 2
  the matching notebook leg on run.py — `--list`, `--no-write-back`, `--retry-from`).
  16 new tests; suite 388 passed / 5 skipped / 0 failed; CI green on all three
  matrix legs (3.12/3.13/3.14) plus the tenant-firewall step in each.
- mind-pr: https://github.com/PyAutoLabs/PyAutoMind/pull/280 MERGED 2026-08-24 → 0cd8544a
- phase-2 findings (these changed the plan, recorded so the workspace PRs inherit them):
  - run_notebook.py writes executed outputs back IN PLACE. Correct for generation
    (the outputs are the product), wrong for a PR gate, which must not dirty the
    tree it tests. Hence `--no-write-back`; it supersedes the workspace copy's
    staged-copy-at-root trick rather than porting it, since the kernel cwd is
    already pinned to the repo root.
  - JUPYTER_MISSING_RC did NOT need promoting. It exists because the workspace copy
    shelled out to a bare `jupyter`; execute_notebook invokes
    `sys.executable run_notebook.py`, so the abort-with-no-summary failure mode is
    structurally absent. One promotion item dissolved on inspection.
- remaining: the 7 workspace collapses (4 *_workspace_test, then 3 workspace), each a
  one-file PR, all blocked on the Hands branch merging first (library-first gate).
  Those repos are not attached to this session — each needs add_repo with push.
- repos:
  - PyAutoHands (branch claude/smoke-copy-drift-ci-docs-ozntvv)
