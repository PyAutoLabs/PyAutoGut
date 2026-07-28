# Active Tasks

## issue-cleanup
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/174
- session: claude
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/issue-cleanup
- autonomy: supervised
- prompt: active/issue_cleanup_skill.md
- note: Builds /issue_cleanup, the missing issue-tracker reconciliation door (no skill owned this — /repo_cleanup is git debris only, /community is external issues). Preceded by an ad-hoc sweep on 2026-07-28 that took the trackers 82 open → 47: closed 29 shipped-but-open (two-leg verified: record header + merged PR) and 6 obsolete 2018–2019 PyAutoCTI (named API greps zero in autocti/). LOAD-BEARING FINDING the skill must encode: the PyAutoMind record header KEY carries the meaning — `issue:` (630 uses) completes, but `followup-issue:`/`follow-up-issue:`/`library-followup-issue:`/`parent-issue:`/`upstream-issues-filed:`/`plan:` (13 uses) mean the record SPAWNED a still-open issue; a loose `*issue*:` match would close live follow-ups. Three more traps: body mentions ≠ header claims (many-vis-prep-dft.md discusses PyAutoArray#326 while its own issue: header says "no GitHub issue"); inline `(open …)`/`(STAYS OPEN …)` annotations override and appear on `plan:` lines too; a record in complete/ can carry `Status: issued` (ep-hierarchical-scale-collapse.md FILED PyAutoFit#1405, which is a live bug). PyAutoHands#16/#17 deliberately LEFT OPEN — same 1337-day vintage as the closed CTI ones but still-valid unimplemented asks (no --pre workflow, no RTD gating exist), so age ≠ obsolescence. Approved mode: audit auto-runs read-only in /wake_up, every close stays human-gated. Brain said large/split-into-phases — OVERRIDDEN to single phase (one skill, one repo, reasoning already settled); its "public-API ripple" risk is a false positive for a skill body. Claimed PyAutoBrain over a STALE guard-followups claim (all 3 of its PRs merged 12:53 2026-07-28; its active.md entry still says "3 PRs open" and needs its own post-merge cleanup — not done here).
- repos:
  - PyAutoBrain: feature/issue-cleanup

## guard-followups
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/204
- status: awaiting-merge — 3 PRs open. PyAutoHands#205 (closes #204), PyAutoBrain#173, autogalaxy_workspace#176.
- worktree: ~/Code/PyAutoLabs-wt/guard-followups
- autonomy: supervised
- prompt: draft/bug/workspaces/notebook_kernel_cwd_breaks_auto_simulate.md
- note: 3 follow-ups from auto-simulate-guard-targets, one PR per repo (a single PR cannot span repos). #204 investigation REFUTED both its own fix options — nbconvert has NO CLI flag for kernel cwd (only resources['metadata']['path'] via the Python API), and `__file__` is UNDEFINED in a notebook kernel so the per-script option was unimplementable. Chose 1b: subprocess a new autohands/run_notebook.py, keeping isolation/timeout/env. TRAP preserved: is_clean_skip_exit string-parses stderr for CellExecutionError + `SystemExit: 0`, so CellExecutionError is left UNCAUGHT on purpose. CI GAP: neither PyAutoHands nor PyAutoBrain runs tests on PRs (python_matrix = dispatch+weekly cron; docs.yml = docs/** on main) — matrix hand-dispatched on the branch for #205.
- repos:
  - PyAutoHands: feature/guard-followups
  - PyAutoBrain: feature/guard-followups
  - autogalaxy_workspace: feature/guard-followups

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
