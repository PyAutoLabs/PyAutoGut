# Active Tasks

## jax-compile-stall-root-cause
- epic: jax-compile-stall (phase 3 of 3; ledger draft/bug/ci/jax_vmap_jit_compile_stall.md)
- phase-prompt (still in draft/, deliberately not advanced to active/): the phase 3 file
  draft/bug/ci/jax_compile_stall_3_root_cause.md has no GitHub issue of its own — the experiments
  run under autolens_workspace_test#271 while they are exploratory. Issue it if phase 3 turns into
  a shippable fix rather than a hunt.
- status: workspace-dev (experiment in flight)
- started: 2026-08-23
- experiment 1 — the vmap-of-jit ordering:
  - Fitness._vmap builds jax.vmap(jax.jit(self.call)); analysis/latent.py builds the conventional
    jax.jit(jax.vmap(...)). The stalling scripts are exactly the vmap-path ones.
  - branch `experiment/jax-vmap-jit-ordering` in PyAutoFit (swapped, NOT for merge) and a
    same-named branch in autogalaxy_workspace_test so the workspace CI's matching-branch clone
    picks the swapped library up.
  - dispatched retime.yml from that branch on imaging/jax_likelihood/rectangular_mge.py,
    repeats=5, 300s cap. Control: the same entry on main measured 4/5 stalls on BOTH legs
    (~80% per compile). A clear drop in stall rate implicates the ordering; no change exonerates it.
- experiment 2 — the persistent compile cache (not yet run): JAX_COMPILATION_CACHE_DIR has been on
  by default since PyAutoConf#128 (2026-07-17); both NEEDS_FIX stalls post-date it, the SLOW batch
  predates it. A/B with the cache disabled.
- in flight from phase 2, kept because they feed phase 3: the 1800s runs on
  imaging/jax_likelihood/mge_group.py (ag_test) and multi_dataset/jax_likelihood/mge.py (al_test),
  repeats=2 — with PyAutoFit#1518 merged these should dump a faulthandler stack at 1440s, which is
  the first look at WHERE the stall sits.
- repos:
  - PyAutoFit: experiment/jax-vmap-jit-ordering
  - autogalaxy_workspace_test: experiment/jax-vmap-jit-ordering

## jax-compile-stall-slow-vs-stall-audit
- issue: https://github.com/PyAutoLabs/autolens_workspace_test/issues/271 (issued 2026-08-23)
- issued: 2026-08-23
- prompt: active/jax_compile_stall_2_slow_vs_stall_audit.md
- status: workspace-dev
- epic: jax-compile-stall (phase 2 of 3; ledger draft/bug/ci/jax_vmap_jit_compile_stall.md)
- worktree: ~/Code/PyAutoLabs-wt/jax-compile-stall-slow-vs-stall-audit
- worktree-note: started in a web-github session with no local tree; no branch cut yet.
- decision: harness lives Heart-side (human choice 2026-08-23) — a `runner` input on the
  reusable smoke-tests.yml rather than a per-workspace duplicate of the ceremony.
- prs: ALL MERGED 2026-08-23
  - https://github.com/PyAutoLabs/PyAutoHeart/pull/161 (runner input) — merged
  - https://github.com/PyAutoLabs/autolens_workspace_test/pull/272 (retime harness) — merged
  - https://github.com/PyAutoLabs/autogalaxy_workspace_test/pull/110 (retime harness) — merged
- harness: `retime.yml` (workflow_dispatch) + `.github/scripts/retime.py` now live in both test
  workspaces. Inputs: scripts (comma-separated, relative to scripts/), repeats, script-timeout
  (300 = smoke, 1800 = release). Verdicts STALL/SLOW/NEITHER/AMBIGUOUS/ERROR + retime_results.json.
- measured 2026-08-23, first dispatch (4 entries x 5 repeats x 2 legs = 40 executions, 300s cap;
  ag_test run 32664679042, al_test run 32664682689) — findings on issue #271:
  - `interferometer/datacube/shared_preloads.py` (al_test) NEITHER — 10/10 completed, slowest
    34.0s = 1.9% of the 1800s cap its SLOW marker says it "flakes at". Marker REFUTED; it should
    be removed, not rewritten. This is finding 1 of the marker-text analysis, now measured.
  - `imaging/jax_likelihood/rectangular_mge.py` (ag_test) STALL — 4/5 capped + one ~22s
    completion (7% of cap), the SAME split independently on 3.12 and 3.13. Bimodality measured;
    ~80% stall probability per compile, indifferent to Python version.
  - `imaging/jax_likelihood/mge_group.py` (ag_test) and `multi_dataset/jax_likelihood/mge.py`
    (al_test) AMBIGUOUS — 20 consecutive cap hits, zero completions. Need the 1800s pass.
- phase-1 defect found by this run: the faulthandler dump NEVER fired — its CI default was a flat
  300s and the smoke cap is also 300s, so the runner's SIGKILL beat the dump in all 20 stalled
  runs. Heartbeats worked; stacks did not. Fix: PyAutoFit#1518 derives the default from
  BUILD_SCRIPT_TIMEOUT at 80% (300s cap -> 240s). Phase 3 needs that stack, so this gates it.
- PyAutoFit#1518 MERGED 2026-08-23 — the dump now fires at 80% of BUILD_SCRIPT_TIMEOUT.
- dispatched 2026-08-23 21:37, the 1800s pass on the two AMBIGUOUS entries, repeats=2 not 5:
  ag_test imaging/jax_likelihood/mge_group.py and al_test multi_dataset/jax_likelihood/mge.py.
  Two repeats because the deliverable here is the STACK, not more distribution — both entries
  already hit the cap 10/10 at 300s, so one completion-or-cap settles the AMBIGUOUS question and
  any single stall yields the 1440s traceback. Caps the bill at ~1h/job instead of ~2.5h.
- SCOPE CUT 2026-08-23 (James): stop widening the measurement — the remaining 17 SLOW entries and
  the marker rewrites move OUT of this epic into `draft/research/ci/smoke_timing_and_profiling.md`,
  a follow-up task for proper smoke timing/profiling. Four entries measured was enough to prove the
  SLOW markers unreliable; sweeping the rest one dispatch at a time was not worth the runner budget.
  Phase 2 is therefore DONE for the epic's purposes — its question is answered.
- next: phase 3, the root cause.
- heart: NOT consulted — pyauto-heart unreachable from this web session.
- repos:

## transformed-message-factor-gradient-unpack
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1501 (issued 2026-08-19)
- issued: 2026-08-19
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
