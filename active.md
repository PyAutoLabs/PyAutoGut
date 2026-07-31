# Active Tasks

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- status: library-dev — phase 5 (PointSolver implicit-diff gradients) IN FLIGHT (started 2026-07-31; plan approved with feasibility gate — negative result is an acceptable close; human warned of difficulty, gravity.jl comparison done: paper itself uses implicit diff at solved positions, never through the solver)
- worktree: ~/Code/PyAutoLabs-wt/point-solver-implicit-diff
- prompt: active/point_source_chi_squared_paper_variants_phase_5_jax_gradients.md (binding equations + phase-1 deltas inside)
- claim-note: PyAutoLens + autolens_workspace_test held CONCURRENTLY with potential-correction-validation (#672) — human-authorized via plan approval 2026-07-31; #672 touches only autolens/potential_correction/** and wst phase2_experiments/ (disjoint); pre-merge origin/main before each PR
- phase-4-pr: autolens_workspace#425 (MERGED 2026-07-31, human merge; record complete/2026/07/point-source-solved-guides.md; comment https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5141094763)
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phase-3-pr: workspace_test#237, profiling#96, workspace_developer#121 (ALL MERGED 2026-07-30; worktree + branches cleaned; shipped comment https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5135275039)
- phases: 1 (design) + 2 (core API) + 3 (examples/profiling) + 4 (guides) COMPLETE. Phase 5 (PointSolver custom_jvp gradients, draft phase-5 prompt) touches PyAutoLens (+PyAutoArray) — NOTE PyAutoLens is claimed by potential-correction-validation (#672); hand-check file overlap before starting.
- resume-context: project memory `point-source-solved-likelihoods` holds phase-3 literals + lessons (H0-matched parity for time-delay fits; fit_from pytree gap is the ONLY remaining jit blocker; output_to_json key-order nondeterminism filed in ideas.md; profiling baselines used PointFlux so solved swap drops 3 params not 2)
- repos:
  - PyAutoLens: feature/point-solver-implicit-diff
  - autolens_workspace_test: feature/point-solver-implicit-diff
  - autolens_workspace_developer: feature/point-solver-implicit-diff
  - autolens_profiling: feature/point-solver-implicit-diff


## potential-correction-validation
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/672
- session: claude --resume 0100b7de-da01-4c18-a8b0-9d0080d5e07f
- status: library-dev (phase 1 SHIPPED wst#238 awaiting human merge; phase 2 root cause CONFIRMED — engines equivalent under matched mu*I damping, trajectories agree to 4 sig figs; c2000 pair still running detached, artifacts auto-copy to worktree phase2_experiments/)
- worktree: ~/Code/PyAutoLabs-wt/potential-correction-validation
- phases: 1 (wst smoke timeout) → 2 (JAX-vs-Python parity hunt vs for_qiuhan tar) → 3 (evidence-sampled recovery test + analysis fast path) → 4 (algorithm review report)
- note: Brain sized too-large (13); content-based 4-phase split recorded in the prompt. wst has feature/point-source-chi-squared-variants checked out in another worktree (empty repos: claim) — files disjoint, pre-merge origin/main before each PR
- repos:
  - PyAutoLens: feature/potential-correction-validation
  - autolens_workspace_test: feature/potential-correction-validation


## multi-galaxy-features-phase-2c
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/426
- status: workspace-dev — SHIPPED autolens_workspace#427 (commit 7fd11daa) AWAITING HUMAN MERGE. All 7 pixelization scripts written + validated (smoke 29/29 clean-slate sequential; navigator clean; catalogue 325→332; smoke_tests.txt 25→27).
- heart-ack: human authorized ship 2026-07-31 against these exact RED reasons — "release validation FAILED (stage integrate)"; "manifest drift: tenant firewall (organ code) — 1 mismatch(es) vs PyAutoMind/repos.yaml" (hardcoded 'PyAutoLabs' at PyAutoHeart/heart/checks/release_run.py:42); "test run status unknown (no report.json)". The two "behind origin" reasons (PyAutoLens, PyAutoGalaxy) were cleared by pull_all_main.sh before shipping. Ack does NOT extend to new reasons.
- bugs-found: linear light profiles put the deflectors' SOLVED INTENSITIES into inversion.reconstruction alongside the source pixels — source_science.py died in griddata ("different number of values and points"), delaunay.py died on inversion.linear_obj_list[0] being LightProfileLinearObjFuncList not Mapper. Fixed with fixed-intensity al.lp.Sersic + inversion.cls_list_from(cls=al.Mapper). The SHIPPED fit.py has the same latent bug (over-counts source pixels by 2) — left alone, filed as a follow-up.
- worktree: ~/Code/PyAutoLabs-wt/multi-galaxy-features-phase-2c
- prompt: active/multi_galaxy_features_group_parity_phase_2_mge_pixelization.md
- arc: PR#417 (phase 1) → #421 (slam follow-up) → #422 (2a MGE) → #423 (2b pixelization core) → #424 (section parity) → THIS (2c). Phases 3 (advanced light) + 4 (advanced mass) prompts already drafted.
- note: Brain sized too-large (11) and proposed a generic 4-way split — rejected, the prompt is already phased and 2c is one folder in one repo (same shape as 2a, 7 files/1 PR). likelihood_function.py added to the 2c list (human-confirmed 2026-07-31): it is in the phase Deliverables and both siblings have one.
- resume-context: length model is the GROUP tier not imaging (shipped modeling.py 334 vs group 331/imaging 546). House style = tutorials explaining the code, NOT analyses — no measured tables, no parameter arithmetic, no science-consequence prose. adaptive.py self-resolves adapt images via two searches in one script. slam.py COPIES multi_galaxy/slam.py's stages (importing a workspace script executes it). Clean the dataset slate before any full-res run — smoke poisons it at 15x15.
- follow-ups: missing `__Dataset Auto-Simulation__` header on the five existing multi_galaxy features slam.py files (needs docstring restructuring, not a text insert); house-style cleanup over merged #417/#422.
- repos:
  - autolens_workspace: feature/multi-galaxy-features-phase-2c
