# PyAutoBrain has no PR test CI — its ~193 tests run nowhere

Type: maintenance
Target: pyautobrain
Repos:
- @PyAutoBrain
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

Found 2026-08-04 while shipping PyAutoBrain#193 (tenant-firewall-hygiene-extras).
That PR — a refactor of the hygiene `extras` prescan plus its tests — reported
**0 check runs** on its head sha, and merged clean because there was nothing to
run, not because checks were skipped.

`PyAutoBrain/.github/workflows/` contains exactly two files:

- `docs.yml` — path-filtered to `docs/**`, `.readthedocs.yaml` and its own file,
  so it never fires for a change under `agents/`, `bin/` or `tests/`.
- `nightly-release.yml` — a `schedule:`-driven release *scheduler*; it gates
  and dispatches, it does not test this repo.

So `PyAutoBrain/tests/` (193 tests as of a1e7098, covering the conductors,
faculties, worktree helpers, skill install and policy seams) executes in **no
CI anywhere**. The only gate on a Brain PR is whatever the authoring session
chooses to run locally — which also means a session that forgets, or one
running in an environment where the suite cannot run, ships unverified.

Two knock-on facts found in the same pass:

1. `tests/test_skill_install.py::test_every_public_agent_has_a_skill_wrapper`
   is currently **failing on `main`** (the `sizing` faculty has no
   `skills/sizing/SKILL.md`). It has presumably been red for a while, which is
   exactly what no CI looks like. Fix it (or make the wrapper) as part of
   turning CI on, or the first green run is impossible.
2. Running the suite trips the PyAuto API gate on the literal `autoarray.egg`
   inside the packaging test fixtures; `PYAUTO_SKIP_API_GATE=1` is the
   legitimate bypass and any workflow will need it.

## Scope

Add a `tests.yml` running `pytest PyAutoBrain/tests/` on `pull_request` and on
push to `main`, mirroring whatever the sibling organ repos (PyAutoHeart,
PyAutoHands) already do — check those first rather than inventing a shape.
Decide whether the suite needs the full workspace checked out (several tests
build tmp_path fixtures, but some read sibling repos) and pin the environment
accordingly.

Blocked-until: the `sizing` SKILL.md failure above must be resolved for the
workflow to ever be green.
