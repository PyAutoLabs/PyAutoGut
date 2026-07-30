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
