# Active Tasks

## multistart-cadence-followups
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1422
- session: claude
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/multistart-cadence-followups
- autonomy: supervised (prompt header `safe`, capped by the `bug` work-type cap in AUTONOMY.md)
- prompt: active/multistart_cadence_followups_combined.md
- note: THREE bugs in one PR at human request (folded from 3 drafts, e623063). All from the Codex gpt-5.6-sol adversarial review of merged PR#1421. (1) emcee:206 + blackjax/nuts:291 crash on a real cadence — fix the PRODUCER (abstract_search.py:219 float() coercion protects nothing; Python ints hold 1e99). DO NOT touch zeus/bfgs/dynesty/nautilus — verified safe/tolerant, an earlier 5-search claim was falsified. (2) MultiStart runs the final perform_update TWICE (search.py:432 during_analysis=not is_final vs siblings emcee:238/bfgs:219/nautilus:438 which pass True unconditionally). (3) stale stop_reason on resume with a larger n_steps (search.py:413-416). Each part independently droppable. Codex review REQUIRED at the end per human instruction.
- repos:
  - PyAutoFit: feature/multistart-cadence-followups

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
- status: workspace-dev
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/411
- worktree: ~/Code/PyAutoLabs-wt/delaunay-nan-callback
- autonomy: supervised (`--auto`; capped by the `bug` work-type cap in AUTONOMY.md)
- prompt: active/delaunay_tables_callback_nan_points_crash.md
- note: PyAutoArray PR #411 merged as 8c5e28ec210b6149ffa0d313f717884271ce722a after comparison with the same-day PyAutoFit #1421 precedent. The library-first gate is clear; workspace regression commit 1324100 is ready to ship.
- repos:
  - PyAutoArray: feature/delaunay-nan-callback
  - autolens_workspace_test: feature/delaunay-nan-callback
