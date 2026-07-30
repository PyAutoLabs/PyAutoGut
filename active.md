# Active Tasks

## optional-none-default-typos
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/674
- session: claude --resume 5b02920f-dfdb-476a-84df-e81a31971d19
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/optional-none-default-typos
- note: worktree conflict guard — 2 concurrent PyAutoLens claims (#408 phase 3, #672); hand-checked file-disjoint (neither branch touches tracer.py / tracer_util.py / max_separation.py)
- note: follow-up drift fix from multi-plane-guide-units (#411); group/start_here.ipynb notebook drift explicitly excluded per human (next generation pass owns it)
- repos:
  - PyAutoLens: feature/optional-none-default-typos

## cluster-dpie-docstring-style
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/410
- session: claude --resume f47a8f9e-ce35-4f6b-bde8-c35ef7338245
- status: awaiting-merge (PR open 2026-07-30; smoke 22/22; Heart YELLOW acked by human at PR-open)
- worktree: ~/Code/PyAutoLabs-wt/cluster-dpie-docstring-style
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/418
- note: worktree_check_conflict fired on 3 concurrent autolens_workspace claims (#407, #408, multi-galaxy-features-parity); hand-checked file-disjoint from scripts/cluster/** — only generated sidecars shared; pre-PR merge of origin/main was already up to date
- repos:
  - autolens_workspace: feature/cluster-dpie-docstring-style

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- session: claude --resume daaa46f9-aac5-48e2-9146-1202a92d879e
- status: phase-3-shipped, phase-4-pending
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phase-3-pr: workspace_test#237, profiling#96, workspace_developer#121 (ALL MERGED 2026-07-30; worktree + branches cleaned; shipped comment https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5135275039)
- phases: 1 (design) + 2 (core API) + 3 (workspace_test jax_likelihood + profiling examples) COMPLETE; next: start_workspace on draft phase-4 prompt (guides; fix cluster/likelihood_function.py false profile=None-centroid claim), then phase 5 (PointSolver custom_jvp gradients)
- repos:

## multi-package-rename-multi-dataset
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/408
- status: awaiting-merge (phases 1 + 3 + 2a PR-open 2026-07-30; phase 2b blocked)
- worktree: ~/Code/PyAutoLabs-wt/multi-package-rename-multi-dataset
- workspace-pr: autolens_workspace#414, autogalaxy_workspace#194 (both OPEN, pending-release)
- phase3-pr: PyAutoLens#673, PyAutoGalaxy#542, autolens_assistant#105, autolens_jax_joss#2 (all OPEN, docs-only)
- phase2a-pr: autogalaxy_workspace_test#101 (OPEN, pending-release) — the one phase-2 repo that was unclaimed
- note: HowToLens needs NO change — its only `multi/start_here` hit is inside a dated 2026-07-23 historical comment recording which override patterns were REMOVED; rewriting it would misrepresent what those patterns said
- note: autolens_assistant wiki-currency `--check-provenance` errors on any edited wiki/core page (content_sha256 stamp). Fix = `audit_skill_apis.py --write-provenance --page <each edited page>`; `--check-citations` passed (0 missing) even pre-merge
- MERGE ORDER: autolens_workspace#414 + autogalaxy_workspace#194 FIRST, then the four phase-3 PRs (they are blob/main URLs + paired_example pointers that 404/dangle until the package actually moves on main)
- heart-ack: YELLOW acknowledged by human 2026-07-30 for exactly these reasons — "manifest drift: tenant firewall (organ code) — 1 mismatch(es) vs PyAutoMind/repos.yaml"; stale: "test run status unknown (no report.json)", "release validation stale: source moved since rehearsal (PyAutoNerves, PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)". Does not extend to new reasons.
- phases: 1 (autolens_workspace + autogalaxy_workspace) PR-OPEN; 2 (autolens_workspace_test, autogalaxy_workspace_test, autolens_profiling, autolens_workspace_developer, HowToLens) BLOCKED on point-source-chi-squared-variants releasing its worktree claims; 3 (PyAutoLens/docs, PyAutoGalaxy/docs, autolens_assistant, autolens_jax_joss) GATED on phase 1 merging — blob/main URLs dangle until then
- note: Brain phase split (design/core_api/examples/docs) overridden for a per-repo, merge-dependency-ordered split; recorded in the prompt
- note: THREE concurrent claims on autolens_workspace (#407, #408 this task, #409). Human authorised proceeding over the worktree_check_conflict block — #407's claim was empty (zero commits). Mitigations: (a) this task touches only the multi/ package + its references, disjoint from #407's scaling_relation/ and #409's multi_galaxy/; (b) regenerate notebooks/markdown/workspace_index.json/llms-full.txt/.script_sizes.json LAST, after a pre-PR merge of origin/main
- repos:
  - autolens_workspace: feature/multi-package-rename-multi-dataset
  - autogalaxy_workspace: feature/multi-package-rename-multi-dataset

## multi-galaxy-features-parity
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/409
- status: workspace-dev (phase 1 starting 2026-07-30)
- worktree: ~/Code/PyAutoLabs-wt/multi-galaxy-features-parity
- workspace-pr: autolens_workspace#417 (OPEN, pending-release) — phase 1
- phases: 1 (slam.py baseline + no_lens_light + linear_light_profiles + extra_galaxies/slam.py + features/README) PR OPEN #417; 2 (MGE + pixelization), 3 (advanced light), 4 (advanced mass) each get their own issue as the prior one lands
- note: Brain phase split (design/core_api/workspace_examples/docs) overridden for a content-based split — no core-API leg in pure workspace-docs work; recorded in the arc prompt
- note: THIRD concurrent claim on autolens_workspace (with #407, #408). Human authorised proceeding over the worktree_check_conflict block (it fired on both). Mitigations: (a) do not touch multi_galaxy/features/scaling_relation/ — #407 owns it, the slam.py re-point is a follow-up; (b) regenerate notebooks/navigator/.script_sizes.json LAST, after a pre-PR merge of origin/main
- repos:
  - autolens_workspace: feature/multi-galaxy-features-parity

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

## jax-guard-pointer-retarget
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/427
- session: claude --resume 1eaf929e-624f-4e22-a28f-9b39e463258e
- status: awaiting-merge (PR open 2026-07-30, CI pending)
- prs: PyAutoArray#428
- heart-ack: same three YELLOW reasons as guides-jax-to-using-jax ack (2026-07-30), re-checked identical at ship time; does not extend to new reasons
- note: 2-line error-message retarget (lens_calc.py Phase 5d → using_jax.py); follow-up to autolens_workspace#412; no worktree (main-checkout branch, since deleted locally after push)
- repos:
  - PyAutoArray: feature/jax-guard-pointer-retarget
