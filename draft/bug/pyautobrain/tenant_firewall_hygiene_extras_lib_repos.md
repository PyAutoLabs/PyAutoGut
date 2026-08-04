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
