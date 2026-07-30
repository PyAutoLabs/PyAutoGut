Phase 2a of the multi_galaxy features parity arc: the `multi_gaussian_expansion`
folder. Plus the `scaling_relation/slam.py` follow-up deferred from phase 1.

**Shipped:** autolens_workspace PR**#422** merged `c473650c`, and PR**#421**
merged `dfc618da` (the follow-up). Phase 2b (pixelization) NOT started.

## Delivered

- `features/multi_gaussian_expansion/` — README, simulator, modeling, fit,
  likelihood_function, source_science, slam. Catalogue 317 -> 323.
- `features/scaling_relation/slam.py` migrated to the `shear_galaxy` idiom (the
  last holdout in the package) and re-pointed to diff against
  `multi_galaxy/slam.py`.

## Why the MGE folder needed its own dataset

`multi_galaxy/modeling.py` already uses an MGE, so the folder had to earn its
place. `simulator.py` writes a dataset whose deflectors each have TWO offset,
differently-rotated Sersic components — isophotal twists a single elliptical
Sersic provably cannot fit. On `simple` (single-Sersic deflectors) an MGE
demonstrates nothing.

## Measured

- single Sersic per deflector at each galaxy's TRUE bulge shape ~ -289,000;
  MGE 10/20/30 Gaussians ~ -4,600 / -4,490 / -4,480; truth ~ +28,000.
  **20 Gaussians is right**: 10->20 gains ~130, 20->30 gains ~8.
- Curvature matrix 41x41. Normalized: within one basis mean 0.459 / max 1.0000;
  **between the two deflectors mean 0.119 / max 0.9877**; to source mean 0.098 /
  max 0.384. Condition number ~1e24; a naive positive-negative solve returns
  **21 of 41 intensities negative**.
- The 0.9877 is the folder's point: within-basis correlation is harmless (no one
  interprets one Gaussian) but the cross-deflector one is not, because the
  per-galaxy SUM is the luminosity people quote. Single-profile equivalent is
  0.296 ([[project_multi_galaxy_features_group_parity]] phase 1).

**Log likelihoods are NOT reproducible** — the simulators use unseeded Poisson
noise, ~1-2% scatter per re-simulation. Quote them to 2 s.f. The curvature
couplings ARE stable to 4 d.p. (they depend on geometry + noise map, not the
draw). Getting this distinction wrong would have put false precision in prose.

## Three errors caught in-session

1. **The smoke auto-sim trap recurred** ([[feedback_smoke_autosim_poisons_full_res_dataset]]).
   Smoke-running `modeling.py` re-simulated `mge` at 16x16; every later
   measurement was garbage. Tell: 10 Gaussians "beat" 20, which is impossible.
   All figures re-derived after regenerating at 200x200.
2. **`slam.py` first IMPORTED the baseline's stages** to avoid ~400 duplicated
   lines. Wrong: `multi_galaxy/slam.py` is a script, so importing executes its
   whole pipeline on the `simple` dataset (verified — the import hangs). Copy,
   as every sibling does.
3. **A wrong bug diagnosis nearly became a filed issue.** See below.

## The INT_MIN bug: do NOT file it

The `IndexError: index -9223372036854775808` in
`mapper_util.adaptive_pixel_signals_from` is NOT a PyAutoArray bug. Concurrent
PR#420 (issue #419) diagnosed it correctly: `PYAUTO_TEST_MODE` makes the
preceding light stage yield no usable samples -> every luminosity is 0.0 -> the
relation evaluates `(0.0/0.0)**0.5` = NaN -> the NaN surfaces far away (INT_MIN
in the mapper under TEST_MODE=2, "cannot convert float NaN to integer" in
autofit's identifier under TEST_MODE=1). Fixed at the producer: `luminosity_from`
raises naming the cause, both slam scripts in `no_run.yaml`.

My own instrumentation refuted my "mask smaller than mesh" theory and I did not
read it: **all 3328 entries of `pix_indexes_for_sub_slim_index` were INT64_MIN
and all 3328 were marked VALID**. A geometry mismatch leaves SOME valid
mappings; zero of 3328 is the signature of NaN coordinates. Correction posted to
PR#421.

Note `interferometer/features/scaling_relation/slam` is NOT affected — it
hardcodes `luminosity_anchor` instead of measuring it.
