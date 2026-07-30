# Active Tasks

## scaling-relation-degraded-profile-fixes
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/419
- session: claude --resume b79e03f8-64be-4fce-8c2d-e8b98ce8f487
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/scaling-relation-degraded-profile-fixes
- note: no real worktree claims on autolens_workspace at start (hand-checked; #414/#416/#417/#418 all merged, zero open PRs)
- note: `ENV: real_search` rejected by measurement — imaging slam.py still running at 1293s vs 300s default cap (lower bound, did not finish); no_run.yaml is the chosen route
- note: interferometer/features/scaling_relation/slam MUST stay runnable (hardcodes its luminosity) — verified rc=0 and asserted via should_skip that the skip set widens by exactly 2
- repos:
  - autolens_workspace: feature/scaling-relation-degraded-profile-fixes

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- status: phases 1-3 SHIPPED; phase 4 PARKED in planned.md; no worktree, no repo claims held (checkpoint 2026-07-30, resume fresh from this entry)
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phase-3-pr: workspace_test#237, profiling#96, workspace_developer#121 (ALL MERGED 2026-07-30; worktree + branches cleaned; shipped comment https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5135275039)
- phases: 1 (design) + 2 (core API) + 3 (examples/profiling) COMPLETE. Phase 4 (guides) PARKED — see planned.md "point-source-chi-squared-variants — phase 4": blocked on the autolens_workspace claims of #408 (PR autolens_workspace#414) and #409 (PR #417); unblocks when both merge, or on explicit human authorization of a third concurrent claim. Phase 5 (PointSolver custom_jvp gradients, draft phase-5 prompt) touches PyAutoLens (+PyAutoArray) — NOTE PyAutoLens is claimed by potential-correction-validation (#672); hand-check file overlap before starting.
- resume-context: project memory `point-source-solved-likelihoods` holds phase-3 literals + lessons (H0-matched parity for time-delay fits; fit_from pytree gap is the ONLY remaining jit blocker; output_to_json key-order nondeterminism filed in ideas.md; profiling baselines used PointFlux so solved swap drops 3 params not 2)
- repos:


## potential-correction-validation
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/672
- session: claude --resume 0100b7de-da01-4c18-a8b0-9d0080d5e07f
- status: library-dev (phase 1 = workspace smoke-timeout fix, ships first as standalone wst PR)
- worktree: ~/Code/PyAutoLabs-wt/potential-correction-validation
- phases: 1 (wst smoke timeout) → 2 (JAX-vs-Python parity hunt vs for_qiuhan tar) → 3 (evidence-sampled recovery test + analysis fast path) → 4 (algorithm review report)
- note: Brain sized too-large (13); content-based 4-phase split recorded in the prompt. wst has feature/point-source-chi-squared-variants checked out in another worktree (empty repos: claim) — files disjoint, pre-merge origin/main before each PR
- repos:
  - PyAutoLens: feature/potential-correction-validation
  - autolens_workspace_test: feature/potential-correction-validation

## sampler-cli-output-numbers
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1434
- session: claude --resume ba3c8adc-e29a-465b-9045-c13f08824092
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/sampler-cli-output-numbers
- phases: 1 (PyAutoFit: quick_update_message + JAX compile message at first call) = this issue; 2 (drop the now-duplicated sentence from 23 workspace scripts + regenerate notebooks/markdown) = follow-up issue
- note: Brain sized large (score 8) and wanted a phase split; score is its repo-count proxy — overridden to medium, library/workspace split kept
- note: CONCURRENT claim on PyAutoFit with multi-start-gradient-progress-logging (#1433, registered minutes earlier). worktree_check_conflict returned 0 only because that worktree did not exist yet — hand-checked instead. Files disjoint: #1433 owns multi_start_gradient/search.py, this owns abstract_search.py + fitness.py. Pre-merge origin/main before PR. Related in substance: #1433's "always log the first step" and this task's first-call compile message both signal "the XLA compile finished" — keep the wording from duplicating
- repos:

## multi-start-gradient-progress-logging
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1433
- session: claude --resume 9b8e086c-0f40-46ad-ae8c-cda3179a335e
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/multi-start-gradient-progress-logging
- note: Brain sized large (score 8); overridden to small / no-phase-split — every point came from prompt prose (521 words +3, science keywords dynesty/emcee/gradient/jax/sampler +3, jax/vmap +1, memory-context +1) while repos_affected=1 and architectural_risk=[] contributed nothing
- repos:
