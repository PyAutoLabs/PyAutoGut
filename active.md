# Active Tasks

## autocti-workspace-navigator-check
- issue: https://github.com/PyAutoLabs/autocti_workspace/issues/29
- issued: 2026-08-24
- prompt: active/autocti_workspace_navigator_check.md
- status: awaiting-merge (PR https://github.com/PyAutoLabs/autocti_workspace/pull/30 — CI running)
- location: cloud-session (web-github; no worktree — session clones under /home/user)
- repos:
  - autocti_workspace: feature/autocti-workspace-navigator-check
- summary: |
    CTI CI standardisation Phase 6, task 1 of 3 (HIGH). Add the missing
    `Navigator Check` workflow so autocti_workspace can roll up green — a
    required workflow with no runs never satisfies Heart's `all_green`, so the
    repo is permanently `in_progress`.

    Correction to the prompt's premise: the repo has NO `llms.txt`,
    `llms-full.txt` or `workspace_index.json` (git ls-files finds none). The
    catalogue must be generated and committed, else the staleness job's
    `git diff --exit-code` on untracked paths exits 0 and the check is vacuous.

    All three reusable-workflow jobs verified passing locally against main.
    PR #30 opened 2026-08-24: navigator_check.yml + generated catalogue (79
    scripts) + 12 docstring underline fixes (`-----` -> `=====`, else the
    generator catalogues a run of dashes as the summary) + AGENTS.md section.
    Heart gate: STALE (score 65) — every reason is `gh: command not found` in
    this cloud session, i.e. an organism-scope evidence gap; STALE passes the
    dev-ship gate by design. Drift-check proposal posted on issue #29.

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
