# Active Tasks

## raw-guard-migration
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/354
- session: claude
- status: awaiting-merge
- workspace-prs:
  - https://github.com/PyAutoLabs/autolens_workspace/pull/355
  - https://github.com/PyAutoLabs/autogalaxy_workspace/pull/171
- worktree: ~/Code/PyAutoLabs-wt/raw-guard-migration
- autonomy: supervised
- heart-ack: 2026-07-27 human acknowledged this workspace ship with the exact YELLOW reasons below; any new reason or RED verdict requires a fresh stop
  - workspace validation not passing (13 failed, 2026-07-21T19-05-22Z)
  - 33 stale parked script(s)
  - manifest drift: tenant firewall (organ code) — 5 mismatch(es) vs PyAutoMind/repos.yaml
  - release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- prompt: active/raw_guard_should_simulate_migration.md
- note: leg 3 of the dataset-bulk series. Migrate 118 (autolens) + 61 (autogalaxy) raw auto-simulate guards to should_simulate; exact exclusion list in the prompt (7 download guards, inverted SDP.81 guard, 8 results-bootstrap, 5 other, 11 file-path guards -> follow-up). HowToFit/autofit_workspace rejected (no PYAUTO_SMALL_DATASETS, would need new af API). One PR per repo. Counts must assert 118+61.
- repos:
  - autolens_workspace: feature/raw-guard-migration
  - autogalaxy_workspace: feature/raw-guard-migration

## multistart-cadence-int-cast
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1420
- session: claude
- status: awaiting-input
- question: https://github.com/PyAutoLabs/PyAutoFit/issues/1420#issuecomment-5092251405
- worktree: ~/Code/PyAutoLabs-wt/multistart-cadence-int-cast
- autonomy: supervised (prompt header `safe`, capped by the `bug` work-type cap in AUTONOMY.md)
- prompt: active/multistart_iterations_per_full_update_float_crash.md
- note: PARKED at ship sign-off, fix DONE + tested on the branch but UNCOMMITTED. Two gates: (a) effective autonomy supervised (bug cap) makes ship sign-off a checkpoint; (b) Heart YELLOW (score 65, ts 2026-07-27T12:11:07Z) with no launch acknowledgement. Tests 1534 passed/1 skipped; regression pinned (removing the int() cast fails exactly 1 new test). RESUME: on "ship it" + a YELLOW ack of that exact reason set, run smoke + review then commit/push/PR. `range(float)` crash in the MultiStart gradient step loop; fires ONLY when the cadence is below the remaining budget (the 1e99 config default always took the int branch, which is why it never fired before). Killed RAL chain jobs 331182-331190 in the wsdev#117 campaign. Fix = int() cast at the consumer via a `_steps_in_chunk` helper; the shared float() coercion in abstract_search.py:219 stays (it serves inf-like config values). Helper exists so the test is NumPy-only — `_fit` needs jax+optax+a JAX Analysis. PyAutoFit claim was released from the completed `testmode-env-drift` task first (3a99904). FOLLOW-UPS (not this PR): 5 sibling searches share the latent float-cadence class (emcee/zeus/blackjax-nuts/bfgs/nautilus+dynesty), unreproduced; and the workspace hotfix in autolens_workspace_developer/searches_minimal/pix_prodigy.py belongs to the live `pix-prodigy-cpu` task.
- repos:
  - PyAutoFit: feature/multistart-cadence-int-cast

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
