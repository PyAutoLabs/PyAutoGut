# Active Tasks

## autogalaxy-assistant-birth
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/188 (epic)
- status: Phase 0 IN PROGRESS 2026-08-01 — repo born public+empty (github.com/PyAutoLabs/autogalaxy_assistant), local checkout cloned, repos.yaml registered + synced; next = Phase 1 frame+tooling PR. Data-sourcing checkpoint OPEN on the epic (gates Phase 2 — human names the real galaxy cutout).
- prompt: active/autogalaxy_assistant_birth.md
- plan: 7 phases (0 epic/repo → 1 frame+tooling+stack → 2 dataset+README+signposts → 3 wiki/core → 4a/4b ag_* skills → 5 wiki/literature → 6 benchmarks+newborn gate); hand-built mirror of autolens_assistant (clone tool NOT run — partition 56/89/301/0 @ b9c10a9 used as checklist); PUBLIC at birth so every merged PR must be residue-free; Opus subagents execute.
- claim-note: assistant repo is new (no contention); external signpost PRs in Phase 2 touch autogalaxy_workspace + PyAutoGalaxy + HowToGalaxy llms.txt only (small, no scope overlap with active claims).
- repos:
  - autogalaxy_assistant: main (in-place feature branches; not worktree-managed)

## point-source-defaults-campaign
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/678
- session: claude --resume ee42120d-c794-4565-804e-d7576d50c37c
- status: library-dev (phase A MERGED #679; phase B evidence COMMITTED to the branch (22/25 JSONs + results/notes/point_source_defaults_campaign.md, pushed 44920b1); bug-fix PRs ALL MERGED 2026-08-01 ~12:47 (PyAutoFit#1441, PyAutoLens#685, autofit_workspace_test#81; branches deleted; RAL mains synced via HPCPullPyAuto); phase C default swap COMMITTED+PUSHED on the campaign branch (d838ca596, origin/main pre-merged, 510 tests pass, 3 new default-pin tests) — PR HELD pending the exp-3 extra-arm verdict; RAL in flight: 331885/331886 simple_extra 8h arms, 331887 msp cluster rerun on the fixed stack, 331888/331889 clean reruns of the exp-2 resume-suspect free cells (outputs wiped first); Monitor bko3dcht6 armed on 331885-887 in session fadbfcbf)
- resume-runbook: (1) when 331885/331886 land -> rsync simple_extra JSONs from laptop -> exp-3 extra-arm verdict -> if PairAll confirmed open the phase C PR from the campaign branch (release notes MUST carry '## API Changes'; downstream default-reliant scripts = autolens_workspace {point_source/start_here.py, guides/modeling/advanced/graphical.py, multi_dataset/features/imaging_and_point_source/modeling.py, weak/features/strong_lensing/a2744.py} — phase D migrates them; workspace_test all pass explicit classes); (2) when 331887 lands -> pull msp cluster image_plane_solved JSON (validates the two merged gradient fixes end-to-end on A100); (3) when 331888/331889 land -> pull clean free-cell JSONs, amend committed exp-2 numbers if they shifted; (4) update notes doc with extra-arm + cluster-rerun numbers; (5) phase D workspace docs (+ cluster/simulator.py:482 plane_redshift fix, coordinate #436)
- discovery: PointSolver.solve defaults plane_redshift to the FINAL plane — both cluster simulators omitted it (z=1.0 source positions unphysical; truth logL −4.2e6 → +26.1 after fix). Profiling sim fixed on branch; workspace cluster/simulator.py:482 STILL AFFECTED — flagged on autolens_workspace#436 (its convergence run is tainted), workspace fix folds into phase D. RAL profiling clone rebuilt as real https clone (was a dead rsync'd worktree pointer; RAL cannot push — pull results from laptop side)
- library-pr: https://github.com/PyAutoLabs/PyAutoLens/pull/679 (phase A; MERGED 86dea4107; was shipped under human-authorized Heart-RED override — RED was the unrelated nightly release-validation integrate failure)
- worktree: ~/Code/PyAutoLabs-wt/point-source-defaults-campaign
- prompt: active/point_source_defaults_campaign.md
- phases: A library prereqs logsumexp + free-centre tensor (PyAutoLens, small PR FIRST, then HPCPullPyAuto) → B evidence campaign (autolens_profiling, RAL A100s, galaxy + cluster tiers) → C defaults change (PyAutoLens, ## API Changes) → D workspace docs (autolens_workspace, END GOAL)
- note: Brain sized too-large (11, prose-driven); human-scoped A–D phasing kept (potential-correction precedent). SUPERSEDES the 2026-07-31 morning galaxy/cluster split; COORDINATES with cluster-point-solved-default (#436 — phase D touches cluster/ only to reconcile); ABSORBS ideas.md PairAll-logsumexp entry (removed) + draft/research/autolens_profiling/cluster_gradient_search_benchmark.md (banner already in file). Time-delay free-H0 arm DEFERRED.
- claim-note: PyAutoLens held CONCURRENTLY with potential-correction-validation (#672) — scopes disjoint (autolens/point/fit/ + point/model vs pixelization/potential-correction); pre-merge origin/main before PR
- repos:
  - PyAutoLens: feature/point-source-defaults-campaign (phase A MERGED via #679; branch retained for phase C) + feature/point-solver-padded-row-grads (bug-fix PR #685 OPEN)
  - PyAutoFit: feature/jax-pytree-traced-aux-fix (bug-fix PR #1441 OPEN; main checkout restored to main)
  - autofit_workspace_test: feature/jax-pytree-traced-aux-fix (regression-test PR #81 OPEN; checkout restored to main)
  - autolens_profiling: feature/point-source-defaults-campaign

## interferometer-start-here-integrate-oom (corrective)
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/449
- status: BOTH MERGED 2026-08-01 ~00:15 BST (#450 merge, #132 merge; CI green). Manual release validation IN FLIGHT: Stage 2 rehearsal run PyAutoHands 30672432924 SUCCESS -> testpypi 2026.7.31.1.dev69301; Stage 3 PyAutoHeart release-integrate run 30672739606 dispatched 23:23 UTC, in progress
- resume: when 30672739606 completes -> `gh run download 30672739606 -R PyAutoLabs/PyAutoHeart -n release-stage-report -D ~/.pyauto-heart/manual_validation_20260801` then `pyauto-brain release validate --ingest ~/.pyauto-heart/manual_validation_20260801 --commit-shas ~/.pyauto-heart/manual_validation_20260801/commit_shas.json` (artifacts dir already holds rehearsal.json + commit_shas.json + testpypi_version.txt). OPTIONAL: heart tick auto-ingests the completed run anyway, and the 05:36 UTC nightly independently re-validates and releases on green (NIGHTLY_RELEASES=true) with no further human step
- corrective-red: Heart RED reason "release validation FAILED (stage integrate)" — authorization quoted+approved live in session 5b29e469 (recorded on #449); cause = MultiStartProdigy 48-start unbatched vmap OOM (~86 GB) introduced d5c9802d (2026-07-29, post-release); fix = batch_size=4, control-vs-patched verified under release-profile env
- repos:
  - autolens_workspace: feature/interferometer-start-here-batch-size
  - PyAutoHeart: feature/release-run-repo-slug-firewall (YELLOW tenant-firewall, not the RED claim)
