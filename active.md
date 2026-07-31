# Active Tasks

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- status: phases 1-5 ALL MERGED (phase 5: PyAutoLens#677 + wst#240 + wsdev#123 + profiling#98, human-merged 2026-07-31; record complete/2026/07/point-solver-implicit-diff.md). ADDENDUM in flight: Prodigy-vs-Nautilus benchmark cells (image_plane + source_plane, free-centre models matching the nautilus reference cells) to empirically validate the gradients in a real search — human-requested 2026-07-31
- worktree: ~/Code/PyAutoLabs-wt/point-solver-implicit-diff (only autolens_profiling active on feature/point-source-prodigy-benchmark; other repos detached at main pending final cleanup)
- phase-5-comment: https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5142215557
- worktree: ~/Code/PyAutoLabs-wt/point-solver-implicit-diff
- prompt: active/point_source_chi_squared_paper_variants_phase_5_jax_gradients.md (binding equations + phase-1 deltas inside)
- claim-note: PyAutoLens + autolens_workspace_test held CONCURRENTLY with potential-correction-validation (#672) — human-authorized via plan approval 2026-07-31; #672 touches only autolens/potential_correction/** and wst phase2_experiments/ (disjoint); pre-merge origin/main before each PR
- phase-4-pr: autolens_workspace#425 (MERGED 2026-07-31, human merge; record complete/2026/07/point-source-solved-guides.md; comment https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5141094763)
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phase-3-pr: workspace_test#237, profiling#96, workspace_developer#121 (ALL MERGED 2026-07-30; worktree + branches cleaned; shipped comment https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5135275039)
- phases: 1 (design) + 2 (core API) + 3 (examples/profiling) + 4 (guides) COMPLETE. Phase 5 (PointSolver custom_jvp gradients, draft phase-5 prompt) touches PyAutoLens (+PyAutoArray) — NOTE PyAutoLens is claimed by potential-correction-validation (#672); hand-check file overlap before starting.
- resume-context: project memory `point-source-solved-likelihoods` holds phase-3 literals + lessons (H0-matched parity for time-delay fits; fit_from pytree gap is the ONLY remaining jit blocker; output_to_json key-order nondeterminism filed in ideas.md; profiling baselines used PointFlux so solved swap drops 3 params not 2)
- repos:
  - autolens_profiling: feature/point-source-prodigy-benchmark


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


## multi-galaxy-features-phase-4b
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/432
- status: workspace-dev — phase 4b of the multi_galaxy features parity arc (mass_stellar_dark; 6 scripts + README, ~2000 lines)
- worktree: ~/Code/PyAutoLabs-wt/multi-galaxy-features-phase-4b
- prompt: draft/docs/workspaces/multi_galaxy_features_group_parity_phase_4_advanced_mass.md (shared by 4a/4b/4c)
- arc: 4a MERGED 9bde8882 (#431, record complete/2026/07/multi-galaxy-features-phase-4a.md). THIS = 4b. Then 4c subhalo, which also runs the arc-closing checks.
- claim-to-verify: prompt says "tying the mass-to-light ratio across galaxies is what makes the decomposition identifiable when the mass split already is not". First half (it's a real choice) is true; second half is a strong identifiability claim — TEST IT. Vary the two M/L ratios anti-correlated vs together and compare residual-surface flatness. TWO phases running the prompt's motivation has been wrong (ph3 shapelets, 4a DSPL).
- watch: inversion.reconstruction contamination (2c); al.SettingsInversion doesn't exist (ph3); al.model_util.mge_from doesn't exist (4a).
- repos:
  - autolens_workspace: feature/multi-galaxy-features-phase-4b

