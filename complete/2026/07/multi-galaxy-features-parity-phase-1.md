Phase 1 of the four-phase arc bringing `scripts/multi_galaxy/features/` to
`group/features` parity at `imaging/features` depth.

**Shipped:** autolens_workspace issue #409 → PR **#417**, merged `f09337ea`
(2026-07-30). 11k+ lines. CI 5/5 green across two matrix legs.

## Delivered

- `multi_galaxy/slam.py` — the regime's SLaM baseline (5 stages), generalized
  over N deflectors: one `lens_i` per deflector in a loop, shear in its own
  `shear_galaxy`, mass centres fixed in `source_lp[1]` then released via
  `unfix_mass_centre=True` in `source_pix[1]`, `n_live` scaling with the
  deflector count.
- `features/no_lens_light/` — README, simulator, modeling, slam.
- `features/linear_light_profiles/` — README, modeling, fit,
  likelihood_function, slam.
- `features/extra_galaxies/slam.py` — the imaging-parity gap.
- `features/README.md` rewritten, incl. the `group_halo` non-analogue section.

## Decisions worth not re-deriving

**`group_halo` is omitted BY DEFINITION.** A multi-galaxy lens is defined as
co-dominant deflectors with no dominant host halo — that is what separates the
rung from `group/`, and the same fact makes the package's scaling tier
untruncated. Human-confirmed; written up in `features/README.md` as a section
rather than left as a missing folder.

**A top-level `multi_galaxy/slam.py` was warranted even though `imaging/` has
none.** imaging's feature pipelines diff straight against
`guides/modeling/slam_start_here` because at galaxy scale that composition is
already right. Multi-galaxy needs a regime baseline for the same reason
`group/slam.py` exists — four changes repeat in every stage.

## Measured, not asserted (full resolution, 11304 masked pixels)

- No-lens-light saves **4** free params (20 → 16), not the 8 the light removed:
  the mass centres must be freed because nothing marks two off-origin
  deflectors. Fixed-centre variant is 12.
- The linear solve **recovers the simulator's truth**: 1.2010 / 0.9978 against
  inputs 1.2 / 1.0. A draft claiming otherwise was wrong and was corrected.
- Normalized curvature matrix: **lens_0–lens_1 = 0.296** vs 0.135 / 0.113 to
  the source. The strongest coupling in the linear system is between the two
  deflectors — the solve mostly separates them from *each other*.
- Consequence: mis-setting `lens_0`'s `effective_radius` 0.6→0.8 moves
  **lens_1's** intensity 5.2% and the flux ratio 1.20 → 0.81 (33%), in the
  galaxy whose model was never wrong. No galaxy-scale equivalent.
- `likelihood_function.py`'s hand-computed reconstruction
  `[1.2010, 0.9978, 3.6904]` matches `FitImaging` exactly.

## Traps hit

**Smoke auto-simulation poisoned the dataset.** The `should_simulate` block
spawns the simulator inheriting the current env, so smoke-running a script
under `PYAUTO_SMALL_DATASETS=1` wrote a 15×15 dataset that every later
full-resolution run silently read (`log_likelihood = -1.5e8`, ratio 2.40 vs a
true 1.2). All numbers were re-derived after regenerating at 200×200. This is
the inverse of the usual staleness trap — your own validation creates the bad
data.

**A rename reached the merge tree but not this branch.** #416 renamed the
scaling-relation anchor BGC → "brightest galaxy" while #417 was open. The merge
was conflict-free, but the rewritten `features/README.md` was not in #416's
tree, so the retired term survived. Caught by grepping after the merge, not by
CI.

**Navigator catches forward references in `.py` docstrings, not just READMEs.**
Six cross-links to phase-2 folders failed `check_navigator.py`. In a phased arc,
point at the `imaging/` sibling until the local folder exists.

**Four concurrent branches held autolens_workspace** (#407, #408, #410, this).
`worktree_check_conflict` fired correctly. Human authorised proceeding with
mitigations: don't touch the folder another task owns; regenerate sidecars last.
Real source overlap was zero — the conflict surface is generated artifacts.
Verified the sidecar text-merge was semantically correct by regenerating and
confirming a zero diff.

## Fixed in passing

- `multi_galaxy/modeling.py` claimed "only `lens_0` carries a `shear`",
  contradicting the `shear_galaxy` section directly above it (stale since #378).
- `notebooks/group/start_here.ipynb` was stale: `b0228fe3` reverted its script
  without regenerating it.

## Open follow-ups

- `features/scaling_relation/slam.py` still uses the OLD
  `shear=... if i == 0 else None` idiom and re-derives the SLaM divergence from
  scratch; re-point it at `multi_galaxy/slam.py`. Deferred because #407 owned
  that folder during this task.
- Phases 2 (MGE + pixelization), 3 (advanced light), 4 (advanced mass) —
  prompts written in `draft/docs/workspaces/`.

Validation: every new script green under the smoke profile from a clean dataset
slate, run sequentially. `smoke_tests.txt` 20 → 22 (23 after merging main).
Catalogue 308 → 317 scripts.

## Original prompt

# multi_galaxy features parity — phase 1: SLaM baseline + simple features

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/multi_galaxy_features_group_parity.md

Phase 1 of 4. See the parent for the original request, the full audit of what
`group/features` has that `multi_galaxy/features` lacks, the scope decisions
(`group_halo` omitted, `potential_correction` and `los_halos` out), and the
**authoring rules that apply to every script in every phase** — regime motivation
rewritten rather than translated, the `shear_galaxy` idiom, the 3.0" mask, the
`__Contents__` block, the README voice, and the cross-link-don't-fork rule.

## Deliverables

- `scripts/multi_galaxy/slam.py` — the regime's SLaM baseline, playing the role
  `group/slam.py` (1086 lines) plays for the group package. Note `imaging/` has **no**
  top-level `slam.py`: its features anchor on `guides/modeling/slam_start_here`. A
  multi-galaxy baseline is warranted for the same reason group's is — the composition
  (N co-dominant deflectors in a loop, shear in its own `shear_galaxy`) diverges enough
  from `slam_start_here` that each feature's `slam.py` needs a regime-local thing to
  diff against. `features/scaling_relation/slam.py` currently has to re-explain that
  divergence from scratch; re-pointing it at the baseline is **deferred to a follow-up**
  (see "Concurrency mitigations" below) — do not touch that folder in this phase.
- `scripts/multi_galaxy/features/no_lens_light/` — `README.md`, `__init__.py`,
  `simulator.py` (writes `dataset/multi_galaxy/simple__no_lens_light`), `modeling.py`,
  `slam.py`. Sibling references: `group/features/no_lens_light` (294/273/614 lines),
  `imaging/features/no_lens_light` (289/258/403).
- `scripts/multi_galaxy/features/linear_light_profiles/` — `README.md`, `__init__.py`,
  `modeling.py`, `fit.py`, `likelihood_function.py`, `slam.py`. Reuses the existing
  `simple` dataset, so no simulator. Sibling references:
  `group/features/linear_light_profiles` (304/216/293/995),
  `imaging/features/linear_light_profiles` (400/253/680/496) — imaging is the deeper
  one on `likelihood_function`.
- `scripts/multi_galaxy/features/extra_galaxies/slam.py` — the imaging-parity gap
  (`imaging/features/extra_galaxies/slam.py`, 570 lines). The folder otherwise shipped
  in PR#391.
- `scripts/multi_galaxy/features/README.md` — rewritten. Currently it describes a
  two-folder package and tells readers that "standard single-galaxy features
  (pixelized source reconstructions, linear light profiles, MGE variations) apply to
  multi-galaxy lenses unchanged — see `imaging/features`". That paragraph is what this
  arc is deleting; replace it with the real inventory. Add the `group_halo`
  non-analogue paragraph: no host halo at this scale, which is why the scaling tier is
  untruncated, pointing at `group/features/group_halo` as the regime boundary.

## Regime motivation to write (phase-specific)

Do not reuse group's "the group model contains many galaxies in tiers" framing — the
multi-galaxy default model has no tiers.

- **no_lens_light**: at galaxy scale removing lens light is mostly a dimensionality
  win. Here it also removes the *asymmetric* absorber: with two co-dominant deflectors,
  residual unmodelled flux is soaked up unevenly by the two light models and biases the
  flux ratio, which is usually the measurement (this is the mechanism already recorded
  in the `extra_galaxies` prose). A mass-only model has nowhere to hide it.
- **linear_light_profiles**: both deflectors' `intensity` parameters leave the
  non-linear search, and — the point worth making at this scale — so do the
  `intensity`-vs-`effective_radius` degeneracies *within each* galaxy, which otherwise
  compound with the across-galaxy mass-split degeneracy the package's core scripts
  document (`multi_galaxy/modeling.py`).
- **extra_galaxies/slam.py**: where the perturber tier's centres and capped Einstein
  radii are carried through the SLaM stages, and where promoting a perturber costs
  identifiability rather than fit quality (the subtle tier error the folder's
  `modeling.py` already teaches).

## Concurrency mitigations (autolens_workspace held by two other tasks)

Registered 2026-07-30: `autolens_workspace` is concurrently claimed by
`scaling-relation-brightest-galaxy` (#407, worktree live) and
`multi-package-rename-multi-dataset` (#408). The human chose to proceed rather than
park this in `planned.md`, on two conditions:

1. **Do not touch `scripts/multi_galaxy/features/scaling_relation/`** in this phase.
   #407 owns that folder. The `slam.py` re-point at the new baseline is a follow-up
   once #407 lands. `features/README.md` may *describe* the scaling tier (it already
   does) but must not restructure that folder's own docs.
2. **Regenerate notebooks / navigator / `.script_sizes.json` LAST**, after a pre-PR
   `git merge origin/main`. #408 already flags the generated-sidecar conflict surface
   between itself and #407; regenerating after the merge resolves it mechanically
   instead of by hand.

Phase 1's substance is all new files, so source-level overlap with either task is
near zero — the conflict surface is generated artifacts and the shared README.

## Acceptance

- All new scripts green under the smoke env from a clean dataset slate
  (`PYAUTO_TEST_MODE=2`, workspace root as CWD, target `dataset/multi_galaxy/<name>`
  deleted first — `should_simulate` tests directory existence only). Run sequentially.
- Selective `smoke_tests.txt` registration only; prove new entries by the count rising.
- Notebooks + navigator catalogue regenerated (repo as CWD, project key `al`).
- `grep -rn "group" scripts/multi_galaxy/` shows only deliberate ladder cross-refs.
- `features/README.md` inventory matches the folders on disk.
