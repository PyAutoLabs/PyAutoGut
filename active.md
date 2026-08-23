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

## run-smoke-per-script-timeout
- issue: https://github.com/PyAutoLabs/autogalaxy_workspace_test/issues/108
- issued: 2026-08-23
- prompt: active/run_smoke_per_script_timeout.md
- status: workspace-dev
- environment: web-github — no local worktree; branch in the session clones.
  autocti_workspace_test and autofit_workspace_test are NOT yet attached to a
  session; they need add_repo with push access before their edits.
- repos:
  - autogalaxy_workspace_test: feature/run-smoke-per-script-timeout
  - autocti_workspace_test: feature/run-smoke-per-script-timeout
  - autofit_workspace_test: feature/run-smoke-per-script-timeout
- summary: |
    Backport the per-script timeout in `.github/scripts/run_smoke.py` from
    autolens_workspace_test (193 lines, has it via PyAutoHands#226/#227) to the three
    siblings still on the un-capped 113-line copy. The three are IDENTICAL in code —
    they differ only in one docstring paragraph — so this is one diff applied 3x.
    Port: the `timeout_for` import + ImportError fallback, Popen(start_new_session=True)
    + communicate(timeout=...), `_kill_group()` SIGKILL of the process group on
    TimeoutExpired, return code 124, and the `TIMEOUT (Ns)` summary status.
    Key verification: ASSERT `timeout_for` actually resolves in each repo's CI. Its
    ImportError fallback silently degrades to the whole-run cap, which would make the
    backport look applied while doing less — the same green-by-accident failure mode
    as the #266 task this came out of.
    Sizing: Feature Agent derived large (score 8) + phasing, on an earlier draft that
    framed this as designing a timeout from scratch. Overridden to low/direct — there
    is a production reference implementation and the targets are code-identical.
    Not in scope: root-causing the hang (draft/research/workspaces/
    intermittent_smoke_hang_jax_mge.md) or unparking rectangular.py.
    Next: /start_workspace (attach the two unattached repos, create branches).
