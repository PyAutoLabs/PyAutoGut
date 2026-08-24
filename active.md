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

## aplt-output-drift-remaining-repos
- issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/585
- issued: 2026-08-24
- session: https://claude.ai/code/session_01LN2Qsx6JjVKV45o17EKGtB (remote/web — no `--resume` id)
- status: library-dev
- environment: web-github — no task worktree; work happens in the session clones
  (`/home/user/pyautogalaxy`), venv at `/home/user/venv312` (Python 3.12, a CI leg).
  Deliberately no `worktree:` field: claiming a `~/Code/PyAutoLabs-wt/` path that
  will never exist is what the resume check treats as drift.
- repos:
  - PyAutoGalaxy: feature/aplt-output-drift-remaining-repos
- summary: |
    Planned and issued by /start_dev; implementation not started. Classification
    is **both** — PyAutoGalaxy (library) merges first under the library-first
    gate, euclid_strong_lens_modeling_pipeline (workspace) behind it.

    Scope changed materially from the prompt during planning, on verified
    evidence:
      * autocti.plot exports no Output (49-line __init__), so the prompt's
        "unverified, may be correct as written" hedge resolves to *broken* —
        but 18 of the 31 broken files are under legacy/, which
        autocti_workspace_test/AGENTS.md:52 forbids editing, and the other 13
        (top-level imaging_ci/) are 2023-era heritage the 2026-07-17 "CTI
        resurrection Phase 5" sweep missed. autocti_workspace_test is therefore
        OUT of scope; a follow-up prompt proposes sweeping imaging_ci/ into
        legacy/ (decide against PyAutoCTI#82).
      * A library defect the prompt did not mention: al.Scribbler's cmap=
        parameter (autogalaxy/gui/scribbler.py:77-82) needs a Cmap-shaped
        object, but Cmap is exported by no public plot namespace. Fixing it
        library-side is what pulls PyAutoGalaxy in as primary repo.
      * euclid has 3 broken files, not the 2 the prompt lists
        (extra_galaxies_mask_gui.py also uses aplt.Cmap).

    /start_library ran 2026-08-24: PyAutoGalaxy claimed on
    feature/aplt-output-drift-remaining-repos.

    Exploration found a SECOND instance of the same library defect, in
    PyAutoGalaxy itself: autogalaxy/gui/clicker.py:31 calls aplt.Cmap(...) on
    autoarray.plot, which exports no Cmap — so Clicker.start() raises
    AttributeError for every caller (worse than Scribbler, which at least works
    when cmap=None). Same bug, same fix locus, adjacent file; folded into
    Phase 1 rather than shipping a half-fix.

    Next step: implement Phase 1, then /ship_library; /start_workspace for
    euclid follows behind the library-first merge gate.
