# Active Tasks

## clean-slate-write-site
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/169
- session: claude
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/clean-slate-write-site
- autonomy: supervised
- heart-ack: 2026-07-27 human acknowledged this ship with the exact YELLOW reasons below; any new reason or RED verdict requires a fresh stop
  - workspace validation not passing (13 failed, 2026-07-21T19-05-22Z)
  - 33 stale parked script(s)
  - manifest drift: tenant firewall (organ code) — 5 mismatch(es) vs PyAutoMind/repos.yaml
  - release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- prompt: active/clean_slate_write_site_provenance.md
- note: leg 5 (final) of the dataset-bulk series. New bin/dataset_provenance.py (write-site classifier: REGENERABLE/DOWNLOADED/ORPHAN; orphans reported not deleted), clean_slate phase 1b uses it; per-dir size warning; git gc --auto phase; .ipynb_checkpoints swept, __pycache__ deliberately left; wake_up.md 'non-destructive' claim fixed; net-new tests for phases 1/1b/2/3 (currently ZERO coverage). Ground-truth catch/never-touch lists in the issue.
- repos:
  - PyAutoBrain: feature/clean-slate-write-site

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

## delaunay-nan-callback
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/410
- session: codex
- status: awaiting-input
- question: https://github.com/PyAutoLabs/PyAutoArray/issues/410#issuecomment-5092923633
- worktree: ~/Code/PyAutoLabs-wt/delaunay-nan-callback
- autonomy: supervised (`--auto`; capped by the `bug` work-type cap in AUTONOMY.md)
- prompt: active/delaunay_tables_callback_nan_points_crash.md
- note: Implementation complete and committed locally. PyAutoArray 906/906 tests; dense/sparse poisoned-lane parity; raw NaN logL; partial/all poisoning gradient isolation; unchanged FD certification all pass. Review CLEAN. PARKED before push/PR because scoped smoke was 20/21 with unrelated imaging/subhalo_recovery.py 300s timeout and Heart is YELLOW; issue comment asks for exact acknowledgement.
- repos:
  - PyAutoArray: feature/delaunay-nan-callback
  - autolens_workspace_test: feature/delaunay-nan-callback
