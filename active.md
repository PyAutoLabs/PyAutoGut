# Active Tasks

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- status: workspace-dev — phase 4 PR OPEN awaiting human merge: autolens_workspace#425 (pending-release; smoke 26/26 local; opened 2026-07-31 under human-acked Heart RED — nightly interferometer release-leg OOM, unrelated, filed draft/bug/autolens/interferometer_release_leg_oom.md)
- heart-ack: release validation FAILED (stage integrate) — human authorized PR-open 2026-07-31; merge stays human
- phase-4-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/425 (comment https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5141094763)
- worktree: ~/Code/PyAutoLabs-wt/point-source-solved-guides
- prompt: active/point_source_chi_squared_paper_variants_phase_4_docs.md (binding phase-1 deltas inside; plan approved in-session — prose-only recommendation, no demonstrated-default swap; cite glafic/Lenstool where implementations match, Lombardi 2024 only for §5.1)
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phase-3-pr: workspace_test#237, profiling#96, workspace_developer#121 (ALL MERGED 2026-07-30; worktree + branches cleaned; shipped comment https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5135275039)
- phases: 1 (design) + 2 (core API) + 3 (examples/profiling) COMPLETE; 4 (guides) IN FLIGHT on branch feature/point-source-solved-guides. Phase 5 (PointSolver custom_jvp gradients, draft phase-5 prompt) touches PyAutoLens (+PyAutoArray) — NOTE PyAutoLens is claimed by potential-correction-validation (#672); hand-check file overlap before starting.
- resume-context: project memory `point-source-solved-likelihoods` holds phase-3 literals + lessons (H0-matched parity for time-delay fits; fit_from pytree gap is the ONLY remaining jit blocker; output_to_json key-order nondeterminism filed in ideas.md; profiling baselines used PointFlux so solved swap drops 3 params not 2)
- repos:
  - autolens_workspace: feature/point-source-solved-guides


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
