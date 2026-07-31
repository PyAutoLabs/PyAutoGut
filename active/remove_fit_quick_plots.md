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
