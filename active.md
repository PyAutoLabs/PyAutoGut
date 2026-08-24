# Active Tasks

## wiki-currency-check-version-gate
- issue: https://github.com/PyAutoLabs/autocti_assistant/issues/25
- issued: 2026-08-24
- prompt: active/wiki_currency_check_version_gate.md
- status: workspace-dev
- location: cloud-session (web-github; no worktree — session clones under /home/user)
- repos:
  - autocti_assistant: feature/wiki-currency-check-version-gate
- summary: |
    CTI CI standardisation Phase 6, task 3 of 3. `--check-version` hashes the
    ENTIRE public surface of autoarray/autofit, so the baseline rots on every
    library main merge that exports a name.

    Design decided by the human at the two-option checkpoint: OPTION 1 —
    record the sorted symbol names in the baseline, print a real +added/-removed
    diff, exit 0 on additions-only, exit 1 on any removal. Chosen over option 2
    (demote to informational) because the baseline stores only a hash today, so
    a red prints "public API surface changed: autofit" and nothing else — which
    is exactly what cost the last session hand-built worktree diffs. Recording
    449 names (~15KB) fixes the noise AND makes every future red diagnosable.
    Caveat recorded: this would NOT have prevented the original red (both
    removed symbols were uncited) — it makes it arrive with names attached.

## heart-smoke-table-autocti
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/172
- issued: 2026-08-24
- prompt: active/heart_smoke_table_autocti.md
- status: library-dev
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
