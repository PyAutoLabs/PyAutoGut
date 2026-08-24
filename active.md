# Active Tasks

## heart-smoke-table-autocti
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/172
- issued: 2026-08-24
- prompt: active/heart_smoke_table_autocti.md
- status: awaiting-merge (PR https://github.com/PyAutoLabs/PyAutoHeart/pull/173 — CI running)
- location: cloud-session (web-github; no worktree — session clones under /home/user)
- repos:
  - PyAutoHeart: feature/heart-smoke-table-autocti
- summary: |
    CTI CI standardisation Phase 6, task 2 of 3. Heart's local smoke runner has
    no autocti entry, so neither CTI suite can be run locally.

    Design decided by the human at the two-option checkpoint: the recipe is
    EXTRACTED into `.github/actions/install-arcticpy/install_arcticpy.sh`, called
    by the action via `${{ github.action_path }}` and by smoke.py from the Heart
    checkout — one file, one 2.6 pin. Trigger is an explicit per-workspace
    `arcticpy: true` key in the `smoke:` block. The local leg BUILDS arcticpy but
    NEVER runs apt: it probes for GSL headers and fails with the apt line if
    absent. Rejected: a Python leg mirroring the recipe (would undo #170).

    PR #173 opened 2026-08-24. Two findings that only came from running it:
    (1) the first GSL probe used `ls a b c`, which exits non-zero if ANY operand
    is missing, so it reported GSL absent on every machine that has it;
    (2) `pip check` can NEVER pass in a CTI environment — arcticpy declares
    numpy~=1.21 and is installed --no-deps deliberately, so the preflight
    destroyed every environment right after building it. Preflight now tolerates
    exactly that one line, only for `arcticpy: true` workspaces.
    Also found the 2.6 pin had re-acquired two copies (action.yml input default,
    and arcticpy-action.yml's `|| '2.6'` — the latter meant the self-test would
    have proven the OLD version built after a bump).
    Acceptance met: BOTH suites run locally, 3/3 PASS each. 602/602 unit tests.

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
