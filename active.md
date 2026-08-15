# Active Tasks

## pix-prodigy-gpu-compat
- issue: https://github.com/PyAutoLabs/autolens_workspace_developer/issues/125
- prompt: active/pixelized_prodigy_laptop_gpu_phase_1_compatibility.md
- pr: https://github.com/PyAutoLabs/autolens_workspace_developer/pull/126 (OPEN, mergeable)
- session: codex (phase 1) -> claude 2026-08-11 evening (n_starts control + phase 2)
- status: workspace-dev — phase 1 and phase 2 COMPLETE 2026-08-13, all 13 cells landed, PR #126 ready for review
- results: `searches_minimal/pix_prodigy_laptop_gpu_findings.md` (§1-6). Phase-1 item 2 (16-start claim) CONFIRMED on GPU. Phase 2 done: DelaunayNN starts curve, VRAM ceiling (batch 8 OOMs family-wide), batch-size comparison, free-vs-fixed regularization, revised four-mesh recommendations, plus two corrections to earlier claims.
- headline: batch size decides whether plain Delaunay finds truth (b2 +30203.3 @ r_E 1.6001 vs b4 +24581.8 @ 1.6314 — the local max was batch-caused). DelaunayNN is batch-INSENSITIVE (0.5 nats apart), matching its continuous Sibson interpolation through triangulation flips. So "batch 4 wins" is a DelaunayNN result that does NOT generalise.
- corrections-made: (a) "4 starts too few" over-attributed — that cell moved starts AND batch AND steps; at batch 4/300 steps 4 starts does reach truth. (b) KNN needs ~300 steps with fixed reg, not the >=1500 extrapolated from free AdaptSplit.
- still-open (documented, not blocking): DelaunayNN free-AdaptSplit beyond 300 steps (still climbing at cap, 109 resurrections); whether those lane deaths are NaN or over-regularized-floor needs a DelaunayNN truth-bar scan at high coefficients.
- worktree: ~/Code/PyAutoLabs-wt/pix-prodigy-gpu-compat
- repos:
  - autolens_workspace_developer: feature/pix-prodigy-gpu-compat

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
