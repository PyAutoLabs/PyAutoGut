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
- ROOT CAUSE FOUND 2026-08-22 (no laptop needed; findings on issue #260):
  PyAutoArray `util/dataset_util.py:72` `should_simulate()` is existence-only and asymmetric —
  it force-regenerates under PYAUTO_SMALL_DATASETS=1 but never under full_datasets. `dataset/**`
  is gitignored, so CI always simulates fresh and CANNOT hit this; locally the dir persists and
  is never refreshed. Any prior smoke run (SMALL_DATASETS=1 is the default for every OTHER
  script) rewrites the FITS at 15x15, and the next jax_grad run silently loads them under
  full-resolution settings. All three failures reproduced exactly from a clean checkout
  (pixelization eager/jit matches the report to 11 s.f.; regularization's tolerance vector
  matches exactly). Full chain proven: fresh=PASS -> one SMALL run -> stale=FAIL -> rm -rf =PASS.
- numpy FALSIFIED: lp.py byte-identical across numpy 2.2.6 / 2.4.6 / 2.5.2 (and across
  1-core vs 4-core). The likelihood runs through JAX/XLA; numpy only does the FD bookkeeping.
- NO tolerance change is warranted — all three asserts did their job on a genuinely invalid
  dataset. assert_eager_jit_consistent's rtol=1e-10 is vindicated, not under-specified.
- RECLASSIFY: the fix belongs upstream in PyAutoArray, not this workspace — every PyAuto
  workspace using the auto-simulate pattern inherits the trap. Awaiting a human call between
  (1) a regime marker and (2) symmetric regeneration; that call moves this to library-dev.
- follow-up (separate defect, not this bug): autolens_workspace_test
  `.github/scripts/smoke_install.sh:9` `pip install "jax<0.7" "jaxlib<0.7"` downgrades jax to
  0.6.2 and conflicts with autonerves' jax>=0.7,<0.11; the run only lands on the intended
  0.10.2 because the next line's [optional] extras pull it back up. CI is right by accident.
- out-of-bounds: moving lp.py's evaluation point, adding skip_indices, or widening a
  tolerance without a measured basis. All three mask the trap instead of removing it.
- repos:
