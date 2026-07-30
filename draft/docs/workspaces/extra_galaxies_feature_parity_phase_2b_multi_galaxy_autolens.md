# Phase 2b — extra_galaxies feature: multi_galaxy (autolens_workspace)

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Blocked-on: autolens_workspace#370 (multi-galaxy-imaging-parity) must MERGE first
Parent: draft/docs/workspaces/extra_galaxies_feature_parity.md

Phase 2b of the extra-galaxies parity task — the autolens half of phase 2, split out
2026-07-30. Phase 1 (point_source) shipped as autolens_workspace#374 / PR#376; phase 2a is
the autogalaxy half.

## Why this is blocked

`multi-galaxy-imaging-parity` (autolens_workspace#370) is in flight and rewrites
`scripts/multi_galaxy/` wholesale — 2,959 insertions across `start_here.py`, `modeling.py`,
`fit.py`, `simulator.py` plus new `likelihood_function.py` / `simulator_sample.py` /
`source_science.py`. Critically for this task, it **adds a faint extra galaxy +
`mask_extra_galaxies.fits` to `multi_galaxy/simulator.py` and an
`__Extra Galaxies Noise Scaling__` section to the core scripts**.

That is the *core-script* noise-scaling treatment; this task is the *features/* modeling
example — the same complementary split the imaging package already has. But the prose here
must reference what #370 actually lands rather than duplicate it, so write this against the
merged `multi_galaxy/`, not today's.

File overlap when it does run: `scripts/multi_galaxy/README.md` only (#370 also edits it).
`smoke_tests.txt` and `scripts/multi_galaxy/features/**` are untouched by #370.

## Scope

New `scripts/multi_galaxy/features/extra_galaxies/{README.md, __init__.py, simulator.py, modeling.py}`.

- Two co-dominant deflectors (the package's `lens_0`, `lens_1`, … loop) **plus** a lower tier
  of extra galaxies at fixed centres. The regime framing already written in
  `multi_galaxy/features/README.md:1-27` is the prose source: extra galaxies are perturbers
  *below* co-dominance, using the same tiered API that becomes the default at group scale.
- Follow the sibling `features/scaling_galaxies/` for structure and conventions —
  `dataset/multi_galaxy/extra_galaxies/`, `main_lens_centres.json` for the co-dominant pair,
  plus `extra_galaxies_centres.json` and `mask_extra_galaxies.fits` for the perturber tier.
- Rewrite the extra-galaxies bullet in `multi_galaxy/features/README.md` so it points at the
  new local example; keep the `imaging/features/extra_galaxies` pointer as the fuller API
  walkthrough.
- Update `multi_galaxy/README.md` `# Folders` if the list changes (coordinate with #370's
  edit to the same file).

## Constraints / known traps

- The new `modeling.py` should join `smoke_tests.txt` (multi_galaxy scripts are smoke-enabled:
  `autolens_workspace/smoke_tests.txt:11-14`).
- `should_simulate` tests directory EXISTENCE only — `rm -rf dataset/multi_galaxy/extra_galaxies`
  before any validation run ([[feedback_should_simulate_existence_only]]).
- **`PYAUTO_TEST_MODE=1` and `=2` share the `output/test_mode/` namespace**, so a bypass run
  silently resumes a reduced-iterations run. `rm -rf output/test_mode` before trusting a
  bypass result ([[feedback_autofit_cache_resume_pyauto_test_mode]]).
- Workspace bulk-edit rule: never whole-file `Write` a file not fully read; run
  `scripts/check_sizes.sh` before committing.
- **Navigator root-name trap** — `check_navigator.py` strips a leading `<root.name>/` prefix
  and CI clones the workspace as `workspace/`, so a literal `autolens_workspace/scripts/...`
  reference passes locally and fails in CI. Use the wildcard `autolens_workspace/*/...` form
  ([[reference_docs_ci_gotchas_workspace_assistant]]).

## Acceptance

- `simulator.py` writes its dataset + metadata from a clean dataset folder.
- `modeling.py` runs under `PYAUTO_TEST_MODE=2` / `PYAUTO_SMALL_DATASETS=1` and is added to
  `smoke_tests.txt`.
- `python .github/scripts/run_smoke.py` green; `scripts/check_sizes.sh` clean.
- Every new folder has a `README.md` + `__init__.py`; parent READMEs' `# Files` / `# Folders`
  lists updated (README ref-drift is CI-gated).
- Notebooks + navigator catalogue regenerated via PyAutoHands `generate.py autolens`.
- `group/` and `cluster/` untouched.
