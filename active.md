# Active Tasks

## numba-cpu-likelihood-profiling
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/151
- status: workspace-dev
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

## markdown-renderings-2a-leftovers
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/247
- status: library-shipped, workspace-pending
- library-pr: https://github.com/PyAutoLabs/PyAutoHands/pull/248 (pending-release, OPEN — merge held for human)
- worktree: ~/Code/PyAutoLabs-wt/markdown-renderings-2a-leftovers
- prompt: active/markdown_renderings_2a_leftovers.md
- plan: Phase A add `--optimize-only` to generate_markdown.py (reuse existing
  optimize_pngs, no dpi knob); Phase B retro-optimize 405 RGBA PNGs across six
  workspaces (~88MB -> ~23MB measured); Phase C measure one ellipse fit, pre-run
  the 22 fits outside nbconvert if under a 2h ceiling then render via resume,
  else close out the yaml exclusion comment; Phase D ship library-first.
- status-detail: Phases A/B/C all DONE 2026-08-20. A: PyAutoHands 1e32e29
  (`--optimize-only` + 5 tests, 354 pass) -> PR#248. B: 66.5MB reclaimed across
  5 workspaces (91.2 -> 24.7MB, 405 PNGs); HowToLens 0 changes, no commit, its
  branch is empty. C: ellipse/modeling premise FALSIFIED — one fit is ~32s not
  hours, flat in major_axis; page rendered in 591s, added at max_minutes 120;
  also fixed 3 pre-existing broken multi/ -> multi_dataset/ index links.
  Heart at ship time: stale-85, sole reason PyAutoGalaxy rehearsal drift
  (unrelated). NOTHING MERGED — all merges held for human.
- repos:
  - PyAutoHands: feature/markdown-renderings-2a-leftovers
  - autolens_workspace: feature/markdown-renderings-2a-leftovers
  - autogalaxy_workspace: feature/markdown-renderings-2a-leftovers
  - autofit_workspace: feature/markdown-renderings-2a-leftovers
  - HowToGalaxy: feature/markdown-renderings-2a-leftovers
  - HowToFit: feature/markdown-renderings-2a-leftovers
  - HowToLens: feature/markdown-renderings-2a-leftovers
