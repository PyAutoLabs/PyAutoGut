# Active Tasks

## jax-compile-stall-slow-vs-stall-audit
- issue: https://github.com/PyAutoLabs/autolens_workspace_test/issues/271 (issued 2026-08-23)
- issued: 2026-08-23
- prompt: active/jax_compile_stall_2_slow_vs_stall_audit.md
- status: workspace-dev
- epic: jax-compile-stall (phase 2 of 3; ledger draft/bug/ci/jax_vmap_jit_compile_stall.md)
- worktree: ~/Code/PyAutoLabs-wt/jax-compile-stall-slow-vs-stall-audit
- worktree-note: started in a web-github session with no local tree; no branch cut yet.
- decision: harness lives Heart-side (human choice 2026-08-23) — a `runner` input on the
  reusable smoke-tests.yml rather than a per-workspace duplicate of the ceremony.
- prs:
  - https://github.com/PyAutoLabs/PyAutoHeart/pull/161 (runner input; MERGES FIRST)
  - https://github.com/PyAutoLabs/autolens_workspace_test/pull/272 (retime harness)
  - https://github.com/PyAutoLabs/autogalaxy_workspace_test/pull/110 (retime harness)
- order: #161 first — a caller cannot pass a `runner` input that does not exist yet, so a
  dispatch of either retime.yml fails at workflow resolution until Heart merges.
- next: once merged, dispatch retime.yml over the 26 entries (300s smoke / 1800s release,
  both matrix legs) and classify from the distributions; then rewrite the markers.
- heart: NOT consulted — pyauto-heart unreachable from this web session.
- repos:

## jax-compile-stall-evidence
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1516 (issued 2026-08-23)
- issued: 2026-08-23
- prompt: active/jax_compile_stall_1_evidence.md
- status: library-dev
- epic: jax-compile-stall (phase 1 of 3; ledger draft/bug/ci/jax_vmap_jit_compile_stall.md)
- worktree: ~/Code/PyAutoLabs-wt/jax-compile-stall-evidence
- worktree-note: started in a web-github session with no local tree — the branch was
  cut against a direct clone at /home/user/pyautofit, not the worktree root above.
  A local-dev session resuming this should create the worktree via worktree_create.
- pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1517 (opened 2026-08-23, awaiting review)
- heart: NOT consulted — pyauto-heart unreachable from the web session that opened the PR;
  run the vitals check before merge.
- repos:
  - PyAutoFit: feature/jax-compile-stall-evidence

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
