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

## pyautoconf-rename-leftovers
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/267
- issued: 2026-08-24
- prompt: active/pyautoconf_rename_functional_leftovers.md
- status: library-shipped, awaiting-merge
- library-pr: https://github.com/PyAutoLabs/PyAutoBrain/pull/268
- was-parked: https://github.com/PyAutoLabs/PyAutoBrain/issues/267#issuecomment-5401398548
  (supervised ship checkpoint; human signed off 2026-08-24 and the PR was opened)
- autonomy: supervised (--auto launch; effective = min(header supervised, bug cap supervised))
- gate: tests PASS (467); smoke n/a (organism repo); review CLEAN (dispositions on the
  question comment); Heart NOT EVALUATED — pyauto-heart unreachable in this web-github
  session, so no YELLOW was acknowledged and no RED was seen
- worktree: n/a — web-github session, working from the session clones
- repos:
  - PyAutoBrain: claude/pyautoconf-rename-leftovers-38ia48

## refactor-witness-map-audit
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/269
- issued: 2026-08-24
- prompt: active/refactor_witness_map_missing_autonerves.md
- status: library-shipped, awaiting-merge
- library-pr: https://github.com/PyAutoLabs/PyAutoBrain/pull/271
- autonomy: safe (--auto launch; effective = min(header safe, maintenance cap safe))
- stacked-on: PyAutoBrain#268 (same policy.yaml maps) — branch based on
  claude/pyautoconf-rename-leftovers-38ia48; merge #268 first
- gate: tests PASS (468); smoke n/a (organism repo); review CLEAN (claim
  basis-cited on the PR); Heart NOT EVALUATED — pyauto-heart unreachable in this
  web-github session
- worktree: n/a — web-github session, working from the session clones
- repos:
  - PyAutoBrain: claude/refactor-witness-map-audit
