# Active Tasks

## cluster-dpie-docstring-style
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/410
- session: claude --resume f47a8f9e-ce35-4f6b-bde8-c35ef7338245
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/cluster-dpie-docstring-style
- note: worktree_check_conflict fired on 3 concurrent autolens_workspace claims (#407, #408, multi-galaxy-features-parity); hand-checked file-disjoint from scripts/cluster/** — only generated sidecars shared, re-merge main + regenerate before PR
- repos:
  - autolens_workspace: feature/cluster-dpie-docstring-style

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- session: claude --resume daaa46f9-aac5-48e2-9146-1202a92d879e
- status: workspace-dev (phase 3 in flight 2026-07-30)
- worktree: ~/Code/PyAutoLabs-wt/point-source-chi-squared-variants
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phases: 1 (design) + 2 (core API) COMPLETE; 3 (workspace_test jax_likelihood + profiling examples) IN FLIGHT on feature/point-source-chi-squared-variants (autolens_workspace_test, autolens_profiling, autolens_workspace_developer stale-claim fix); then phase 4 (guides), phase 5 (JAX solver gradients)
- repos:

## scaling-relation-brightest-galaxy
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/407
- session: claude --resume b79e03f8-64be-4fce-8c2d-e8b98ce8f487
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/scaling-relation-brightest-galaxy
- repos:
  - autolens_workspace: feature/scaling-relation-brightest-galaxy

## multi-package-rename-multi-dataset
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/408
- status: workspace-dev (phase 1 starting 2026-07-30)
- worktree: ~/Code/PyAutoLabs-wt/multi-package-rename-multi-dataset
- phases: 1 (autolens_workspace + autogalaxy_workspace) IN FLIGHT; 2 (autolens_workspace_test, autogalaxy_workspace_test, autolens_profiling, autolens_workspace_developer, HowToLens) BLOCKED on point-source-chi-squared-variants releasing its worktree claims; 3 (PyAutoLens/docs, PyAutoGalaxy/docs, autolens_assistant, autolens_jax_joss) GATED on phase 1 merging — blob/main URLs dangle until then
- note: Brain phase split (design/core_api/examples/docs) overridden for a per-repo, merge-dependency-ordered split; recorded in the prompt
- note: THREE concurrent claims on autolens_workspace (#407, #408 this task, #409). Human authorised proceeding over the worktree_check_conflict block — #407's claim was empty (zero commits). Mitigations: (a) this task touches only the multi/ package + its references, disjoint from #407's scaling_relation/ and #409's multi_galaxy/; (b) regenerate notebooks/markdown/workspace_index.json/llms-full.txt/.script_sizes.json LAST, after a pre-PR merge of origin/main
- repos:
  - autolens_workspace: feature/multi-package-rename-multi-dataset
  - autogalaxy_workspace: feature/multi-package-rename-multi-dataset

## multi-galaxy-features-parity
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/409
- status: workspace-dev (phase 1 starting 2026-07-30)
- worktree: ~/Code/PyAutoLabs-wt/multi-galaxy-features-parity
- phases: 1 (slam.py baseline + no_lens_light + linear_light_profiles + extra_galaxies/slam.py + features/README) IN FLIGHT; 2 (MGE + pixelization), 3 (advanced light), 4 (advanced mass) each get their own issue as the prior one lands
- note: Brain phase split (design/core_api/workspace_examples/docs) overridden for a content-based split — no core-API leg in pure workspace-docs work; recorded in the arc prompt
- note: THIRD concurrent claim on autolens_workspace (with #407, #408). Human authorised proceeding over the worktree_check_conflict block (it fired on both). Mitigations: (a) do not touch multi_galaxy/features/scaling_relation/ — #407 owns it, the slam.py re-point is a follow-up; (b) regenerate notebooks/navigator/.script_sizes.json LAST, after a pre-PR merge of origin/main
- repos:
  - autolens_workspace: feature/multi-galaxy-features-parity
