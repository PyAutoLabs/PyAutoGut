# Active Tasks

## auto-simulate-guard-targets
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/359
- status: awaiting-merge — PRs open, all CI green (Smoke Tests + Navigator Check on both). autolens_workspace#364, autogalaxy_workspace#175, both labelled pending-release. Heart was YELLOW (score 65, no RED) at ship; human acked the 3 unrelated reasons.
- worktree: ~/Code/PyAutoLabs-wt/auto-simulate-guard-targets
- autonomy: supervised
- prompt: draft/bug/autolens_workspace/auto_simulate_guard_wrong_simulator_target.md
- note: 6 mis-wired auto-simulate guards (2 reported + 4 found by audit), not 2. Root-cause question on #359 RESOLVED — should_simulate is a faithful drop-in for `not path.exists()`; no wider bug. Hazard: under PYAUTO_SMALL_DATASETS=1 it rmtree's the dir first, so a mis-targeted guard DESTROYS a correct dataset. None of the 6 scripts are in smoke_tests.txt, so smoke cannot verify this fix. Brain `bug` returned too-large + "fix locus = config/build/*.yaml, never the script body" — BOTH OVERRIDDEN (score is repo-count-driven; no config knob can repoint a hardcoded simulator path). Sibling PyAutoHands#204 keeps notebook shards red regardless.
- repos:
  - autolens_workspace: feature/auto-simulate-guard-targets
  - autogalaxy_workspace: feature/auto-simulate-guard-targets

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
  - autolens_profiling: feature/pix-prodigy-cpu
  - autolens_workspace: feature/pix-prodigy-cpu

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- session: claude --resume daaa46f9-aac5-48e2-9146-1202a92d879e
- status: library-merged, workspace-pending
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phases: 1 (design) + 2 (core API) COMPLETE; next: start_workspace on active/../draft phase-3 prompt (workspace_test jax_likelihood + profiling examples), then phase 4 (guides), then phase 5 (JAX solver gradients)
- repos:
