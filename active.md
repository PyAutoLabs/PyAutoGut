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

## python-312-autolens-wiki-currency-ci
- issue: https://github.com/PyAutoLabs/autolens_assistant/issues/94
- status: awaiting-merge
- workspace-pr: https://github.com/PyAutoLabs/autolens_assistant/pull/95 (OPEN, pending-release)
- prompt: active/python_312_autolens_wiki_currency_ci.md
- branch: feature/python-312-release-surfaces
- worktree: ~/Code/PyAutoLabs-wt/python-312-release-surfaces
- parent: python-312-floor
- repos:
  - autolens_assistant: feature/python-312-release-surfaces
- notes: Python 3.12 version, symbol, and idiom checks pass. Merge remains
  blocked by unrelated baseline drift: unclassified `AI_POLICY.md` and the
  missing `autolens_workspace:scripts/guides/hpc/example_cpu.py` citation.

## python-312-memory-validation-ci
- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/30
- status: workspace-dev, ship-blocked
- prompt: active/python_312_memory_validation_ci.md
- branch: feature/python-312-release-surfaces
- worktree: ~/Code/PyAutoLabs-wt/python-312-release-surfaces
- parent: python-312-floor
- repos:
  - PyAutoMemory: feature/python-312-release-surfaces
- notes: Python 3.12 workflow selector is staged but uncommitted. Shipping is
  blocked by the pre-existing `AI_POLICY.md` structure-test failure on current
  `origin/main`; do not broaden this task to fix that unrelated regression.

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

## assistant-output-folder-pointer
- issue: https://github.com/PyAutoLabs/autolens_assistant/issues/96
- session: claude --resume 6a3b0456-4835-4b11-9d18-fcb9ad9087f3
- status: awaiting-merge
- workspace-prs: https://github.com/PyAutoLabs/autolens_assistant/pull/97, https://github.com/PyAutoLabs/autofit_assistant/pull/26, https://github.com/PyAutoLabs/autocti_assistant/pull/16 (all OPEN, pending-release)
- heart-ack: 2026-07-30 — YELLOW 65, all three reasons pre-existing and structurally unrelated to markdown-only assistant edits: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); release validation stale: source moved since rehearsal (PyAutoFit, PyAutoGalaxy, PyAutoLens)
- ship-evidence: `audit_skill_apis.py` 0 missing/broken in autolens (66 files/124 symbols) and autofit (29/38); autocti NOT verifiable locally (`autocti` not installed → all 18 misses are `ModuleNotFoundError`, on pre-existing symbols). CI: autofit#26 and autocti#16 fully GREEN
- ci-preexisting-reds: autolens#97 hit two failures NEITHER caused by this branch. (1) `wiki-currency --check-citations`: `wiki/core/operations/hpc.md` still cited `autolens_workspace:scripts/guides/hpc/example_cpu.py`, renamed to `example_cpu_and_gpu.py` by autolens_workspace#360 (b0836b72), and `batch/` which is now `batch_cpu/` + `batch_gpu/` — FIXED in this PR (commit da75c27; 407 citations, 0 missing). (2) `clone-boundary`: `AI_POLICY.md` unclassified, red on EVERY branch since feature/ai-policy merged 2026-07-27 — filed as draft/bug/pyautobrain/clone_boundary_ai_policy_unclassified.md, NOT fixed here (needs autolens_assistant `modes/maintainer.md` + PyAutoBrain `_clone.py` together)
- prompt: active/output_folder_layout_pointer.md
- scope: three assistant cells gain an "announce the output folder at fit launch" rule for novice/teacher-mode users — a new `## Output folder announcement` section in each `skills/_style.md` (sibling of `## Plot output and path announcement`), a `modes/teacher.md` bullet, and the pointer wired into the fit-launch skills (`al_run_search`, `al_configure_search`, `af_run_search`, `ac_fit_cti_model`)
- citations: pointer ONLY, never a copied tree (it would rot) — autolens → `autolens_workspace/scripts/imaging/modeling.py` `__Output Folder Layout__` (:548-585); autofit → `autofit_workspace/scripts/overview/overview_2_scientific_workflow.py` (:197-223); autocti → `autocti_workspace/scripts/dataset_1d/modeling/start_here.py` `__Output Folder__` + `__On The Fly Outputs__` (:346-371)
- depth-gate: reuses the EXISTING cue in `skills/_style.md` "Adaptive depth" / "Newcomer mode" — no second depth rule invented
- out-of-scope: `euclid_assistant` (the Feature Agent listed it, but it is a paper repo with no `modes/` and no `skills/`); there is no `autogalaxy_assistant`, so the lens cell carries the galaxy citation. No `## Further reading` edit and no new row in `wiki/core/external/skill_citation_map.md` — those blocks are generated from that table and this is not a per-skill citation row. `llms.txt` is hand-maintained, not generated from `skills/`
- brain-override: Feature Agent returned too-large (score 11) / split-into-4-phases (design, core_api, workspace_examples, docs) off its repo-count proxy ([[feedback_brain_repo_count_difficulty_proxy]]). Three of the four phases are vacuous — no library code, no API, no workspace example. Overridden to one task, one PR per repo (~10 markdown edits of uniform shape)
- parallel-claim: `worktree_check_conflict` FIRED on all three repos — `python-312-auto{lens,fit,cti}-wiki-currency-ci` claim them from worktree `~/Code/PyAutoLabs-wt/python-312-release-surfaces`, each with an OPEN pending-release PR (autolens_assistant#95, autofit_assistant#25, autocti_assistant#15). Human decision 2026-07-30: proceed in parallel — every one of those PRs changes exactly ONE file, `.github/workflows/wiki-currency.yml` (verified via `gh api .../pulls/N/files`), so there is zero overlap with `modes/` + `skills/`, and they are blocked on the next release merging. (Contrast [[feedback_worktree_conflict_guard_never_fires]]: the guard DOES fire when the claim uses the `  - <repo>: <branch>` form, which these entries do)
- ci-note: each repo's `wiki-currency` workflow runs on pull_request and audits `skills/` + `wiki/` + `AGENTS.md` + `llms.txt` for stale API symbols — validate locally with `make audit` before shipping. `pending-release` label already present on all three repos
- worktree-base: branched off origin/main — autolens_assistant `89a2cc3`, autofit_assistant `d83500e`, autocti_assistant `1907634` (all verified equal to origin/main, [[feedback_worktree_base_drifts_from_main]])
- worktree: ~/Code/PyAutoLabs-wt/assistant-output-folder-pointer
- repos:
  - autolens_assistant: feature/assistant-output-folder-pointer
  - autofit_assistant: feature/assistant-output-folder-pointer
  - autocti_assistant: feature/assistant-output-folder-pointer

## remove-finish-docstring-hack
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/211
- session: claude --resume 60926d52-cc7f-4e42-8d79-92a618520f05
- status: library-dev
- prompt: active/remove_finish_docstring_hack.md
- scope: PyAutoHands `add_notebook_quotes` fix + 3 regression tests, then remove all 166 `Finish.` / `Finished.` occurrences across 10 workspace repos and regenerate artifacts
- root-cause: `py2nb` splits the intermediate `.py` on `'\n\n# %%\n'` but the docstring-OPENER branch (`add_notebook_quotes.py:133`) emits `'# %%\n'` after a SINGLE newline, so a docstring opened on the line immediately after code never splits — the marker and both `'''` delimiters land inside the preceding code cell as literal text. 13 committed notebook code cells are SyntaxError today (autolens_workspace 4, autogalaxy_workspace 3, autocti_workspace 4, HowToLens 2). The CLOSING path is fine (it emits `"'''", "\n\n"` first)
- finding: the hack itself is already obsolete — deleting the trailing block from `imaging/features/no_lens_light/slam.py` (23→22 cells) and `imaging/features/pixelization/source_science.py` (41→40) through the real conversion chain gives a complete unmangled final code cell, as does every other tail shape (no trailing newline / trailing blanks / trailing comment). So step 1 is a regression test pinning that, plus the separate live bug above
- fix-constraints: the blank line must be emitted ONLY when `out` is non-empty (`py2nb` strips a LEADING `# %%\n` header; a leading `\n` defeats that strip and yields a spurious empty first code cell) and ONLY when not already blank-terminated (unconditional emission appends a trailing blank line to EVERY code cell and churns every notebook in every workspace)
- merge-gate: the PyAutoHands PR must land on main before any workspace regeneration — workspaces invoke `../PyAutoHands/autohands/generate.py` from the local checkout
- shapes: 126 sole-content trailing blocks at EOF; 33 lines inside a block that continues (`__Env__`, `__JAX Variant__`); 2 `Finished.` leading a real sentence (drop the word only); 2 empty `__Finish__` headers; 5 indented-in-function or commented-out. A blanket regex over all five is wrong
- markdown-decision: human-approved 2026-07-30 — delete the paragraph IN PLACE in the 5 curated pages rather than re-running `generate_markdown.py`, which re-executes real model fits and re-quantizes every figure PNG ([[feedback_ship_workspace_binary_leak]]). Most `Finish` hits under `markdown/` are Nautilus status tables (`Finished | 18 | 1 | …`) and must be left alone
- brain-override: Feature Agent returned too-large (score 29) / split-into-4-phases (design, core_api, workspace_examples, docs) off its repo-count proxy ([[feedback_brain_repo_count_difficulty_proxy]]). `design` and `core_api` are vacuous (no library API touched) and `docs` is empty — the convention is documented NOWHERE (`AGENTS.md`, `CONTRIBUTING.md`, `PyAutoHands/docs/`, Brain skills all checked). Overridden to one PR per repo behind a single PyAutoHands-first gate
- parallel-claim: human decision 2026-07-30 — proceed in parallel. `autolens_workspace` is claimed by THREE tasks, `autogalaxy_workspace` by one, `autolens_workspace_test` by `vacuous-jax-assertions`, `PyAutoHands` by `python-312-release-surfaces` (live uncommitted work in `.gitignore`, `bin/autohands`, `docs/internals.md`, `pre_build.sh`, `run_logs/` — zero overlap with `autohands/add_notebook_quotes.py` + its test). Hand-read; the guard reported nothing ([[feedback_worktree_conflict_guard_never_fires]])
- carve-out: SKIP `autolens_workspace/scripts/multi_galaxy/simulator.py` — one `Finished.` line, uncommitted in `multi-galaxy-imaging-parity`'s worktree. It is the ONLY script-level overlap; the other 8 files the contending branches touch carry zero occurrences
- follow-up: a column-0 CLOSING `"""` of a triple-quoted string literal in code toggles docstring state the same way — one occurrence, `autolens_workspace_test/gallery/gallery_build.py:42`, outside `scripts/` so never converted. Needs tokenization, not a line-prefix test; file as its own prompt
- worktree: ~/Code/PyAutoLabs-wt/remove-finish-docstring-hack
- repos:
