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


## multi-galaxy-features-phase-3
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/428
- status: workspace-dev — phase 3 of the multi_galaxy features parity arc (advanced light: operated_light_profile, shapelets, sky_background; creates features/advanced/)
- worktree: ~/Code/PyAutoLabs-wt/multi-galaxy-features-phase-3
- prompt: active/multi_galaxy_features_group_parity_phase_3_advanced_light.md
- arc: #417 (ph1) → #421 → #422 (2a) → #423 (2b) → #424 → #427 (2c, MERGED bb1f850c) → THIS (ph3). Phase 4 (advanced mass: double_source_plane_lens, mass_stellar_dark, subhalo) prompt drafted.
- depth-decision: operated_light_profile + sky_background take GROUP tier (group is the deeper sibling for both). shapelets takes GROUP tier too despite imaging being 2x deeper (1072 vs 567) — the parent's "cross-link, do not fork where the physics is regime-independent" rule beats its "match the deeper sibling" rule here; imaging's extra ~500 lines are the scale-independent shapelet-basis API walkthrough.
- watch: (1) linear light profiles put deflector SOLVED INTENSITIES into inversion.reconstruction — bit twice in 2c; use fixed-intensity profiles + cls_list_from when reading the reconstruction. (2) PyAutoFit identifiers ignore the data, so new datasets need their own unique_tag (dataset_name handles it here).
- repos:
  - autolens_workspace: feature/multi-galaxy-features-phase-3
