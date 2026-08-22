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

## jax-grad-local-vs-ci-assertions
- issue: https://github.com/PyAutoLabs/autolens_workspace_test/issues/260 (issued 2026-08-22)
- session: https://claude.ai/code/session_01VEHLT33XpVcRt5YCJGLRMJ (web-github; no local worktree yet)
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/jax-grad-local-vs-ci-assertions
- prompt: active/jax_grad_local_assertions_fail_but_pass_in_ci.md
- classification: workspace (single repo) — routes to /start_workspace
- strategy: investigate-first. Bug Agent: severity=critical, scope=single-repo,
  type=wrong-result, confidence=LOW. Reproduce and confirm root cause BEFORE patching.
  Brain sizing disagreement: declared medium, derived large.
- control: imaging/jax_grad/lp.py is the discriminator — the only script known to PASS in
  CI and FAIL locally. Every A/B runs against it first (~41s).
- blocked-on-input: the failing local venv cannot be read from a cloud session. Capture
  `pip freeze` + `np.show_config()` from the machine that reproduces the failure before it
  drifts — otherwise step 2 has no ground truth. Raised at plan time; not yet supplied.
- out-of-bounds: moving lp.py's evaluation point, adding skip_indices, or widening a
  tolerance without a measured basis. All three mask the trap instead of removing it.
- repos:
