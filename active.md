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

## ci-status-head-sha-without-gh
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/178 (issued 2026-08-25)
- issued: 2026-08-25
- prompt: active/read_ci_status_head_shas_without_gh.md
- status: library-dev — implemented and pushed, PR not yet opened.
- repos:
  - PyAutoHeart: branch claude/heart-evidence-gaps-6svdjk
- worktree: none — implemented from a cloud session, which has no
  ~/Code/PyAutoLabs-wt/ root; the branch is pushed, so a dev-box session can pick it up
  with a plain checkout rather than a worktree claim.

## ci-status-cloud-runs-drop-point
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/179 (issued 2026-08-25)
- issued: 2026-08-25
- prompt: active/feed_ci_status_run_conclusions_from_an.md
- status: library-dev — implemented and pushed on the same branch as #178, PR not yet opened.
- repos:
  - PyAutoHeart: branch claude/heart-evidence-gaps-6svdjk
- worktree: none — see the #178 entry above.
- note: shares a branch with #178 by design — the two halves of one no-gh path, split
  into separate prompts/issues per "one prompt = one task"; if they need separate PRs the
  #178 commit (3f57cfd) is the earlier of the two and can be split off cleanly.
