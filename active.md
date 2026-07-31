# Active Tasks

## cluster-point-solved-default
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/436
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/cluster-point-solved-default
- prompt: active/cluster_default_point_solved.md
- scope: autolens_workspace only — cluster modeling.py + start_here.py demonstrated default swaps to al.ps.PointSolved + FitPositionsSourceSolved; lenstool mirror stays free-centre; likelihood_function.py prose check; notebooks regenerated; real Nautilus convergence run on cluster/modeling.py
- repos:
  - autolens_workspace: feature/cluster-point-solved-default

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
