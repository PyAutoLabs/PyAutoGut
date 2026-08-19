# Active Tasks

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
