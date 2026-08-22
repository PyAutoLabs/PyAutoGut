# Active Tasks

## reconstruction-noise-map-covariance-sqrt
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/468 (issued 2026-08-22)
- prompt: active/reconstruction_noise_map_covariance_sqrt.md
- status: library-dev
- branch: claude/numerical-inversion-failures-7xsp1k (harness-designated, not the usual feature/ prefix)
- scope-note: phase 1 only — the numerics + semantics half. The estimator-level defects
  (covariance describes the unconstrained solve while use_positive_only_solver=true is the
  default; noise map ignores zeroed_ids_to_keep; use_edge_zeroed_pixels silently ignored when
  the positive-only solver is off) are deliberately OUT of this PR and tracked in
  draft/bug/autoarray/reconstruction_noise_map_solver_mismatch.md.
- pushed: PyAutoArray branch pushed, PR NOT opened (awaiting human go-ahead).
- tests: 1152 passed, 1 skipped; 3 test_transformer.py pynufft failures pre-exist on a6b07cd.
- reviewed: adversarial review 2026-08-22 found a MAJOR regression in the first commit --
  scipy cho_factor raises ValueError (not LinAlgError) on non-finite input, escaping both
  callers' guards and aborting a model-fit the CSV writer promises not to abort. Fixed by
  raising LinAlgError explicitly inside the property. Also symmetrizes the input now
  (cho_factor reads only the upper triangle) and the tautological symmetry test was given a
  real accuracy oracle.
- downstream-grep: zero consumers of reconstruction_noise_map_with_covariance in PyAutoGalaxy
  (3ca31bf), PyAutoLens (87e5827) or autolens_workspace, so the alias's value change is safe.
  reconstruction_noise_map IS used in autolens_workspace source_science.py for
  signal_to_noise_map = reconstruction / reconstruction_noise_map -- values unchanged.
  NOT checked: autogalaxy_workspace, HowTo repos, user code.
- repos:
  - PyAutoArray: claude/numerical-inversion-failures-7xsp1k

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
