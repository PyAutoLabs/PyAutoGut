# Active Tasks

## python-312-floor
- issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/142
- status: Phase 3 live release published; Phase 5A cleanup complete; Phase 5B waiting on one workspace claim
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
- phase-5b: blocked only by `extra-galaxies-multi-galaxy` claiming autogalaxy_workspace — raise `runtime.txt` in autofit/autogalaxy/autolens_workspace and HowToFit/HowToGalaxy/HowToLens as one batch once that claim clears
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
- next-phase: run the six-file Phase 5B `runtime.txt` batch once autogalaxy_workspace is free; do not repeat the full ecosystem suite; source development remains unblocked
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

## scaling-relation-bgc-anchored
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/385
- session: claude --resume c351dadf-a66d-4a7e-891f-d8771123d77d
- status: workspace-dev
- scope: phase 1 of 2 — BGC-anchored scaling_relation packages for imaging + multi_galaxy
- phase-2-prompt: draft/docs/workspaces/scaling_relation_bgc_anchored_phase_2_interferometer_point_source.md (interferometer + point_source, mass-only regimes)
- parent-prompt: draft/docs/workspaces/scaling_relation_bgc_anchored_feature_packages.md (verbatim request + research findings)
- brain-override: Brain scored too-large/13 with four generic phases (design/core_api/workspace_examples/docs); overridden to two phases split by regime — one repo, zero library API change, so core_api was vacuous
- collision-cleared: launched authorised to run parallel to PR#383/#384, but both merged 2026-07-30T10:24-10:25Z before any edit — branch is off clean post-merge main, no "take ours" resolution needed
- heart-ack: YELLOW score 70 acknowledged by human 2026-07-30 for phase 1 ship; exact reasons:
  - "workspace validation not passing (0 failed, cloud#30516167217)"
  - "manifest drift: tenant firewall (organ code) — 2 mismatch(es) vs PyAutoMind/repos.yaml"
  - "release validation stale: source moved since rehearsal (PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)"
  (ack does not extend to any new reason)
- worktree: ~/Code/PyAutoLabs-wt/scaling-relation-bgc-anchored
- base: branched off post-merge main 264d4ab9 (includes PR#383 + PR#384)
- repos:
  - autolens_workspace (feature/scaling-relation-bgc-anchored)

## interferometer-subhalo-to-advanced
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/392
- status: workspace-dev
- prompt: active/interferometer_subhalo_to_advanced.md
- scope: `git mv` `scripts/interferometer/features/subhalo/` (6 files) + its `notebooks/` mirror (3 ipynb) into `features/advanced/subhalo/`, matching the imaging twin `scripts/imaging/features/advanced/subhalo/`; drop the `- subhalo:` bullet from `scripts/interferometer/features/README.md`; author the missing `scripts/interferometer/features/advanced/README.md`. Zero script-content change
- path-safety: scripts are location-independent — every dataset/output path is workspace-root-relative (`Path("dataset") / "interferometer" / dataset_name`). NO in-script edits
- refs: ZERO hand-written cross-references to `interferometer/features/subhalo` exist anywhere. All 12 occurrences are in GENERATED artifacts — `llms-full.txt` (3), `workspace_index.json` (3), `.script_sizes.json` (6). Regenerate, never hand-edit
- config-check: `config/build/no_run.yaml:41` excludes only the IMAGING twin (`imaging/features/advanced/subhalo/sensitivity/`); `profile_release.yaml` has no subhalo pattern. Expect NO config edit — confirm by re-grepping `config/build/` after the move, don't assume
- no-smoke-coverage: `smoke_tests.txt` has NO interferometer subhalo entry (16 entries; only `interferometer/modeling.py` + `interferometer/features/pixelization/delaunay.py`). The curated smoke set will NOT exercise this move — proof is generator-clean + the three notebooks reappearing at the new paths + `simulator.py` running from the workspace root + a post-move grep for `features/subhalo` empty outside imaging
- FINDING-extension-filtered-grep-missed-a-real-ref: the pre-plan sweep used `--include="*.py" --include="*.md"` … and so MISSED `.navigator_check_ignore:7`, a DOTFILE holding a hand-written path to the moved script. Only an UNRESTRICTED grep (excluding just `.git` + the 3 generated artifacts) found it. Re-pointed to the new path. CONTROL-TESTED both ways with `autohands.check_navigator --ignore-file`: stale entry → "Banner lint: 1 banner-style comment(s)" (CI FAILS); re-pointed → "Banner lint: OK". The entry is load-bearing because `sensitivity/start_here.py` is fully commented out, so its `===` docstring underline reads as a `#`-banner. Lesson: never extension-filter a pre-move reference sweep
- verified: moved `simulator.py` runs clean (exit 0, 7 outputs) from the workspace root under `PYAUTO_SMALL_DATASETS=1`; `dataset/.gitignore` is `*` so no binary-leak risk. Remaining stale refs are ONLY `llms-full.txt` (3) + `workspace_index.json` (3) — regenerated, never hand-edited
- pre-existing-not-fixed: `subhalo/sensitivity/start_here.py` is ENTIRELY commented out (every line incl. the docstring) — a disabled placeholder; the move neither breaks nor repairs it. Interferometer subhalo also has no per-folder READMEs while imaging has three (`subhalo/`, `detect/`, `sensitivity/`) — human-confirmed out of scope
- brain-override: Brain scored large/9 + split-into-phases with a "public-API change may ripple downstream" risk — VACUOUS, no library code is touched. Same repo-count-proxy misfire as `potential-correction-start-here` (too-large/12). Overridden to ONE phase
- parallel-claim: human-authorised alongside `scaling-relation-bgc-anchored` (#385), `extra-galaxies-multi-galaxy-lens` (#387), `potential-correction-start-here` (#389), `dspl-terminology-rename` (#390), all claiming autolens_workspace. Each worktree's ACTUAL diff hand-checked disjoint. NOTE #389 modifies `scripts/interferometer/features/advanced/potential_correction/start_here.py` — a different file inside this task's DESTINATION parent; git tracks files not directories, so the `git mv` does not touch it. Only overlap is the regenerated catalogue — whichever merges last rebases and re-runs the generator
- heart-ack: human-acknowledged YELLOW (score 70, no RED) at ship time, exact reason set — "workspace validation not passing (0 failed, cloud#30516167217)"; "manifest drift: tenant firewall (organ code) — 2 mismatch(es) vs PyAutoMind/repos.yaml"; [stale] "release validation stale: source moved since rehearsal (PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)". Does NOT extend to new reasons
- base-drift: worktree was cut at `f5d03984`, but #391 (extra-galaxies-multi-galaxy-lens) merged mid-task making origin/main `9b274ff2`. Pre-merged origin/main into the branch BEFORE regenerating and opening the PR — conflict-free, and it means the catalogue was regenerated on top of #391's entries rather than reverting them
- script-sizes-decision: `check_sizes.sh --update` rewrites 138/129 lines because `.script_sizes.json` is ALREADY stale repo-wide (cluster/, group/, double_einstein_ring… all drifted). Refused to bake that unrelated drift into a folder-move PR; instead re-keyed ONLY the 6 moved entries via a script, sizes byte-identical (proving a pure move). Note stale keys are IGNORED silently by the checker — it still exits 0 — so a moved script loses truncation protection with no warning. Pre-existing repo-wide snapshot drift is an open hygiene item
- commits: `151c9145` (move + READMEs + navigator ignore), `12537fe4` (regenerated notebooks/catalogue + re-keyed sizes)
- worktree: ~/Code/PyAutoLabs-wt/interferometer-subhalo-to-advanced
- repos:
  - autolens_workspace (feature/interferometer-subhalo-to-advanced)
