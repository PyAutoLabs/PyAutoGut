# Active Tasks

## release-board
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/239
- status: in-dev — issued 2026-08-19, plan approved; implementing on
  PyAutoHands feature/release-board (PR to follow)
- prompt: active/release_board.md
- repos:
  - PyAutoHands: feature/release-board
- summary: phone-readable release board (API-first: release.yml runs + nightly outcomes +
  library tags + PyPI + Releases links) with one-tap 📋 /release · rehearse · validate ·
  /build chips and /bug prompts on failed train runs; Pages twin + badge + README strip;
  README on the arc pattern (stale rename banners dropped); AGENTS verb prose fixed;
  AI_POLICY/CONTRIBUTING → .github/. Past-tense record only — readiness stays the Heart's.

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

## sub-312-install-tombstone
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/238
- session: claude --resume b3ad53ad-8075-440f-af34-a01b950894fb
- status: phase-1 merged, rehearsing the publish — phase 1 of 2
- library-pr: https://github.com/PyAutoLabs/PyAutoHands/pull/240 MERGED (squash 2ddab4a); CI green
  3.12/3.13/3.14. No pending-release label: does not depend on a release, and gating it on one would
  block the fix.
- testpypi rehearsal GREEN (run 32309854365): all five tombstones live, verified by resolving on real
  3.9/3.10/3.11 (loud failure, correct version named), 3.12 (unaffected), and an exact old pin (still
  resolves). twine check PASSED on all five. First attempt 32309423898 failed at build — --no-isolation
  with no setuptools on a 3.12 runner — fixed in PyAutoHands#242 (merged 8724b05).
- next: (1) pypi publish with the confirm phrase `publish tombstones` — PERMANENT, awaiting explicit
  human go; (2) phase 2 — the three docs/installation/pip.md notes + PyAutoHeart verify_install Check B.
- worktree: ~/Code/PyAutoLabs-wt/sub-312-install-tombstone
- repos:
  - PyAutoHands: feature/sub-312-install-tombstone
- phase-2-repos-not-yet-claimed: PyAutoLens, PyAutoGalaxy, PyAutoFit (docs/installation/pip.md)
  and PyAutoHeart (verify_install Check B) are claimed via worktree_add_repo when phase 2 starts —
  deliberately not held idle while phase 1 builds and publishes the tombstones.
