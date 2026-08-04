- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/192 (auto-closed by the merge)
- completed: 2026-08-04
- pr: https://github.com/PyAutoLabs/PyAutoBrain/pull/193 (MERGED, squash a1e7098)
- notes: The tenant firewall reported 2 mismatches — `_hygiene_extras.py:47` hard-coding `LIB_REPOS = (PyAutoNerves, PyAutoArray, PyAutoFit, PyAutoGalaxy, PyAutoLens)` in an UNLISTED organ file, and `PyAutoLens` as a new token in the already-allowlisted `tests/test_hygiene_conductor.py`. Resolution was REFACTOR, NOT ALLOWLIST, and this is the reusable judgment: the module's own docstring already defined the set derivably ("Expected coverage is the union of every library's [optional] closure — the set mode=release guarantees"), and the scan ALREADY parsed the workflow that names them. So `smoke_roots(root)` became the step-parameterised `install_roots(root, step)`, a `RELEASE_STEP` regex was added beside `SMOKE_STEP`, and `libraries()` now derives the set from the `[mode=release]` install step of `PyAutoHeart/.github/workflows/workspace-validation.yml`, mapping each declared distribution to a checkout by `project.name` (folder names carry NO meaning). Same pattern `PyAutoHeart/heart/checks/release_run.py:46` uses. `FIREWALL_ALLOWLIST` did not grow — the 2026-07-18 tenant-firewall-drift task allowlisted 10 findings because every one was a genuine branded fact; this one was not, because the code could derive it. Side benefit beyond the firewall: a library added to the release leg is now picked up automatically instead of silently falling out of the scan.
- second-mismatch-fell-out-free: the `PyAutoLens` token was a FIXTURE DIRECTORY NAME in `_PYPROJECTS`. Once resolution keys on `project.name`, fixture dirs no longer need real repo names — renamed to `checkout_a/b/c` declaring `base-layer`/`mid-layer`/`top-layer`, which also turns the fixture into proof that folder names cannot influence the result. The fixture's `[mode=release]` step had to list all THREE (it listed 2) or `base-layer` stops counting as a library and the multi-declarer `astropy` case loses its meaning. New test `test_extras_resolves_libraries_by_distribution_not_by_folder` adds a sibling checkout the release leg never installs, with an unreachable optional dep of its own — it must not be scanned; it FAILS on the old folder-matching code.
- CONTROL TRAP (the thing to repeat): the extras scan reports `0|clean` on the UNCHANGED tree, so "clean after the refactor" proves NOTHING — a derivation returning an empty library set reads identically quiet (it would say "not scannable", but the count is 0 either way). The verification therefore asserted the DERIVED COUNT: 5 libraries, resolved autoarray→PyAutoArray, autofit→PyAutoFit, autogalaxy→PyAutoGalaxy, autolens→PyAutoLens, autonerves→PyAutoNerves. Positive control alongside it: the fixture drift (`tfp-nightly`) is still flagged, so the scan can still fail.
- verify: `repos_sync.py --check --root <branch worktree>` → tenant firewall OK (was 2 mismatches), every other manifest check OK. Heart's own producer `heart/checks/manifest_drift.run()` with `PYAUTO_ROOT=<branch worktree>` → `problem_count: 0`. Post-merge on canonical main: `repos_sync --check` → "check tenant firewall (organ code): OK" and `pyauto-brain health` → **0 real warning(s)** (was 1). Heart stays YELLOW/70 on the unrelated pre-existing workspace-validation gap (autolens interferometer/likelihood_function .py + .ipynb).
- GRADING GROUND TRUTH: `pyauto-brain health` and Heart's manifest_drift check grade the CANONICAL checkout (`PYAUTO_ROOT`), never the task worktree — so the warning provably persisted through the whole branch life and only cleared on merge. To grade a branch before merging, run `repos_sync.py --check --root <worktree>` or set `PYAUTO_ROOT=<worktree>` on `manifest_drift.run()`. Do not read a stale canonical verdict as "the fix didn't work".
- pre-existing failure (NOT ours): `PyAutoBrain/tests/test_skill_install.py::test_every_public_agent_has_a_skill_wrapper` fails — the `sizing` faculty has no `skills/sizing/SKILL.md`. Reproduced on unmodified main at a565750 before any edit. Full suite otherwise 192 passed.
- CI GAP FOUND (filed as its own draft prompt, `draft/maintenance/pyautobrain/no_pr_test_ci.md`): PyAutoBrain PRs carry **0 check runs**. The repo has only `docs.yml` (path-filtered to `docs/**`, `.readthedocs.yaml`, its own file) and `nightly-release.yml` (a cron scheduler) — so its ~193 tests run in NO CI anywhere, and a Brain PR's only gate is whatever the session runs locally. PR #193 merged with zero checks for exactly this reason, not because they were skipped.
- gh trap: this `gh` build has no `gh label` subcommand — use `gh api repos/<owner>/<repo>/labels`. `pending-release` EXISTS in PyAutoBrain but was deliberately not applied: the convention there is unlabelled (sibling PR #191, same module, carried none) and Brain is an organ repo with no PyPI release to gate on.
- API gate: running `pytest PyAutoBrain/tests/` trips the PyAuto API gate on the string `autoarray.egg` inside the test file (packaging fixtures), reported as a stale symbol. Legitimate bypass: `PYAUTO_SKIP_API_GATE=1`.
- Brain sizing (again): the Feature Agent scored this `large (8)` / split-into-phases on a one-module change, because the score is PROSE-driven and the prompt carried the whole survey. `repos_affected: pyautobrain` (one repo) was the correct signal. Override recorded in the issue, same as the mge-sigma-min `sizing-note` precedent.

## Original prompt

# Tenant firewall: _hygiene_extras.py hardcodes the library repo names

Type: bug
Target: pyautobrain
Repos:
- @PyAutoBrain
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

## Original request (verbatim)

> 6. Tenant-firewall manifest drift (clears Heart YELLOW)
>
> PyAutoHeart reports YELLOW (score 70) with one real warning: manifest
> drift, check "tenant firewall (organ code)", 2 mismatches vs
> PyAutoMind/repos.yaml.
>
>   PyAutoBrain/agents/conductors/hygiene/_hygiene_extras.py:47
>     new instance fact(s) in UNLISTED file — 'PyAutoArray', 'PyAutoFit',
>     'PyAutoGalaxy', 'PyAutoLens'
>   PyAutoBrain/tests/test_hygiene_conductor.py:547
>     new instance fact(s) in ALLOWLISTED file — 'PyAutoLens'
>
> All other manifest checks pass. Fix the firewall violation properly —
> decide whether _hygiene_extras.py should be allowlisted or should stop
> hard-coding instance names, rather than papering over it with an
> allowlist entry if the code is what's wrong. Then re-run
> `bash PyAutoBrain/bin/pyauto-brain health` and confirm the warning is gone.

## Judgment (survey done 2026-08-04, before any edit)

The code is what's wrong — **refactor, do not allowlist**.

`_hygiene_extras.py:47` hardcodes
`LIB_REPOS = ("PyAutoNerves", "PyAutoArray", "PyAutoFit", "PyAutoGalaxy",
"PyAutoLens")` (commented "Mirrors hygiene.sh's LIB_REPOS") and uses it only to
locate `<root>/<repo>/pyproject.toml`. The module's own docstring already
defines that set derivably: expected coverage is "the union of every library's
`[optional]` closure — the set `mode=release` guarantees". The scan already
parses `PyAutoHeart/.github/workflows/workspace-validation.yml` for the
`[mode=smoke]` step's `pip install` roots; the `[mode=release]` step in the same
file names the libraries. Deriving from it and resolving each declared
distribution to a checkout by `project.name` recovers exactly the five repos
(prototyped against the live workflow), drops the non-library roots
(`pynufft`, `numba`, `jax`, ...) because no checkout declares them, and single-
sources the list against the very file that defines it. This is the pattern
`PyAutoHeart/heart/checks/release_run.py:46` already uses ("derived rather than
hard-coded so the tenant firewall holds").

The second mismatch then falls out for free: `PyAutoLens` in
`tests/test_hygiene_conductor.py:547` is a *fixture directory name* in
`_PYPROJECTS`. Once the scan resolves libraries by `project.name` rather than
folder name, the fixture dirs no longer need real repo names — and neutral
names make the test prove the resolution is by pyproject name, not by folder.
No allowlist growth; the file's existing `PyAutoArray` entry stays (used by an
unrelated test at line 231).

## Scope

- `PyAutoBrain/agents/conductors/hygiene/_hygiene_extras.py` — generalise the
  step parser, derive the library set from the `[mode=release]` install step,
  delete `LIB_REPOS` and the "mirrors hygiene.sh" comment, report the resolved
  checkout dir in findings.
- `PyAutoBrain/tests/test_hygiene_conductor.py` — neutral fixture dir names;
  keep the existing extras assertions; add coverage that folder names are
  irrelevant.
- `PyAutoMind/scripts/repos_sync.py` — **unchanged** (no allowlist edit).
- `hygiene.sh`'s own `LIB_REPOS` stays: it is an allowlisted declared config
  surface used by the other hygiene modes.

## Verification

- Control (unchanged tree, 2026-08-04): `_hygiene_extras.py --root . --summary`
  -> `0|clean: the smoke install set reaches every dependency the libraries
  declare optional`. After the refactor it must still be `0|clean` **and**
  derive 5 libraries — an empty derivation would also look quiet, so assert the
  count, not just the verdict.
- `python3 PyAutoMind/scripts/repos_sync.py --check` -> tenant firewall OK.
- `pytest PyAutoBrain/tests/test_hygiene_conductor.py`.
- `bash PyAutoBrain/bin/pyauto-brain health` -> the manifest-drift warning gone.
