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

## autofit-plot-functions-kwargs
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1523
- issued: 2026-08-24
- prompt: active/plot_functions_discard_kwargs.md
- status: library-shipped, workspace-pending
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1524
- workspace-pr: https://github.com/PyAutoLabs/autofit_workspace/pull/148 (blocked on the library PR by the library-first gate)
- env: web-github (no local worktree; clones at /home/user/pyautofit + /home/user/autofit_workspace, venv /home/user/.venv-af on py3.12)
- repos:
  - PyAutoFit: claude/autofit-plot-functions-kwargs-vvwj5x
  - autofit_workspace: claude/autofit-plot-functions-kwargs-vvwj5x
- summary: |
    Routed by /start_dev in a web-github session (branch
    claude/autofit-plot-functions-kwargs-vvwj5x). Fix direction approved by the
    human: forward **kwargs with a strict signature filter (unrecognised names
    raise TypeError), not plain forwarding and not dropping **kwargs.
    Scope also covers a second silent defect found during verification:
    corner_cornerpy passes weight_list= to corner.corner, which has no such
    parameter (it is weights), so sample weights are ignored on every weighted
    corner plot. Approved for the same PR.
    Brain bug agent + sizing faculty both scored this too-large (13) and advised
    phasing; overridden deliberately — the score is inflated by prompt word
    count plus the multi-repo flag. Library PR merges first, workspace PR
    follows behind the library-first gate.
    Implemented and pushed 2026-08-24. PyAutoFit 8cdcff3: forward-with-strict-filter
    (PlotKwargsError + checked_kwargs in plot_util), the weight_list=/weights= fix,
    anesthetic kwargs split between make_2d_axes and plot_2d, mle traces forward Line2D
    properties. Full suite 2088 passed / 36 skipped. autofit_workspace: the four plot
    scripts' kwarg lists rewritten to genuine corner.py arguments (15 wrong-library names
    removed, zeus's list rebuilt), prose corrected, notebooks regenerated.
    Shipped 2026-08-24: PyAutoFit#1524 and autofit_workspace#148, both labelled
    pending-release. Gate was the per-repo pytest fallback (pyauto-heart is not
    available in this web-github session): full suite 2089 passed / 36 skipped on a
    clean serial run. Merge is human — library PR first, then the workspace PR.
    Next: /prm to watch CI and close out.
