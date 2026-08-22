# Parked tasks

Tasks that were started or scoped but are not currently in flight. Listed
here so they remain visible across machines instead of disappearing into
unindexed worktrees or stashes. Move an entry back to `active.md` (or to
`planned.md` if re-scoping is needed) when work resumes; on shipping,
write the dated `complete/<YYYY>/<MM>/<slug>.md` record instead.

<!-- toc:start -->

**Contents**

- [single-source-density-design](#single-source-density-design)
- [prior-message-collapse-design](#prior-message-collapse-design)
- [pyautoreduce-slacs1430-acs-comparison](#pyautoreduce-slacs1430-acs-comparison)
- [pyautonerves-release-for-regime-stamp](#pyautonerves-release-for-regime-stamp)

<!-- toc:end -->

## single-source-density-design
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1500 (open — the parked design hub)
- prompt: active/12_single_source_density_refactor.md
- parked: 2026-08-18 — **human-confirmed deferral** of the design decision (census wrap-up chat).
  The bundled 12+13 design issue is filed with full evidence and four decision asks
  (one-hierarchy-vs-two, #1498 logpdf contract, EP-mixin scope, prompt-14 sequencing); nothing is
  blocked by deferring — bugs are fixed and the #1497/#1499 property sweep (134 tests, merged
  `21288bb`) guards current behaviour regardless.
- classification: refactor design (PyAutoFit); DESIGN ONLY — no code until #1500 is answered.
- resume: answer the decisions on #1500, move this back to active.md, cut stage-1 as its own task
  (Distribution sibling layer, Gaussian family first, property tests as the safety net).
- note: bug/priors/15 (#1498 — TransformedMessage.logpdf missing Jacobian) is a LIVE wrong answer,
  not part of this deferral; it can be fixed standalone once the contract is picked.
- repos-none-claimed: claims no repos while parked.

## prior-message-collapse-design
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1500 (shared — bundled with single-source-density-design)
- prompt: active/13_collapse_prior_and_message.md
- parked: 2026-08-18 — same human-confirmed deferral; prompt 13 is the hierarchy-collapse half of
  the #1500 bundle. Resume and retire together with single-source-density-design.
- repos-none-claimed: claims no repos while parked.

## pyautoreduce-slacs1430-acs-comparison
- prompt: active/pyautoreduce_slacs1430_acs_comparison.md
- parked: 2026-08-08 — surfaced by the orphaned-prompt triage; STATE UNVERIFIED
- classification: test (PyAutoReduce + autolens_assistant)
- why unverified: the comparison targets a collaborator dataset at
  `/mnt/c/Users/Jammy/Science/subhalo/dataset/slacs/slacs1430+4105`, which this session cannot
  see. Confirm from the laptop whether the reduction and parity fits were ever run.

## pyautonerves-release-for-regime-stamp
- status: PARKED — ready to release, but NOT runnable from a cloud/web session
- blocks: PyAutoNerves#153/#154 (the SMALLDAT regime stamp) is merged but INERT until released.
  autoarray's floor `autonerves>=2026.8.22.1` is the newest release on PyPI and predates the
  stamp, so a PyPI-installed autoarray sees no card and falls back to the shape heuristic.
- unreleased on nerves main: 8 commits, PRs #154 (stamp) and #155 (header comment). Both
  change FITS bytes, so one release covers both.
- WHY NOT FROM HERE — three of the release's own instruments are blind in a web session,
  verified 2026-08-22 rather than assumed:
  1. `pyauto-heart readiness` returns **STALE**, every reason "status unknown". It shells out
     to `gh api` for CI status (`heart/checks/ci_status.sh:45`) and `gh` is not installed —
     this session's GitHub access is via MCP tools, not a gh credential. It also scans 25
     repos under $PYAUTO_MAIN; only 12 exist here, at scattered paths.
  2. `PyAutoBrain/bin/version_drift.sh` reports "No stamps resolved — cannot assess
     consistency", same root cause.
  3. The release chain ends in `autohands pre_build` dispatching `release.yml`; PyAutoHands
     is not attached to the session.
  Running `/release --force` here would force past a gate that never measured anything. The
  gate would be fabricated, not passed.
- WHERE TO RUN IT: a local workspace with the full ~/Code/PyAutoLabs checkout, gh
  authenticated, and autohands on PATH — i.e. the CLI, not a cloud session.
- ALSO STILL UNRUN: the workspace smoke suite has never exercised any of the five merged PRs,
  all of which change what every FITS the stack writes looks like. Worth a run before
  publishing to PyPI.
- AFTER the release: `draft/maintenance/libraries/bump_autoarray_autonerves_floor_after_stamp_release.md`
  — bumping autoarray's floor is what makes the stamp non-optional for fresh installs.
