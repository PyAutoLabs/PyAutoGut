# Phase 2 — extra_galaxies feature: multi_galaxy (both workspaces)

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/extra_galaxies_feature_parity.md

Phase 2 of the extra-galaxies parity task.

> Adopt same style and approach for documenting extra galaxies in multi_galaxy,
> do same in autogalaxy_workspace.

Human decision 2026-07-29: **full worked example** (own simulator + own simulated dataset),
not a cross-link — matching the sibling tier `multi_galaxy/features/scaling_galaxies/`,
which already gets full-example treatment.

## Scope 2a — autolens_workspace

New `scripts/multi_galaxy/features/extra_galaxies/{README.md, __init__.py, simulator.py, modeling.py}`.

- Two co-dominant deflectors (the package's `lens_0`, `lens_1`, … loop) **plus** a lower tier
  of extra galaxies at fixed centres. The regime framing already written in
  `multi_galaxy/features/README.md:1-27` is the prose source: extra galaxies are perturbers
  *below* co-dominance, using the same tiered API that becomes the default at group scale.
- Follow the sibling `features/scaling_galaxies/` for structure and conventions —
  `dataset/multi_galaxy/extra_galaxies/`, `main_lens_centres.json` for the co-dominant pair
  (`multi_galaxy/simulator.py:311`), plus `extra_galaxies_centres.json` and
  `mask_extra_galaxies.fits` for the perturber tier.
- Rewrite the extra-galaxies bullet in `multi_galaxy/features/README.md` so it points at the
  new local example; keep the `imaging/features/extra_galaxies` pointer as the fuller API
  walkthrough. Update `multi_galaxy/README.md` `# Folders` if the list changes.

## Scope 2b — autogalaxy_workspace

`scripts/multi_galaxy/` has **no `features/` folder at all**. Create
`features/{README.md, __init__.py}` and
`features/extra_galaxies/{README.md, __init__.py, simulator.py, modeling.py}`.

- **Light-only** — PyAutoGalaxy has no mass. Extra galaxies blend with the co-equal pair and
  are either noise-scaled out or fitted with their own light model at fixed centre.
  `autogalaxy_workspace/scripts/imaging/features/extra_galaxies/` is the direct prose source.
- AG naming differs from AL: the centres file is `galaxy_centres.json`, not
  `main_lens_centres.json` (`autogalaxy_workspace/scripts/multi_galaxy/simulator.py:143-145`).
- Add a `# Folders` section to `autogalaxy_workspace/scripts/multi_galaxy/README.md`
  (it currently has none).

## Constraints / known traps

- Both `modeling.py` scripts should join `smoke_tests.txt` — multi_galaxy scripts are
  smoke-enabled in both workspaces (`autolens_workspace/smoke_tests.txt:11-14`,
  `autogalaxy_workspace/smoke_tests.txt:6-7`).
- `should_simulate` tests directory EXISTENCE only — `rm -rf dataset/multi_galaxy/extra_galaxies`
  before any validation run ([[feedback_should_simulate_existence_only]]).
- Workspace bulk-edit rule: never whole-file `Write` a file not fully read; run
  `scripts/check_sizes.sh` before committing.
- **Complementary, not overlapping, with `multi-galaxy-imaging-parity`** (planned.md, blocked
  on #366): that task adds a faint extra galaxy + `mask_extra_galaxies.fits` to
  `multi_galaxy/simulator.py` and an `__Extra Galaxies Noise Scaling__` section to
  `start_here/modeling/fit/likelihood_function` — the *core-script* noise-scaling treatment.
  This task is the *features/* modeling example. Exactly the imaging arrangement; disjoint
  files. Do not merge the two tasks.
- Parallel claim on both repos: #368 (likelihood-function-jax-pointer, in dev).
  (#366 multistart-prodigy MERGED 2026-07-29 — no longer a claim, which also UNBLOCKS the
  `multi-galaxy-imaging-parity` task in planned.md.) Human decision 2026-07-29: proceed in
  parallel — this task creates only NEW folders. Generated artifacts (`notebooks/`,
  `llms-full.txt`, `workspace_index.json`) collide; last PR to merge re-runs `generate.py`.

## Acceptance

- Each new `simulator.py` writes its dataset + metadata from a clean dataset folder.
- Each new `modeling.py` runs under `PYAUTO_TEST_MODE=2` / `PYAUTO_SMALL_DATASETS=1` and is
  added to `smoke_tests.txt`.
- `python .github/scripts/run_smoke.py` green in both workspaces; `scripts/check_sizes.sh` clean.
- Every new folder has a `README.md` + `__init__.py`; every parent README's `# Files` /
  `# Folders` list is updated (README ref-drift is CI-gated).
- Notebooks + navigator catalogue regenerated via PyAutoHands `generate.py` in both workspaces.
- `group/` and `cluster/` untouched.
