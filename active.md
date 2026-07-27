# Active Tasks

## clean-slate-write-site
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/169
- session: claude
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/clean-slate-write-site
- autonomy: supervised
- prompt: active/clean_slate_write_site_provenance.md
- note: leg 5 (final) of the dataset-bulk series. New bin/dataset_provenance.py (write-site classifier: REGENERABLE/DOWNLOADED/ORPHAN; orphans reported not deleted), clean_slate phase 1b uses it; per-dir size warning; git gc --auto phase; .ipynb_checkpoints swept, __pycache__ deliberately left; wake_up.md 'non-destructive' claim fixed; net-new tests for phases 1/1b/2/3 (currently ZERO coverage). Ground-truth catch/never-touch lists in the issue.
- repos:
  - PyAutoBrain: feature/clean-slate-write-site

## multistart-cadence-int-cast
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1420
- session: claude
- status: library-shipped, awaiting-merge
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1421
- worktree: ~/Code/PyAutoLabs-wt/multistart-cadence-int-cast
- autonomy: supervised (prompt header `safe`, capped by the `bug` work-type cap in AUTONOMY.md)
- prompt: active/multistart_iterations_per_full_update_float_crash.md
- heart-ack: 2026-07-27 human acknowledged this library ship with the exact YELLOW reasons below (Heart score 65, ts 2026-07-27T12:11:07Z, no RED); any new reason or RED verdict requires a fresh stop
  - workspace validation not passing (13 failed, 2026-07-21T19-05-22Z)
  - 33 stale parked script(s)
  - manifest drift: tenant firewall (organ code) — 5 mismatch(es) vs PyAutoMind/repos.yaml
  - release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)
- note: SHIPPED to PR#1421 (3 commits), awaiting merge. Codex gpt-5.6-sol adversarial review (2nd opinion) CORRECTED me: sibling list is TWO confirmed-broken (emcee range(iterations) no cast; blackjax jax.random.split(key,50.0)) not five — zeus is SAFE (casts internally), bfgs/dynesty/nautilus tolerated. It also killed my rationale for not touching abstract_search.py:219 (Python ints represent 1e99 fine — the coercion protects nothing). Commit 3 replaced the silent max(1,...) floor with ValueError validation of BOTH cadence and n_steps. 3 draft prompts filed (Mind 8a3a4d1): emcee/blackjax crash + 2 pre-existing MultiStart bugs (duplicate final perform_update — MultiStart is the OUTLIER, every sibling passes during_analysis=True unconditionally; stale stop_reason on resume). Tests 1541 passed/1 skipped. Tests 1535 passed/1 skipped; review CLEAN on pass 2 — pass 1 caught a defect I introduced (int() truncates toward zero, so a fractional cadence <1 gave range(0) => zero-length chunk => infinite while-loop; floored at 1, test added). Smoke 50 pass/7 fail, all 7 identical on main (jax_likelihood parity scripts run under PYAUTO_DISABLE_JAX=1); a further 5 failed ONLY in the parallel sweep and pass sequentially on the branch — runner contention over shared output/dataset state, NOT a regression. `range(float)` crash in the MultiStart gradient step loop; fires ONLY when the cadence is below the remaining budget (the 1e99 config default always took the int branch, which is why it never fired before). Killed RAL chain jobs 331182-331190 in the wsdev#117 campaign. Fix = int() cast at the consumer via a `_steps_in_chunk` helper; the shared float() coercion in abstract_search.py:219 stays (it serves inf-like config values). Helper exists so the test is NumPy-only — `_fit` needs jax+optax+a JAX Analysis. PyAutoFit claim was released from the completed `testmode-env-drift` task first (3a99904). FOLLOW-UPS (not this PR): 5 sibling searches share the latent float-cadence class (emcee/zeus/blackjax-nuts/bfgs/nautilus+dynesty), unreproduced; and the workspace hotfix in autolens_workspace_developer/searches_minimal/pix_prodigy.py belongs to the live `pix-prodigy-cpu` task.
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

## delaunay-nan-callback
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/410
- session: codex
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/delaunay-nan-callback
- autonomy: supervised (`--auto`; capped by the `bug` work-type cap in AUTONOMY.md)
- prompt: active/delaunay_tables_callback_nan_points_crash.md
- repos:
  - PyAutoArray: feature/delaunay-nan-callback
  - autolens_workspace_test: feature/delaunay-nan-callback
