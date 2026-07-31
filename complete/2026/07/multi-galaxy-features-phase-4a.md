# multi-galaxy-features-phase-4a

Phase 4a of the multi_galaxy features parity arc — `double_source_plane_lens`, the first of three sub-phases
that close it.

## Shipped

- **autolens_workspace#431** (MERGED 2026-07-31, human merge; commit `977b4842`, merge `9bde8882`).
  Issue autolens_workspace#430. 6 scripts + README, ~2160 lines.

| File | Lines | group sibling |
|---|---|---|
| `simulator.py` | 257 | 222 |
| `modeling.py` | 337 | 276 |
| `fit.py` | 271 | 248 |
| `likelihood_function.py` | 274 | 242 |
| `chaining.py` | 319 | 298 |
| `slam.py` | 703 | 717 |

New `dataset/multi_galaxy/dspl` dataset. `advanced/README.md` and `features/README.md` inventories updated.
`smoke_tests.txt` 30 -> 32 (`modeling.py` + `chaining.py`). Catalogue 339 -> 345.

## Phase 4 split

Phase 4 measured **~5174 lines across 15 scripts** at implementation time — larger than all of phase 2 was,
and phase 2 was itself split for that reason. Human-confirmed 2026-07-31 to split one folder per PR:
**4a `double_source_plane_lens`** (this), 4b `mass_stellar_dark`, 4c `subhalo`. The arc-closing checks in the
phase-4 prompt run at the end of **4c**, not each sub-phase.

## THE FINDING: the prompt's DSPL regime claim is WRONG, and it was measured

The phase-4 prompt said the folder's prose should lead with *"two source planes give the extra constraint that
breaks the multi-galaxy mass-split degeneracy — the ratio of deflections at two redshifts depends on the mass
distribution, not just the total."*

Tested before writing any of it. Perturb the mass split at FIXED total Einstein radius; compare how each source
plane's image-plane light responds (curvature of the residual curve at the truth, each plane normalised by its
own flux):

| Configuration | plane-1 / plane-0 sensitivity to the split |
|---|---|
| Baseline (source_1 offset in sky position, source_0 has mass) | **8.17** |
| Control 1 — source_1 moved to source_0's sky position | **0.89** |
| Control 2 — source_0 made MASSLESS, offset kept | **17.48** |
| Control 3 — both removed | 1.48 |

Same sky position kills the effect. Removing the multi-plane mass structure STRENGTHENS it. So:

**The extra mass-split constraint comes from the second source sitting at a DIFFERENT SKY POSITION**, so its
ring's images sample the deflection field where the first source's images do not reach. It is NOT the redshift
ratio and NOT the multi-plane structure. The extra redshift is what constrains cosmology; the extra sky
position is what constrains the mass split. The scripts keep the two benefits explicitly separate.

Consequences baked into the folder: `simulator.py` offsets `source_1` deliberately and says why; `modeling.py`
insists the mask contain both rings; `slam.py`'s mass stage is identified as the one that pays off.

Independent confirmation inside the shipped code: `likelihood_function.py` prints the ratio of the
plane-1→plane-2 deflection to the image→plane-1 deflection, which spans ~0.001 to ~28 across the grid — so the
second trace is demonstrably not a constant rescaling of the first.

**This is the second phase running where the prompt's stated motivation did not survive checking** (phase 3's
shapelets claim was contradicted by `imaging/features/advanced/shapelets/modeling.py`'s own `__Lens Shapelets__`
section). Check 4b's and 4c's stated motivations the same way.

## Other findings

- **`al.model_util.mge_from` does not exist** — only `mge_model_from`, which returns an `af.Model`. A concrete
  (non-model) fit builds its basis by hand from `al.lp_linear.Gaussian` wrapped in `al.lp_basis.Basis`, which is
  what the group DSPL `fit.py` does too.
- **Group is the deeper sibling on every DSPL file except `simulator.py`** (222 vs imaging's 196), so group tier
  was the plain rule here — no judgement call needed, unlike phases 2c and 3.
- **Terminology verified** against `imaging/features/advanced/double_source_plane_lens`: "double source-plane
  lens (DSPL)", morphology kept as "appear as two distinct Einstein rings", no retired names anywhere.
- **`slam.py` has six stages, not five** — the extra one (`source_lp[2]`) introduces `source_1` and
  `source_0`'s mass on the full mask, with the deflectors held from stage 1. The second ring cannot be found
  while the first is still being solved.
- **Two masks, deliberately.** Stage 1 / search 1 uses a 1.6" mask that excludes the second ring, so `source_1`
  is invisible rather than merely un-modelled and cannot bias the deflectors with residuals they absorb. The
  small mask is the point, not an approximation.

## Heart

Shipped against the same three RED reasons the human authorized for #427, unchanged: `release validation FAILED
(stage integrate)`; `manifest drift: tenant firewall (organ code)` (hardcoded `'PyAutoLabs'` at
`PyAutoHeart/heart/checks/release_run.py:42`); `test run status unknown (no report.json)`.

## Validation

Full smoke suite from a clean dataset slate, sequential: 34/34 passed. Navigator path + banner checks clean.
`check_sizes.sh` OK. CI green on all five checks.
