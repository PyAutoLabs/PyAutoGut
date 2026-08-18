# Active Tasks

## cli-noise-pyautofit-batch
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1495
- session: Claude Code web (remote), branch claude/pyautofit-cli-noise-fixes-vqs7mg
- status: library-dev — IMPLEMENTATION PUSHED 2026-08-18 as PyAutoFit `7d1fe19` (6 files, +42/−5);
  full suite 1884 passed / 3 skipped on py3.13 + scipy 1.17.1; all five warnings verified
  reproduced-then-gone. No PR opened yet.
- worktree: none (remote web session — session clone, no local worktree)
- repos:
  - PyAutoFit: claude/pyautofit-cli-noise-fixes-vqs7mg
- prompt: active/cli_noise_pyautofit_batch.md
- CONFLICT OVERRIDE (deliberate, 2026-08-18): PyAutoFit is also claimed by
  `stored-sample-reconstruction-guard` (`autofit/non_linear/samples/`) and
  `version-stamp-sync-guards` (`autofit/__init__.py` + `files/release.sh`). This task is
  FILE-DISJOINT from both: it touches `non_linear/search/abstract_search.py`,
  `non_linear/search/nest/nautilus/search.py`, `non_linear/search/mle/bfgs/search.py`,
  `database/model/array.py` and two test files. Remote session on its own branch; if either
  in-flight task grows into these files, re-coordinate before merge.
- summary: five mechanical CLI-noise fixes from the 2026-08-06 `-W all` audit — close the
  `search.log` FileHandler in `configure_handler`'s `finally`; add SQLAlchemy `overlaps=` to the
  `Fit.arrays`/`Fit.hdus`/`HDU.fit` relationship overlap; nautilus `evidence()` → `.log_z`;
  stop passing scipy-deprecated `disp`/`iprint` to L-BFGS-B; module-local fork()
  DeprecationWarning filter in `test_fork_context.py`.

## stored-sample-reconstruction-guard
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1486
- status: library-dev — WORKSPACE HALF SHIPPED; the PyAutoFit hardening (#1486) is what remains
- worktree: ~/Code/PyAutoLabs-wt/stored-sample-reconstruction-guard
- repos:
  - PyAutoFit: feature/stored-sample-reconstruction-guard
  - autogalaxy_workspace: feature/stored-sample-reconstruction-guard
- workspace-PR: **MERGED 2026-08-17T22:08Z** as `1b5005c8` (squash), branch deleted. All 6 checks green
  (smoke 3.12 3m37s, smoke 3.13 3m44s, 3x navigator). Verified present on origin/main. This closes the
  nightly Workspace Smoke red; Heart's `workspace validation not passing` reason should clear on its
  next tick. Was: https://github.com/PyAutoLabs/autogalaxy_workspace/pull/210 (no pending-release label —
  `valid_sample_instance_pairs` ships in RELEASED autofit 2026.8.15.1, wheel inspected, so the
  library-first gate does not apply)
- heart-ack (2026-08-17, human): acknowledged YELLOW score 70 to ship PR#210. Exact reasons acked:
  "workspace validation not passing (1 failed, cloud#31992749671: autogalaxy notebooks/guides/samples.ipynb)";
  "manifest drift: tenant firewall (organ code) — 9 mismatch(es) vs PyAutoMind/repos.yaml";
  "release validation incomplete: no rehearsal for current source". Ack does NOT extend to new reasons.
- prompt: active/to_instance_guard_gap.md
- CONFLICT OVERRIDE (deliberate, 2026-08-17): `worktree_check_conflict` exits 1 — PyAutoFit is also
  claimed by `version-stamp-sync-guards` (PyAutoHands#235). Proceeding was authorized by the human
  after verifying the two are FILE-DISJOINT: that branch's only commit (`9ec8a3877`) touches
  `autofit/__init__.py` + `files/release.sh`; this task touches `autofit/non_linear/samples/`.
  Two git worktrees on one repo with different branches is legal; the guard is a workflow
  convention, not a git limit. If #235 starts touching `non_linear/samples/`, stop and re-coordinate.
- summary: `Sample.instance_for_model(ignore_assertions=True)` (`sample.py:178-212`, the CI failure
  site) and the shared `to_instance` decorator (`interface.py:32-40`) materialize stored samples with
  no `FitException` recovery. PyAutoFit#1466 wrote recovery by hand at two call sites only
  (`max_log_likelihood`, `draw_randomly_via_pdf`). Fails PyAutoHeart Workspace Smoke nightly on
  `autogalaxy_workspace guides/results/aggregator/samples.ipynb`; holds Heart's
  `workspace validation not passing` reason open.
- design (human-decided): `to_instance` takes a per-method recovery policy — `recover="next_valid"`
  for `max_log_posterior`, `recover="raise"` (typed `SamplesException`) for `from_sample_index` and
  the marginalized methods. Release note: raise path changes the user-visible type from
  `ModelParameterException` (a ValueError) to `SamplesException` (plain Exception).
- split-out: PyAutoFit#1487 — weight-threshold prune retains zero-weight samples with checks ENABLED.
  Do not fix here.
- do-not: do NOT weaken PyAutoGalaxy `validate_ell_comps`; do NOT edit the tutorial. Test mode is NOT
  implicated (`ENV: real_search` releases `PYAUTO_TEST_MODE`) — verified, do not re-open.

## heart-green-validation-ingest
- issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/567 (open, reopened 2026-08-11T00:22Z)
- session: none — the Codex session that did the work ran out of credits after merging, before any bookkeeping. Registered 2026-08-11 by a cloud session reconstructing its state from GitHub.
- status: EVIDENCE PENDING INGEST — not a code task. All four fixes are MERGED (see complete/2026/08/heart-red-guarded-sample-escape.md); the green run exists; only the ingest is owed.
- what is owed: PyAutoHeart `Release Integrate` run **31534325304** (dispatched 2026-08-11T20:42:55Z on main `b7634e2c`, finished 21:50:07Z) came back **SUCCESS** — 53 jobs, 52 green, `integrate / run_notebooks` skipped by design. Its `release-stage-report` artifact has never been consumed, so Heart's verdict does not yet reflect it.
- resume: **nothing to type.** `heart/checks/release_run.py` self-refreshes this channel — the next Heart tick on the dev box reads the latest completed `release-integrate` run, finds no sidecar for run id 31534325304, and downloads + ingests its `release-stage-report` through `heart.validate.run()` automatically (a fresher local ingest is never regressed; an ingested run is never re-downloaded). So any `/health`, `/wake_up` or bare tick from the laptop closes this out. Manual fallback only if that path fails: `gh run download 31534325304 -R PyAutoLabs/PyAutoHeart -n release-stage-report -D <dir>` then `pyauto-brain release validate --ingest <dir>`.
- deadline: the artifact expires **2026-11-09**. After that the evidence is gone and the run must be re-dispatched from scratch.
- why not from a cloud session: two independent reasons, and the second is the load-bearing one. (1) Actions artifact downloads 403 at the egress proxy (`productionresultssa14.blob.core.windows.net` CONNECT refused) even though the GitHub API returns a valid signed URL — the `artifacts-are-laptop-only` trap already recorded under release-drive-2026-08-07; the proxy README classes that as an org policy denial to report, not route around. (2) Even with the file in hand, `validate --ingest` writes `validation_report.json` into `HEART_STATE_DIR` (`~/.pyauto-heart`), which on a cloud container is ephemeral and shared with nothing — the dev box's verdict would be untouched. Heart's authoritative verdict lives where its state lives.
- note on the README dashboard: the `<!-- heart:begin -->` block is rendered by the CLOUD `Heart Health` job, which runs only the two GitHub-API checks against an empty `.heart-state`. Its `test run status unknown` / `install verification not run` / `no release validation for current source` gaps are inherent to that cloud snapshot, NOT a claim that the dev box lacks the evidence. Do not read the README block as the dev-box verdict.
- current verdict: Heart's last committed dashboard (2026-08-11T05:51Z, i.e. BEFORE the green run) reads STALE score 65, listing `no release validation for current source` among its evidence gaps. That is the STALE tier behaving correctly — an evidence gap, not a fault, and this ingest is its remedy.
- do-not: do NOT re-dispatch `Release Integrate` to "refresh" this. The run is green and its artifact is live; a re-dispatch costs ~70 minutes of CI and proves nothing new. Only re-dispatch if the artifact has expired or main has moved.
- repos-none-claimed: this entry claims NO repos — deliberately on one line, NOT as 2-space `  - Repo` bullets, because `worktree_check_conflict` treats any such bullet as a live claim.
## version-stamp-sync-guards
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/235
- prompt: active/version_stamp_sync_and_release_sed_guards.md
- session: claude --resume d73342fb-c33f-4028-8741-30cbe0c856a3
- status: pr-open (https://github.com/PyAutoLabs/PyAutoLens/pull/700)
- worktree: ~/Code/PyAutoLabs-wt/version-stamp-sync-guards
- repos:
  - PyAutoNerves: feature/version-stamp-sync-guards
  - PyAutoArray: feature/version-stamp-sync-guards
  - PyAutoFit: feature/version-stamp-sync-guards
  - PyAutoGalaxy: feature/version-stamp-sync-guards
  - PyAutoLens: feature/version-stamp-sync-guards
  - PyAutoHands: feature/version-stamp-sync-guards
