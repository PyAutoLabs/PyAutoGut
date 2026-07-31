# multi_galaxy/features: bring to group/features parity at imaging/features depth

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: large
Autonomy: supervised
Priority: normal
Status: PHASES 1 + 2 COMPLETE. Phase 3 IN FLIGHT (issue #428). REMAINING: phase 3, phase 4.
  - phase 1 SHIPPED 2026-07-30 — autolens_workspace#409 closed, PR#417 merged `f09337ea`;
    record: complete/2026/07/multi-galaxy-features-parity-phase-1.md. Plus the
    scaling_relation/slam.py follow-up, PR#421.
  - phase 2a (MGE) SHIPPED 2026-07-30 — PR#422. Catalogue 317 → 323.
  - phase 2b (pixelization core: README, modeling, fit) SHIPPED 2026-07-30 — PR#423. 323 → 325.
    Section parity follow-up PR#424.
  - phase 2c (pixelization variants: adaptive, delaunay, cpu_fast_modeling, likelihood_function,
    slam, source_science, plot) SHIPPED 2026-07-31 — issue #426, PR#427 merged `bb1f850c`;
    record: complete/2026/07/multi-galaxy-features-phase-2c.md. Catalogue 325 → 332.
  - phase 3 (advanced light) IN FLIGHT 2026-07-31 — issue #428,
    prompt active/multi_galaxy_features_group_parity_phase_3_advanced_light.md.
  - phase 4 (advanced mass) not started; prompt drafted.
  Open follow-ups from phase 2c: `features/pixelization/fit.py` over-counts its source pixels by 2
  (linear light profiles land in `inversion.reconstruction`); `__Dataset Auto-Simulation__` still
  missing on the five existing `multi_galaxy/features/*/slam.py` files (needs docstring
  restructuring, not a text insert); house-style cleanup over merged #417/#422 offered but
  unrequested.
Parent: draft/docs/autolens/multi_galaxy_package.md
Phases:
- draft/docs/workspaces/multi_galaxy_features_group_parity_phase_1_baseline_simple.md
- draft/docs/workspaces/multi_galaxy_features_group_parity_phase_2_mge_pixelization.md
- draft/docs/workspaces/multi_galaxy_features_group_parity_phase_3_advanced_light.md
- draft/docs/workspaces/multi_galaxy_features_group_parity_phase_4_advanced_mass.md

## Original request (verbatim)

> Flesh out multi_galaxy/features with all the same features as group/features, same style, level
> of detail, etc, where you can also compare to imaging/features for the same level of detail. Dont
> include potential corrections yet. Obviously lots of text to update from referring to a group to a
> multi_galaxy

## Why this task exists

The parent prompt shipped `scripts/multi_galaxy/` and its core scripts, but left the feature tier
unfinished, recording under **Remaining**:

> Extra-galaxies / pixelization feature variants remain README cross-links (the group/imaging
> feature scripts apply verbatim with the lens loop).

Its **Contents** section had always specified `features/` should hold "pixelization, MGE,
no_lens_light, following `group/features/` layout". Two of the planned folders since shipped
(`extra_galaxies` via PR#391, `scaling_relation` via PR#396); the rest are still cross-links.

## Current state (audited 2026-07-30, autolens_workspace `main` @ 2f66fab6)

`scripts/multi_galaxy/features/` holds only:

- `extra_galaxies/` — README, simulator, modeling (no `slam.py`; imaging has one)
- `scaling_relation/` — README, simulator, modeling, fit, likelihood_function, slam

`scripts/group/features/` holds five core folders plus six under `advanced/`:

| Folder | Scripts in group | Scripts in imaging |
|---|---|---|
| `linear_light_profiles` | fit, likelihood_function, modeling, slam | same 4, deeper |
| `multi_gaussian_expansion` | fit, likelihood_function, modeling, simulator, slam, source_science | same 6, deeper |
| `no_lens_light` | modeling, simulator, slam | same 3 |
| `pixelization` | adaptive, cpu_fast_modeling, delaunay, fit, likelihood_function, modeling, slam, source_science | same 8 + `plot.py`, much deeper |
| `group_halo` | modeling, simulator | (group-only) |
| `advanced/double_source_plane_lens` | chaining, fit, likelihood_function, modeling, simulator, slam | present |
| `advanced/mass_stellar_dark` | chaining, fit, likelihood_function, modeling, simulator, slam | present |
| `advanced/operated_light_profile` | modeling, simulator | present |
| `advanced/shapelets` | fit, modeling | present |
| `advanced/sky_background` | fit, modeling, simulator | present |
| `advanced/subhalo` | simulator, detect/start_here | present (+ `los_halos`) |

`group/features` is ~17.4k lines of Python; `imaging/features` ~15.5k but consistently deeper
per script (e.g. pixelization/delaunay 1518 lines vs group's 364).

## Scope decisions (confirmed with the human 2026-07-30)

1. **`group_halo` is OMITTED.** A multi-galaxy lens has no host halo by definition — this is
   already asserted in `multi_galaxy/features/README.md` and
   `multi_galaxy/features/scaling_relation/README.md`, and it is *why* the scaling tier there uses
   untruncated isothermals. Instead, `multi_galaxy/features/README.md` gains a short paragraph
   explaining that there is no analogue at this scale and pointing at `group/features/group_halo`
   as the regime boundary.
2. **`advanced/` is IN SCOPE in full** (all six folders).
3. **`potential_correction` is OUT OF SCOPE** (explicit in the request). It exists only in
   `imaging/features/advanced/`, not in `group/features/advanced/`, so this is a no-op for the
   group-parity list but must not be added opportunistically from the imaging comparison.
   `imaging/features/advanced/los_halos` is likewise not in `group/features/advanced/` — out of
   scope for the same reason.
4. **A top-level `multi_galaxy/slam.py` is added** as part of this work. `group/` has one and
   every ported `slam.py` needs a baseline to diff against ("identical to `multi_galaxy/slam.py`
   except…"), which is the relationship group's features have to `group/slam.py`. Today
   `multi_galaxy/features/scaling_relation/slam.py` has to anchor on
   `guides/modeling/slam_start_here` instead.
5. **Depth target: whichever of group/imaging is deeper**, per the request. In practice imaging is
   the deeper sibling on most folders, and `multi_galaxy/`'s own core scripts (post-#378) are
   written at imaging depth — `modeling.py` 887 lines, `likelihood_function.py` 689 — so imaging
   depth is also what keeps the package internally consistent.

## Brain routing (phase-split override recorded)

`bin/pyauto-brain feature` returned: docs / autolens_workspace, difficulty
**too-large (score 11)**, workflow **workspace**, decision **split-into-phases** — all
correct. Its *generic* phase split (`design → core_api → workspace_examples → docs`) was
**overridden**: this is pure workspace-docs work with no core-API leg, so the phases
below are content-based instead. Same failure mode as recorded on the extra_galaxies
arc — the difficulty score is a repo-count proxy and the emitted phase names are a
template, not a judgment about this task.

## Phasing

Four sequential issues/PRs. Each is independently reviewable and shippable; later phases depend on
earlier ones only for the baseline `slam.py` and README wiring.

- **Phase 1 — baseline + simple features.** `multi_galaxy/slam.py`; `features/no_lens_light`;
  `features/linear_light_profiles`; `features/extra_galaxies/slam.py` (the imaging-parity gap);
  `features/README.md` rewrite covering the full new inventory + the `group_halo` non-analogue
  paragraph.
- **Phase 2 — MGE + pixelization.** `features/multi_gaussian_expansion` (6 scripts);
  `features/pixelization` (8 scripts + `plot.py` from imaging). The largest phase by volume.
- **Phase 3 — advanced light.** `advanced/README.md`; `advanced/operated_light_profile`;
  `advanced/shapelets`; `advanced/sky_background`.
- **Phase 4 — advanced mass.** `advanced/double_source_plane_lens`;
  `advanced/mass_stellar_dark`; `advanced/subhalo`.

## Requirements applying to every ported script

- **Regime prose is rewritten, not find-replaced.** Every "group-scale" / "group lens" / "main
  lens and extra galaxies" framing must become the multi-galaxy statement: *N co-dominant
  deflectors, one free light and mass model each, no host halo, no galaxy tiers in the default
  model*. Wherever group's prose motivates a feature by "the group model contains many galaxies in
  tiers", the multi-galaxy motivation is different and must be written fresh — usually "two
  co-dominant deflectors whose mass split is degenerate", which is the package's throughline.
- **Follow the shipped multi_galaxy idioms**, not group's:
  - external shear lives in its own `shear_galaxy` at `(0.0, 0.0)`, **not**
    `shear=... if i == 0 else None` (group and cluster still use the old idiom — see
    `draft/docs/workspaces/propagate_shear_galaxy_idiom_to_group_cluster.md`);
  - main lenses are `lens_0`, `lens_1`, … built in a loop over `main_lens_centres.json`;
  - `dataset_path = Path("dataset", "multi_galaxy", dataset_name)` with the
    `al.util.dataset.should_simulate` auto-simulation block pointing at the correct simulator.
- **Mask/over-sampling numbers are multi-galaxy's, not group's.** Group uses ~7.5" masks; check
  what `multi_galaxy/modeling.py` uses and match it. Adaptive over-sampling must be applied at the
  centre of *every* deflector.
- **`__Contents__` blocks** at the top of each script, matching the house style of the
  `multi_galaxy/` core scripts.
- **A README per folder**, following the multi_galaxy README voice (the `scaling_relation` and
  `extra_galaxies` READMEs are the in-package models — a Files list, a Related list linking the
  imaging and group siblings, and a Results footer).
- **Cross-link, do not fork, where the physics is regime-independent.** Where a feature's mechanics
  are identical at galaxy scale, point at `imaging/features/<x>` for the full API walkthrough and
  keep the multi-galaxy script focused on what the second deflector changes. This is the division
  of labour the existing `multi_galaxy/features/README.md` already uses.
- **Simulators write to `dataset/multi_galaxy/**`** (gitignored — no committed binaries).

## Acceptance

- `python .github/scripts/run_smoke.py` green; new entries registered in `smoke_tests.txt`
  selectively (the file is a small curated subset — do not bulk-register every new script).
- Notebooks + navigator catalogue regenerated per phase (`generate.py` run with the workspace repo
  as CWD and the short project key `al`).
- No "group" framing left in `multi_galaxy/`: `grep -rn "group" scripts/multi_galaxy/` returns only
  deliberate up-the-ladder cross-references.
- `multi_galaxy/features/README.md` inventory matches the folders on disk.
- No `potential_correction` or `los_halos` folder created.
