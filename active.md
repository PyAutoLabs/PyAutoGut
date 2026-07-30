# Active Tasks

## python-312-floor
- issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/142
- status: Phase 3 live release published; two corrective tracks remain
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
- phase-5a: unconflicted — PyAutoHands staging cleanup/guard plus Python 3.12 in autofit_assistant, autolens_assistant, autocti_assistant, and PyAutoMemory CI
- phase-5b: blocked by current task claims — raise `runtime.txt` in autofit/autogalaxy/autolens_workspace and HowToFit/HowToGalaxy/HowToLens after their active branches merge
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
- next-phase: complete Phase 5A with targeted static/CI checks, then Phase 5B after the six claimed repos are free; do not repeat the full ecosystem suite; source development remains unblocked
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

## python-312-prebuild-debris-guard
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/209
- status: library-dev
- prompt: active/python_312_prebuild_debris_guard.md
- branch: feature/python-312-release-surfaces
- worktree: ~/Code/PyAutoLabs-wt/python-312-prebuild-debris-guard
- parent: python-312-floor
- repos:
  - PyAutoHands: feature/python-312-release-surfaces
- notes: Remove the recoverable `95f7502` debris, prevent future whole-repo
  pre-build staging, update canonical docs, and run focused checks only.

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

## likelihood-function-jax-pointer
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/368
- status: workspace-dev
- prompt: active/likelihood_function_jax_section_to_pointer.md
- scope: six `likelihood_function.py` scripts (autolens imaging/interferometer/group/cluster, autogalaxy imaging/interferometer) lose their trailing 25-45 line `__JAX__` block; each gains a `__JAX__` heading + ONE sentence at the end of the opening header docstring (after `__Contents__`) pointing at `scripts/guides/using_jax.py`, plus a `__JAX__` bullet as the FIRST `__Contents__` entry. The deleted detail migrates into `scripts/guides/using_jax.py` in BOTH workspaces as a new `__Custom Likelihood Functions__` section
- guide-content: the new guide section shows a likelihood function JAX-compiled two ways — (a) via the `Analysis` object (`al.AnalysisImaging(dataset=dataset)`, `use_jax=True` default, `@jax.jit` around `analysis.log_likelihood_function(instance=instance)`) and (b) via `Fitness` (`from autofit.non_linear.fitness import Fitness` — NOT exported as `af.Fitness`; `fitness._vmap(jnp.array([parameters]))[0]`). Plus the hand-rolled `Tracer`+`FitImaging` pattern with `autolens.jax.register_tracer_classes(tracer)` (autogalaxy: `ag.AnalysisImaging` init registers pytrees as a side effect) and the interferometer `TransformerDFT`-not-`TransformerNUFFT` caveat
- contents-bullet: human decision 2026-07-29 — ADD a `__JAX__` bullet to all six `__Contents__` lists (they list no JAX entry today), as the first entry, since the section now sits immediately after the list
- cluster-exception: cluster's block is `FitPositionsSource`-shaped, not `FitImaging`. It is REDUCED to the pointer, NOT migrated — folding a point-source recipe into an imaging-shaped guide example would muddy it; `cluster/modeling.py` already carries the `AnalysisPoint(use_jax=True)` path
- brain-override: Feature Agent returned too-large (score 13) / split-into-4-phases off its repo-count proxy ([[feedback_brain_repo_count_difficulty_proxy]]). Actual change is 8 docstring-only files of uniform shape — overridden to one PR per repo
- parallel-claim: `multistart-prodigy-start-here` (#366) and `assistant-start-here-scripts` (#367) BOTH claim the same two repos. Human decision 2026-07-29: proceed in parallel — zero source-file overlap (those edit `start_here.py`; this edits `likelihood_function.py` + `guides/using_jax.py`). Only the GENERATED artifacts collide (notebooks/, llms-full.txt, workspace_index.json); whichever PR merges last must re-run generate.py rather than hand-resolve
- guard-bug: `worktree_check_conflict` reported NO conflict on both repos despite the two claims above. `worktree_list_claimed` (PyAutoBrain/bin/worktree.sh:326-333) parses `  - <repo>: <branch>` but active.md writes `  - <repo> (<branch>)`, so `repo` swallows the branch and the `==` compare at :346 never matches — the guard has never fired for any task. Filed as draft/bug/pyautobrain/worktree_check_conflict_never_fires.md; NOT fixed in this task
- heart-ack: 2026-07-29 — YELLOW 80, both reasons pre-existing and unrelated to a docstring-only docs change: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s)
- finding: the `@jax.jit` recipe in ALL SIX deleted `__JAX__` blocks did not run. Two independent failures, reproduced in both workspaces: (1) `register_tracer_classes(tracer)` (autolens) / constructing an `AnalysisImaging` (autogalaxy) does NOT let a `ModelInstance` cross the jit boundary — that needs `autofit.jax.pytrees.enable_pytrees()` + `register_model(model)`, which only `Fitness.__init__` does automatically (fitness.py:125-130); (2) even past that, a hand-rolled `FitImaging` without `xp=jnp` raises `TracerArrayConversionError`. The autogalaxy blocks' claim that `AnalysisImaging.__init__` runs `_register_fit_imaging_pytrees()` is false — it is called from `fit_from`, not `__init__`. The guide carries the VERIFIED recipe instead of a copy
- verification: all three published guide paths (jit-around-Analysis, hand-rolled+`xp=jnp`, `Fitness._vmap`) executed verbatim and agree with the eager NumPy reference to ~1e-15; all six likelihood_function.py scripts run green; `check_sizes.sh` OK
- worktree: ~/Code/PyAutoLabs-wt/likelihood-function-jax-pointer
- repos:
  - autolens_workspace (feature/likelihood-function-jax-pointer)
  - autogalaxy_workspace (feature/likelihood-function-jax-pointer)

## extra-galaxies-point-source
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/374
- status: workspace-dev
- prompt: active/extra_galaxies_feature_parity_phase_1_point_source.md
- parent: draft/docs/workspaces/extra_galaxies_feature_parity.md (phase 2 = multi_galaxy, both workspaces, not yet issued)
- scope: new `scripts/point_source/features/extra_galaxies/{README.md,__init__.py,simulator.py,modeling.py}` — NO slam.py (user-specified). Mass-only example: point-source data has no image pixels, so there is nothing to noise-scale and no extra-galaxy light to fit; extra galaxies perturb the deflection field and therefore the solved multiple-image positions. Plus `point_source/features/README.md` `# Folders` entry
- library-support: verified, NO library change needed — `AnalysisPoint(AgAnalysis, AnalysisLens)` (PyAutoLens/autolens/point/model/analysis.py:36) inherits `tracer_via_instance_from`, which appends `instance.extra_galaxies` to the tracer's galaxy list (PyAutoLens/autolens/analysis/analysis/lens.py:127-129)
- smoke-trap: NO point-source script is smoke-enabled. `smoke_tests.txt:7` disables `point_source/start_here.py` for a bypass-mode tuple-path KeyError (rhayes777/PyAutoFit#1179), so `PYAUTO_TEST_MODE=2` cannot validate these scripts. Add the new modeling.py as a COMMENTED-DISABLED entry citing the same reason and validate with a real short run (`PYAUTO_TEST_MODE=1`)
- brain-override: Feature Agent returned too-large (score 13) / split-into-4-phases (design, core_api, workspace_examples, docs) off its repo-count proxy ([[feedback_brain_repo_count_difficulty_proxy]]). The `core_api` and `design` phases are vacuous — no library code is touched at all. Overridden to two phases split by REGIME (point_source; multi_galaxy)
- parallel-claim: `likelihood-function-jax-pointer` (#368) also claims autolens_workspace. Human decision 2026-07-29: proceed in parallel — zero source-file overlap (this task creates only NEW folders). Only the GENERATED artifacts collide (notebooks/, llms-full.txt, workspace_index.json); whichever PR merges last must re-run generate.py. `multistart-prodigy-start-here` (#366) MERGED 2026-07-29 and is no longer a claim
- out-of-scope: `group/` (already uses the extra-galaxies API in start_here.py + modeling.py — user confirmed nothing to change) and `cluster/` (user confirmed it is right not to document them). `imaging/` + `interferometer/` in both workspaces are the confirmed STANDARD to copy
- worktree: ~/Code/PyAutoLabs-wt/extra-galaxies-point-source
- repos:
  - autolens_workspace (feature/extra-galaxies-point-source)

## multi-galaxy-imaging-parity
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/370
- status: workspace-dev
- prompt: active/multi_galaxy_parity_with_imaging.md
- scope: bring `scripts/multi_galaxy/` to `scripts/imaging/`'s teaching depth — trim start_here's `__Model__` + add its missing sections (extra-galaxy removal + GUI, pre-search `__JAX__`, iterations-per-update, live-visual-update, both `__Simulator__` blocks); rewrite modeling.py (327 lines) and fit.py (166) against their imaging counterparts; add `likelihood_function.py` / `simulator_sample.py` / `source_science.py`; delete `__Mass/Light Offsets__` package-wide
- extra-galaxies: human decision 2026-07-29 — `multi_galaxy/simulator.py` gains a faint extra galaxy + writes `mask_extra_galaxies.fits` mirroring `imaging/simulator.py`, so `__Extra Galaxies Noise Scaling__` lands in start_here/modeling/fit/likelihood_function too. `dataset/multi_galaxy/**` is gitignored so NO committed binary. Trap: `should_simulate` tests directory EXISTENCE only, so `rm -rf dataset/multi_galaxy/simple` before any run ([[feedback_should_simulate_existence_only]])
- unblocked: autolens_workspace#366 MERGED + closed 2026-07-29T19:00Z; worktree based on origin/main `8aa1087c` which carries its `af.MultiStartProdigy` swap. Its multi_galaxy + imaging edits are PRESERVED, not reverted — start_here keeps `MultiStartProdigy` + `__Multi Start Gradient Optimization__` + `__Posterior__`, and `__Iterations Per Update__` is written against gradient-step semantics (`n_steps` / `iterations_per_quick_update=50`), NOT Nautilus's cadence
- likelihood-function-convention: autolens_workspace#368 retires the trailing 25-45 line `__JAX__` block in every `likelihood_function.py` for a one-sentence pointer at `scripts/guides/using_jax.py` + a `__JAX__` bullet as the FIRST `__Contents__` entry. The new `multi_galaxy/likelihood_function.py` is written in that NEW shape; #368 gains a seventh script
- brain-override: Feature Agent scored large (9) / split-into-phases off its repo-count proxy ([[feedback_brain_repo_count_difficulty_proxy]]); one directory of one repo with cross-referencing scripts — overridden to one PR
- guard-note: `worktree_check_conflict` returned 0 but never fires ([[feedback_worktree_conflict_guard_never_fires]]); the #366 collision was found by hand-diffing its worktree
- worktree: ~/Code/PyAutoLabs-wt/multi-galaxy-imaging-parity
- repos:
  - autolens_workspace (feature/multi-galaxy-imaging-parity)
