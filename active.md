# Active Tasks

## history-blob-purge
- issue: (none — human-directed operation, tracked here + in complete/ record)
- session: claude
- status: in-progress
- autonomy: human-required — EXPLICITLY AUTHORIZED 2026-07-27 by the human: rewrite pushed history of autolens_workspace, autogalaxy_workspace, autofit_workspace with the extended dead-path lists; costs accepted (2026.7.27.1 tag content change in autolens+autogalaxy, 17 autolens fork divergences, early void of 6 condemned recover-points). Mirror backups kept permanently in ~/Code/PyAutoLabs-backups/. HowTo repos SKIPPED (under bar); autocti DEFERRED until leg 6 merges.
- prompt: active/history_blob_purge.md
- note: sequence autogalaxy (rehearsal) -> verify -> autofit -> verify -> autolens; per-repo gates: HEAD tree byte-identical, tags preserved by name, 0 open PRs re-checked, backup mirror verified BEFORE force-push. Measurement: reclaim 83+25+235 MiB (73-89% of clone).
- repos:
  - autogalaxy_workspace: main (history rewrite)
  - autofit_workspace: main (history rewrite)
  - autolens_workspace: main (history rewrite)

## purge-autocti-datasets
- issue: https://github.com/PyAutoLabs/autocti_workspace/issues/11
- session: claude
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/purge-autocti-datasets
- autonomy: supervised
- heart-ack: 2026-07-27 human acknowledged this workspace ship with the exact YELLOW reasons below AND pre-authorized merge on green smoke; any new reason or RED verdict requires a fresh stop
  - workspace validation not passing (13 failed, 2026-07-21T19-05-22Z)
  - 33 stale parked script(s)
  - manifest drift: tenant firewall (organ code) — 5 mismatch(es) vs PyAutoMind/repos.yaml
  - release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- prompt: active/purge_autocti_committed_datasets.md
- note: leg 6 of the dataset-bulk series — ~120 MB imaging_ci datasets behind guards; leg-1 recipe; adopt allowlist regime if absent; check autocti_workspace_test consumers; datasets whose guards can't be added cleanly stay committed. Leg 7 (history blob purge, human-gated) filed as draft.
- repos:
  - autocti_workspace: feature/purge-autocti-datasets

## jax-joss-benchmarks
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/281
- status: PARKED-ON-JOB — #282 MERGED+cleaned; 8/8 runnable A100 rows committed (autolens_jax_joss@64204f6). SDP.81 prep = detached RAL job 330608 (330605 diagnosed: empty extracted/ leftover skipped untar via test-d guard; casatools import needs ~/.casa/data — both fixed; 42GB tarball CACHED, no re-download) (45GB ALMA Band6 download -> casatools venv -> 3-level export -> installs dataset/interferometer/{sdp81,sdp81_mid,sdp81_full} in /mnt/ral/jnightin/autolens_jax_joss). RESUME (short session): (1) check log /mnt/ral/jnightin/sdp81_prep_330608.log — expect 'SDP81 PREP ALL DONE' + per-level visibility counts; failure modes: casatools pip wheel on py3.12 (fallback = monolithic CASA tarball), datacolumn, MS_LIST empty (check find patterns); (2) sbatch interferometry benchmarks on A100: benchmarks/interferometer.py at --nvis default/mid/full + benchmarks/imaging_and_interferometer.py (pattern: /mnt/ral/jnightin/autolens_jax_joss/run_rest.sbatch); (3) scp results/*.json back, regen RESULTS.md, commit (guard: explicit file paths); (4) copy small sdp81/ product locally, rewrite scripts/interferometer/start_here.py on NEW branch (start_workspace; #282 merged) using it — decide hosting (commit few-MB FITS to workspace w/ .gitignore allowlist + git add -f, or Zenodo+SDP81_URL); (5) final issue #281 update. Also pending: cluster-tuning prompt draft/feature/autolens_workspace/joss_cluster_benchmark_tuning.md; weak JAX-viz PyAutoLens#614
- worktree: ~/Code/PyAutoLabs-wt/jax-joss-benchmarks
- autonomy: supervised
- prompt: active/autolens_jax_joss_benchmark_repo.md
- note: 5-phase epic (one-shot attempt per user); new repo autolens_jax_joss (PyAutoLabs, public) born alongside; datasets SDP.81 / RXJ1131 / A2744 user-approved
- repos:
  - autolens_jax_joss: main (born this task)

## pix-prodigy-cpu
- issue: https://github.com/PyAutoLabs/autolens_workspace_developer/issues/117
- session: claude
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/pix-prodigy-cpu
- autonomy: supervised
- prompt: active/pixelized_multistart_prodigy_cpu.md
- repos:
  - autolens_workspace_developer: feature/pix-prodigy-cpu
