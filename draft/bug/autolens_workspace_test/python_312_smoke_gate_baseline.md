---
Title: Repair the Python 3.12 campaign smoke baseline
Autonomy: supervised
Difficulty: large
---

# Repair the Python 3.12 campaign smoke baseline

## User request (verbatim)

> go one shot it all

> go

The final `go` answers the checkpoint question on PyAutoNerves issue #142:
repair the organism's existing smoke failures as prerequisite tasks, then
resume the Python >=3.12 ecosystem campaign.

## Context

Phase 1A of the Python >=3.12 campaign is implemented and locally committed in
PyAutoNerves, but its autonomous ship gate parked because 11 curated scripts in
`autolens_workspace_test` fail. A targeted control run reproduced all 11 with
identical signatures on unmodified library `main`, proving the Python-floor
diff did not introduce them. The durable evidence is recorded at:

- https://github.com/PyAutoLabs/PyAutoNerves/issues/142#issuecomment-5109079935

## Requirements

- Reproduce and classify all 11 failures by root cause before editing.
- Prefer general fixes in the owning library source over workspace-only symptom
  patches.
- Do not weaken assertions, remove curated smoke entries, inject environment
  variables, hard-code paths, add silent guards, or otherwise change code only
  to make the gate pass.
- Split independent root causes into dependency-ordered phases/issues when
  needed; keep each change reviewable and regression-tested.
- Run the affected unit suites and the six-workspace curated smoke gate with
  the relevant task worktree sourced.
- Once the smoke baseline is genuinely green, resume the parked
  `python-312-floor` task from PyAutoMind `active.md` and continue the reviewed
  ecosystem rollout.
- Autonomous work ends at PR-open. Do not merge or release without the human.

## Known failures

- `imaging/jax_likelihood/rectangular.py`
- `imaging/jax_likelihood/mge.py`
- `imaging/jax_likelihood/lp.py`
- `interferometer/jax_likelihood/rectangular.py`
- `point_source/jax_likelihood/point.py`
- `interferometer/jax_likelihood/potential_correction.py`
- `multi/jax_likelihood/mge.py`
- `interferometer/subhalo_recovery_interferometer.py`
- `multi_galaxy/composition_mge.py`
- `imaging/subhalo_recovery.py`
- `multi_galaxy/jax_likelihood/lp.py`

