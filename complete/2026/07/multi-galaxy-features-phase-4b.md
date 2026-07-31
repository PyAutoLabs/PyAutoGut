# multi-galaxy-features-phase-4b

Phase 4b of the multi_galaxy features parity arc — `mass_stellar_dark`, the second of three sub-phases.

## Shipped

- **autolens_workspace#433** (MERGED 2026-07-31, human merge; commit `226ccf43`, merge `0e254390`).
  Issue autolens_workspace#432. 6 scripts + README, ~2010 lines.

`simulator.py` 236 / `modeling.py` 315 / `fit.py` 258 / `likelihood_function.py` 273 / `chaining.py` 291 /
`slam.py` 639. New `dataset/multi_galaxy/mass_stellar_dark`. `smoke_tests.txt` 32 -> 34. Catalogue 345 -> 351.

## THE FINDING: the prompt's claim HOLDS here (first of the last three that did)

The phase-4 prompt said tying the mass-to-light ratio across galaxies *"is what makes the decomposition
identifiable when the mass split already is not"*. Tested before writing, walking two directions at fixed total
M/L and measuring the residual curve's curvature at truth:

| Direction | Curvature |
|---|---|
| ANTI-CORRELATED — trade stellar mass between the two galaxies (the direction tying forbids) | 2.54e-03 |
| TOGETHER — both ratios move the same way (survives tying) | 3.12e-02 |
| **ratio together/anti** | **12.3x** |

The direction tying removes is ~12x flatter, so it is genuinely near-degenerate. Confirmed independently by
parameter count: `prior_count` 16 untied -> 15 tied, so the tie binds rather than merely co-priming.

Running tally across the last three phases: **ph3 shapelets motivation WRONG** (contradicted by
`imaging/features/advanced/shapelets/modeling.py`'s own `__Lens Shapelets__` section), **4a DSPL motivation
WRONG** (refuted by measurement — it is sky position, not redshift), **4b M/L-tying motivation RIGHT**. Always
test; do not assume either way.

## Other findings

- **`al.util.chaining.mass_light_dark_from` is unusable for this regime.** It reads
  `light_result.instance.galaxies.lens.<name>` — a hardcoded single-lens path — so a `lens_0`/`lens_1` model
  must build its decomposition by hand. The group pipeline does the same and says so.
- **With `lmp.Sersic` the light and the stellar mass are ONE object.** Changing a deflector's light model
  changes the deflection field, which is not true anywhere else in the package. This is why `light[1]` is more
  load-bearing in this pipeline than in the baseline: light-model error propagates directly into stellar mass.
- **The components separate in the OUTSKIRTS, not the centre.** `fit.py` prints the stellar fraction of
  `lens_0`'s deflection: 0.924 at 0.25" -> 0.854 at 0.5" -> 0.721 at 1.0" -> 0.514 at 2.0" -> 0.382 at 3.0".
  A tight mask removes exactly the pixels that constrain the decomposition. Written as a mask warning in
  `modeling.py` and `slam.py`.
- **The simulator gives the two galaxies DIFFERENT mass-to-light ratios on purpose** (0.6 and 0.4). A dataset
  simulated with a shared ratio would make the tied model correct by construction and teach nothing.
- **Dark halos are deliberately never tied.** A shared stellar population is defensible for an interacting
  pair; equal dark masses is close to asserting the mass split the regime exists to measure.
- `fit.py` verifies the summed components match the tracer's own deflection field to ~4e-16 — so the
  decomposition shown is the one the tracer actually uses.

## Heart

Shipped against the same three RED reasons the human authorized for #427, unchanged.

## Validation

Full smoke suite from a clean dataset slate, sequential: 36/36 passed. Navigator + banner checks clean.
`check_sizes.sh` OK. CI green on all five checks.
