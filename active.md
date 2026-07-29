# Active Tasks

## python-312-floor
- issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/142
- status: Phase 3 validation passed; corrective PR merged; live release held on Heart YELLOW
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
- phase-3-status: rehearsal and definitive Stage 3 validation passed; corrective PyAutoHeart PR merged unchanged; live release not dispatched
- phase-3-fix-issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/116
- phase-3-fix-pr: https://github.com/PyAutoLabs/PyAutoHeart/pull/117
- phase-3-fix-status: merged-unchanged (bda57c16; reviewed head 8259dcfb; merged tree identical)
- phase-3-final-validation: https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/30472573498 (588 passed, 0 failed, 91 skipped, 0 timeouts; install A-F PASS)
- phase-3-heart: YELLOW 80 — workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code) — 6 mismatch(es) vs PyAutoMind/repos.yaml
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
- next-phase: resolve or refresh the three current Heart YELLOW reasons before live release; source development is unblocked and no duplicate full-main suite is needed
- branch: none for Phase 3 — release must use the recorded exact `main` heads
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
- heart-ack: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code) — 6 mismatch(es) vs PyAutoMind/repos.yaml; release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- repos:
  - PyAutoNerves: main (`a9bf4561`)
  - PyAutoHands: main (`1e9ac6d5`)
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

## contributing-natural-language-reframe
- issue: https://github.com/PyAutoLabs/PyAutoScientist/issues/9
- status: workspace-shipped, awaiting-merge
- prompt: active/contributing_natural_language_reframe.md
- workspace-pr: https://github.com/PyAutoLabs/PyAutoScientist/pull/10 (pending-release labelled; repo has no CI workflows)
- scope: docs prose only — PyAutoScientist CONTRIBUTING.md (rewrite) + README.md (positioning prose); generated organs table verified byte-identical
- heart-ack: 2026-07-29 — workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code) — 6 mismatch(es) vs PyAutoMind/repos.yaml (all pre-existing, none in PyAutoScientist)
- verdict: natural-language-first reframe shipped. CONTRIBUTING.md rewritten with the trust-first testing section (measured figures: ~3,900 unit tests; ~960 workspace/tutorial scripts run as release validation across 10 repos), the PyAutoScientist/organs explainer, and three contribution routes. README.md headline moved off "human-led AI ... organism" to natural-language-first.
- resume-next: (1) merge PR#10 + close #9 (human); (2) post-merge cleanup (worktree, branch, complete/2026/07 record)
- worktree: ~/Code/PyAutoLabs-wt/contributing-natural-language-reframe
- repos:
  - PyAutoScientist (feature/contributing-natural-language-reframe)

## hygiene-refs-readme-drift
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/177
- status: library-dev
- prompt: active/hygiene_refs_readme_drift_class.md
- scope: phase 1 of 3 — widen `_hygiene_refs.py` (scanned set + 3 new reference shapes) + tests + mode docs; read-only scanner, no repo mutation
- phases: (1) this — hygiene refs scanner; (2) draft/docs/workspaces/workspace_readme_drift_sweep.md — sweep autolens+autogalaxy READMEs; (3) draft/feature/pyautohands/navigator_check_readme_ref_shapes.md — CI gate, lands AFTER phase 2 merges
- brain-override: Feature Agent scored large/split-into-phases off its repo-count proxy; split already applied (this is phase 1), single repo — override recorded
- heart-ack: 2026-07-29 — YELLOW 80: workspace validation not passing (13 failed); 33 stale parked script(s); manifest drift tenant firewall (all pre-existing, none related to a read-only Brain scanner)
- worktree: ~/Code/PyAutoLabs-wt/hygiene-refs-readme-drift
- repos:
  - PyAutoBrain (feature/hygiene-refs-readme-drift)

## multistart-prodigy-start-here
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/366
- status: workspace-dev
- prompt: active/multistart_prodigy_in_start_here.md
- scope: 8 of 13 dataset-type start_here.py convert to af.MultiStartProdigy; 5 stay on af.Nautilus with a "not available here" note; all 13 modeling.py get a 2-3 line Search-docstring mention with ZERO code
- blocked-cells: autolens point_source + cluster (AnalysisPoint — point-source JAX gradients do not exist; draft/feature/autolens/point_source_chi_squared_paper_variants_phase_5_jax_gradients.md blocked on phase 2); autolens weak (use_jax=False pinned by PyAutoLens#614, confirmed OPEN); autolens multi + autogalaxy multi (multi-band FactorGraphModel value_and_grad cold compile unbounded on CPU, >2h observed — draft/research/autofit/multi_band_factorgraphmodel_value_and_grad_cold.md, whose named reproducer IS autolens multi/start_here.py)
- brain-override: Feature Agent returned too-large (score 10) / split-into-phases (design, core_api, workspace_examples, docs) off its repo-count proxy; core_api phase is vacuous (no library code touched at all). Overridden to one PR — uniform prose + search-swap sweep over 26 files in 2 repos
- smoke-caveat: PYAUTO_TEST_MODE=2 skips search sampling, so smoke does NOT exercise a real MultiStartProdigy fit — needs a separate no-test-mode spot check
- worktree: ~/Code/PyAutoLabs-wt/multistart-prodigy-start-here
- repos:
  - autolens_workspace (feature/multistart-prodigy-start-here)
  - autogalaxy_workspace (feature/multistart-prodigy-start-here)

## assistant-start-here-scripts
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/367
- status: workspace-dev
- prompt: active/assistant_section_workspace_start_here_scripts.md
- scope: the one surface `assistant-first-docs` (PyAutoLens#645, complete 2026-07-24) missed — the ROOT start_here.py of each workspace. autolens: replace `__Three Ways To Learn PyAutoLens__` (lines 353-372, the Manual Navigation / AI Chat Assistant / Fully Agentic AI split) with one `__PyAutoLens AI Assistant__` section mirroring the shipped README/RTD wording. autogalaxy: has NO AI section at all — add the equivalent between `__Wrap Up__` and `__What Data Type?__`
- autogalaxy-404: https://github.com/PyAutoLabs/autogalaxy_assistant does not exist (gh API 404). Keeping the link is the already-recorded decision — the assistant-first-docs completion record states the URL "is intentionally allowed to return 404 until its repository is created", and it already ships in the AG README + RTD. Re-confirmed by the human 2026-07-29. Neither workspace runs a url_check workflow, so no CI gate is involved
- brain-override: Feature Agent scored large (6) / split-into-phases off its repo-count proxy; actual change is a ~20-line prose edit in one file per repo, identical in shape — overridden to one PR
- parallel-claim: `multistart-prodigy-start-here` (#366) claims the SAME two repos. Human decision 2026-07-29: proceed in parallel — zero source-file overlap (that task edits `scripts/<type>/start_here.py`, this one the ROOT `start_here.py`). Only the GENERATED artifacts collide (notebooks/, start_here.ipynb, markdown/, llms-full.txt, workspace_index.json); whichever PR merges second must re-run generate.py + generate_markdown.py rather than hand-resolve
- regen-note: markdown/start_here.md is NOT produced by generate.py — it comes from PyAutoHands `generate_markdown.py --only start_here.py`, which EXECUTES the script for real figures and hard-exits if PYAUTO_TEST_MODE is set. Cheap here: neither root start_here.py imports autofit or runs a fit
- retire-candidate: draft/docs/workspaces/unify_ai_assistant_workspace_readmes.md ("Phase 2: workspace READMEs assistant-first") is already satisfied — assistant-first-docs lists autolens_workspace#329 + autogalaxy_workspace#155 as merged and both READMEs carry the unified section today
- worktree: ~/Code/PyAutoLabs-wt/assistant-start-here-scripts
- repos:
  - autolens_workspace (feature/assistant-start-here-scripts)
  - autogalaxy_workspace (feature/assistant-start-here-scripts)

## register-tenant-firewall-surfaces
- issue: https://github.com/PyAutoLabs/PyAutoMind/issues/114
- session: codex
- status: library-dev
- prompt: active/register_recent_tenant_firewall_surfaces.md
- scope: declare the six intentional Brain/Hands instance-fact surfaces introduced after the frozen tenant-firewall baseline; no organ-source changes
- worktree: ~/Code/PyAutoLabs-wt/register-tenant-firewall-surfaces
- repos:
