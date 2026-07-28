# Active Tasks

## python-312-floor
- issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/142
- status: library-shipped, awaiting-merge
- library-pr: https://github.com/PyAutoLabs/PyAutoNerves/pull/143
- prompt: active/python_312_floor_phase_1a_nerves.md
- branch: feature/python-312-floor
- worktree: /home/jammy/Code/PyAutoLabs/.codex-worktrees/python-312-floor
- checkpoint-superseded: https://github.com/PyAutoLabs/PyAutoNerves/issues/142#issuecomment-5109079935
- resume-evidence: https://github.com/PyAutoLabs/PyAutoNerves/issues/142#issuecomment-5109572194
- commits: PyAutoNerves f06dd40, a3ed651 (pushed)
- heart-ack: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code) — 6 mismatch(es) vs PyAutoMind/repos.yaml; release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- repos:
  - PyAutoNerves: feature/python-312-floor
- notes: Phase 1A of the reviewed Python >=3.12 ecosystem campaign. Shared
  branch/worktree task will grow through the dependency-ordered core stack;
  JAX 0.11 and Python 3.14 support remain separate follow-ups. Tests, review and
  corrected smoke are green (62 passed, 0 failed, 3 intentional skips). The
  earlier 11-failure checkpoint was a local wrapper error: relative script
  paths were resolved from the parent cwd, so in-file ENV declarations were
  missed. No ecosystem defect was present. PyAutoNerves PR #143 is open with
  `pending-release`; merge remains human-gated before dependent phases advance.

## python-312-floor-autocti
- issue: https://github.com/PyAutoLabs/PyAutoCTI/issues/100
- status: library-dev
- prompt: active/python_312_floor_phase_4a_autocti.md
- branch: feature/python-312-floor
- worktree: /home/jammy/Code/PyAutoLabs/.codex-worktrees/python-312-floor
- heart-ack: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code) — 6 mismatch(es) vs PyAutoMind/repos.yaml; release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- repos:
  - PyAutoCTI: feature/python-312-floor
- notes: Independent-package phase 4A. Metadata and living installation claim
  only; archival paper and historical traceback remain unchanged. Release stays
  behind the PyAutoCTI resurrection/readiness gate and human approval.

## vacuous-jax-assertions
- issue: https://github.com/PyAutoLabs/autolens_workspace_test/issues/229
- status: awaiting-merge
- workspace-pr: autolens_workspace_test#230, autogalaxy_workspace_test#99 (both OPEN, pending-release)
- prompt: active/vacuous_jax_assertions_release_profile.md
- heart-ack: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code) — 6 mismatch(es) vs PyAutoMind/repos.yaml; release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- notes: follow-up to PyAutoFit#1372 (CLOSED — its library finding was already fixed by PyAutoLens@83016c1ea, "PYAUTO_DISABLE_JAX has exactly one reader"; the sentinel it proposed was closed won't-do, no live consumer). Case A (latent_nan_robustness.py, both repos) is genuinely vacuous → RENAME to `_jax.py` so `derive_jax_markers` fires. Do NOT use an in-file `ENV: jax` declaration: it is profile-agnostic, so it would also flip SMOKE (both scripts are in smoke_tests.txt = the per-PR gate), and validate_env_profiles.py:152-161 calls that exact move "NOT migratable"; it would also evade the marker audit at :190-198, which tests `== "0"` while a declaration pops the var to absent. Case B (visualization.py, both repos) — `use_jax=True` is a NO-OP everywhere since ag/al default it True; drop the kwarg, fix the ag `"JAX/"` label; do NOT add ENV: jax (the modeling_visualization_jit family is already parked >300s). Profile default stays "1" per the release-profile-jax-default "DO NOT COPY" caveat. Brain scored large/8/research-first — OVERRIDDEN to small (scored the prompt's prose, not the work: 4 files, ~6 lines, 2 renames).
- worktree: ~/Code/PyAutoLabs-wt/vacuous-jax-assertions
- repos:
  - autolens_workspace_test (feature/vacuous-jax-assertions)
  - autogalaxy_workspace_test (feature/vacuous-jax-assertions)

## api-validation-and-crash-fixes
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/416
- epic: https://github.com/PyAutoLabs/PyAutoArray/issues/415
- status: phase-1-merged, phases 2-4 remain
- library-pr: PyAutoArray#417 MERGED (9411904d), PyAutoLens#662 MERGED (2a3f1a63); PyAutoLens#531 CLOSED
- user-facing: true
- prompt: active/rhayes_audit_validation_and_crashes.md
- heart-ack: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code); release validation stale
- phases: 1 (crash bugs) MERGED 2026-07-28 (smoke clean, 0 regressions; 5 jax_likelihood failures were pre-existing → autolens_workspace_test#231/PR#232); 2 (9 constructor guards, needs shared `_validate_*` home decision — PyAutoArray is the natural floor); 3 (adapt_images error legibility + B10 tolerance test); 4 HELD awaiting @rhayes777's answer on the z_lens>z_source warning
- notes: @rhayes777's 2026-05-23 audit, 5 issues, 66d unanswered — all 5 replied 2026-07-28, all 16 findings re-verified on main. Brain scored 17/too-large and proposed design/core_api/workspace/docs; OVERRIDDEN to split by defect class (no workspace or docs work exists here) — recorded per the repo-count-difficulty-proxy caveat. #332's "Delaunay/KNN unusable" headline is FALSE (they need adapt_images); the real defect is the opaque error, so the regression test asserts a CLEAR FAILURE, not a successful fit. Split-on-rectangular: DESIGN INTENT is that rectangular does NOT support Split — fix is a clear "unsupported" exception, NOT the missing capability. Scope is 9 combos / 2 failure modes (3 rect meshes x 3 Split regs), not the 1 reported: RectangularUniform → AttributeError; RectangularAdaptDensity/AdaptImage → IndexError via the FALSE pass-through at rectangular.py:460 (delete it). Delaunay+ConstantSplit works (5096.4420). Constructors are JAX-traced — no Python `if` on possible tracers.
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
