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

## inbox-board-staleness-signal
- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/58
- issued: 2026-08-25
- prompt: active/inbox_board_staleness_signal.md
- status: ready-to-ship — both legs implemented, tested and pushed; no PR opened yet
- environment: web-github (no worktree — the session's clones: /home/user/pyautomemory,
  /home/user/PyAutoMind)
- repos:
  - PyAutoMemory: claude/inbox-board-staleness-signal-onzg34
  - PyAutoMind: claude/inbox-board-staleness-signal-onzg34
- summary: |
    Sixth in the paper-management line, split out of arxiv-inbox-pat-scope: the board's
    empty arXiv inbox reads the same whether arXiv was quiet or the filing broke.
    Fix is a `last digest: <date>` line in arxiv-inbox.md owned by inbox_actions.py
    (no new state file), rendered on the board with the staleness warning computed
    client-side — a render-time warning could never fire, since a broken digest means
    no push and the published page freezes at its last good render.
    PyAutoMind leg (beyond the prompt's stated scope, deliberate): arxiv_papers.yml must
    stamp on quiet days too, or the stamp goes stale on exactly the days it should prove
    were quiet.
    Also clearing a pre-existing red on PyAutoMemory main — 498e1a8 added a tracked
    .claude/ without adding it to ALLOWED_TOP_DIRS in validate_structure.py, so both
    `make validate` and `make test` fail on arrival.
    Done: PyAutoMemory 05aa803 (the allowlist red, separate commit) + a4c5b64 (stamp,
    board, 23 new tests — 92 green, make validate green); PyAutoMind 1bc6a47a (the
    workflow leg; YAML parses, every run block passes bash -n, 197 tests green).
    All four digest paths rehearsed against a real PyAutoMemory checkout with the
    shell blocks extracted verbatim from the workflow, and the shipped freshness JS
    cross-checked against the Python over 30 consecutive stamp dates.
    NOT fired live: claude-code-action refuses to run when arxiv_papers.yml differs
    from the default branch's copy and then exits success, so no branch dispatch can
    reach those steps — the scheduled run on main is the first genuine exercise.
