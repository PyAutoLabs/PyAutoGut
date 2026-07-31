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


## multi-galaxy-features-phase-4a
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/430
- status: workspace-dev — phase 4a of the multi_galaxy features parity arc (double_source_plane_lens; 6 scripts + README, ~2000 lines)
- worktree: ~/Code/PyAutoLabs-wt/multi-galaxy-features-phase-4a
- prompt: draft/docs/workspaces/multi_galaxy_features_group_parity_phase_4_advanced_mass.md (shared by 4a/4b/4c; stays in draft/ until 4c ships)
- arc: #417 (ph1) → #421 → #422 (2a) → #423 (2b) → #424 → #427 (2c, MERGED bb1f850c) → #429 (ph3, MERGED 974fc3d7) → THIS (4a). Then 4b mass_stellar_dark, 4c subhalo.
- split: phase 4 measured ~5174 lines / 15 scripts at implementation time — larger than all of phase 2. Human-confirmed 2026-07-31 to split one folder per PR. Arc-closing checks run at the end of 4c, NOT each sub-phase.
- claim-to-verify: the prompt says two source planes BREAK the multi-galaxy mass-split degeneracy via "the ratio of deflections at two redshifts". Suspect wrong — both sources sit behind the SAME lens plane, so plane 2's deflection is plane 1's scaled by a geometric factor, which carries no info about the split. The real mechanism is likely that source 2 sits at a different sky position and so samples the deflection field at different image-plane locations. TEST BOTH before writing either.
- watch: (1) linear light profiles put deflector solved intensities into inversion.reconstruction; (2) al.SettingsInversion does NOT exist — use settings=al.Settings(...).
- repos:
  - autolens_workspace: feature/multi-galaxy-features-phase-4a

