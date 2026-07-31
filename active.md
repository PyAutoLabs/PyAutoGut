# Active Tasks

## potential-correction-validation
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/672
- session: claude --resume 0100b7de-da01-4c18-a8b0-9d0080d5e07f
- status: library-dev (phases 1-4 delivered 2026-07-31: wst#238 + PyAutoLens#676 both OPEN awaiting human merge; Phase 2 closed — engines equivalent, damping was the whole discrepancy; Phase 3 evidence grids done — evidence-max localizes but map-corr peaks on the ridge, prior-family finding; Phase 4 review report posted to #672; final end-to-end run of subhalo_recovery_evidence.py in flight, gates the phase-3 wst PR)
- worktree: ~/Code/PyAutoLabs-wt/potential-correction-validation
- phases: 1 (wst smoke timeout) → 2 (JAX-vs-Python parity hunt vs for_qiuhan tar) → 3 (evidence-sampled recovery test + analysis fast path) → 4 (algorithm review report)
- note: Brain sized too-large (13); content-based 4-phase split recorded in the prompt. wst has feature/point-source-chi-squared-variants checked out in another worktree (empty repos: claim) — files disjoint, pre-merge origin/main before each PR
- repos:
  - PyAutoLens: feature/potential-correction-validation
  - autolens_workspace_test: feature/potential-correction-validation

## point-source-defaults-campaign
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/678
- session: claude --resume ee42120d-c794-4565-804e-d7576d50c37c
- status: library-dev (phase A MERGED #679; phase B harness PUSHED autolens_profiling ef7da54 — truth anchors + tensor/discriminator/near-caustic cells + cluster factor-graph searches; 25 A100 jobs submitting on RAL via detached submit_all_678_phase_b.sh; awaiting results pull → notes synthesis)
- discovery: PointSolver.solve defaults plane_redshift to the FINAL plane — both cluster simulators omitted it (z=1.0 source positions unphysical; truth logL −4.2e6 → +26.1 after fix). Profiling sim fixed on branch; workspace cluster/simulator.py:482 STILL AFFECTED — flagged on autolens_workspace#436 (its convergence run is tainted), workspace fix folds into phase D. RAL profiling clone rebuilt as real https clone (was a dead rsync'd worktree pointer; RAL cannot push — pull results from laptop side)
- library-pr: https://github.com/PyAutoLabs/PyAutoLens/pull/679 (phase A; MERGED 86dea4107; was shipped under human-authorized Heart-RED override — RED was the unrelated nightly release-validation integrate failure)
- worktree: ~/Code/PyAutoLabs-wt/point-source-defaults-campaign
- prompt: active/point_source_defaults_campaign.md
- phases: A library prereqs logsumexp + free-centre tensor (PyAutoLens, small PR FIRST, then HPCPullPyAuto) → B evidence campaign (autolens_profiling, RAL A100s, galaxy + cluster tiers) → C defaults change (PyAutoLens, ## API Changes) → D workspace docs (autolens_workspace, END GOAL)
- note: Brain sized too-large (11, prose-driven); human-scoped A–D phasing kept (potential-correction precedent). SUPERSEDES the 2026-07-31 morning galaxy/cluster split; COORDINATES with cluster-point-solved-default (#436 — phase D touches cluster/ only to reconcile); ABSORBS ideas.md PairAll-logsumexp entry (removed) + draft/research/autolens_profiling/cluster_gradient_search_benchmark.md (banner already in file). Time-delay free-H0 arm DEFERRED.
- claim-note: PyAutoLens held CONCURRENTLY with potential-correction-validation (#672) — scopes disjoint (autolens/point/fit/ + point/model vs pixelization/potential-correction); pre-merge origin/main before PR
- repos:
  - PyAutoLens: feature/point-source-defaults-campaign (phase A MERGED via #679; branch retained for phase C)
  - autolens_profiling: feature/point-source-defaults-campaign

## group-extra-galaxies-dpie
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/444
- pr: https://github.com/PyAutoLabs/autolens_workspace/pull/446
- session: claude (this session)
- status: awaiting-merge (PR #446 open, pending-release; smoke 34/34; shipped under recorded heart-ack)
- worktree: ~/Code/PyAutoLabs-wt/group-extra-galaxies-dpie
- prompt: active/group_extra_galaxies_dpie_truncation.md
- heart-ack: RED 'release validation FAILED (stage integrate)' + YELLOW manifest drift + stale test report acknowledged by human 2026-07-31 (unrelated release-pipeline state); ship-anyway authorized to PR-open
- claim-note: autolens_workspace held CONCURRENTLY with start-here-other-feature-sections (#442, docs-only docs/overview/overview_3_features.md) — this task touches scripts/group + scripts/cluster + features/extra_galaxies docs, zero file overlap, human-approved parallel run; pre-merge origin/main before PR. Coordinate cluster/ prose with #678 phase D and #436.
- repos:
  - autolens_workspace: feature/group-extra-galaxies-dpie
