# Active Tasks

## python-312-floor
- issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/142
- status: parked; five PRs awaiting-merge; next core phase dependency/claim blocked
- library-pr: https://github.com/PyAutoLabs/PyAutoNerves/pull/143
- prompt: active/python_312_floor_phase_1a_nerves.md
- phase-4a-issue: https://github.com/PyAutoLabs/PyAutoCTI/issues/100
- phase-4a-prompt: active/python_312_floor_phase_4a_autocti.md
- phase-4a-pr: https://github.com/PyAutoLabs/PyAutoCTI/pull/101
- phase-4b-issue: https://github.com/PyAutoLabs/PyAutoReduce/issues/59
- phase-4b-prompt: active/python_312_floor_phase_4b_autoreduce.md
- phase-4b-pr: https://github.com/PyAutoLabs/PyAutoReduce/pull/60
- phase-4b-status: library-shipped, awaiting-merge
- phase-4c-issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/113
- phase-4c-prompt: active/python_312_floor_phase_4c_heart.md
- phase-4c-pr: https://github.com/PyAutoLabs/PyAutoHeart/pull/114
- phase-4c-status: library-shipped, awaiting-merge
- phase-4d-issue: https://github.com/Jammy2211/euclid_assistant/issues/10
- phase-4d-prompt: active/python_312_floor_phase_4d_euclid_assistant.md
- phase-4d-pr: https://github.com/Jammy2211/euclid_assistant/pull/11
- phase-4d-status: workspace-shipped, awaiting-merge
- next-phase: phase 1B — PyAutoArray
- next-phase-blockers: PyAutoNerves PR #143 remains unmerged; PyAutoArray is
  claimed by active task api-validation-and-crash-fixes
- branch: feature/python-312-floor
- worktree: /home/jammy/Code/PyAutoLabs/.codex-worktrees/python-312-floor
- checkpoint-superseded: https://github.com/PyAutoLabs/PyAutoNerves/issues/142#issuecomment-5109079935
- resume-evidence: https://github.com/PyAutoLabs/PyAutoNerves/issues/142#issuecomment-5109572194
- queue-checkpoint: https://github.com/PyAutoLabs/PyAutoNerves/issues/142#issuecomment-5114496576
- commits: PyAutoNerves f06dd40, a3ed651 (pushed)
- heart-ack: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code) — 6 mismatch(es) vs PyAutoMind/repos.yaml; release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- repos:
  - PyAutoNerves: feature/python-312-floor
  - PyAutoCTI: feature/python-312-floor
  - PyAutoReduce: feature/python-312-floor
  - PyAutoHeart: feature/python-312-floor
  - euclid_assistant: feature/python-312-floor
- notes: Phase 1A of the reviewed Python >=3.12 ecosystem campaign. Shared
  branch/worktree task will grow through the dependency-ordered core stack;
  JAX 0.11 and Python 3.14 support remain separate follow-ups. Tests, review and
  corrected smoke are green (62 passed, 0 failed, 3 intentional skips). The
  earlier 11-failure checkpoint was a local wrapper error: relative script
  paths were resolved from the parent cwd, so in-file ENV declarations were
  missed. No ecosystem defect was present. PyAutoNerves PR #143 is open with
  `pending-release`; merge remains human-gated before dependent phases advance.
  Independent Phases 4A–4C are shipped as open pending-release PRs for
  PyAutoCTI, PyAutoReduce, and PyAutoHeart. Their metadata and living
  installation claims are in scope, while archival paper/history and release
  execution remain out of scope. PyAutoCTI PR #101 is open with
  `pending-release`, fully tested on 3.12/3.13 and review CLEAN. Independent
  Phase 4B is also active in
  PyAutoReduce; its census found only package metadata below the floor. Issue
  #59 is filed and PR #60 is open with `pending-release`, fully tested on
  3.12/3.13 and review CLEAN. Independent Phase 4C is shipped as PyAutoHeart
  PR #114 with 289 tests green on each supported interpreter and review CLEAN;
  release/install verification remains reserved for Phase 2. Independent Phase
  4D is shipped as euclid_assistant PR #11: local and GitHub 3.12/3.13 tests,
  wheel metadata, CLI smoke, and review are green; source papers, generated
  content, and provenance were untouched. All independent Phase 4 slices are
  now at PR-open. Phase 1B cannot start until PyAutoNerves PR #143 is merged
  and the existing api-validation-and-crash-fixes claim on PyAutoArray clears.

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
- status: workspace-shipped, awaiting-merge
- workspace-pr: https://github.com/PyAutoLabs/autolens_profiling/pull/94 (results-only, pending-release labelled, lint running at hand-off)
- heart-ack: 2026-07-28 — workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code); release validation stale (all pre-existing, none in autolens_profiling)
- verdict: phase A DONE. Single-band MultiStartProdigy compile is BENIGN on all endorsed model types (mge/rect/knn/delaunay_matern; worst ~3.5min cold 1-core laptop, <=75s cold / <=2s warm RAL 32-core). Multi-band lax.map explosion does NOT reproduce single-band -> **phase B (PyAutoFit pyloop) is an evidence-based NO-GO**; pyloop lever stays multi-band-FactorGraphModel-only. No PyAutoFit branch was ever created; #1414 serialisation concern is moot.
- resume-next: (1) RAL A100 job 331380 (queued behind external multi-day array on gpu-2; gpu-1 down) — when it runs, rsync rows from /mnt/ral/jnightin/autolens_profiling_census/scripts/misc/jax_compile/results/, filter tag `prodigy-census-a100-*`, append to README table + results JSON, commit to same branch (confirmatory only — do NOT block the merge on it); (2) merge PR#94 + close #93 (human); (3) route draft/research/autoarray/delaunay_callback_persistent_cache_miss.md via /start_dev — the one real defect found; (4) post-merge cleanup (worktree, branch, complete/2026/07 record).
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
