# Active Tasks

## worktree-drift-fixes
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/123
- status: awaiting-merge — PyAutoHeart#124 OPEN 2026-07-30
- pr: https://github.com/PyAutoLabs/PyAutoHeart/pull/124
- evidence: suite 328 passed (8 new tests); live run — only real missing claim surfaced, canonical dirt deduped to once-per-checkout
- prompt: active/worktree_drift_false_missing_and_symlink_double_count.md
- classification: bug (PyAutoHeart) — CI/release audit series task 5; monitoring-only check
- worktree: ~/Code/PyAutoLabs-wt/worktree-drift-fixes
- repos:
  - PyAutoHeart (feature/worktree-drift-fixes)

## multiband-pyloop-batching
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1430
- session: claude --resume ed9e7d65-ca7d-4718-8f02-d77a2ad27017
- status: library-dev
- prompt: active/multi_band_factorgraph_compile_deeper_dig.md
- classification: research / autofit — library (PyAutoFit pyloop batching) + autolens_profiling benchmark validation; Brain scored too-large-13 off repo count with a generic 4-phase split, overridden to one implement+benchmark task (#93 precedent)
- conflict-note: worktree_check_conflict flagged PyAutoFit claimed by python-312-floor; hand-checked stale — that worktree's branch is 0 commits ahead of origin/main (PR#1429 merged)
- worktree: ~/Code/PyAutoLabs-wt/multiband-pyloop-batching
- repos:
  - PyAutoFit (feature/multiband-pyloop-batching)
  - autolens_profiling (feature/multiband-pyloop-batching)

## plot-guides-restructure
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/400
- status: awaiting-merge — phases 0–2 shipped 2026-07-30; phase 3 (autolens_assistant) gated on workspace merges
- prs: PyAutoGalaxy#538 (merges FIRST), autolens_workspace#401, autogalaxy_workspace#190 (after PyAutoGalaxy#538)
- validation: AL 13/13 + AG 10/10 sequential test-mode runs with visualization on; check_sizes OK both; legacy grep zero both; PyAutoGalaxy 1009 tests passed
- heart-ack: YELLOW 70 acknowledged 2026-07-30 — workspace validation not passing (0 failed, cloud#30516167217); manifest drift: tenant firewall (organ code) — 2 mismatch(es) vs PyAutoMind/repos.yaml; release validation stale: source moved since rehearsal (PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- prompt: active/plot_guides_legacy_removal_restructure.md
- classification: docs / workspaces — both (1-line PyAutoGalaxy library leg + workspace restructure); Brain scored large-8 off repo count, overridden to one task with 4 phases
- conflict-note: worktree_check_conflict flagged PyAutoGalaxy claimed by python-312-floor; hand-checked stale — phase-1d PR#535 merged, claiming checkout on main at the merge commit
- worktree: ~/Code/PyAutoLabs-wt/plot-guides-restructure
- repos:
  - PyAutoGalaxy (feature/plot-guides-restructure)
  - autolens_workspace (feature/plot-guides-restructure)
  - autogalaxy_workspace (feature/plot-guides-restructure)
  - autolens_assistant (feature/plot-guides-restructure)

## python-312-floor
- issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/142
- status: Phase 3 live release published; Phase 5A cleanup complete; Phase 5B COMPLETE 2026-07-30 — all tracked selectors now at 3.12+; parent awaits explicit human close (PyAutoNerves#142)
- library-pr: https://github.com/PyAutoLabs/PyAutoNerves/pull/143 (MERGED a9bf4561)
- prompt: active/python_312_floor_phase_1a_nerves.md
- phase-1b-issue: https://github.com/PyAutoLabs/PyAutoArray/issues/418
- phase-1b-prompt: active/python_312_floor_phase_1b_array.md
- phase-1b-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/419
- phase-1b-status: merged-unchanged (41c55a44; head ca98473a; CI 4/4 green)
- phase-1b-question: https://github.com/PyAutoLabs/PyAutoArray/issues/418#issuecomment-5115166953
- phase-1b-authorization: https://github.com/PyAutoLabs/PyAutoArray/issues/418#issuecomment-5115445646
- phase-1b-review: Claude Opus 5 CLEAN on the exact ca98473a tree
- phase-1c-issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1428
- phase-1c-prompt: active/python_312_floor_phase_1c_fit.md
- phase-1c-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1429
- phase-1c-status: merged-unchanged (241f2d69c; head 70d31a3e; CI 5/5 green)
- phase-1c-review: Claude Opus 5 CLEAN on the exact 70d31a3e tree
- phase-1d-issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/534
- phase-1d-prompt: active/python_312_floor_phase_1d_galaxy.md
- phase-1d-pr: https://github.com/PyAutoLabs/PyAutoGalaxy/pull/535
- phase-1d-status: merged-unchanged (b9d9927f; head 1c34f3c8; CI 5/5 green)
- phase-1d-review: Claude Opus 5 CLEAN on exact byte-identical review tree `cd8b35da`
- phase-1e-issue: https://github.com/PyAutoLabs/PyAutoLens/issues/663
- phase-1e-prompt: active/python_312_floor_phase_1e_lens.md
- phase-1e-pr: https://github.com/PyAutoLabs/PyAutoLens/pull/664
- phase-1e-status: merged-unchanged (b40fb0ba; head 5b42f3e4; CI 5/5 green)
- phase-1e-review: Claude Opus 5 CLEAN on exact byte-identical review tree `83b157014`
- phase-2-issue: https://github.com/PyAutoLabs/PyAutoHands/issues/206
- phase-2-prompt: active/python_312_floor_phase_2_build_health.md
- phase-2-hands-pr: https://github.com/PyAutoLabs/PyAutoHands/pull/207
- phase-2-heart-pr: https://github.com/PyAutoLabs/PyAutoHeart/pull/115
- phase-2-status: merged-unchanged (Hands `1e9ac6d5`, head `f2e990e0`; Heart `eda92a6b`, head `37783335`)
- phase-2-review: Claude Opus 5 CLEAN on both exact heads after two remediation rounds
- phase-2-hosted-matrix: https://github.com/PyAutoLabs/PyAutoHands/actions/runs/30453073189 (22/22 jobs green)
- phase-3-issue: https://github.com/PyAutoLabs/PyAutoHands/issues/208
- phase-3-prompt: active/python_312_floor_phase_3_core_release.md
- phase-3-status: live release `2026.7.29.2` published; packages valid; downstream workflow completed with five classified failures
- phase-3-fix-issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/116
- phase-3-fix-pr: https://github.com/PyAutoLabs/PyAutoHeart/pull/117
- phase-3-fix-status: merged-unchanged (bda57c16; reviewed head 8259dcfb; merged tree identical)
- phase-3-final-validation: https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/30472573498 (588 passed, 0 failed, 91 skipped, 0 timeouts; install A-F PASS)
- phase-3-heart: YELLOW 80 — workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s)
- phase-3-live-release: https://github.com/PyAutoLabs/PyAutoHands/actions/runs/30487799523 (31 success, 5 failure, 1 skipped)
- phase-3-live-authorization: https://github.com/PyAutoLabs/PyAutoHands/issues/208#issuecomment-5122957688
- phase-3-live-outcome: https://github.com/PyAutoLabs/PyAutoHands/issues/208#issuecomment-5123225967
- phase-3-pypi: autonerves/autofit/autoarray/autogalaxy/autolens `2026.7.29.2`; all unyanked with two artifacts and `Requires-Python >=3.12`
- phase-3-followups: assistant wiki-currency workflows still run Python 3.11; PyAutoHands pre-build commit `95f7502` accidentally staged `=3.12` and `run_logs/`; the AutoGalaxy nufftax smoke failure is within the already-acknowledged workspace-validation class
- phase-5-census: tracked active selectors below 3.12 remain in three assistant wiki workflows, PyAutoMemory validation, and six workspace/HowTo `runtime.txt` files; PyAutoHeart's Python 3.11 rejection job is intentional, while the PyAutoHands summary text and PyAutoFit `h5py>=3.11.0` dependency are not interpreter selectors
- phase-5a: COMPLETE — PyAutoHands#210, autofit_assistant#25, autolens_assistant#95, autocti_assistant#15, and PyAutoMemory#31 merged; related assistant baseline fixes #97/#98, #26/#27, and #16/#17 also merged green
- phase-5b: COMPLETE 2026-07-30 — six `runtime.txt` PRs merged unchanged (autofit_workspace#128, autogalaxy_workspace#189, autolens_workspace#399, HowToFit#40, HowToGalaxy#51, HowToLens#63); record: complete/2026/07/python-312-workspace-runtime-pins.md
- phase-3-release-decision: https://github.com/PyAutoLabs/PyAutoHands/issues/208#issuecomment-5121606547
- phase-3-fallbacks: autoconf `2026.7.15.1`; autoarray/autofit/autogalaxy/autolens `2026.7.29.1` (all unyanked, Requires-Python `>=3.9`)
- phase-3-question: https://github.com/PyAutoLabs/PyAutoHands/issues/208#issuecomment-5118261332
- phase-3-authorization: https://github.com/PyAutoLabs/PyAutoHands/issues/208#issuecomment-5118295258
- phase-4a-issue: https://github.com/PyAutoLabs/PyAutoCTI/issues/100
- phase-4a-prompt: active/python_312_floor_phase_4a_autocti.md
- phase-4a-pr: https://github.com/PyAutoLabs/PyAutoCTI/pull/101
- phase-4a-status: merged-unchanged (3ba4f7a3)
- phase-4b-issue: https://github.com/PyAutoLabs/PyAutoReduce/issues/59
- phase-4b-prompt: active/python_312_floor_phase_4b_autoreduce.md
- phase-4b-pr: https://github.com/PyAutoLabs/PyAutoReduce/pull/60
- phase-4b-status: merged-unchanged (d7bd916a)
- phase-4c-issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/113
- phase-4c-prompt: active/python_312_floor_phase_4c_heart.md
- phase-4c-pr: https://github.com/PyAutoLabs/PyAutoHeart/pull/114
- phase-4c-status: merged-unchanged (8fb1171f)
- phase-4d-issue: https://github.com/Jammy2211/euclid_assistant/issues/10
- phase-4d-prompt: active/python_312_floor_phase_4d_euclid_assistant.md
- phase-4d-pr: https://github.com/Jammy2211/euclid_assistant/pull/11
- phase-4d-status: merged-unchanged (51143df2); issue auto-closed
- next-phase: none — all phases complete; remaining act is the explicit human close of PyAutoNerves#142 (and PyAutoCTI#100, PyAutoReduce#59, PyAutoHeart#113)
- branch: none for the completed release; corrective follow-ups require normal task branches
- worktree: /home/jammy/Code/PyAutoLabs/.codex-worktrees/python-312-floor
- checkpoint-superseded: https://github.com/PyAutoLabs/PyAutoNerves/issues/142#issuecomment-5109079935
- resume-evidence: https://github.com/PyAutoLabs/PyAutoNerves/issues/142#issuecomment-5109572194
- queue-checkpoint: https://github.com/PyAutoLabs/PyAutoNerves/issues/142#issuecomment-5114496576
- commits: PyAutoNerves f06dd40, a3ed651 (pushed)
- opus-review: Claude Opus 5 CLEAN on all five exact PR heads; cross-repository
  consistency CLEAN; all five safe to merge in any order
- issue-close-status: euclid_assistant#10 auto-closed by its PR; PyAutoNerves#142,
  PyAutoCTI#100, PyAutoReduce#59, and PyAutoHeart#113 remain open for explicit
  human close authorization
- heart-ack: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s)
- repos:
  - PyAutoNerves: main (`a9bf4561`)
  - PyAutoArray: main (`41c55a44`)
  - PyAutoFit: main (`241f2d69`)
  - PyAutoGalaxy: main (`b9d9927f`)
  - PyAutoLens: main (`b40fb0ba`)
  - PyAutoCTI: main (`3ba4f7a3`)
  - PyAutoReduce: main (`d7bd916a`)
  - euclid_assistant: main (`51143df2`)
- notes: Phase 1A and all independent Phase 4 slices merged unchanged after a
  combined max-effort Claude Opus 5 review returned CLEAN for each exact head.
  Tests, CI where present, wheel metadata, smoke checks, dependency caps, live
  documentation, and protected historical/provenance scope were independently
  checked. Opus confirmed two planned release-sequencing hazards: the remaining
  four core library floors must rise before publication, and Heart's legacy
  below-floor install/banner checks must be rewritten in Phase 2. JAX 0.11 and
  Python 3.14 support remain separate follow-ups. Phase 1B merged unchanged as
  PyAutoArray#419 (`41c55a44`) after all four CI jobs passed the exact Claude
  Opus 5-reviewed head `ca98473a`; no release was performed. The human accepted
  the sole sequential smoke timeout as non-causal. Phase 1C now starts in
  PyAutoFit. A separate pre-existing PyNUFFT/SciPy dev-extra incompatibility was
  reproduced on unmodified main and recorded as a draft bug. Phase 1C is open
  as PyAutoFit#1429 at exact reviewed commit `70d31a3e`: both supported
  runtimes pass 1559 tests with one skip, wheel metadata is correct, Claude
  Opus 5 returned CLEAN, and Heart remains within the acknowledged YELLOW set.
  The identical accepted subhalo smoke timeout is the sole sequential failure.
  Phase 1C merged unchanged as PyAutoFit#1429 (`241f2d69c`) after all five CI
  checks passed the exact reviewed head. Phase 1D is open as PyAutoGalaxy#535
  at exact reviewed tree `1c34f3c8`: both supported runtimes pass 1009 tests,
  wheel metadata and the live census are correct, and the sole sequential
  smoke timeout is the exact accepted subhalo case. Opus 5 returned CLEAN
  after the separate pip-rollback documentation hazard was durably assigned
  to Phases 3 and 6 in Mind `e2acf4a`; Heart remains within the acknowledged
  YELLOW set. Phase 1D merged unchanged as PyAutoGalaxy#535 (`b9d9927f`)
  after all five CI checks passed the exact reviewed head. Phase 1E is
  registered as PyAutoLens#663; PyAutoHands remains deferred to Phase 2.
  Phase 1E merged unchanged as PyAutoLens#664 (`b40fb0ba`) after Claude Opus 5
  returned CLEAN on byte-identical review tree `83b157014` and all five CI
  checks passed exact head `5b42f3e4`. The full five-library core floor is now
  merged; no release or issue closure was performed. Advance to Phase 2.

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

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- session: claude --resume daaa46f9-aac5-48e2-9146-1202a92d879e
- status: library-merged, workspace-pending
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phases: 1 (design) + 2 (core API) COMPLETE; next: start_workspace on active/../draft phase-3 prompt (workspace_test jax_likelihood + profiling examples), then phase 4 (guides), then phase 5 (JAX solver gradients)
- repos:
