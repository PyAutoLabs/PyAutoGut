Phase 5B of the Python 3.12 ecosystem-floor migration: raised all six
workspace/HowTo deployment runtimes to `python-3.12.1` as one coordinated batch.

- issue: https://github.com/PyAutoLabs/autofit_workspace/issues/125 (left open
  for explicit human close; parent python-312-floor / PyAutoNerves#142)
- prs (all merged unchanged, merge trees byte-identical to the pushed heads):
  autofit_workspace#128 (`14d878ad3`), autogalaxy_workspace#189 (`768d9e339`),
  autolens_workspace#399 (`f666e4569`), HowToFit#40 (`432a55b00`),
  HowToGalaxy#51 (`260aecae4`), HowToLens#63 (`2db766d99`)
- change: each root `runtime.txt` → exactly `python-3.12.1` + terminating
  newline (autofit was `python-3.10`, the other five `python-3.11`).
- validation (intentionally narrow per the prompt): exact-value census
  (six × 14 bytes) + `git diff --check` clean; no test sweep for
  deployment-selector lines. PR CI (navigator + smoke) green everywhere.
- the long-standing claim blockers (`extra-galaxies-multi-galaxy` on
  autogalaxy_workspace; `scaling-relation-bgc-anchored` +
  `interferometer-subhalo-to-advanced` on autolens_workspace) had all cleared
  by 2026-07-30, so the indivisible six-repo batch ran in one worktree.
- this closes the last Python-floor selector: the python-312-floor parent's
  tracked census is now fully at 3.12+.

## Original prompt

# Raise workspace deployment runtimes to Python 3.12

Type: release
Target: workspaces
Repos:
- autofit_workspace
- autogalaxy_workspace
- autolens_workspace
- HowToFit
- HowToGalaxy
- HowToLens
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Parent: python-312-floor / PyAutoNerves#142
Blocked-on: extra-galaxies-multi-galaxy releasing autogalaxy_workspace

## Scope

Complete Phase 5B of the Python 3.12 ecosystem-floor migration as one coordinated
batch. Change the root `runtime.txt` in all six listed repositories to exactly
`python-3.12.1`, preserving a terminating newline.

Do not split the batch while one repository is claimed. Do not edit workspace
scripts, notebooks, generated documentation, dependencies, or build workflows.
Validation is intentionally static and targeted: verify all six exact values and
run `git diff --check`; do not repeat the ecosystem test or smoke-test sweep for
six deployment-selector lines.

## Current census (2026-07-30)

- `autofit_workspace/runtime.txt`: `python-3.10`
- the other five `runtime.txt` files: `python-3.11`
- all six canonical checkouts are clean on `main`
- only `autogalaxy_workspace` is claimed, by `extra-galaxies-multi-galaxy`

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.
