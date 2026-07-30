# scaling_relation BGC-anchored — phase 2: interferometer + point_source

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/scaling_relation_bgc_anchored_feature_packages.md
Depends-on: draft/docs/workspaces/scaling_relation_bgc_anchored_phase_1_imaging_multi_galaxy.md

Phase 2 of 2. Read the parent for the verbatim request and verified research findings, and phase 1
for the canonical prose these two packages defer to.

These are the **mass-only** regimes, and that is the whole reason they are a separate phase: neither
can measure the luminosities its own scaling relation needs.

## Scope

`scripts/interferometer/features/scaling_relation/` and
`scripts/point_source/features/scaling_relation/`, each with `simulator.py`, `modeling.py`,
`fit.py`, `likelihood_function.py`, `README.md`, `__init__.py`.

- **interferometer** — gets `slam.py`. Foreground galaxy light is not detected at mm wavelengths, so
  `interferometer/features/extra_galaxies/slam.py` has no `light_lp` stage
  (source_lp -> source_pix_1 -> source_pix_2 -> mass_total). Its `slam.py` therefore does NOT
  measure luminosities the way phase 1's does — it loads them from ancillary optical/NIR photometry
  and says so explicitly. This is the one place the phase-1 pattern cannot be copied.
- **point_source** — no `slam.py` (per the request, and matching the tier's own precedent).
  A `PointDataset` is positions + fluxes, so there is no foreground light in the data at all:
  mass-only, luminosities from the accompanying imaging, nothing to mask or noise-scale.
  `point_source/` has no top-level `likelihood_function.py` to defer to; `point_source/fit.py` is
  where the chi-squared story lives, so defer there instead.

New datasets `dataset/interferometer/scaling_relation` and `dataset/point_source/scaling_relation`.
The point-source simulator writes the accompanying `data.fits` imaging (the extra_galaxies
point-source example's precedent) so the reader can see the galaxies the centres refer to, plus
fluxes — a quad gives only 8 positional constraints, so the information budget is tight.

## Docs register

Same as phase 1: minimal, non-CSV interface first and CSV near the end, untruncated-vs-dPIE thread
present, ladder wrap-up pointing at multi_galaxy / group. Cross-link phase 1's imaging package
rather than forking near-identical prose, but do not cross-link away the parts that genuinely
differ per regime (where luminosities come from, and the absence of foreground light).

## Housekeeping

- Register both `modeling.py` entries in `smoke_tests.txt`. Note PyAutoFit#1179 disables
  `point_source/start_here.py` for a bypass tuple-path `KeyError`, but that is script-specific —
  `point_source/features/extra_galaxies/modeling.py` passes under `PYAUTO_TEST_MODE=2` and is
  enabled, so the new point-source `modeling.py` should be too. Verify rather than assume, and
  delete any stale `output/test_mode/` first so a resumed earlier run cannot fake a pass.
- Notebooks + navigator regenerated; `scripts/check_sizes.sh` clean.

## Acceptance

- Smoke green for both `modeling.py`; both `fit.py` / `likelihood_function.py` run for real.
- Prose consistent with phase 1, with the mass-only and luminosity-provenance differences explicit.
