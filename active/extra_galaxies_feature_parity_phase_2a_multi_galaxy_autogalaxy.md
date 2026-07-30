# Phase 2a — extra_galaxies feature: multi_galaxy (autogalaxy_workspace)

Type: docs
Target: autogalaxy_workspace
Repos:
- autogalaxy_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/extra_galaxies_feature_parity.md

Phase 2a of the extra-galaxies parity task. Phase 1 (point_source) shipped as
autolens_workspace#374 / PR#376.

> Adopt same style and approach for documenting extra galaxies in multi_galaxy,
> do same in autogalaxy_workspace.

Human decision 2026-07-29: **full worked example** (own simulator + own simulated dataset),
not a cross-link — matching `autolens_workspace`'s sibling tier
`multi_galaxy/features/scaling_galaxies/`, which gets full-example treatment.

**Split decision 2026-07-30:** phase 2 was split by repo. `multi-galaxy-imaging-parity`
(autolens_workspace#370) is actively in flight in another session and rewrites
`autolens_workspace/scripts/multi_galaxy/` wholesale — 2,959 insertions across
`start_here`/`modeling`/`fit`/`simulator` plus 3 new scripts, including adding a faint extra
galaxy + `mask_extra_galaxies.fits` to `multi_galaxy/simulator.py` and an
`__Extra Galaxies Noise Scaling__` section to the core scripts. The autolens half of this
task must be written against that merged result, so it is deferred to **phase 2b**. The
autogalaxy half has **zero contention** (#370 does not touch autogalaxy_workspace) and runs
now.

## Scope

`autogalaxy_workspace/scripts/multi_galaxy/` has **no `features/` folder at all**. Create:

- `scripts/multi_galaxy/features/{README.md, __init__.py}`
- `scripts/multi_galaxy/features/extra_galaxies/{README.md, __init__.py, simulator.py, modeling.py}`

Plus: add a `# Folders` section to `scripts/multi_galaxy/README.md` (it currently has none —
its last line is a one-liner pointing at `imaging/features`).

## The shape of the example

**Light-only.** PyAutoGalaxy has no mass, so unlike the point-source phase (mass-only) and
like the autogalaxy imaging example, extra galaxies here are faint companions whose *light*
blends with the co-equal pair. Both levers exist and both should be shown, as
`autogalaxy_workspace/scripts/imaging/features/extra_galaxies/modeling.py` does:

1. **Noise scaling** — `mask_extra_galaxies.fits` + `dataset.apply_noise_scaling(mask=...)`,
   then fit the pair without the extras in the model.
2. **Modeling** — extras in the model as `ag.lp_linear.SersicSph` with `bulge.centre` fixed
   to the loaded centre (Option A), with the `ag.model_util.mge_model_from(centre_fixed=...)`
   MGE variant shown commented-out as Option B. Both are the established autogalaxy
   convention — keep them.

**What is new relative to the imaging example** is the base model: two co-equal blended
galaxies via the `galaxy_0`, `galaxy_1`, ... loop over `galaxy_centres.json`
(`multi_galaxy/modeling.py:109-122`, one `mge_model_from` per galaxy), *plus* a lower tier of
extra galaxies at fixed centres. That contrast — co-equal subjects and sub-dominant
perturbers in one model — is the point of the example, and the prose should say so.

## Conventions to match (autogalaxy differs from autolens)

- The main pair's centres file is **`galaxy_centres.json`**, not autolens's
  `main_lens_centres.json` (`multi_galaxy/simulator.py:143-145`).
- The main pair sits at `(0.0, -0.75)` / `(0.0, 0.75)` with `Sersic` bulges, and
  `modeling.py` uses `mask_radius=3.0`. A larger mask is needed to admit the extra galaxies —
  the imaging example uses 6.0" for exactly this reason.
- Imports are `ag.` / `aplt.`; scripts open with `from autogalaxy import jax_wrapper` then the
  commented `setup_notebook` line.
- Dataset path is `Path("dataset", "multi_galaxy", <name>)`.
- The new `features/README.md` should carry the autogalaxy-specific
  **"Scaling Relations (not applicable in autogalaxy)"** framing already written in
  `scripts/imaging/features/extra_galaxies/README.md:18-47` — do not imply the autolens
  scaling-relation tier transfers.

## Constraints / known traps

- The new `modeling.py` should join `smoke_tests.txt` — multi_galaxy scripts are smoke-enabled
  in this repo (`autogalaxy_workspace/smoke_tests.txt:6-7`).
- `should_simulate` tests directory EXISTENCE only — `rm -rf dataset/multi_galaxy/extra_galaxies`
  before any validation run ([[feedback_should_simulate_existence_only]]).
- **`PYAUTO_TEST_MODE=1` and `=2` share the `output/test_mode/` namespace**, so a bypass run
  silently resumes a reduced-iterations run. `rm -rf output/test_mode` before trusting a
  bypass result ([[feedback_autofit_cache_resume_pyauto_test_mode]]).
- Workspace bulk-edit rule: never whole-file `Write` a file not fully read; run
  `scripts/check_sizes.sh` before committing.
- **Navigator root-name trap** — `check_navigator.py` strips a leading `<root.name>/` prefix
  and CI clones the workspace as `workspace/`, so a literal `autogalaxy_workspace/scripts/...`
  reference passes locally and fails in CI. Use the wildcard `autogalaxy_workspace/*/...`
  form. Reproduce CI by cloning into a dir named `workspace` and passing `--root workspace`
  ([[reference_docs_ci_gotchas_workspace_assistant]]).

## Acceptance

- `simulator.py` writes its dataset + `galaxy_centres.json` + `extra_galaxies_centres.json` +
  `mask_extra_galaxies.fits` from a clean dataset folder.
- `modeling.py` runs under `PYAUTO_TEST_MODE=2` / `PYAUTO_SMALL_DATASETS=1` and is added to
  `smoke_tests.txt`.
- `python .github/scripts/run_smoke.py` green; `scripts/check_sizes.sh` clean.
- Every new folder has a `README.md` + `__init__.py`; `multi_galaxy/README.md` gains a
  `# Folders` section (README ref-drift is CI-gated).
- Notebooks + navigator catalogue regenerated via PyAutoHands `generate.py autogalaxy`.
- `cluster/` untouched.
