# Active Tasks

## point-source-defaults-campaign
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/678
- session: claude --resume ee42120d-c794-4565-804e-d7576d50c37c
- status: library-dev (phase A MERGED #679; phase B RUNNING on RAL — CHECKPOINT 2026-08-01 00:xx: 22/25 result JSONs written on the RAL clone branch, remaining cluster long-wall cells overnight; TWO cells TIMED OUT at 2h walls: nautilus image_plane_solved + image_plane_repeat_solved on simple_extra — the spurious-position arms; itself an exp-3 robustness signal, but resubmit both with --time=8:00:00 for posteriors)
- resume-runbook: (1) squeue/sacct check remaining cluster cells; (2) resubmit the 2 simple_extra TIMEOUT cells with 8h walls (edit the two submit files on the RAL clone or locally+push+pull); (3) VERIFY the wall=1s free cells (nautilus image_plane + source_plane on simple) were not silent PyAutoFit resumes of pre-logsumexp state (identifiers ignore data) — if resumed, wipe their search output on RAL and re-run, exp-2 depends on it; (4) pull result JSONs to laptop (RAL CANNOT push — rsync/scp from laptop side; RAL clone branch = feature/point-source-defaults-campaign at ef7da54; JSONs named hpc_hpc_a100_fp64.json, path quirk known); (5) commit JSONs + write results/notes/point_source_defaults_campaign.md (Issue/Branch/Status/TL;DR skeleton per repo convention); (6) phase C default swap keyed on exp-3 discriminator verdict — MUST pre-merge origin/main (#680/#683 merged into PyAutoLens since phase A); (7) phase D + workspace cluster/simulator.py:482 plane_redshift fix (coordinate #436). Validated: 4 early cells reproduce truth-anchor literals exactly (7.20/7.74/−33788.4/+0.60), backend=gpu, posterior_stats populated; zero job failures post shadow-package fix (RAL root searches/+simulators/ moved to _legacy_root_shadow_backup/)
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
