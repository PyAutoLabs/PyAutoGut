# Active Tasks

## sub-312-pip-install-backtracks-silently
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/238
- status: in-flight — issued 2026-08-19 by a concurrent session; this entry registered by
  the release-board session, which found the prompt in active/ with no ledger entry
  (lifecycle drift). Verify claims with the issuing session before touching repos.
- prompt: active/sub_312_pip_install_backtracks_silently.md
- repos-none-claimed: registered from the ledger side only — the issuing session owns
  any worktrees/branches; claims not recorded here to avoid conflicting with it.

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
- status: shipped-awaiting-merge — phase 1 MERGED + PUBLISHED; phase 2 PRs open, all CI green
- phase 1 (done): PyAutoHands#240 (2ddab4a) tombstone mechanism + dispatch-only publish workflow;
  PyAutoHands#242 (8724b05) --no-isolation needs setuptools explicitly on 3.12 runners.
  Tombstones 2026.7.29.1.post1 PUBLISHED to PyPI (run 32310162773) after a TestPyPI rehearsal
  (32309854365) that caught the setuptools bug at build, before any upload.
- verified on real PyPI: 3.9/3.10/3.11 pip install of all five packages fails loudly naming the
  running version; 3.12 still resolves 2026.8.17.1; autolens==2026.7.29.1 still resolves on 3.10.
  Known hole, documented not hidden: --only-binary=:all: skips sdists and still lands on the old wheel.
- phase 2 PRs (green, awaiting merge): PyAutoLens#706, PyAutoGalaxy#576, PyAutoFit#1507 (install page:
  wrong failure mode + wrong cut release 2026.4.5.3 -> 2026.7.29.2 + the yank that never happened +
  overview 3.12-3.13 -> 3.12 or later), PyAutoHeart#155 (Check B unpinned leg + release_validation),
  autogalaxy_assistant#17 (wiki said the opposite of reality; needed a --write-provenance re-stamp).
- deliberately NOT changed after checking: PyAutoCTI "3.12 or 3.13" is accurate (classifiers stop at
  3.13, never promoted); workspace AGENTS.md "3.12 and 3.13" is accurate (Heart's reusable smoke
  workflow defaults to ["3.12","3.13"], no overrides).
- follow-up filed: PyAutoReduce#71 — published autoreduce 0.9 still declares >=3.9,<=3.14.7 a fortnight
  after its floor merged; the sharp question is whether the build path assembles metadata independently
  of pyproject.toml.
- worktree: ~/Code/PyAutoLabs-wt/sub-312-install-tombstone
- repos:
  - PyAutoHands: feature/sub-312-install-tombstone (merged, branch deleted)
  - PyAutoLens: feature/sub-312-install-tombstone
  - PyAutoGalaxy: feature/sub-312-install-tombstone
  - PyAutoFit: feature/sub-312-install-tombstone
  - PyAutoHeart: feature/sub-312-install-tombstone
  - autogalaxy_assistant: feature/sub-312-install-tombstone
- prompt: active/sub_312_pip_install_backtracks_silently.md
