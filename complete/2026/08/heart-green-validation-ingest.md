# heart-green-validation-ingest — COMPLETE 2026-08-19

- issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/567 (leave-open decision is human's;
  the evidence gap it tracked is closed)
- what was owed: ingest release-validation evidence into the dev box's Heart state so the
  `release validation incomplete: no rehearsal for current source` STALE reason clears.
- how it closed (NOT the run originally owed): the entry waited on Release Integrate run
  31534325304 (2026-08-11, green, artifact live until 2026-11-09). Library mains moved past it,
  so that artifact became evidence for stale source and was never ingested. Fresh evidence
  covering *current* source appeared 2026-08-19:
  - **rehearsal**: PyAutoHands `release.yml` run 32210450811 (02:58 UTC, dispatched by the
    nightly driver, rehearsal=true) — `testpypi-rehearsal-version` artifact, TestPyPI
    2026.8.19.1.dev72301, all five wheels.
  - **integrate**: PyAutoHeart `Release Integrate` run 32264548345 (14:31 UTC, human-dispatched
    first pass) — `release-stage-report`, 663 passed / 0 failed / 101 skipped, commit_shas
    matching all five library mains (Nerves b6b6ab6, Fit 21288bb, Array 74cf5a0,
    Galaxy 49115ad, Lens 6087581).
  Both artifacts were downloaded on the dev box and ingested together via
  `pyauto-brain release validate --ingest <dir>`: `validation_outcome: pass`,
  `release_ready: true`, stages `rehearse:pass, integrate:pass`.
- trap recorded: `validate --ingest` REPLACES `validation_report.json` with what the ingest
  directory contains — a rehearsal-only ingest wiped the integrate stage (commit_shas fell back
  to PyAutoHands only, totals zeroed) and readiness degraded to
  `release validation source unconfirmed (current HEADs unknown)`. Always ingest the stage
  report and the rehearsal artifact **in one directory, one call**.
- why Heart never self-served this: `heart/checks/release_run.py` auto-ingests only PyAutoHeart
  Release Integrate artifacts (`release-stage-report`); the rehearsal artifact lives on the
  PyAutoHands release run and needs the manual download+ingest above.
- residual readiness reasons at close (unrelated to this task): RED
  `autofit_workspace_test: Smoke Tests failure on main` — pip 26 resolution-too-deep, fix open
  as autofit_workspace_test PR#87; `test run status unknown` while the 2026-08-19 16:47 UTC
  workspace-smoke dispatch (run 32277952488) is in flight.
