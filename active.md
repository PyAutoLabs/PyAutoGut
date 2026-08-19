# Active Tasks

## knowledge-board
- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/32
- status: in-dev — issued 2026-08-19, plan approved (management-first direction from the
  human); implementing on PyAutoMemory feature/knowledge-board (PR to follow)
- prompt: active/knowledge_board.md
- repos:
  - PyAutoMemory: feature/knowledge-board
- summary: management-first knowledge board (scripts/board.py, stdlib local parse; Pages +
  badge + README strip via knowledge_board.yml, nothing committed — validator bans .html):
  reading-queue/citation-TODO/maturity work queues with one-tap 📋 workflow prompts +
  /memory recall chips, contents-level only. Plus pointer-docs → .github/ (validator+spawn
  lockstep), status: draft fixes, index/bib archaeology trims, AGENTS scope-rule rewording.

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
