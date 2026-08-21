# Active Tasks

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

## interferometer-operated-override
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/459
- user-facing: true
- session: https://claude.ai/code/session_01Lv2LDovvSQydk8biNMSAPL (remote; receipt + plan comments)
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/interferometer-operated-override
- plan: honor LinearObj.operated_mapping_matrix_override in interferometer inversions
  (direct data-space bypass in InversionInterferometer operated_mapping_matrix_list,
  consistent with imaging); guard autogalaxy LightProfileLinearObjFuncList override to
  return None when psf is None (prevents crash + preserves mapping_matrix→NUFFT path);
  add scripts/interferometer/features/operated_light_profile/ example packages to
  autogalaxy_workspace + autolens_workspace mirroring the imaging packages.
- progress: all four branches implemented, tested (autoarray 1090 pass + 3 pre-existing
  pynufft env failures; autogalaxy 1112 pass) and pushed 2026-08-21 from the remote
  session. Notebooks regenerated via PyAutoHands generate.py. PR-open milestone comment
  posted to reporter (visibility-space bypass semantics — watch for HRSAstro reply
  before merge).
- prs: PyAutoArray#460 (lead; closes #459) + PyAutoGalaxy#578 (merge together with #460);
  autogalaxy_workspace#220 + autolens_workspace#494 (pending-release, merge after
  library PRs). Next milestone: merged + released comment to reporter.
- repos:
  - PyAutoArray: feature/interferometer-operated-override
  - PyAutoGalaxy: feature/interferometer-operated-override
  - autogalaxy_workspace: feature/interferometer-operated-override
  - autolens_workspace: feature/interferometer-operated-override

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
