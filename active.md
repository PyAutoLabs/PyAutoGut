# Active Tasks

## transformed-message-factor-gradient-unpack
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1501 (issued 2026-08-19)
- issued: 2026-08-19
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

## autoreduce-pypi-name-collision
- issue: https://github.com/PyAutoLabs/PyAutoReduce/issues/71 (issued 2026-08-19)
- issued: 2026-08-19
- prompt: active/autoreduce_pypi_name_collision.md
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/autoreduce-pypi-name-collision
- registered: 2026-08-24 by the start_dev session (claude/pyautoreduce-312-floor-t7bmpa) — the
  prompt was filed with `Status: issued` but left in `draft/` and never registered, so it was
  carrying Lifecycle Drift; moved to `active/` and reframed here.
- reframed: 2026-08-24 — the original premise ("published autoreduce 0.9 never got the 3.12
  floor") is disproved. `autoreduce` on PyPI is ayush9pandey/AutoReduce, unrelated to PyAutoLabs;
  PyAutoReduce has zero git tags and zero references in PyAutoHands, so it has never been
  published. The real defect is that we claim a distribution name we do not own and our READMEs
  tell users to install it.
- follow-up: draft/release/pyautoreduce/pyautoreduce_release_induction.md (Hands induction +
  date versioning) — blocked until this task merges.
- pr-open: https://github.com/PyAutoLabs/PyAutoReduce/pull/72 (library) — CI green
  2026-08-24 (run 32782915519; unittest 3.12 + 3.13 pass, unittest-nojax skipped by design),
  mergeable_state clean, no review threads. Awaiting human merge.
- pr-open: https://github.com/PyAutoLabs/autoreduce_workspace/pull/1 (workspace; merges behind
  #72) — CI green 2026-08-24 (run 32783038199; workspace_smoke 3.12 + 3.13 pass, cloned the
  matching PyAutoReduce branch so the pair was exercised together), mergeable_state clean.
- environment: web-github — no local worktree; clones at /home/user/pyautoreduce and
  /home/user/autoreduce_workspace, so no `worktree:` claim beyond the recorded path.
- repos:
  - PyAutoReduce: feature/autoreduce-pypi-name-collision
  - autoreduce_workspace: feature/autoreduce-pypi-name-collision
