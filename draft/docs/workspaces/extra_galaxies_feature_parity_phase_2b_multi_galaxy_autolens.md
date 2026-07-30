# Phase 2b — extra_galaxies feature: multi_galaxy (autolens_workspace)

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Unblocked: autolens_workspace#370 MERGED and closed 2026-07-30
Parent: draft/docs/workspaces/extra_galaxies_feature_parity.md

Phase 2b of the extra-galaxies parity task — the autolens half of phase 2, split out
2026-07-30. Phase 1 (point_source) shipped as autolens_workspace#374 / PR#376; phase 2a is
the autogalaxy half.

## Now unblocked — what #370 actually landed

`multi-galaxy-imaging-parity` (autolens_workspace#370) merged and closed 2026-07-30. Verified on
`origin/main` @ `264d4ab9`:

- `scripts/multi_galaxy/` gained `likelihood_function.py`, `simulator_sample.py`,
  `source_science.py`; `modeling.py` is now 886 lines, `fit.py` 614, `start_here.py` 673.
- `simulator.py` (439 lines) adds **one** faint extra galaxy at `(2.2, 1.6)` — an
  `ExponentialSph` **light profile only, deliberately no mass**, so "the lensed source arcs are
  unchanged and the dataset remains a clean two-deflector lens for all other examples".
- It writes `mask_extra_galaxies.fits`, and `start_here`/`modeling`/`fit`/`likelihood_function`
  all carry an `__Extra Galaxies Noise Scaling__` section.
- `multi_galaxy/README.md` already has a `# Folders` section naming `features` — so this task
  does **not** need to add one (the earlier plan assumed it would).

**This settles the division of labour.** The core scripts teach the **noise-scaling lever** with a
massless contaminant. This task is the **modeling lever**: extra galaxies carried in the model with
light *and* mass, on top of N co-dominant deflectors. Exactly the imaging arrangement, and
complementary rather than duplicative — do not repeat the noise-scaling walkthrough, reference it.

The core `simulator.py` prose already raises the tier question ("telling them apart is the first
judgement you make about a multi-galaxy field — if in doubt, the test is whether it contributes
significantly to the lensing"). This example is where that judgement should be **operationalised**:
what actually goes wrong in each direction when you get it wrong.

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
