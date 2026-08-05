# PyAutoHands — 238 own tests run in zero workflows; gate them on PRs

Type: test
Target: pyautohands
Repos:
- PyAutoHands
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised

Found 2026-08-05 while shipping the interferometer OOM fix
(`active/interferometer_release_leg_oom.md`, PyAutoFit#1452). Two PRs
(PyAutoHands#228, #229) merged into the repo that owns every workspace's CI
tooling **with no automated validation whatsoever** — the only checking they
got was a human running assertions by hand in a session. That is the gap this
prompt closes.

## The finding (verified, not inferred)

`PyAutoHands/tests/` holds **238 tests across 28 files**. **No workflow runs
them.** Nothing in the repo invokes `pytest tests/`.

The three workflows and what they actually do:

| Workflow | Triggers | What it runs |
|---|---|---|
| `navigator_check.yml` | `workflow_call` only | navigator + catalogue + (new) unbatched-search checks, against a **calling workspace**, never this repo |
| `python_matrix.yml` | `workflow_dispatch`, `schedule` (Mon 03:00 UTC) | `pytest` over the **five libraries** (PyAutoNerves/Array/Fit/Galaxy/Lens) × Python 3.12/3.13/3.14 — a cross-library compatibility matrix, not this repo's tests |
| `release.yml` | `workflow_dispatch` | `pytest` inside `matrix.project.path` — again the **libraries**, at release time |

Both existing `pytest` invocations were checked line by line
(`python_matrix.yml:71`, `release.yml:272`); both `cd` into a library checkout
first. Neither touches `tests/`.

So: a PR to PyAutoHands can break `env_config.py`, `check_navigator.py`,
`check_search_memory.py`, `repro_command.py` or the release-notes tooling and
**nothing will say so** — including changes that then run inside every
workspace's CI via the reusable workflow.

## Why this is worth a `high`

PyAutoHands is not a leaf. `navigator_check.yml` is `workflow_call`, so its
checkers execute in the CI of autolens_workspace, autogalaxy_workspace,
autofit_workspace, autocti_workspace, HowToLens, HowToGalaxy and HowToFit. A
regression here fails seven downstream repos, and the repo itself has no gate
to catch it first.

## Scope

Add a PR-triggered workflow that runs this repo's own test suite. Suggested
shape, but the implementer should confirm each point:

1. **New `.github/workflows/tests.yml`**, `on: [pull_request, push: main]`.
   Do *not* just add `pull_request` to `python_matrix.yml` — that job is a
   15-cell matrix that installs the entire five-library stack and would be a
   very heavy per-PR gate for a repo whose own tests are fast and stdlib-ish.
2. **Python matrix 3.12 + 3.13**, matching the definition of green used by
   every other PyAuto repo (`requires-python >=3.12`; note `python_matrix.yml`
   already probes 3.14 on its weekly run, so 3.14 is a deliberate *non*-gate).
3. **Dependencies.** `requirements.txt` currently lists only `jupyterlab`,
   `ipynb-py-convert`, `ipykernel`, `numpy<3.0.0` — **`pytest` is not
   declared anywhere**, and there is no `pyproject.toml`/`setup.py` (the
   package is run by path, not installed). Decide deliberately whether to add
   a `requirements-dev.txt`/test extra or just `pip install pytest pyyaml` in
   the workflow. Several tests need `pyyaml`; `check_search_memory.py` is
   stdlib-only on purpose.
4. **Confirm the suite actually passes on a clean runner before gating.** It
   has never run in CI, so treat a green local run as a hypothesis. Some tests
   may depend on repo-relative paths or a `tests/scripts_folder` fixture.
   `tests/test_python_matrix_workflow.py` asserts things about workflow YAML
   and may need updating when a new workflow appears.

## Traps

- **Do not gate on `python_matrix.yml`'s existing `unit_tests` job.** Its name
  is misleading: it tests the five libraries, not this repo. Renaming it is
  optional but would prevent the next person making the same misreading.
- `tests/` has no `pyproject.toml`/`pytest.ini`, so `pytest` discovery relies
  on `tests/__init__.py` and `sys.path` juggling inside the test files (they
  do `sys.path.insert(0, AUTOHANDS_DIR)`). Run from the repo root.
- Two test files currently define **zero** tests (`test_generate_markdown.py`,
  `test_script_timeout.py`). Not necessarily broken — but if the suite is
  being gated for the first time, worth a glance rather than a silent pass.

## Related, do not fold in

- The same session found that **`autofit_workspace_test` has 4 `MultiStart*`
  sites with no explicit `batch_size`**, and that the new gate does not cover
  `*_workspace_test` / `*_workspace_developer` / `autolens_profiling` (they do
  not call `navigator_check.yml`). Deliberately left: they are 1D-toy
  likelihoods and arguably testing the default on purpose. Extending gate
  coverage to the test repos is a separate decision.
- `autohands/check_search_memory.py` silently reports "no findings" when
  pointed at a repo with no `scripts/` dir (e.g. `autolens_workspace_developer`,
  whose code lives in `searches_minimal/`, `jax_profiling/`, …). Reading that
  as coverage is a real sharp edge — worth an error-or-warn on a missing
  scripts dir, but it is a checker change, not a CI change.

## Exit criteria

- A PR to PyAutoHands runs its 238 tests on 3.12 and 3.13 and blocks on
  failure.
- The suite is confirmed green on a clean runner, not just locally.
- A deliberate answer recorded for how `pytest`/`pyyaml` are provisioned.
