Removed the special `fit_quick.png` quick-update figures: `perform_quick_update`
now plots the normal fit subplot for every Analysis type, so there is only one
fit-plot layout to recognise.

- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/680 (closed)
- prs: PyAutoLens#682 (`8064fe1db`), PyAutoFit#1438 (`1d9a268a6`),
  autolens_workspace_test#241 (`6e66917`) — all merged 2026-07-31, library
  first; shipped under human-authorized Heart-RED override (unrelated nightly
  "release validation FAILED (stage integrate)")
- change: the `quick_update=True` path in the four PyAutoLens model plotters
  (imaging, interferometer, point, weak) writes the normal fit subplot and
  returns, still skipping the heavy extras (log10 / planes / tracer /
  dirty-image variants / FITS). Deleted `subplot_fit_quick` ×4 +
  `subplot_fit_combined_quick` (no callers; −256 lines; none exported via
  `aplt`). Imaging quick calls `subplot_fit` without `plane_index` so plain
  `fit.png` is always the file, any plane count. PyAutoFit
  `_DISPLAY_CANDIDATES` reduced to `("fit.png",)`. PyAutoGalaxy already
  behaved this way; PyAutoCTI never special-cased the flag.
- workspace: the three wst `*/visualization/modeling_visualization_jit.py`
  scripts assert `fit.png` instead of `fit_quick.png`; comments note quick
  updates run on the main thread by default, so their guarded KeyError
  regression would crash the search (PNG existence is a secondary signal —
  the final full visualize also writes `fit.png`).
- validation: test_autofit 1637/2 skipped; test_autolens 498 + 4 new
  `quick_update=True` routing tests (one per plotter, incl. a new
  `test_autolens/weak/model/` package). End-to-end: imaging wst script under
  the branch — quick update fired, wrote `fit.png`, no `fit_quick.png`.
- timing (loaded WSL box, load ~5): old `fit_quick` cold 199s / warm 184s vs
  new normal-subplot quick update 296s first call — cold ≈ warm, so the cost
  is recurring fit-quantity computation + rendering, NOT one-off JAX compile
  (Part-1 `fit_for_visualization` compile is ~27s and shared by both paths).
  Quick-update plotting cost is a candidate for a future profiling prompt.
- known quirk (pre-existing): weak fits write `subplot_fit_weak.png`, which
  the now-`fit.png`-only live viewer does not surface.

## Original prompt

# Remove special fit_quick.png — quick updates plot the normal fit subplot

Type: feature
Target: autolens
Repos:
- PyAutoLens
- PyAutoFit
- autolens_workspace_test
Difficulty: small
Autonomy: safe
Priority: medium
Status: draft

## Original request (verbatim)

> Remove special fit_quick.png for all types of Analysis, instead just plotting
> the normal fit, same for any other quick plot. ultimately it was annoying
> having to visually recognise two types of fit plot.

## Why

The quick-update hook (`Analysis.perform_quick_update`) writes a special
lighter-weight `fit_quick.png` for the PyAutoLens dataset types (imaging,
interferometer, point, weak), while full visualization writes `fit.png`. The
user then has to visually recognise two different fit-plot layouts for the same
fit. PyAutoGalaxy's quick path already just writes the normal `subplot_fit` —
PyAutoLens should do the same.

## What

- Quick updates output the **normal** fit subplot (`fit.png`) instead of any
  `*_quick` variant; the quick path still skips the heavy extras (log10 /
  planes / FITS / tracer / dirty-image variants).
- Delete the `subplot_fit_quick` / `subplot_fit_combined_quick` figure
  functions and the `fit_quick` filenames from the PyAutoLens plot modules and
  model plotters.
- PyAutoFit's live-display candidate list (`_DISPLAY_CANDIDATES` in
  `autofit/non_linear/quick_update.py`) reduces to `fit.png`.
- Update the `autolens_workspace_test` visualization scripts that assert
  `fit_quick.png` is produced to assert `fit.png` instead.
