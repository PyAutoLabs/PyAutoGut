# Active Tasks

## arcticpy-install-standardisation
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/170
- issued: 2026-08-24
- prompt: active/arcticpy_install_standardisation.md
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/arcticpy-install-standardisation
- repos:
  - PyAutoHeart: feature/arcticpy-install-standardisation
  - autocti_workspace_test: feature/arcticpy-install-standardisation
  - autocti_assistant: feature/arcticpy-install-standardisation
  - PyAutoCTI: feature/arcticpy-install-standardisation
  - autocti_workspace: feature/arcticpy-install-standardisation
- summary: |
    One canonical Heart-owned arcticpy install step (a composite action at
    .github/actions/install-arcticpy), consumed by every CTI repo, replacing four
    divergent shell copies. Audit corrected the prompt's site list: PyAutoCTI has no
    recipe of its own (its main.yml is a thin caller of Heart's lib-tests.yml, which
    carries two copies), and smoke_install.sh is not one runner-image change from
    breaking — Heart's smoke-tests.yml installs setuptools immediately before calling
    it. The real defect is that implicit cross-repo coupling, plus four documented
    recipes that are incomplete for a clean venv (PyAutoCTI/AGENTS.md omits Cython
    as well as setuptools). Build-wheel caching deliberately deferred as a measured
    follow-up rather than an assumed win.

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
