# Active Tasks

## pixelization-eager-jit-divergence
- issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/580
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/pixelization-eager-jit-divergence
- prompt: active/pixelization_eager_vs_jit_divergence.md
- plan: unblock `jax_profiling/jit/imaging/pixelization.py` (broken on main two ways:
  `RectangularAdaptDensity` renamed by PyAutoArray#461 f9aceea3; `Basis.image_2d_list_from`
  assumes `grid.mask`, dies on `Grid2DIrregular` at basis.py:164), then settle the eager-vs
  step-by-step log-evidence gap. Working hypothesis (probe before writing it up): eager
  `Inversion.reconstruction` is fnnls non-negative (`use_positive_only_solver: true`) while the
  script's step-by-step does a plain pos/neg `solve(F+H, D)` — a genuine difference, not FP drift
  as the current comment claims. Prompt suspects 1/2/4 already falsified.
- scope-note: the ~40 OTHER files still naming `RectangularAdapt{Density,Image}` are PyAutoArray#461's
  announced workspace follow-up campaign — deliberately NOT in this PR. File a separate prompt.
- stale-prompt-note: the prompt's `-1.3e9` values, two constants and FIXME are superseded by
  workspace_developer PR #60; `EXPECTED_LOG_EVIDENCE_HST` has also drifted ~1e-2 and needs re-pinning.
- repos:
  - PyAutoGalaxy: feature/pixelization-eager-jit-divergence
  - autolens_workspace_developer: feature/pixelization-eager-jit-divergence

## numba-cpu-likelihood-profiling
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/151
- pr: https://github.com/PyAutoLabs/autolens_profiling/pull/152
- status: awaiting-merge — infra + Rectangular euclid/hst pass + Delaunay euclid pass on PR #152
  (last commit 8e742e9, 2026-08-20). CAMPAIGN FIDUCIAL = Delaunay + Hilbert(1500) AdaptImage +
  ConstantSplit (user pivot 2026-08-20); Rectangular kernel-CDF speed-up DEFERRED.
- delaunay-verdict: euclid 4.6 s/eval — RECONSTRUCTION SOLVE 3.73 s (~78%, 1560-param
  positive-only); MGE matrices 0.51 s; triplets only 15 ms. Prime restoration suspect: legacy
  numba fnnls + cholesky_funcs deleted in PyAutoArray 8bb449a1 (2025-06-18).
- RESUME: (1) run delaunay_numba runtime+breakdown at hst, pin hst value, push to PR #152;
  (2) verify which solver runs (settings.use_positive_only_solver) + its source-pixel scaling;
  (3) write + start_dev a PyAutoArray solver-restoration prompt, and start_dev
  draft/feature/autoarray/numba_cpu_likelihood_mge_convolution_and_caching.md (still valid);
  (4) on merge: RAL scaling sweep (hpc/batch_cpu/...), worktree cleanup, completion record.
  Bug prompt filed: draft/bug/autoarray/numba_first_call_garbage_psf_weighted_data.md.
  Full findings trail: issue #151 comments.
- worktree: ~/Code/PyAutoLabs-wt/numba-cpu-likelihood-profiling
- prompt: active/numba_cpu_likelihood_profiling.md
- plan: build numba-CPU sparse-operator likelihood profiling infra in autolens_profiling —
  runtime cell + step-by-step breakdown cell (euclid default, hst/jwst) + multiprocessing
  scaling harness (serial vs Nautilus object-pool vs initializer-cached pool, pickle payload,
  BLAS interplay) + RAL SLURM submit; then first local pass (euclid+hst, cores 1-8) and
  findings. Repos edited: autolens_profiling only.
  - Repo autolens_profiling: branch feature/numba-cpu-likelihood-profiling

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

## hands-hygiene-leftovers
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/249
- session: claude --resume 08f77ea2-bf3a-42f4-a427-e01da3a4ce2d
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/hands-hygiene-leftovers
- prompt: active/hands_hygiene_leftovers.md
- scope-note: the prompt's third bullet (~30 stale PyAutoHands remote branches, incl.
  origin/master, origin/release) is deliberately OUT of this task's PR — run it as a
  separate /repo_cleanup sweep so a destructive branch delete never rides a code diff.
- repos:
  - PyAutoHands: feature/hands-hygiene-leftovers

## autofit-sampler-database
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1508
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/autofit-sampler-database
- prompt: active/autofit_sampler_database.md
- plan: REPRODUCTION-GATED. Phase 1 re-runs the nine release-run scripts (2 autofit_workspace
  cookbooks + 7 autofit_workspace_test database/output scripts) on current main from a clean
  output/ under each workspace's config/build/profile_release.yaml, env resolved via PyAutoHands
  build_env_for_script with the workspace as CWD. Only survivors get fix phases: (2) Emcee /
  bounded-prior NaN in PyAutoFit source, (3) database directory/scrape/grid/sensitivity/
  minimal-output audit, (4) regression tests + pytest + clean re-run, then library-first ship.
- staleness-warning: the premise is 6+ weeks old and the SIBLING prompt from this exact release
  run (samples_parameter_paths, PyAutoFit#1327) was PARKED as not-reproducing — root cause judged
  stale cached output/ in the run, not a library defect; its planned.md entry warns the other
  health_fixes/ siblings are suspect too. A second sibling (aggregator_output_contracts) already
  SHIPPED 2026-07-07. PyAutoFit has since merged #1413, 9f887a9b1, 8f6f4ef7d, #1377, #1401,
  #1422, #1470, #1486, #1391 — all touching the exact scrape/aggregator/emcee machinery blamed.
  If 0/9 fail, park this like its sibling and close with the evidence; do NOT fix a phantom.
- clean-state-note: clearing output/database/ alone is NOT clean — output/database.sqlite and
  output/database.info are SIBLINGS of it and the aggregator reads the stale rows.
- cost-note: autofit_workspace_test runs at PYAUTO_TEST_MODE=0 (FULL searches, 1800s release cap);
  one clean pass over the seven scripts plausibly takes hours — run Phase 1 detached.
- repos:
  - PyAutoFit: feature/autofit-sampler-database
  - autofit_workspace: feature/autofit-sampler-database
  - autofit_workspace_test: feature/autofit-sampler-database
