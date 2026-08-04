- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/194 (auto-closed by the merge)
- completed: 2026-08-04
- pr: https://github.com/PyAutoLabs/PyAutoBrain/pull/195 (MERGED, squash 1b7a23b)
- notes: PyAutoBrain had NO PR test workflow — `.github/workflows/` held only `docs.yml` (path-filtered to `docs/**` + `.readthedocs.yaml`, so it never fires for `agents/`, `bin/`, `tests/`) and `nightly-release.yml` (a cron release scheduler). Every Brain PR's head sha returned `total_count: 0` check runs, so ~190 tests covering the conductors, faculties, worktree helpers, skill install and policy seams ran in NO CI anywhere and a PR's only gate was whatever the authoring session happened to run locally. Found while shipping #193, which itself merged with zero checks. Added `.github/workflows/tests.yml` modelled on `PyAutoHeart/.github/workflows/heart-tests.yml`: push to `main` + `pull_request`, concurrency keyed on the ref with `cancel-in-progress` off main only (a cancelled main run reads as red CI — `cancelled` is in Heart's FAILURE_CONCLUSIONS), python 3.12/3.13, pytest ONLY (no `pyauto-brain <agent>` runs, no network — those need the full workspace and belong to the scheduled health/nightly drivers).
- THE LOAD-BEARING FINDING (measured before writing the workflow, not assumed): a LONE PyAutoBrain checkout does not merely fail the suite, it cannot even COLLECT it. `agents/faculties/sizing/_sizing.py` reads the body map (`BRAIN_HOME.parent / "PyAutoMind" / "repos.yaml"`) at IMPORT time and is deliberately strict, so `tests/test_policy_seams.py` and `tests/test_sizing_paths.py` raise FileNotFoundError during collection and nothing runs. The workflow therefore checks out PyAutoBrain AND PyAutoMind side by side via two `actions/checkout@v4` steps with `path:`, reproducing the workspace layout the code assumes. Both repos are public so the default GITHUB_TOKEN suffices — no PAT. Verified no other sibling repo is needed and that the entire dependency set is `pytest` + `PyYAML`. Probe method worth repeating: clone the repo alone into a scratch dir, run with `env -u PYTHONPATH HOME=<tmp>`, then add siblings one at a time until it collects — running from the full workspace HIDES this class of bug completely.
- part 2 (same PR, deliberately): `skills/sizing/SKILL.md` + `skills/sizing/agents/openai.yaml`. `test_skill_install.py::test_every_public_agent_has_a_skill_wrapper` had been RED ON MAIN (`assert ['sizing'] == []`) since #141 wired the sizing faculty into `pyauto-brain help` without a wrapper — which is exactly what no CI looks like. `sizing` is listed under "Faculties (read-only … also runnable directly)" and ships its own `sizing.sh`, and its four sibling faculties (vitals, review, memory, samplers) all carry SKILL.md + agents/openai.yaml, so the WRAPPER was the missing piece; delisting sizing from `help` would have been the wrong fix and suppressing the test worse. Splitting the two changes would have merged a knowingly-failing gate, so they landed together.
- verify: ran the suite in the EXACT two-repo layout the workflow builds (scratch copy of the branch + fresh PyAutoMind clone, `env -u PYTHONPATH`, isolated HOME) -> 193 passed. Same layout on main -> 192 passed / 1 failed, so the wrapper is what closes it. `bash bin/check_skill_line_counts.sh` -> "all 45 skills within the 200-line budget" (44 before). Live proof: PR #195 is the FIRST PyAutoBrain PR with a non-zero check count — `pytest (3.12)` + `pytest (3.13)` both green on the `pull_request` leg, and both green again on the `push | main` leg after merge (checked BOTH triggers, not just the PR).
- NOT fixed here (pre-existing, unrelated): the `Nightly Release` scheduled workflow on PyAutoBrain main shows `completed failure` for its last three runs. Surfaced while listing workflow runs; out of scope for this task, needs its own triage.
- local note: the new `/sizing` skill only appears in a session's skill list after `bash PyAutoBrain/bin/install.sh` runs (it installs from the `skills/` discovery root). Not run as part of this task — it writes to `~/.claude` / `~/.codex`.

## Original prompt

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
