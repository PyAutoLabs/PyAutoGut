## regime-conventions-stragglers
- completed: 2026-07-25
- summary: Three consumers still on pre-split conventions after the regime reorganization merged; light-touch fixes shipped as autolens_workspace#348 + HowToLens#57 (merged 2026-07-25).

## Lifecycle note

Record backfilled 2026-08-06 (draft Status-sweep): the task shipped but its prompt never advanced out of draft/; retired here dated by ship day.

## Original prompt (regime_conventions_stragglers)

# Regime-split stragglers: consumers still on pre-split conventions

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- HowToLens
Difficulty: small
Autonomy: supervised
Priority: normal
Status: shipped 2026-07-25 (autolens_workspace#348 + HowToLens#57 merged) — awaiting lifecycle completion record
Parent: draft/docs/autolens/split_lensing_regimes.md

The post-merge Opus residual sweep (2026-07-25) found three consumers still
on pre-split conventions after the regime reorganization merged. None are
CI-visible; all need a light touch.

1. `autolens_workspace/scripts/weak/features/strong_lensing/a2744.py`
   (lines ~177-193) still uses all three superseded cluster conventions the
   merged guide repudiates: `scaling_radius_exponent = 0.5`,
   `r_cut_ref = 15.8`, and a luminosity-scaled `r_core = 0.158 * L^0.5` —
   while its own input `dataset/cluster/a2744/mass.csv` now carries the
   vanishing-core convention. no_run-skipped (SLOW), so nothing surfaces it.
   Needs the swept conventions applied + a quick science sanity check that
   the weak-lensing comparison it feeds is unaffected.
2. `HowToLens/scripts/simulator/lens_x2.py` (lines ~10-11) routes a
   two-deflector system to the `group` package — that is now precisely the
   `multi_galaxy` exemplar; update the pointer (and any surrounding prose).
3. `autolens_workspace/scripts/cluster/lenstool/parameterization_mapping.py`
   (lines ~180-191) documents Lenstool's native L^0.5 / 15.8" / 0.158"
   convention — defensibly, since its job is Lenstool interop — but never
   labels it as the legacy convention vs the modern tied exponent now used
   by `scripts/cluster/`. Add one labelling sentence.

Shipped note: all three items landed and merged same-day (weak/a2744
conventions applied — compile-clean, SLOW/no_run so GPU-validate on first
GPU session; lenstool mapping legacy label added, numeric self-checks green;
HowToLens lens_x2 rerouted to multi_galaxy, notebook regenerated).

Acceptance: smoke suite green; notebooks + navigator regenerated for any
touched workspace scripts; HowToLens smoke green on its own CI.
