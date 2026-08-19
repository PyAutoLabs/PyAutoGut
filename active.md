# Active Tasks

## brain-readability-pass
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/237
- status: in-dev — issued 2026-08-19, plan approved; implementing on
  PyAutoBrain feature/brain-readability-pass (PR to follow)
- prompt: active/brain_readability_pass.md
- repos:
  - PyAutoBrain: feature/brain-readability-pass
- summary: README on the Mind/Heart pattern (drifted hand copies replaced by links to
  ORGANISM.md + the generated AGENTS.md table); ORGANISM.md Nerves rename currency
  (PyAutoConf -> PyAutoNerves) + docs/example.md + skill-doc prose; AI_POLICY/CONTRIBUTING
  -> .github/; 14 merged remote branches deleted. NO dashboard (parked in research prompt).

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

## lazy-heavy-imports
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1505
- status: library-dev — issued 2026-08-19, plan approved; implementation starting
- worktree: ~/Code/PyAutoLabs-wt/lazy-heavy-imports
- repos:
  - PyAutoFit: feature/lazy-heavy-imports
  - PyAutoArray: feature/lazy-heavy-imports
  - PyAutoNerves: feature/lazy-heavy-imports
  - PyAutoGalaxy: feature/lazy-heavy-imports
  - PyAutoLens: feature/lazy-heavy-imports
- scope-note (2026-08-19): PyAutoGalaxy/PyAutoLens added mid-implementation — 8 aggregator files
  evaluate `af.Aggregator` in def-time annotations, re-triggering the sqlalchemy import the task
  removes; fix is one-line `from __future__ import annotations` headers only.
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
