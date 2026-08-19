# Active Tasks

## mind-readability-pass
- issue: https://github.com/PyAutoLabs/PyAutoMind/issues/248
- status: in-dev — issued 2026-08-19, plan approved; direct-main edits in Mind/Heart,
  Brain renderer change via feature/mind-dashboard-header-trim PR
- prompt: active/mind_readability_pass.md
- repos-none-claimed: no worktrees — Mind + Heart edits land on main (Mind convention);
  the only branch is PyAutoBrain feature/mind-dashboard-header-trim (renderer header trim).
- summary: root declutter (overview.md deleted, queue.md emptied, AI_POLICY/CONTRIBUTING →
  .github/, health*.sh shims deleted, OWNERSHIP.md trimmed, lifecycle_drift.yml stale paths),
  dashboard header rewrite in the intake renderer, registry TOC self-heal script, README
  rewrite with a step-by-step "How PyAutoMind works".

## jax-default-dependency
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/702
- status: shipped-awaiting-release-followups — ALL ELEVEN PRs merged 2026-08-19 (human-authorized):
  six library (PyAutoHeart#150, PyAutoNerves#150, PyAutoFit#1503, PyAutoArray#450, PyAutoGalaxy#574,
  PyAutoLens#703) + five workspace (autolens_workspace#486, autogalaxy_workspace#212,
  autofit_workspace#139, HowToLens#71, HowToGalaxy#67; pending-release hold waived by human — prose-only,
  few-hour docs-ahead window until the nightly). Worktree removed, claims released, branches deleted.
- nojax CI leg caught two real bugs day one: unmarked jax-requiring autolens test (94d8f54ba);
  NumPy-scalar misrouting in autofit Beta/Gamma/Normal message dispatch (19c679583).
- jax cap stays <0.11 (widen reverted 848a254; jax 0.11 bug prompt:
  draft/bug/autofit/jax_011_message_log_partition_tuple_shape.md).
- NEXT (release-blocked; nightly 02:00 UTC): (1) bump intra-family floors `>=2026.7.29.2` → first
  promoted version in all five pyprojects, then move this task to complete/; (2) later, make
  unittest-nojax a required check once it has green history.
- prompt: active/jax_default_dependency.md

## stored-sample-reconstruction-guard
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1486
- status: library-shipped, workspace-pending — PyAutoFit hardening shipped as PR#1504 (2026-08-19);
  remaining: one-line autocti_workspace migration (samples.py:286 catch must add `SamplesException`)
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1504
- worktree: ~/Code/PyAutoLabs-wt/stored-sample-reconstruction-guard
- repos:
  - PyAutoFit: feature/stored-sample-reconstruction-guard
- claim-pruned (2026-08-19): autogalaxy_workspace released — PR#210 merged 2026-08-17, remote branch
  deleted, local worktree clean; the physical worktree dir remains for post-merge cleanup.
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

## transformed-message-factor-gradient-unpack
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1501 (issued 2026-08-19)
- prompt: active/16_transformed_message_factor_gradient_unpack.md
- status: HOLD — do not start dev. Fix-or-delete hangs off the PyAutoFit#1498 logpdf-contract
  decision (parked #1500 design bundle); dead code (zero production callers), crashes on first
  call if ever exercised.
- external: community PR https://github.com/PyAutoLabs/PyAutoFit/pull/1502 (@trexfr-ops) targets
  this exact unpack — review via /community before any local work; the #1498 adjudication decides
  whether the method should exist at all.
- registered: 2026-08-19 by the wake_up session — the issuing session (claude/autofit-priors-messages-audit-ylvenv)
  filed the prompt + issue but not this entry, tripping Lifecycle Drift on main.
- repos-none-claimed: this entry claims NO repos — one line deliberately, not 2-space bullets.

## lazy-heavy-imports
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1505
- status: library-dev — issued 2026-08-19, plan approved; implementation starting
- worktree: ~/Code/PyAutoLabs-wt/lazy-heavy-imports
- repos:
  - PyAutoFit: feature/lazy-heavy-imports
  - PyAutoArray: feature/lazy-heavy-imports
  - PyAutoNerves: feature/lazy-heavy-imports
- prompt: active/import_time_lazy_heavy_imports.md
- CONFLICT OVERRIDE (deliberate, 2026-08-19, human-approved): `worktree_check_conflict` exits 1 —
  PyAutoFit is also claimed by `stored-sample-reconstruction-guard` (#1486, library half shipped as
  PR#1504). FILE-DISJOINT: that task touches `autofit/non_linear/samples/` + `updater.py`; this one
  touches `autofit/__init__.py`, `non_linear/fitness.py`, `database/sqlalchemy_.py`, `paths/database.py`,
  search-module annotation headers. Also note `version-stamp-sync-guards` (PyAutoHands#235) has a
  PyAutoFit branch touching `autofit/__init__.py` version-stamp lines — coordinate at merge if both land.
- summary: defer jax chain (nufftax/blackjax/optax, measured 1.75s = 43% of import), IPython,
  sqlalchemy, numba (decoration-time), astropy to first use; dedupe autonerves version warning.
  Target `import autolens` 4.1s → ≤ ~1.9s. Matplotlib deferral deliberately scoped OUT (no
  smoke/user win — scripts import aplt anyway).
