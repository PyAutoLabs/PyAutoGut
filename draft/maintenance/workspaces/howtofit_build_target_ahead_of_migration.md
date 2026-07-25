# HowToFit build target registered but repo is an empty shell (no config/build/)

Type: maintenance
Target: workspaces
Repos:
- @PyAutoHands
- @HowToFit
Difficulty: easy
Autonomy: supervised
Priority: normal
Status: draft

## Finding (2026-07-25 full health sweep)

PyAutoHands `autohands/config/workspaces.yaml` registers the build target
`howtofit: {repo: HowToFit}`, and its own test
`test_workspace_config_precedence.py::test_every_build_target_owns_no_run`
asserts every registered target's repo owns `config/build/no_run.yaml`
(otherwise `run.py` raises FileNotFoundError).

PyAutoLabs/HowToFit currently contains **only a README** — the tutorial content
still lives at jammy2211/HowToFit, mid-migration. So the test FAILS whenever
HowToFit is checked out as a sibling (as a full dev box does), and passes
vacuously in CI where the sibling is absent. `pyauto-hands run howtofit` would
crash.

## Decision needed (owner call — do not resolve mechanically)

- If the migration lands soon: seed HowToFit with `config/build/no_run.yaml`
  (+ `profile_smoke.yaml`) as part of the content migration, mirroring
  HowToLens/HowToGalaxy.
- If not: de-register (or comment out) the `howtofit` target in
  workspaces.yaml until the repo is populated, so the registry reflects
  reality and the Hands test is honest.

## Acceptance

`pytest tests/test_workspace_config_precedence.py` in PyAutoHands passes with
ALL sibling repos checked out.
