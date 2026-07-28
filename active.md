# Active Tasks

## api-validation-and-crash-fixes
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/416
- epic: https://github.com/PyAutoLabs/PyAutoArray/issues/415
- status: library-dev
- user-facing: true
- prompt: active/rhayes_audit_validation_and_crashes.md
- heart-ack: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code); release validation stale
- phases: 1 (crash bugs — ConstantSplit×RectangularUniform + 2 PointSolver) IN FLIGHT; 2 (9 constructor guards, needs shared `_validate_*` home decision — PyAutoArray is the natural floor); 3 (adapt_images error legibility + B10 tolerance test); 4 HELD awaiting @rhayes777's answer on the z_lens>z_source warning
- notes: @rhayes777's 2026-05-23 audit, 5 issues, 66d unanswered — all 5 replied 2026-07-28, all 16 findings re-verified on main. Brain scored 17/too-large and proposed design/core_api/workspace/docs; OVERRIDDEN to split by defect class (no workspace or docs work exists here) — recorded per the repo-count-difficulty-proxy caveat. #332's "Delaunay/KNN unusable" headline is FALSE (they need adapt_images); the real defect is the opaque error, so the regression test asserts a CLEAR FAILURE, not a successful fit. ConstantSplit gap is wider than reported: InterpolatorRectangularUniform lacks `_mappings_sizes_weights_split`, breaking all THREE Split regularizations. Constructors are JAX-traced — no Python `if` on possible tracers.
- worktree: ~/Code/PyAutoLabs-wt/api-validation-and-crash-fixes
- repos:
  - PyAutoArray (feature/api-validation-and-crash-fixes)
  - PyAutoLens (feature/api-validation-and-crash-fixes)
  - PyAutoGalaxy (phase 2 — not yet claimed)

## multistart-prodigy-compile
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/93
- session: claude --resume 73eff5ef-e2f6-46ba-9304-60dade7008ac
- status: workspace-dev
- notes: phase A (measure, autolens_profiling) in flight; phase B (PyAutoFit pyloop batching) serialises behind preserve-in-zip-replace-member's PyAutoFit merge (#1414 / PR#1427)
- worktree: ~/Code/PyAutoLabs-wt/multistart-prodigy-compile
- repos:
  - autolens_profiling (feature/multistart-prodigy-compile)

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- session: claude --resume daaa46f9-aac5-48e2-9146-1202a92d879e
- status: library-merged, workspace-pending
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phases: 1 (design) + 2 (core API) COMPLETE; next: start_workspace on active/../draft phase-3 prompt (workspace_test jax_likelihood + profiling examples), then phase 4 (guides), then phase 5 (JAX solver gradients)
- repos:
