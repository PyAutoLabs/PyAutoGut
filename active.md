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

## smoke-install-stale-jax-pin
- issue: https://github.com/PyAutoLabs/autolens_workspace_test/issues/266
- issued: 2026-08-23
- prompt: active/smoke_install_stale_jax_pin.md
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/smoke-install-stale-jax-pin
- repos:
  - autolens_workspace_test: feature/smoke-install-stale-jax-pin
  - autogalaxy_workspace_test: feature/smoke-install-stale-jax-pin
- summary: |
    Remove the vestigial `jax<0.7 jaxlib<0.7` pin from `.github/scripts/smoke_install.sh`
    in both workspace_test repos, and add a post-install assertion on the resolved jax
    version. History established the pin's sole purpose was keeping
    `tensorflow-probability==0.25.0` importable (#82, 2026-05-08); that dependency was
    removed in #184 (2026-07-19) when the stack moved to `tfp-nightly`, leaving the pin
    protecting nothing while conflicting with autonerves' base `jax>=0.7.0,<0.12.0`.
    CI is currently green only because line ordering repairs the downgrade.
    Scope widened from the prompt's single repo: autogalaxy_workspace_test carries the
    identical line; autocti_ and autofit_workspace_test were checked and are clean.
    Next: /start_workspace (worktree + branches), then edits, then ship_workspace —
    the PR's own Smoke Tests run is the from-scratch install replay.
