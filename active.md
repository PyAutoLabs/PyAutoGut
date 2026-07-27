# Active Tasks

## spawn-drift-issued-orphan-ai-policy
- issue: none (same-session continuation of the 2026-07-27 /wake_up red-jobs sweep)
- session: claude
- status: library-shipped, awaiting-merge
- library-pr: PyAutoMind#113
- autonomy: supervised
- prompt: none (diagnosed inline from the failing Spawn Drift run)
- note: THREE stacked spec gaps, each surfacing only once the prior is cleared — issued/ orphan, then AI_POLICY.md (added org-wide today), then CONTRIBUTING.md (KEEP verbatim would stamp "Contributing to PyAutoLabs" into a fresh-slate template). After merge the job still needs a TEMPLATE REPUBLISH to clear content drift (AI_POLICY.md new + CONTRIBUTING/ROUTING/lifecycle.py/repos_sync.py/spawn.py/arxiv stale) — outward-facing, human-gated, NOT done yet.
- repos:
  - PyAutoMind: feature/spawn-drift-issued-orphan-ai-policy

## potential-correction-jax-skip
- issue: none (same-session continuation of the 2026-07-27 /wake_up red-jobs sweep)
- session: claude
- status: library-shipped, awaiting-merge
- library-pr: PyAutoLens#658 (pending-release)
- autonomy: supervised
- prompt: none (diagnosed inline from the failing python_matrix run)
- note: SECOND cause of python_matrix red, pre-existing and missed in the morning digest (job list truncated at 25 lines). 5 potential_correction tests reach the JAX-only sparse-operator path; jax is gated to py>=3.11. Skip-marked exactly those 5, per-test not module-level so the dense-route numpy cases keep running on 3.9/3.10. A numpy port was considered and rejected (3 jax sites incl. lax + segment_sum; imaging counterpart 8+). Verified: jax present 9 passed/0 skipped; jax absent 4 passed/5 skipped.
- repos:
  - PyAutoLens: feature/potential-correction-jax-skip


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

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- session: claude --resume daaa46f9-aac5-48e2-9146-1202a92d879e
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/point-source-chi-squared-variants
- repos:
  - PyAutoArray: feature/point-source-chi-squared-variants
  - PyAutoGalaxy: feature/point-source-chi-squared-variants
  - PyAutoLens: feature/point-source-chi-squared-variants
