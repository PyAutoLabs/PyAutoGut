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

## message-log-partition-tuple-shape
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1510 (issued 2026-08-22)
- prompt: active/jax_011_message_log_partition_tuple_shape.md
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/message-log-partition-tuple-shape
- root-cause: jax 0.11 changed `jnp.broadcast_arrays` list -> tuple (NumPy 2 alignment), so
  `MessageInterface.shape`'s `isinstance(..., list)` JAX branch stops matching and falls
  through to `.shape` on a tuple. Reproduced; 4 failing tests, not the reported 5 (the
  fifth, graphical `test_beta`, was already cleared by PyAutoFit 19c679583).
- scope-change: the one-line `isinstance` widen was REJECTED by adversarial review — it
  preserves a silent numerical bug live on jax 0.10 today (batched JAX `logpdf` returns a
  (2,2) matrix instead of (2,)). The PR fixes `shape`/`size`/`ndim` semantically instead.
  Reviewer-visible consequence: batched JAX message output values change.
- merge-order: PyAutoFit PR merges FIRST; the PyAutoNerves `jax`/`jaxlib` cap widen to
  `<0.12.0` follows. Every supported env is Python >=3.12, so the widen puts jax 0.11 in
  front of all users — PyAutoGalaxy and PyAutoLens must be green under 0.11 before it merges
  (PyAutoFit and PyAutoArray already verified clean on both versions).
- verification-note: `test_autofit` alone is NOT the JAX gate — install the `[optional]`
  extras (blackjax, nautilus-sampler) or 18 tests silently skip, and also run the ten
  scripts in `autofit_workspace_test/scripts/jax_assertions/` (JAX unit coverage moved
  out of the library suite in #1247).
- implemented: 2026-08-22 — fix + parity regression test pushed on the branches below,
  verified 2030 passed on jax 0.10.2 and 0.11.1 (full matrix on the issue). The
  downstream gate note: PyAutoGalaxy/PyAutoLens CI resolves jax from the autonerves cap,
  so pre-widen CI green does not cover 0.11 — gate via forced jax==0.11.1 runs or
  matching-branch CI against the PyAutoNerves branch.
- repos:
  - PyAutoFit: feature/message-log-partition-tuple-shape
  - PyAutoNerves: feature/message-log-partition-tuple-shape
