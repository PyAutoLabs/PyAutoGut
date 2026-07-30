# Plot guides: legacy-API removal + restructure to per-dataset plot.py

Restructure the `scripts/guides/plot/` examples in **autolens_workspace** and
**autogalaxy_workspace**: remove all legacy plot-API documentation (Visuals2D,
MatPlot, `mat_plot.py`, `plotters.py`), flatten the `examples/` folder into
`plot/`, and move dataset-specific fit plotting out into per-dataset
`plot.py` example scripts (`scripts/imaging/plot.py`, etc.). Document the
`Visualizer` at the end of each per-dataset `plot.py`. Then update
`autolens_assistant` accordingly.

## Original request (verbatim)

- Remove all mention of legacy API (e.g. Visuals2D, MatPlot, mat_plot.py)
- Keep plot/start_here.py, but dont do a fit plot, as these will move to dataset packages.
- remove examples/mat_plot.py, but any content work documenting move to plot/start_here.py. in style of other scripts, i.e. a bit more detail and explanation.
- mat_plot.py is legacy, as is plotters.py.
- I think we should keep the start_here.py, examples/
- Retain examples/plotters.py, but remove any repetition, but it has important content, also move to just plot folder.
- move searches.py to plot folder.
- retain visuals.py, but move to plot folder.
- We can now remove examples folder.
- For all dataset plots (e.g. FitImaging) we will make a scripts/imaging/plot.py example, same for interferometer, point_source, cluster, etc.
- For advanced, anticipate that pixelization will move to a plot.py example in features/pixelization and same for double_einstein_ring.
- Apply changes over both autolens workspace and autogalaxy workspace.
- for multi, make sure we can plot all datasets in one subplot in plot.py like dont in source code.
- I guess also use this opportunity to document the Visualizer in each plot.py, at the end of each, so users can use that functionality linked to Analysis.
- After all this, update autolens assistant accordingly.
- delegate where possible.

## Repos

- @autolens_workspace — `scripts/guides/plot/` restructure + new per-dataset `plot.py` scripts (imaging, interferometer, point_source, cluster, multi, …) + `features/` plot.py placement for pixelization / double_einstein_ring.
- @autogalaxy_workspace — mirror of the above for its dataset folders.
- @autolens_assistant — update skills/wiki references to the new layout after the workspace changes land.

## Notes

- `.py` scripts are canonical; notebooks are generated. Sweep ALL references
  (READMEs, navigator sidecars, `.script_sizes.json`, docs, assistant) with a
  non-extension-filtered grep before any move — path-keyed sidecars fail open
  on `git mv`.
- The multi `plot.py` must demonstrate plotting all datasets of a multi fit in
  one subplot, matching what the source-code Visualizer does.
