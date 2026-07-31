# Active Tasks

## py314-fork-context
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1437
- session: claude --resume 5bc6c978-cb8f-4353-a66c-158a74103a17
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/py314-fork-context
- prompt: active/factor_graph_3_14_instance_iteration.md
- note: root cause CONFIRMED (py3.14 forkserver default start method; fork-forced tutorial passes end-to-end). Fix = fork-context pin at ~7 autofit pool sites + numpy-only unit test. Follow-ups AFTER merge: PyAutoHands python_matrix.yml 3.14 re-add, library classifiers, PyAutoNerves banner retarget. Repro venv: scratchpad py314 (session-local).
- repos:
  - PyAutoFit: feature/py314-fork-context

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

## point-source-defaults-campaign
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/678
- session: claude --resume ee42120d-c794-4565-804e-d7576d50c37c
- status: library-dev (phase A PR OPEN PyAutoLens#679 awaiting human merge; on merge: HPCPullPyAuto then phase B)
- library-pr: https://github.com/PyAutoLabs/PyAutoLens/pull/679 (phase A; commit 0cebe059d; shipped under human-authorized Heart-RED override — RED was the unrelated nightly release-validation integrate failure)
- worktree: ~/Code/PyAutoLabs-wt/point-source-defaults-campaign
- prompt: active/point_source_defaults_campaign.md
- phases: A library prereqs logsumexp + free-centre tensor (PyAutoLens, small PR FIRST, then HPCPullPyAuto) → B evidence campaign (autolens_profiling, RAL A100s, galaxy + cluster tiers) → C defaults change (PyAutoLens, ## API Changes) → D workspace docs (autolens_workspace, END GOAL)
- note: Brain sized too-large (11, prose-driven); human-scoped A–D phasing kept (potential-correction precedent). SUPERSEDES the 2026-07-31 morning galaxy/cluster split; COORDINATES with cluster-point-solved-default (#436 — phase D touches cluster/ only to reconcile); ABSORBS ideas.md PairAll-logsumexp entry (removed) + draft/research/autolens_profiling/cluster_gradient_search_benchmark.md (banner already in file). Time-delay free-H0 arm DEFERRED.
- claim-note: PyAutoLens held CONCURRENTLY with potential-correction-validation (#672) — scopes disjoint (autolens/point/fit/ + point/model vs pixelization/potential-correction); pre-merge origin/main before PR
- repos:
  - PyAutoLens: feature/point-source-defaults-campaign

## start-here-other-feature-sections
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/442
- session: claude (this session)
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/start-here-other-feature-sections
- prompt: active/start_here_other_stub_feature_sections.md
- claim-note: PyAutoLens held CONCURRENTLY with #672 and #678 worktrees — this task is docs-only (docs/overview/overview_3_features.md), zero file overlap, human-approved parallel run; pre-merge origin/main before PR
- repos:
  - autolens_workspace: feature/start-here-other-feature-sections
  - autogalaxy_workspace: feature/start-here-other-feature-sections
  - PyAutoLens: feature/start-here-other-feature-sections
  - PyAutoGalaxy: feature/start-here-other-feature-sections

## group-extra-galaxies-dpie
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/444
- session: claude (this session)
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/group-extra-galaxies-dpie
- prompt: active/group_extra_galaxies_dpie_truncation.md
- claim-note: autolens_workspace held CONCURRENTLY with start-here-other-feature-sections (#442, docs-only docs/overview/overview_3_features.md) — this task touches scripts/group + scripts/cluster + features/extra_galaxies docs, zero file overlap, human-approved parallel run; pre-merge origin/main before PR. Coordinate cluster/ prose with #678 phase D and #436.
- repos:
  - autolens_workspace: feature/group-extra-galaxies-dpie
