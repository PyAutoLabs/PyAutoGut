# Active Tasks

## cluster-point-solved-default
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/436
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/cluster-point-solved-default
- prompt: active/cluster_default_point_solved.md
- scope: autolens_workspace only — cluster modeling.py + start_here.py demonstrated default swaps to al.ps.PointSolved + FitPositionsSourceSolved; lenstool mirror stays free-centre; likelihood_function.py prose check; notebooks regenerated; real Nautilus convergence run on cluster/modeling.py
- repos:
  - autolens_workspace: feature/cluster-point-solved-default

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
