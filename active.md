# Active Tasks

## intake-declared-difficulty
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/274 (issued 2026-08-24)
- issued: 2026-08-24
- prompt: active/intake_ignores_declared_difficulty.md
- status: library-dev
- worktree: none — remote web session (`web-github`), work done in the session clones
- repos:
  - PyAutoBrain: claude/intake-declared-difficulty-icstba
  - PyAutoMind: claude/intake-declared-difficulty-icstba
- summary: |
    Third instance of one family: a conductor deriving from prose while ignoring a
    declared header key (1 = feature ranker, fixed #217; 2 = the Bug Agent's Type:
    leg, fixed in this pass; 3 = intake's Difficulty:). Per the prompt, the
    precedence rule moves INTO the sizing faculty — one `effective_difficulty`
    both conductors call — rather than being re-implemented per conductor:
    declared wins, derived level + score reported alongside on disagreement.
    Intake also reads a declaration out of unstructured raw text (the ideas.md
    "Difficulty large, supervised." idiom), keeps it out of the derived
    title/slug, and honours a declared `Type:` over prose classification.
    The prompt file on main (c1927d5) is authoritative; the session's earlier
    reconstruction of it was dropped in the merge.

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
