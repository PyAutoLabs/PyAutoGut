# Active Tasks

## point-source-defaults-campaign
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/678
- session: claude --resume ee42120d-c794-4565-804e-d7576d50c37c
- status: phases A-D ALL STAGED (session fadbfcbf, 2026-08-01 pm): A merged #679; B evidence committed (22/25 JSONs + notes doc, 44920b1) with bug-fix PRs #1441/#685/wst#81 MERGED + RAL synced; C default swap OPEN as PyAutoLens#686 (includes register_tracer_classes Galaxy-redshift no_flatten aux fix; MERGE GATE = exp-3 extra-arm cells) ; D workspace docs OPEN as autolens_workspace#453 (PENDING RELEASE — merge after #686 ships in a release): all point_source+cluster examples on PointSolved + solved all-to-all default, pairing guide carries the truth-anchored evidence, cluster/simulator.py per-source plane_redshift FIXED (the #436 taint) + validated end-to-end, a2744 adopts the cluster solved convention. RAL in flight: 331885 (running 2h+, past old wall), 331886/331887/331888/331889 queued; Monitor bko3dcht6 armed
- resume-runbook: (1) when 331885/331886 land -> rsync simple_extra JSONs -> exp-3 extra-arm verdict -> post on #678 -> HUMAN merges #686; (2) when 331887 lands -> pull msp cluster JSON (end-to-end validation of the merged gradient fixes on A100); (3) when 331888/331889 land -> pull clean free-cell JSONs, refresh exp-2 numbers if shifted; (4) refresh results/notes + the pairing guide's extra-arm sentence with final numbers, regen that notebook; (5) after #686 merges + releases -> merge workspace#453 (pending-release gate); (6) close #678 + lifecycle record
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

## nautilus-1core-serial-pool (corrective)
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1442
- status: PR OPEN 2026-08-01 evening (PyAutoFit#1443, head 75dccb92a) — awaiting CI; merge + Stage 2/3 validation dispatch to follow in-session, nightly releases on green (standing grant)
- corrective-red: Heart RED reason "release validation FAILED (stage integrate)" — hierarchical.py TIMEOUT 1800s (was 76s) in runs 30672739606 + 30686136529; authorization = human session instruction 2026-08-01 quoted verbatim on #1442 ("do a release, fine if any blockers need sorting…"), given at launch for any blockers rather than post-surfacing (noted on issue + log row); cause = e6279c53f (#1439) always builds fork Pool(1) for Nautilus, bypassing nautilus's pool∈[None,1]→serial guard, forked worker deadlocks in XLA compile under release-profile JAX; fix = pool=None at number_of_cores=1, fork pool kept for >1
- evidence: regression test red-on-main/green-patched; test_autofit/non_linear 411 passed; py-spy stacks (main in pool.map wait, worker in backend_compile_and_load) on #1442; control-vs-patched hierarchical.py release-env run in flight
- not-claimed: delaunay.py intermittent TIMEOUT (pre-existing, crosses SHA windows) stays open
- repos:
  - PyAutoFit: feature/nautilus-1core-serial-pool (canonical checkout on branch; restore main after merge)
