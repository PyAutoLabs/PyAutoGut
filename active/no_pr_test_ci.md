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

**Both parts land together** — the workflow can never be green while the suite
is red, so splitting them would merge a knowingly-failing gate.

1. Add `PyAutoBrain/skills/sizing/SKILL.md` (+ `agents/openai.yaml`), mirroring
   the sibling faculty wrappers `vitals/`, `samplers/`, `memory/`, `review/`.
   `sizing` is listed under "Faculties (read-only … also runnable directly)" in
   `pyauto-brain help` and has its own `sizing.sh`, so the wrapper is the
   missing piece — delisting it from `help` would be the wrong fix.
2. Add `PyAutoBrain/.github/workflows/tests.yml`, modelled on
   `PyAutoHeart/.github/workflows/heart-tests.yml` (push to `main` +
   `pull_request`, concurrency cancel on PR refs only, python 3.12/3.13).

**Measured 2026-08-04, not assumed:** a lone-repo checkout cannot even COLLECT
— `agents/faculties/sizing/_sizing.py` reads `PyAutoMind/repos.yaml` at import
time and is deliberately strict, so `test_policy_seams.py` and
`test_sizing_paths.py` error out. The workflow must therefore check out
**PyAutoBrain + PyAutoMind side by side** (`BRAIN_HOME.parent/PyAutoMind`);
both repos are public, so the default `GITHUB_TOKEN` suffices. With that layout
the suite is 192 passed / 1 failed (the sizing wrapper) in ~30s, and needs only
`pytest` + `PyYAML`. No other sibling repo is required.
