# Active Tasks

## numba-cpu-likelihood-mge-operated-matrix-memo
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/454 (issued 2026-08-20)
- pr: https://github.com/PyAutoLabs/PyAutoArray/pull/455 — MERGED 2026-08-21 (1c33850,
  human-authorized from the cloud session); issue #454 closed; branch deleted
- status: merged-awaiting-release-followups — cross-eval memo for the MGE operated mapping matrices in
  imaging_numba/sparse.py only (user-constrained scope: numba bit, active only when MGE actually
  fixed via sha256 state fingerprint; batched-convolution half DEFERRED). Validated: euclid MGE
  step 0.56 s -> 0.004 s on hits; steady-state eval 2.34 -> 1.34 s; stacked with PyAutoArray#453
  today's euclid total is 4.92 -> 1.34 s (3.7x). Pins pass; +8 unit tests (1034 passed).
  Adversarial parameterization check clean (memo on/off ground-truth twin: 12 interleaved evals,
  worst 4.5e-10 rel; gating exact — see PR #455 comment). Post-release re-profile covered by the
  armed 02:45 UTC wake-up (now captures #453 + #455 together).
- prompt: active/numba_cpu_likelihood_mge_convolution_and_caching.md
- plan: see issue #454. Repos edited: PyAutoArray only.
  - Repo PyAutoArray: branch feature/numba-mge-operated-matrix-memo

## numba-cpu-likelihood-positive-only-solver-speedup
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/452 (issued 2026-08-20)
- pr: https://github.com/PyAutoLabs/PyAutoArray/pull/453 — MERGED 2026-08-20 (c7330a7,
  human-authorized from the cloud session); issue #452 closed; branch deleted
- status: merged-awaiting-release-followups — in-place factor buffer + copy-free numba
  solves + numba delete-shift kernel: euclid solve 3.29 -> 1.16 s (2.83x), euclid eval
  4.92 -> 2.34 s (2.10x), hst 3.95 -> 3.43 s; both autolens_profiling pins PASS at rtol
  1e-6 (existing pins stay valid — the solution shifts only ~1e-9 relative).
  PHASE 2 PROTOTYPED AND REJECTED (findings on issue #452): PJV block pivoting cycles on
  the near-degenerate columns; block-insertion Bro-Jong terminates non-converged via the
  no_update safeguard (KKT violated 3.7e3). Best remaining lever: cross-eval warm starts
  (option 3). NEXT (release-blocked; nightly 02:00 UTC; cloud session wake-up armed for
  ~02:45 UTC): install the released autolens in the cloud venv, re-run the delaunay_numba
  runtime/breakdown cells at euclid+hst, commit the new-version artifacts on a fresh PR,
  then completion record + prompt to complete/.
- prompt: active/numba_cpu_likelihood_positive_only_solver_speedup.md
- plan: see issue #452. Repos edited: PyAutoArray only.
  - Repo PyAutoArray: branch feature/fnnls-inplace-cholesky-buffer

## numba-cpu-likelihood-profiling
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/151 (closed by merge)
- pr: https://github.com/PyAutoLabs/autolens_profiling/pull/152 — MERGED 2026-08-20
  (564d51e, human-authorized from the cloud session); branch deleted
- status: merged-awaiting-hpc-sweep — infra + Rectangular euclid/hst + Delaunay euclid/hst passes,
  re-fiducialed to 1250 vertices per user (runs from a 4-core cloud
  container that first reproduced the 1500 euclid pin exactly). CAMPAIGN FIDUCIAL = Delaunay +
  Hilbert(1250) AdaptImage + ConstantSplit; Rectangular kernel-CDF speed-up DEFERRED.
  New pins: euclid 7215.3687893658935, hst 29090.527192092646 (rtol 1e-6).
- delaunay-verdict (1250): solve cost is ITERATION-BOUND, not resolution/param-bound — euclid
  3.61 s of 4.92 s (~74%, 153 active-set iterations); hst only 1.42 s of 3.95 s (near-perfect
  warm start at 1250; was 4.23 s at 1500). SOLVER VERIFIED (instrumented probe): positive-only
  fnnls_cholesky IS live in autoarray 2026.8.20.1 — the "deleted in 8bb449a1, restore it"
  hypothesis is RETIRED. Real cost: cholinsertlast/choldeleteindexes rebuild the ~1200^2 factor
  via np.insert/np.delete every iteration (2.41 s of 3.52 s) vs 0.047 s for ONE from-scratch
  Cholesky at n=1310. Speed-up prompt filed (numbers current for 1250):
  draft/feature/autoarray/numba_cpu_likelihood_positive_only_solver_speedup.md (in-place factor
  buffer / block pivoting / cross-eval warm starts).
- parallel_scaling: pixelization_numba.py now has --mesh delaunay (campaign fiducial); first
  euclid pass done 2026-08-20 (4-core container): 3.4x at P=4, 84-86% efficiency, pool variants
  indistinguishable, zero corrupted evals; RAL submit script added
  (submit_parallel_scaling_delaunay_numba_euclid, 1-32 cores).
- RESUME: (1) solver speed-up prompt now ISSUED + implemented (see
  numba-cpu-likelihood-positive-only-solver-speedup above, PyAutoArray#452); MGE memo prompt
  now also ISSUED + implemented (PyAutoArray#454/#455, entry above);
  (2) NOW UNBLOCKED BY MERGE (laptop/HPC): RAL scaling sweeps
  (submit_parallel_scaling_pixelization_numba_euclid + ..._delaunay_numba_euclid), local
  worktree cleanup (~/Code/PyAutoLabs-wt/numba-cpu-likelihood-profiling), then completion
  record.
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

## script-size-guard-git-based
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/490
- session: claude --resume 453f0202-8188-4e01-89a4-67bdb99523a2
- status: workspace-dev — PLANNED ONLY, NOT STARTED. Plan approved and filed on #490;
  human moved to mobile before implementation. Next action: /start_workspace on this
  entry (creates the worktree + branch); no repo has been edited and no worktree exists.
- worktree: ~/Code/PyAutoLabs-wt/script-size-guard-git-based
- prompt: active/script_sizes_snapshot_drift.md
- plan: replace the rotting `.script_sizes.json` snapshot with a git-diff truncation guard —
  `check_sizes.sh` compares each CHANGED `scripts/**/*.py` against its size at HEAD (local)
  or the PR merge-base (CI); delete the snapshot + the `--update` contract from AGENTS.md;
  add an advisory `script_size_guard.yml` to both workspaces. Design validated in planning
  with 6 controls (incl. a truncation 2 commits back caught via merge-base) and a
  zero-false-positive replay over 402/150 changed scripts of real history.
- scope-note: the original prompt named autolens_workspace only; autogalaxy_workspace has a
  BYTE-IDENTICAL check_sizes.sh and the same rot (81 stale, 5 unsnapshotted), so it is IN
  scope — human confirmed. Two PRs, one issue.
- ci-constraint: do NOT add the new workflow to `repos.yaml -> required_workflows`. That key is
  group-wide (`workspaces` = ["Smoke Tests", "Navigator Check"]) and the other five workspace
  repos have no size guard — adding it would red their Heart ws_ci gate. Guard stays advisory.
- finding: the prompt's headline count is a red herring — 212 stale sizes are near-harmless
  (worst case degrades detection from <50% to <34% of current); the 39 scripts with NO
  baseline are the entire real hole, and that count grew 12 -> 39 in three weeks.
- repos:
  - autolens_workspace: feature/script-size-guard-git-based (not yet created)
  - autogalaxy_workspace: feature/script-size-guard-git-based (not yet created)
