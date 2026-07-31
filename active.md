# Active Tasks

## potential-correction-validation
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/672
- session: claude --resume 0100b7de-da01-4c18-a8b0-9d0080d5e07f
- status: awaiting-merge (ALL FOUR PHASES DELIVERED 2026-07-31; end-to-end acceptance run PASSED. Merge queue: PyAutoLens#676 first, then wst#243; wst#238 independent. Phase 4 review report on #672. Post-merge: completion record + worktree cleanup + close #672)
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

## interferometer-start-here-integrate-oom (corrective)
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/449
- status: corrective PR open (autolens_workspace#450; sibling YELLOW fix PyAutoHeart#132); merge human-authorized 2026-07-31 live session; validation = nightly rehearse→integrate on fresh wheels
- corrective-red: Heart RED reason "release validation FAILED (stage integrate)" — authorization quoted+approved live in session 5b29e469 (recorded on #449); cause = MultiStartProdigy 48-start unbatched vmap OOM (~86 GB) introduced d5c9802d (2026-07-29, post-release); fix = batch_size=4, control-vs-patched verified under release-profile env
- repos:
  - autolens_workspace: feature/interferometer-start-here-batch-size
  - PyAutoHeart: feature/release-run-repo-slug-firewall (YELLOW tenant-firewall, not the RED claim)

## llms-txt-census-fixes
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/451
- session: claude --resume bbc37e50-2f17-41c1-9180-14a1cd647a1c
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/llms-txt-census-fixes
- prompt: active/llms_txt_census_fixes.md
- note: Brain sized too-large (25, repo-count/prose-driven); override — few-line docs edits across 6 repos, one task, per-repo PRs. Merge order: PyAutoHands FIRST (GROUP_ORDER), then workspaces (navigator_check regenerates vs PyAutoHands main; same-named branches keep PR CI green)
- claim-note: autolens_workspace held CONCURRENTLY with interferometer-start-here-integrate-oom (#449 — its scope is interferometer/start_here.py; ours is llms.txt + scripts/README.md + generated catalogue, disjoint); PyAutoLens held CONCURRENTLY with #672/#678 worktrees (ours touches llms.txt only) — pre-merge origin/main before each PR
- repos:
