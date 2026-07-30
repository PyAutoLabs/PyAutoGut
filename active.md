# Active Tasks

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- session: claude --resume daaa46f9-aac5-48e2-9146-1202a92d879e
- status: phase-3-shipped, phase-4-pending
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phase-3-pr: workspace_test#237, profiling#96, workspace_developer#121 (ALL MERGED 2026-07-30; worktree + branches cleaned; shipped comment https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5135275039)
- phases: 1 (design) + 2 (core API) + 3 (workspace_test jax_likelihood + profiling examples) COMPLETE; next: start_workspace on draft phase-4 prompt (guides; fix cluster/likelihood_function.py false profile=None-centroid claim), then phase 5 (PointSolver custom_jvp gradients)
- repos:


## potential-correction-validation
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/672
- session: claude --resume 0100b7de-da01-4c18-a8b0-9d0080d5e07f
- status: library-dev (phase 1 = workspace smoke-timeout fix, ships first as standalone wst PR)
- worktree: ~/Code/PyAutoLabs-wt/potential-correction-validation
- phases: 1 (wst smoke timeout) → 2 (JAX-vs-Python parity hunt vs for_qiuhan tar) → 3 (evidence-sampled recovery test + analysis fast path) → 4 (algorithm review report)
- note: Brain sized too-large (13); content-based 4-phase split recorded in the prompt. wst has feature/point-source-chi-squared-variants checked out in another worktree (empty repos: claim) — files disjoint, pre-merge origin/main before each PR
- repos:
  - PyAutoLens: feature/potential-correction-validation
  - autolens_workspace_test: feature/potential-correction-validation

## lifecycle-drift-self-heal
- issue: https://github.com/PyAutoLabs/PyAutoMind/issues/116
- status: library-shipped, awaiting-merge
- library-pr: PyAutoMind#117 (OPEN)
- worktree: ~/Code/PyAutoLabs-wt/lifecycle-drift-self-heal
- note: single-file change to .github/workflows/lifecycle_drift.yml — self-heal stale complete/index.md on push to main (bot commit + rebase-retry push); PR runs stay read-only; `lifecycle.py check` stays hard-fail
- repos:
  - PyAutoMind: feature/lifecycle-drift-self-heal
