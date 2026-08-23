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
- environment: web-github — no local worktree; branched in the session clones.
  Deliberately no `worktree:` field (PyAutoBrain skills/WORKFLOW.md "Execution
  environments"), so the entry claims no worktree path a local session could
  mistake for an existing checkout.
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
    start_workspace done (standalone mode, web-github): branched both clones at
    feature/smoke-install-stale-jax-pin, `pending-release` label verified canonical
    on both repos via the API (no gh CLI in this session).
    Edits committed + pushed: autolens_workspace_test a97f052, autogalaxy_workspace_test
    b0bd72d. Validated `bash -n` on both scripts, unit-tested the guard's boundary
    cases, and executed the guard against stub jax 0.10.2/0.6.2/0.12.0 (pass/fail/fail).
    Confirmed the reusable workflow uses actions/setup-python on ubuntu-latest, so
    `python` is on PATH and jax is always installed there.
    ship_workspace done — PRs OPEN, NOT merged (merge stays human):
      autolens_workspace_test#268   (closes #266)
      autogalaxy_workspace_test#107
    Both carry the `pending-release` label, verified after creation.
    Ship gate: Heart returned STALE (score 35) with red_reasons=[] and
    yellow_reasons=[] — only evidence gaps (no library checkouts or report.json in
    this web-github session). Per agents/faculties/vitals/AGENTS.md the dev-ship
    gate treats STALE as passing (a release would still require GREEN), so the gate
    is satisfied on its own terms, not waived.
    No upstream library PR, so the library-first merge gate does not apply.
    MERGED: autolens_workspace_test#268 -> merge commit 9348e152 (all 3 legs green).
    CI proved the point: the install log prints `resolved jax 0.11.1` — NOT the 0.10.2
    the prompt observed. Removing the pin moved CI onto a newer jax that autonerves'
    widened cap (<0.12.0) now permits, and the full smoke suite passed on 3.12 and
    3.13 at that version. `incompatible` no longer appears in the install log at all.
    This retrospectively vindicates deleting the pin rather than restating it as
    `jax>=0.7,<0.11` per the prompt's quoted range: that would have pinned CI a full
    minor version behind what the stack supports.
    OPEN: autogalaxy_workspace_test#107 — `smoke / changes` green; both smoke legs
    still in `Run smoke tests` at 39min (autolens took 11min; this suite is simply
    longer). Its Install step ALREADY passed (16:39:30-16:40:47), so the assertion
    passed on this repo too — the epilogue this task changes is verified green here;
    only the smoke scripts themselves are still running.
    Active polling stopped at /prm's ~30min cap. PR subscription + a 17:36Z check-in
    are armed. Next: merge #107 when green, then the Shipped comment on #266 and
    lifecycle.py record. Issue #266 close is a separate human decision.
