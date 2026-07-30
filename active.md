# Active Tasks

## multi-plane-guide-units
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/411
- session: claude --resume 5b02920f-dfdb-476a-84df-e81a31971d19
- status: awaiting-merge (PR https://github.com/PyAutoLabs/autolens_workspace/pull/413 opened 2026-07-30; Heart YELLOW at ship — manifest drift tenant firewall — surfaced on issue for human ack; merge human)
- worktree: ~/Code/PyAutoLabs-wt/multi-plane-guide-units
- note: worktree_check_conflict fired on 4 concurrent autolens_workspace claims (#407, #408, #409, #410); hand-checked file-disjoint — this task touches only scripts/guides/advanced/multi_plane.py and no in-flight branch touches scripts/guides/advanced/; shared surfaces are generated notebooks/sidecars — re-merge origin/main + regenerate LAST before PR
- note: Brain FeatureDecision difficulty large (score 9, repo-count proxy) overridden to small, no phasing — single-file docs rewrite, no API surface
- repos:
  - autolens_workspace: feature/multi-plane-guide-units

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
- heart-ack: YELLOW acknowledged 2026-07-30 by human, exact reasons:
  - "manifest drift: tenant firewall (organ code) — 1 mismatch(es) vs PyAutoMind/repos.yaml"
  - "test run status unknown (no report.json)" (stale)
  - "release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)" (stale)
- note: docs-only terminology rename; group/ deliberately excluded (a group genuinely has a BCG/BGG)
- note: overlaps multi-package-rename-multi-dataset (#408) on autolens_workspace generated sidecars
  (llms-full.txt, workspace_index.json) — whichever merges second must regenerate
- repos:
  - autolens_workspace: feature/scaling-relation-brightest-galaxy

## multi-package-rename-multi-dataset
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/408
- status: awaiting-merge (phases 1 + 3 PR-open 2026-07-30; phase 2 blocked)
- worktree: ~/Code/PyAutoLabs-wt/multi-package-rename-multi-dataset
- workspace-pr: autolens_workspace#414, autogalaxy_workspace#194 (both OPEN, pending-release)
- phase3-pr: PyAutoLens#673, PyAutoGalaxy#542, autolens_assistant#105, autolens_jax_joss#2 (all OPEN, docs-only)
- MERGE ORDER: autolens_workspace#414 + autogalaxy_workspace#194 FIRST, then the four phase-3 PRs (they are blob/main URLs + paired_example pointers that 404/dangle until the package actually moves on main)
- heart-ack: YELLOW acknowledged by human 2026-07-30 for exactly these reasons — "manifest drift: tenant firewall (organ code) — 1 mismatch(es) vs PyAutoMind/repos.yaml"; stale: "test run status unknown (no report.json)", "release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)". Does not extend to new reasons.
- phases: 1 (autolens_workspace + autogalaxy_workspace) PR-OPEN; 2 (autolens_workspace_test, autogalaxy_workspace_test, autolens_profiling, autolens_workspace_developer, HowToLens) BLOCKED on point-source-chi-squared-variants releasing its worktree claims; 3 (PyAutoLens/docs, PyAutoGalaxy/docs, autolens_assistant, autolens_jax_joss) GATED on phase 1 merging — blob/main URLs dangle until then
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

## guides-jax-to-using-jax
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/412
- session: claude --resume 1eaf929e-624f-4e22-a28f-9b39e463258e
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/guides-jax-to-using-jax
- note: worktree_check_conflict fired on 6 concurrent/stale autolens_workspace claims; hand-checked file-disjoint — this task owns scripts/guides/{using_jax,data_structures,galaxies,lens_calc,tracer}.py + smoke_tests.txt; only generated sidecars/notebooks shared with #407/#408/#410/multi-plane-guide-units — re-merge main + regenerate before PR
- note: Model Fable (human decision 2026-07-30); one PR per repo (recorded override of Feature Agent 4-phase split, #368 precedent); using_jax.py becomes runnable + smoke-listed (user scope addition)
- repos:
  - autolens_workspace: feature/guides-jax-to-using-jax
  - autogalaxy_workspace: feature/guides-jax-to-using-jax

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
